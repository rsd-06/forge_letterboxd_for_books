import json
import logging
import time
import uuid
import requests
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, Http404
from django.views.decorators.http import require_POST
from django.db.models import Q, Avg, Count
from django.core.exceptions import PermissionDenied, SuspiciousOperation

from .models import (
    Book, ReadList, ReadListItem, RatingReview, ReviewComment,
    Friendship, Activity, UserProfile, FAQ, SupportTicket
)
from .openlibrary import search_open_library, get_or_create_book_from_ol
from .gemini_service import chat_with_gemini, get_ai_recommendations_for_user, is_gemini_configured, create_support_ticket, ERROR_CODES_GUIDE
from .mongo_service import (
    log_chat_to_mongo, log_chat_feedback_to_mongo, log_user_crud_to_mongo,
    log_book_crud_to_mongo, get_mongo_stats
)

logger = logging.getLogger(__name__)


def home(request):
    """
    Main landing dashboard: Letterboxd style.
    Shows featured books, friend activity stream, popular reviews,
    and embedded FAQs on the landing page.
    """
    popular_books = Book.objects.order_by('-ratings_count', '-average_rating')[:8]
    recent_reviews = RatingReview.objects.select_related('user', 'book', 'user__profile').prefetch_related('comments', 'comments__user').order_by('-created_at')[:6]

    activities = []
    if request.user.is_authenticated:
        following_ids = list(Friendship.objects.filter(from_user=request.user).values_list('to_user_id', flat=True))
        following_ids.append(request.user.id)
        activities = Activity.objects.filter(user_id__in=following_ids).select_related(
            'user', 'user__profile', 'book', 'review', 'readlist', 'target_user'
        ).order_by('-created_at')[:15]
    else:
        activities = Activity.objects.select_related(
            'user', 'user__profile', 'book', 'review', 'readlist', 'target_user'
        ).order_by('-created_at')[:10]

    # Minimum of 10 FAQs displayed on landing page and home page
    landing_faqs = FAQ.objects.filter(is_active=True).order_by('order')[:12]

    context = {
        'popular_books': popular_books,
        'recent_reviews': recent_reviews,
        'activities': activities,
        'landing_faqs': landing_faqs,
        'is_gemini_configured': is_gemini_configured(),
    }
    return render(request, 'books/home.html', context)


def faq_view(request):
    """
    Dedicated FAQ page displaying minimum 10 FAQs stored in SQL database.
    """
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    faqs = FAQ.objects.filter(is_active=True)
    if query:
        faqs = faqs.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    if category:
        faqs = faqs.filter(category=category)

    categories = FAQ.CATEGORY_CHOICES

    context = {
        'faqs': faqs,
        'query': query,
        'current_category': category,
        'categories': categories,
        'total_faqs_count': FAQ.objects.count(),
    }
    return render(request, 'books/faq.html', context)


def book_search(request):
    """
    Search books locally and from Open Library (3rd-party API with timeout & fallback).
    """
    query = request.GET.get('q', '').strip()
    local_books = []
    ol_results = []

    if query:
        local_books = list(Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(genre__icontains=query)
        )[:10])

        ol_results = search_open_library(query, limit=12)

        local_keys = {b.openlibrary_key for b in local_books if b.openlibrary_key}
        local_titles = {b.title.lower() for b in local_books}
        ol_results = [
            r for r in ol_results
            if r.get('openlibrary_key') not in local_keys and r.get('title', '').lower() not in local_titles
        ]

    context = {
        'query': query,
        'local_books': local_books,
        'ol_results': ol_results,
    }
    return render(request, 'books/search.html', context)


