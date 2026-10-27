import json
import logging
import os
import re
import uuid
from decimal import Decimal
from django.conf import settings
from .models import Book, RatingReview, ReadList, ReadListItem, FAQ, SupportTicket
from .mongo_service import log_chat_to_mongo

logger = logging.getLogger(__name__)

ERROR_CODES_GUIDE = {
    '400': '400 Bad Request — The server could not understand the request due to invalid syntax or missing required parameters.',
    '401': '401 Unauthorized — You must be logged in with a valid Bookboxd account to view this resource.',
    '403': '403 Forbidden — You do not have permission to access or edit this resource (e.g. attempting to edit another user’s private shelf or review).',
    '404': '404 Not Found — The requested book, user profile, or page does not exist or may have been removed.',
    '422': '422 Unprocessable Entity (Site-Specific) — The book data or rating format submitted failed validation checks.',
    '429': '429 Too Many Requests — You have exceeded the rate limit. Please pause for a moment before searching or making more requests.',
    '500': '500 Internal Server Error — An unexpected glitch occurred on our server. Our team has been notified.',
    '503': '503 Service Unavailable — The server or external database (such as Open Library) is temporarily overloaded or undergoing maintenance.'
}


def get_genai_client():
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    if not api_key:
        return None, None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash') or 'gemini-2.5-flash'
        return client, model
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini Client: {e}")
        return None, None


def is_gemini_configured():
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    return bool(api_key and api_key.strip() and not api_key.startswith('YOUR_'))


def build_system_prompt_with_faqs():
    faqs = FAQ.objects.filter(is_active=True).order_by('order')[:15]
    faq_text = "\n".join([f"Q: {f.question}\nA: {f.answer}" for f in faqs])

    errors_text = "\n".join([f"• {code}: {desc}" for code, desc in ERROR_CODES_GUIDE.items()])

    prompt = f"""You are "The Bibliophile" — the official AI assistant for Bookboxd (a Letterboxd-inspired web app for books with Goodreads warmth).
Your primary duties:
1. Answer literary questions, give book recommendations, and discuss reading themes.
2. Answer questions about Bookboxd using the knowledge base below.
3. Explain HTTP error codes whenever asked.
4. If a user has a problem you cannot resolve or explicitly requests support/ticket, offer to create or confirm a Support Ticket.

KNOWLEDGE BASE (FAQs):
{faq_text}

SUPPORTED ERROR CODES:
{errors_text}

Rules:
- Be warm, bookish, helpful, and concise.
- Format answers using clean Markdown with bolding and bullet points.
- If you cannot answer a technical issue, tell the user you can file a support ticket for them.
"""
    return prompt