def book_detail(request, book_id=None, ol_key=None):
    """
    Detail page for a specific book.
    """
    book = None
    if book_id:
        book = get_object_or_404(Book, pk=book_id)
    elif ol_key:
        book = get_or_create_book_from_ol(ol_key)

    user_review = None
    user_shelves_with_book = set()
    if request.user.is_authenticated:
        user_review = RatingReview.objects.filter(user=request.user, book=book).first()
        user_shelves_with_book = set(
            ReadListItem.objects.filter(readlist__user=request.user, book=book).values_list('readlist_id', flat=True)
        )

    reviews = book.reviews.select_related('user', 'user__profile').prefetch_related(
        'comments', 'comments__user', 'comments__user__profile'
    ).order_by('-created_at')

    ratings_dist = {
        5: book.reviews.filter(rating__gte=4.5).count(),
        4: book.reviews.filter(rating__gte=3.5, rating__lt=4.5).count(),
        3: book.reviews.filter(rating__gte=2.5, rating__lt=3.5).count(),
        2: book.reviews.filter(rating__gte=1.5, rating__lt=2.5).count(),
        1: book.reviews.filter(rating__lt=1.5).count(),
    }

    context = {
        'book': book,
        'user_review': user_review,
        'reviews': reviews,
        'ratings_dist': ratings_dist,
        'user_shelves_with_book': user_shelves_with_book,
        'rating_choices': [
            (5.0, '5.0 ★★★★★ Masterpiece'),
            (4.5, '4.5 ★★★★½ Outstanding'),
            (4.0, '4.0 ★★★★ Great'),
            (3.5, '3.5 ★★★½ Very Good'),
            (3.0, '3.0 ★★★ Good'),
            (2.5, '2.5 ★★½ Average'),
            (2.0, '2.0 ★★ Okay'),
            (1.5, '1.5 ★½ Mediocre'),
            (1.0, '1.0 ★ Poor'),
        ]
    }
    return render(request, 'books/book_detail.html', context)


@login_required
@require_POST
def log_or_rate_book(request, book_id):
    """
    Create or update rating & review for book, with spoiler checkbox.
    Audits operation to MongoDB.
    """
    book = get_object_or_404(Book, pk=book_id)
    rating_val = request.POST.get('rating')
    review_text = request.POST.get('review_text', '').strip()
    contains_spoilers = request.POST.get('contains_spoilers') in ['on', 'true', 'True', '1']

    if not rating_val:
        messages.error(request, "Please provide a star rating out of 5.")
        return redirect('book_detail', book_id=book.id)

    try:
        rating_decimal = Decimal(rating_val)
        if not (Decimal('0.5') <= rating_decimal <= Decimal('5.0')):
            raise ValueError()
    except (ValueError, Exception):
        messages.error(request, "Invalid rating value.")
        return redirect('book_detail', book_id=book.id)

    review, created = RatingReview.objects.update_or_create(
        user=request.user,
        book=book,
        defaults={
            'rating': rating_decimal,
            'review_text': review_text,
            'contains_spoilers': contains_spoilers,
        }
    )

    act_type = 'reviewed' if review_text else 'rated'
    Activity.objects.create(
        user=request.user,
        activity_type=act_type,
        book=book,
        review=review
    )

    # MongoDB CRUD audit log
    log_book_crud_to_mongo('RATE_REVIEW', {
        'username': request.user.username,
        'book_title': book.title,
        'book_id': book.id,
        'rating': float(rating_decimal),
        'has_review': bool(review_text),
        'contains_spoilers': contains_spoilers,
    })

    read_shelf = ReadList.objects.filter(user=request.user, list_type='read').first()
    if read_shelf:
        ReadListItem.objects.get_or_create(readlist=read_shelf, book=book)

    messages.success(request, f"Logged rating for '{book.title}' ({rating_decimal}★)!")
    return redirect('book_detail', book_id=book.id)


@login_required
@require_POST
def toggle_readlist_item(request, book_id):
    """
    Add or remove book from a shelf. Audits to MongoDB.
    """
    book = get_object_or_404(Book, pk=book_id)
    readlist_id = request.POST.get('readlist_id')
    readlist = get_object_or_404(ReadList, pk=readlist_id, user=request.user)

    existing = ReadListItem.objects.filter(readlist=readlist, book=book).first()
    if existing:
        existing.delete()
        added = False
        messages.info(request, f"Removed '{book.title}' from {readlist.name}.")
    else:
        ReadListItem.objects.create(readlist=readlist, book=book)
        added = True
        Activity.objects.create(
            user=request.user,
            activity_type='shelved',
            book=book,
            readlist=readlist
        )
        messages.success(request, f"Added '{book.title}' to {readlist.name}!")

    log_book_crud_to_mongo('SHELF_TOGGLE', {
        'username': request.user.username,
        'book_title': book.title,
        'shelf_name': readlist.name,
        'action': 'added' if added else 'removed',
    })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'ok', 'added': added, 'readlist_id': readlist.id})

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'book_detail'
    return redirect(next_url if next_url != 'book_detail' else 'book_detail', book_id=book.id)


@login_required
@require_POST
def add_review_comment(request, review_id):
    """
    Add a comment to someone's review. Audits to MongoDB.
    """
    review = get_object_or_404(RatingReview, pk=review_id)
    comment_text = request.POST.get('comment_text', '').strip()

    if comment_text:
        comment = ReviewComment.objects.create(
            review=review,
            user=request.user,
            comment_text=comment_text
        )
        log_book_crud_to_mongo('ADD_COMMENT', {
            'username': request.user.username,
            'review_id': review.id,
            'book_title': review.book.title,
            'comment': comment_text[:100],
        })
        messages.success(request, "Comment posted successfully!")
    else:
        messages.error(request, "Comment cannot be blank.")

    return redirect('book_detail', book_id=review.book.id)


def readlists_view(request, username=None):
    if username:
        target_user = get_object_or_404(User, username=username)
    elif request.user.is_authenticated:
        target_user = request.user
    else:
        return redirect('login')

    is_owner = (request.user == target_user)
    if is_owner:
        readlists = ReadList.objects.filter(user=target_user)
    else:
        readlists = ReadList.objects.filter(user=target_user, is_public=True)

    readlists = readlists.annotate(item_count=Count('items')).prefetch_related('items__book')

    context = {
        'target_user': target_user,
        'readlists': readlists,
        'is_owner': is_owner,
    }
    return render(request, 'books/readlists.html', context)


def readlist_detail(request, username, slug):
    target_user = get_object_or_404(User, username=username)
    is_owner = (request.user == target_user)

    readlist = get_object_or_404(ReadList, user=target_user, slug=slug)
    if not readlist.is_public and not is_owner:
        raise PermissionDenied("This readlist is private.")

    items = readlist.items.select_related('book').order_by('-added_at')

    context = {
        'readlist': readlist,
        'target_user': target_user,
        'items': items,
        'is_owner': is_owner,
    }
    return render(request, 'books/readlist_detail.html', context)