def create_support_ticket(subject, message, user=None, email='', priority='medium'):
    """
    Store support ticket in SQL database.
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    ticket = SupportTicket.objects.create(
        ticket_id=ticket_id,
        user=user if (user and user.is_authenticated) else None,
        guest_name=user.username if (user and user.is_authenticated) else 'Guest Reader',
        guest_email=email or (user.email if (user and user.is_authenticated) else ''),
        subject=subject[:250],
        message=message,
        priority=priority,
        created_by_ai=True,
    )
    return ticket


def chat_with_gemini(message, history=None, user=None, session_id=None):
    """
    Handle user query, with FAQ knowledge, error code explanation, ticket generation,
    and MongoDB logging.
    """
    session_id = session_id or str(uuid.uuid4())
    client, model_name = get_genai_client()

    # Check if user query asks for support ticket creation or contains unanswerable frustration
    msg_lower = message.lower()
    needs_ticket = any(kw in msg_lower for kw in [
        'create a ticket', 'create ticket', 'file a ticket', 'open a ticket',
        'contact support', 'talk to human', 'report a bug', 'support ticket', 'file ticket'
    ])

    if needs_ticket:
        ticket = create_support_ticket(
            subject=f"Support Request: {message[:60]}",
            message=message,
            user=user
        )
        reply = (
            f"🎫 **Support Ticket Created: #{ticket.ticket_id}**\n\n"
            f"I have filed a formal support ticket for your issue in our database.\n\n"
            f"• **Ticket ID:** `{ticket.ticket_id}`\n"
            f"• **Status:** Open\n"
            f"• **Subject:** *\"{ticket.subject}\"*\n\n"
            "Our support team will review this shortly. You can also view and track tickets on the **Support & Tickets** page!"
        )
        log_chat_to_mongo(session_id, user.id if (user and user.is_authenticated) else None,
                          user.username if (user and user.is_authenticated) else 'guest',
                          message, reply, is_live_ai=False)
        return {
            'response': reply,
            'is_live_ai': False,
            'ticket_id': ticket.ticket_id,
            'model': 'bookboxd-ticket-bot'
        }

    # Check for direct error code lookup in query
    for code, desc in ERROR_CODES_GUIDE.items():
        if f"error {code}" in msg_lower or f"code {code}" in msg_lower or f"{code} error" in msg_lower or msg_lower.strip() == code:
            reply = (
                f"ℹ️ **Explanation of HTTP Error {code}:**\n\n"
                f"{desc}\n\n"
                f"• **Recommended Action:** If you encountered this error while using Bookboxd, "
                f"check our **Error Codes & Diagnostics** page or ask me to *create a support ticket* if the issue persists!"
            )
            log_chat_to_mongo(session_id, user.id if (user and user.is_authenticated) else None,
                              user.username if (user and user.is_authenticated) else 'guest',
                              message, reply, is_live_ai=False)
            return {'response': reply, 'is_live_ai': False, 'model': 'faq-engine'}

    # If live Gemini client is available
    if client:
        try:
            system_prompt = build_system_prompt_with_faqs()
            full_prompt = f"{system_prompt}\n\n"
            if history:
                for h in history[-4:]:
                    role = "User" if h.get('sender') == 'user' else "Assistant"
                    full_prompt += f"{role}: {h.get('text')}\n"
            full_prompt += f"User: {message}\nAssistant:"

            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
            )
            if response and response.text:
                resp_text = response.text
                log_chat_to_mongo(session_id, user.id if (user and user.is_authenticated) else None,
                                  user.username if (user and user.is_authenticated) else 'guest',
                                  message, resp_text, is_live_ai=True)
                return {
                    'response': resp_text,
                    'is_live_ai': True,
                    'model': model_name
                }
        except Exception as e:
            logger.error(f"Gemini live error: {e}")

    # Fallback response using SQL FAQ match or smart rules
    fallback_res = get_smart_fallback_with_faqs(message, user)
    log_chat_to_mongo(session_id, user.id if (user and user.is_authenticated) else None,
                      user.username if (user and user.is_authenticated) else 'guest',
                      message, fallback_res['response'], is_live_ai=False)
    return fallback_res


def get_smart_fallback_with_faqs(message, user=None):
    msg_lower = message.lower()

    # Search in FAQ table
    faqs = FAQ.objects.filter(is_active=True)
    for faq in faqs:
        # Match keywords in question
        words = [w.lower() for w in re.findall(r'\w+', faq.question) if len(w) > 3]
        if any(w in msg_lower for w in words):
            reply = f"📖 **From our FAQ Database:**\n\n**{faq.question}**\n\n{faq.answer}"
            return {'response': reply, 'is_live_ai': False, 'model': 'sql-faq-matched'}

    # Check for general themes
    if 'error' in msg_lower or 'code' in msg_lower:
        reply = (
            "🛠️ **HTTP Error Codes on Bookboxd:**\n\n"
            "We handle and explain 8 key error codes:\n"
            "• **400 Bad Request** — Malformed query\n"
            "• **401 Unauthorized** — Login required\n"
            "• **403 Forbidden** — Permission denied\n"
            "• **404 Not Found** — Missing book or page\n"
            "• **422 Unprocessable Entity** — Book metadata validation failed\n"
            "• **429 Rate Limited** — Too many requests\n"
            "• **500 Server Error** — Internal server error\n"
            "• **503 Unavailable** — Maintenance or upstream timeout\n\n"
            "Need more help? Type **'create a ticket'** and I'll file a support ticket for you!"
        )
        return {'response': reply, 'is_live_ai': False, 'model': 'error-guide'}

    # If completely unanswerable, offer ticket creation
    ticket = create_support_ticket(
        subject=f"Unresolved AI Query: {message[:50]}",
        message=f"User asked: '{message}' — AI could not find an exact match in FAQs.",
        user=user,
        priority='low'
    )
    reply = (
        f"I couldn't find an exact match for *\"{message}\"* in our FAQ database, so I went ahead and created a support ticket for our team:\n\n"
        f"🎫 **Ticket #{ticket.ticket_id} Logged**\n"
        f"• **Status:** Open\n"
        f"• Our moderators and librarians will review this.\n\n"
        "In the meantime, feel free to check the **FAQ page** or explore popular book recommendations!"
    )
    return {'response': reply, 'is_live_ai': False, 'ticket_id': ticket.ticket_id, 'model': 'auto-ticket'}


def get_ai_recommendations_for_user(user):
    """
    Generate personalized recommendations for user profile.
    """
    if not user.is_authenticated:
        return get_curated_fallback_recommendations("General Fiction")

    high_reviews = RatingReview.objects.filter(user=user, rating__gte=3.5).select_related('book')[:8]
    readlist_items = ReadListItem.objects.filter(readlist__user=user).select_related('book')[:10]

    fav_books = []
    for r in high_reviews:
        fav_books.append(f"'{r.book.title}' by {r.book.author} ({r.rating}★)")
    for item in readlist_items:
        t = f"'{item.book.title}' by {item.book.author}"
        if t not in fav_books:
            fav_books.append(t)

    client, model_name = get_genai_client()
    if client and fav_books:
        try:
            prompt = f"""