@login_required
def create_readlist(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_public = request.POST.get('is_public') in ['on', 'true', 'True', '1']

        if not name:
            messages.error(request, "Please enter a name for your list.")
            return redirect('create_readlist')

        new_list = ReadList.objects.create(
            user=request.user,
            name=name,
            description=description,
            list_type='custom',
            is_default=False,
            is_public=is_public,
        )
        log_book_crud_to_mongo('CREATE_SHELF', {
            'username': request.user.username,
            'shelf_name': new_list.name,
            'is_public': is_public
        })
        messages.success(request, f"Created readlist '{new_list.name}'!")
        return redirect('readlist_detail', username=request.user.username, slug=new_list.slug)

    return render(request, 'books/create_readlist.html')


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_self = (request.user == profile_user)

    is_following = False
    if request.user.is_authenticated and not is_self:
        is_following = Friendship.are_friends(request.user, profile_user)

    reviews = RatingReview.objects.filter(user=profile_user).select_related('book').order_by('-created_at')
    shelves = ReadList.objects.filter(user=profile_user, is_public=True if not is_self else None).annotate(item_count=Count('items'))

    read_shelf = ReadList.objects.filter(user=profile_user, list_type='read').first()
    books_read_count = read_shelf.items.count() if read_shelf else reviews.count()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0.0

    following_count = Friendship.objects.filter(from_user=profile_user).count()
    followers_count = Friendship.objects.filter(to_user=profile_user).count()

    ai_recs = get_ai_recommendations_for_user(profile_user)

    context = {
        'profile_user': profile_user,
        'is_self': is_self,
        'is_following': is_following,
        'reviews': reviews[:10],
        'shelves': shelves,
        'books_read_count': books_read_count,
        'avg_rating': round(avg_rating, 2),
        'following_count': following_count,
        'followers_count': followers_count,
        'ai_recs': ai_recs,
        'is_gemini_configured': is_gemini_configured(),
    }
    return render(request, 'books/profile.html', context)


@login_required
@require_POST
def toggle_friend(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.warning(request, "You cannot follow yourself.")
        return redirect('user_profile', username=username)

    friendship = Friendship.objects.filter(from_user=request.user, to_user=target).first()
    if friendship:
        friendship.delete()
        action = 'UNFOLLOW'
        messages.info(request, f"Unfollowed {target.username}.")
    else:
        Friendship.objects.create(from_user=request.user, to_user=target)
        Activity.objects.create(
            user=request.user,
            activity_type='friended',
            target_user=target
        )
        action = 'FOLLOW'
        messages.success(request, f"You are now following {target.username}!")

    log_user_crud_to_mongo('FRIENDSHIP_TOGGLE', {
        'from_user': request.user.username,
        'to_user': target.username,
        'action': action,
    })

    return redirect('user_profile', username=username)


def community(request):
    users = User.objects.exclude(id=request.user.id if request.user.is_authenticated else -1).annotate(
        review_count=Count('reviews')
    ).order_by('-review_count', '-date_joined')[:24]

    following_set = set()
    if request.user.is_authenticated:
        following_set = set(Friendship.objects.filter(from_user=request.user).values_list('to_user_id', flat=True))

    context = {
        'community_users': users,
        'following_set': following_set,
    }
    return render(request, 'books/community.html', context)


def ai_assistant(request):
    """
    Interactive Bookboxd Gemini AI Assistant Page & API endpoint.
    Answers from FAQ data, explains error codes, creates support tickets, and logs to MongoDB.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            history = data.get('history', [])
            session_id = data.get('session_id')
        except Exception:
            message = request.POST.get('message', '').strip()
            history = []
            session_id = None

        if not message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        result = chat_with_gemini(message, history=history, user=request.user, session_id=session_id)
        return JsonResponse(result)

    recent_faqs = FAQ.objects.filter(is_active=True).order_by('order')[:6]
    return render(request, 'books/ai_assistant.html', {
        'is_gemini_configured': is_gemini_configured(),
        'recent_faqs': recent_faqs,
        'error_codes': ERROR_CODES_GUIDE,
    })


@require_POST
def submit_chat_feedback(request):
    """
    Save chat feedback to MongoDB.
    """
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id', str(uuid.uuid4()))
        rating = data.get('rating', 5)
        feedback_text = data.get('feedback', '')
        log_chat_feedback_to_mongo(
            chat_id=chat_id,
            user_id=request.user.id if request.user.is_authenticated else None,
            rating=rating,
            feedback_text=feedback_text
        )
        return JsonResponse({'status': 'ok', 'message': 'Feedback logged to MongoDB.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def support_ticket_view(request):
    """
    Support tickets page: create and view support tickets stored in SQL.
    """
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        guest_email = request.POST.get('email', '').strip()
        priority = request.POST.get('priority', 'medium')

        if not subject or not message:
            messages.error(request, "Subject and message are required.")
            return redirect('support_tickets')

        ticket = create_support_ticket(
            subject=subject,
            message=message,
            user=request.user if request.user.is_authenticated else None,
            email=guest_email,
            priority=priority
        )
        messages.success(request, f"Support Ticket #{ticket.ticket_id} created successfully!")
        return redirect('support_tickets')

    tickets = []
    if request.user.is_authenticated:
        tickets = SupportTicket.objects.filter(user=request.user)
    else:
        tickets = SupportTicket.objects.all()[:10]

    return render(request, 'books/support_tickets.html', {
        'tickets': tickets,
    })


def health_check(request):
    """
    Health check page: verifies SQL database, MongoDB status, Gemini API,
    and 3rd-party Open Library API with strict 3.0s time limit and fallback.
    """
    # 1. SQL Database Check
    sql_ok = False
    sql_books_count = 0
    try:
        sql_books_count = Book.objects.count()
        sql_ok = True
    except Exception as e:
        logger.error(f"SQL health check failed: {e}")

    # 2. MongoDB Check
    mongo_stats = get_mongo_stats()

    # 3. Gemini API Check
    gemini_ready = is_gemini_configured()

    # 4. Third-Party API with Time Limit and Fallback (Open Library)
    third_party_status = "Online"
    third_party_latency_ms = 0
    try:
        t0 = time.time()
        # Strict 3.0s timeout requirement
        res = requests.get("https://openlibrary.org/search.json?q=dune&limit=1", timeout=3.0)
        third_party_latency_ms = round((time.time() - t0) * 1000, 1)
        if res.status_code != 200:
            third_party_status = f"Degraded (HTTP {res.status_code})"
    except requests.Timeout:
        third_party_status = "Timed out (>3.0s) — Fallback to local catalog active"
    except Exception as e:
        third_party_status = f"Unreachable ({str(e)[:40]}) — Fallback active"

    health_data = {
        'status': 'healthy' if sql_ok else 'degraded',
        'sql_database': {
            'status': 'Connected' if sql_ok else 'Error',
            'books_count': sql_books_count,
            'faqs_count': FAQ.objects.count() if sql_ok else 0,
            'tickets_count': SupportTicket.objects.count() if sql_ok else 0,
        },
        'mongodb': mongo_stats,
        'gemini_ai': {
            'is_configured': gemini_ready,
            'model': getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash'),
        },
        'third_party_api': {
            'name': 'Open Library Search API',
            'status': third_party_status,
            'timeout_limit': '3.0s',
            'latency_ms': third_party_latency_ms,
            'fallback_strategy': 'Local Book Database & Curated Classics',
        },
        'version': '1.0.0-beta',
    }

    if request.GET.get('format') == 'json' or request.headers.get('accept') == 'application/json':
        return JsonResponse(health_data)

    return render(request, 'books/health_check.html', {'health': health_data})


def error_code_explorer(request, code=None):
    """
    Error code explorer page explaining all 8 required error codes
    (400, 401, 403, 404, 422, 429, 500, 503) with interactive simulation triggers.
    """
    if code:
        if code == 400:
            return HttpResponseBadRequest("400 Bad Request — Simulated by Error Code Explorer. The request was invalid or malformed.")
        elif code == 401:
            return HttpResponse("401 Unauthorized — Authentication is required to access this resource.", status=401)
        elif code == 403:
            raise PermissionDenied("403 Forbidden — You do not have permission to perform this action.")
        elif code == 404:
            raise Http404("404 Not Found — Simulated missing book or page.")
        elif code == 422:
            return HttpResponse("422 Unprocessable Entity (Site-Specific) — The book data or rating failed validation checks.", status=422)
        elif code == 429:
            return HttpResponse("429 Too Many Requests — Rate limit exceeded. Please wait 30 seconds before submitting more reviews.", status=429)
        elif code == 500:
            raise Exception("500 Internal Server Error — Simulated unexpected server glitch for verification.")
        elif code == 503:
            return HttpResponse("503 Service Unavailable — External book database is currently undergoing maintenance.", status=503)

    return render(request, 'books/error_codes.html', {
        'error_codes': ERROR_CODES_GUIDE,
    })


def custom_404_view(request, exception=None):
    """
    Custom 404 Not Found error page with an 'Ask the assistant' option.
    """
    context = {
        'path': request.path,
        'ask_assistant_query': f"I received a 404 Not Found error trying to visit {request.path}. How can I find this book or page?",
    }
    return render(request, '404.html', context, status=404)


def custom_500_view(request):
    """
    Custom 500 Internal Server Error page with an 'Ask the assistant' option.
    """
    context = {
        'ask_assistant_query': "I encountered an internal 500 server error on Bookboxd. Can you explain what happened and file a support ticket?",
    }
    return render(request, '500.html', context, status=500)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'books/register.html')

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'books/register.html')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'books/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)

        # Audit CRUD to Mongo
        log_user_crud_to_mongo('REGISTER_USER', {'username': username, 'email': email})

        messages.success(request, f"Welcome to Bookboxd, {username}! Your shelves are ready.")
        return redirect('home')

    return render(request, 'books/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            log_user_crud_to_mongo('LOGIN_USER', {'username': username})
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'books/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        log_user_crud_to_mongo('LOGOUT_USER', {'username': request.user.username})
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')