You are a master book recommender for Bookboxd.
The reader has enjoyed or logged the following books:
{', '.join(fav_books)}

Generate exactly 5 distinct, highly recommended book suggestions that this reader would adore based on those tastes.
Return strictly a valid JSON array of 5 objects, with NO markdown backticks or commentary outside the JSON:
[
  {{
    "title": "Book Title",
    "author": "Author Name",
    "genre": "Genre",
    "reason": "Personalized 1-2 sentence explanation of why they will love it based on their taste.",
    "match_vibe": "e.g. Atmospheric, Fast-Paced, Thought-Provoking"
  }}
]
"""
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            raw = resp.text.strip()
            raw = re.sub(r'^```json\s*', '', raw)
            raw = re.sub(r'^```\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
            parsed = json.loads(raw)

            recs = []
            for item in parsed:
                title = item.get('title')
                author = item.get('author')
                existing = Book.objects.filter(title__icontains=title[:30]).first()
                cover = existing.get_cover_image() if existing else None
                ol_key = existing.openlibrary_key if existing else None

                recs.append({
                    'title': title,
                    'author': author,
                    'genre': item.get('genre', 'Fiction'),
                    'reason': item.get('reason', 'Matches your high-rated literary taste.'),
                    'match_vibe': item.get('match_vibe', 'Recommended'),
                    'cover_url': cover,
                    'openlibrary_key': ol_key,
                    'is_ai_generated': True
                })
            if recs:
                return recs
        except Exception as e:
            logger.error(f"Error in Gemini recommendations: {e}")

    genre = "Fiction"
    if hasattr(user, 'profile') and user.profile.favorite_genres:
        genre = user.profile.favorite_genres.split(',')[0].strip()
    return get_curated_fallback_recommendations(genre, user_books=fav_books)


def get_curated_fallback_recommendations(preferred_genre="Fiction", user_books=None):
    user_titles_str = ' '.join(user_books or []).lower()

    curated_pool = [
        {
            'title': 'Dune',
            'author': 'Frank Herbert',
            'genre': 'Science Fiction',
            'reason': 'A colossal masterpiece of political intrigue, ecology, and myth-building on the desert planet Arrakis.',
            'match_vibe': 'Epic Worldbuilding',
            'cover_url': 'https://covers.openlibrary.org/b/id/12547191-L.jpg',
            'openlibrary_key': 'OL893415W'
        },
        {
            'title': 'Project Hail Mary',
            'author': 'Andy Weir',
            'genre': 'Science Fiction',
            'reason': 'A solitary astronaut must save humanity with relentless optimism, scientific problem-solving, and an unforgettable companion.',
            'match_vibe': 'Humorous & Inspiring',
            'cover_url': 'https://covers.openlibrary.org/b/id/11197775-L.jpg',
            'openlibrary_key': 'OL20150917W'
        },
        {
            'title': 'The Secret History',
            'author': 'Donna Tartt',
            'genre': 'Dark Academia / Thriller',
            'reason': 'Intoxicating, atmospheric tale of classics students at an elite New England college who cross moral boundaries.',
            'match_vibe': 'Atmospheric & Tense',
            'cover_url': 'https://covers.openlibrary.org/b/id/8231856-L.jpg',
            'openlibrary_key': 'OL27479W'
        },
        {
            'title': 'Tomorrow, and Tomorrow, and Tomorrow',
            'author': 'Gabrielle Zevin',
            'genre': 'Contemporary Fiction',
            'reason': 'A magnificent novel about identity, creativity, and the complex love between two game designers over decades.',
            'match_vibe': 'Heartfelt & Creative',
            'cover_url': 'https://covers.openlibrary.org/b/id/12843515-L.jpg',
            'openlibrary_key': 'OL25672935W'
        },
        {
            'title': 'Piranesi',
            'author': 'Susanna Clarke',
            'genre': 'Fantasy / Mystery',
            'reason': 'A wondrous, dreamlike mystery set inside an infinite labyrinth of halls lined with thousands of statues and surging tides.',
            'match_vibe': 'Poetic & Mystical',
            'cover_url': 'https://covers.openlibrary.org/b/id/10389364-L.jpg',
            'openlibrary_key': 'OL20882606W'
        }
    ]

    filtered = [b for b in curated_pool if b['title'].lower() not in user_titles_str]
    return (filtered or curated_pool)[:5]
