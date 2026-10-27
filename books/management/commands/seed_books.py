import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from books.models import Book, ReadList, ReadListItem, RatingReview, ReviewComment, Friendship, Activity, UserProfile, FAQ


class Command(BaseCommand):
    help = "Seed initial books, demo users, reviews, and reading lists"

    def handle(self, *args, **options):
        self.stdout.write("Seeding books and initial community data...")

        # 1. Sample books
        books_data = [
            {
                'title': 'Dune',
                'author': 'Frank Herbert',
                'isbn': '9780441172719',
                'openlibrary_key': 'OL893415W',
                'cover_url': 'https://covers.openlibrary.org/b/id/12547191-L.jpg',
                'description': 'Set on the desert planet Arrakis, Dune tells the story of Paul Atreides, heir to a noble family tasked with ruling an inhospitable world where the only thing of value is the spice melange.',
                'first_publish_year': 1965,
                'genre': 'Science Fiction',
                'page_count': 688,
            },
            {
                'title': 'Project Hail Mary',
                'author': 'Andy Weir',
                'isbn': '9780593135204',
                'openlibrary_key': 'OL20150917W',
                'cover_url': 'https://covers.openlibrary.org/b/id/11197775-L.jpg',
                'description': 'Ryland Grace is the sole survivor on a desperate, last-chance mission—and if he fails, humanity and the earth itself are doomed. Except right now, he doesn\'t even remember his own name.',
                'first_publish_year': 2021,
                'genre': 'Science Fiction',
                'page_count': 496,
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'isbn': '9780547928227',
                'openlibrary_key': 'OL262758W',
                'cover_url': 'https://covers.openlibrary.org/b/id/12029983-L.jpg',
                'description': 'Bilbo Baggins is a hobbit who enjoys a comfortable, unambitious life, rarely traveling further than the pantry of his hobbit-hole in Bag End. But his contentment is disturbed when Gandalf and a company of dwarves arrive.',
                'first_publish_year': 1937,
                'genre': 'Fantasy',
                'page_count': 310,
            },
            {
                'title': 'Tomorrow, and Tomorrow, and Tomorrow',
                'author': 'Gabrielle Zevin',
                'isbn': '9780593321201',
                'openlibrary_key': 'OL25672935W',
                'cover_url': 'https://covers.openlibrary.org/b/id/12843515-L.jpg',
                'description': 'A dazzling novel about identity, creativity, and the complex love between two childhood friends who become legendary game designers in the 1990s and 2000s.',
                'first_publish_year': 2022,
                'genre': 'Contemporary Fiction',
                'page_count': 416,
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'isbn': '9780451524935',
                'openlibrary_key': 'OL1168083W',
                'cover_url': 'https://covers.openlibrary.org/b/id/8575708-L.jpg',
                'description': 'Winston Smith toes the Party line, rewriting history to satisfy the Ministry of Truth. With each lie he writes, he grows to secretly hate the Party that seeks power for its own sake and persecutes individualism.',
                'first_publish_year': 1949,
                'genre': 'Dystopian Classics',
                'page_count': 328,
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'isbn': '9780141439518',
                'openlibrary_key': 'OL66554W',
                'cover_url': 'https://covers.openlibrary.org/b/id/12749455-L.jpg',
                'description': 'The romantic clash between the opinionated Elizabeth Bennet and her proud beau, Mr. Darcy, is a splendid performance of civilized sparring in Regency England.',
                'first_publish_year': 1813,
                'genre': 'Romance / Classic',
                'page_count': 432,
            },
            {
                'title': 'The Secret History',
                'author': 'Donna Tartt',
                'isbn': '9781400031702',
                'openlibrary_key': 'OL27479W',
                'cover_url': 'https://covers.openlibrary.org/b/id/8231856-L.jpg',
                'description': 'Under the influence of their charismatic classics professor, a group of clever, eccentric misfits at an elite New England college discover a way of thinking and living that is a world away from the humdrum existence of their contemporaries.',
                'first_publish_year': 1992,
                'genre': 'Dark Academia',
                'page_count': 559,
            },
            {
                'title': 'Piranesi',
                'author': 'Susanna Clarke',
                'isbn': '9781635575637',
                'openlibrary_key': 'OL20882606W',
                'cover_url': 'https://covers.openlibrary.org/b/id/10389364-L.jpg',
                'description': 'Piranesi lives in the House. Perhaps he always has. In his notebooks day after day he makes a clear and careful record of its wonders: the labyrinth of halls, the thousands upon thousands of statues, the tides that surge up staircases.',
                'first_publish_year': 2020,
                'genre': 'Fantasy Mystery',
                'page_count': 245,
            }
        ]

        created_books = []
        for bdata in books_data:
            book, created = Book.objects.update_or_create(
                openlibrary_key=bdata['openlibrary_key'],
                defaults=bdata
            )
            created_books.append(book)

        # 2. Demo users
        demo_users_data = [
            {
                'username': 'clara_reads',
                'email': 'clara@example.com',
                'bio': 'Literature nerd & tea enthusiast. Obsessed with sci-fi world-building and 19th century prose.',
                'genres': 'Science Fiction, Dark Academia, Classic'
            },
            {
                'username': 'marcus_lit',
                'email': 'marcus@example.com',
                'bio': 'Letterboxd addict now logging 100 books a year. Give me high fantasy and character studies.',
                'genres': 'Fantasy, Speculative Fiction, Contemporary'
            },
            {
                'username': 'elena_pages',
                'email': 'elena@example.com',
                'bio': 'Always reading three books at once. Fiction & philosophy.',
                'genres': 'Contemporary Fiction, Literary, Mystery'
            }
        ]

        users = []
        for udata in demo_users_data:
            u, created = User.objects.get_or_create(
                username=udata['username'],
                defaults={'email': udata['email']}
            )
            if created:
                u.set_password('demo1234')
                u.save()
            profile = u.profile
            profile.bio = udata['bio']
            profile.favorite_genres = udata['genres']
            profile.save()
            users.append(u)

        # 3. Friendships
        if len(users) >= 3:
            Friendship.objects.get_or_create(from_user=users[0], to_user=users[1])
            Friendship.objects.get_or_create(from_user=users[1], to_user=users[0])
            Friendship.objects.get_or_create(from_user=users[0], to_user=users[2])
            Friendship.objects.get_or_create(from_user=users[2], to_user=users[0])

        # 4. Reviews & Ratings with spoiler tags
        sample_reviews = [
            (
                users[0], created_books[0], Decimal('5.0'),
                "One of the greatest achievements in speculative fiction. The ecological world-building of Arrakis and the tragic prescience of Paul Atreides are peerless.",
                False
            ),
            (
                users[1], created_books[0], Decimal('4.5'),
                "Dense, atmospheric, and unforgettable. The ending reveals how Paul chooses the path of jihad despite his resistance.",
                True  # Spoiler review!
            ),
            (
                users[0], created_books[1], Decimal('5.0'),
                "Andy Weir knocked this out of the park! The camaraderie between Ryland Grace and Rocky is pure joy. Fist my bump!",
                False
            ),
            (
                users[2], created_books[3], Decimal('4.5'),
                "A love letter to storytelling, video games, and human connection. Gabrielle Zevin's prose flows effortlessly.",
                False
            ),
            (
                users[1], created_books[7], Decimal('5.0'),
                "The House is infinite, and so is my love for this book. The way the mystery unfolds around the 16th person and the Other is sheer perfection.",
                True  # Spoiler review!
            ),
            (
                users[2], created_books[6], Decimal('4.0'),
                "Dark academia at its finest. Donna Tartt captures collegiate pretension and dread with such poetic elegance.",
                False
            )
        ]

        for u, b, r, txt, sp in sample_reviews:
            rev, _ = RatingReview.objects.update_or_create(
                user=u,
                book=b,
                defaults={
                    'rating': r,
                    'review_text': txt,
                    'contains_spoilers': sp
                }
            )
            # Create Activity
            Activity.objects.get_or_create(
                user=u,
                activity_type='reviewed',
                book=b,
                review=rev
            )

        # 5. Review comments
        rev_dune = RatingReview.objects.filter(book=created_books[0], user=users[0]).first()
        if rev_dune:
            ReviewComment.objects.get_or_create(
                review=rev_dune,
                user=users[1],
                comment_text="Couldn't agree more Clara! The political maneuvering in the first half alone is top tier."
            )

        # 6. Custom Readlists
        custom_list, _ = ReadList.objects.get_or_create(
            user=users[0],
            name="Mind-Bending Sci-Fi & Space Operas",
            defaults={
                'description': 'Books that explore deep cosmos, first contact, and philosophical science fiction.',
                'list_type': 'custom',
                'is_public': True
            }
        )
        ReadListItem.objects.get_or_create(readlist=custom_list, book=created_books[0])
        ReadListItem.objects.get_or_create(readlist=custom_list, book=created_books[1])

        # 7. FAQs (Minimum 10 detailed FAQs)
        faqs_data = [
            {
                'question': 'What is Bookboxd and how does it compare to Goodreads and Letterboxd?',
                'answer': 'Bookboxd combines the social film diary appeal of Letterboxd with the warm, bookish aesthetic of Goodreads. You can rate books on a 5-star scale, write spoiler-protected reviews, organize multiple custom readlists, follow friends, and receive AI-curated reading recommendations.',
                'category': 'general',
                'order': 1,
            },
            {
                'question': 'How does the 5-star rating system work?',
                'answer': 'You can rate any book from 1.0 to 5.0 stars with 0.5 half-star increments (e.g. 3.5, 4.0, 4.5). Simply visit a book page, click the interactive stars or use the dropdown, and submit your score.',
                'category': 'ratings',
                'order': 2,
            },
            {
                'question': 'How do spoiler-protected reviews work?',
                'answer': 'When reviewing a book, check the "Contains spoilers" box if your review reveals plot twists or endings. Bookboxd will automatically blur the review text and show a "Reveal Spoilers" toggle so fellow readers can browse safely.',
                'category': 'ratings',
                'order': 3,
            },
            {
                'question': 'Can I create my own multiple custom readlists and shelves?',
                'answer': 'Yes! Every user starts with three default shelves: "Want to Read", "Currently Reading", and "Read". You can also create unlimited custom readlists (e.g. "Favorite Sci-Fi", "Summer 2024", "Dystopian Masterpieces") with descriptions and public/private privacy controls.',
                'category': 'shelves',
                'order': 4,
            },
            {
                'question': 'How do friends and the social activity stream work?',
                'answer': 'You can discover readers in the Community section and follow them. Once you follow friends, your home feed displays a live Letterboxd-style stream showing what books your friends recently rated, reviewed, or added to their shelves.',
                'category': 'social',
                'order': 5,
            },
            {
                'question': 'Can I comment on other members\' reviews?',
                'answer': 'Yes. Under every review on a book\'s detail page, there is an open comment section. Authenticated readers can join the discussion, discuss literary interpretations, and share counter-arguments.',
                'category': 'social',
                'order': 6,
            },
            {
                'question': 'Where does the book catalog data come from?',
                'answer': 'Bookboxd integrates directly with the free Open Library Internet API. You can search millions of global works, fetch high-resolution cover artwork, authors, and first publication dates without any proprietary API keys.',
                'category': 'general',
                'order': 7,
            },
            {
                'question': 'How does the Gemini AI Assistant work and is it free?',
                'answer': 'The assistant ("The Bibliophile") uses Google Gemini models to answer literary queries, recommend books based on moods or reading habits, and explain website features. Gemini Flash has a generous free tier available via Google AI Studio.',
                'category': 'ai',
                'order': 8,
            },
            {
                'question': 'What happens if the AI assistant cannot answer my question?',
                'answer': 'When the AI cannot resolve an issue or if you request technical support, it automatically files a Support Ticket stored in our SQL database with a unique Ticket ID (e.g. TKT-XXXX). Our moderation and support team can then review and resolve it.',
                'category': 'ai',
                'order': 9,
            },
            {
                'question': 'What does HTTP 404 Not Found mean on Bookboxd?',
                'answer': 'A 404 error indicates that the URL, book ID, or user profile you are looking for does not exist or has been removed. Our custom 404 page provides quick links back home and an "Ask the Assistant" option to help you find the right book.',
                'category': 'technical',
                'order': 10,
            },
            {
                'question': 'What does HTTP 500 Internal Server Error mean?',
                'answer': 'A 500 error signifies an unexpected internal problem on our server. Our error logging middleware records the event for diagnosis, and you can click "Ask the Assistant" on the custom 500 page to file a support ticket.',
                'category': 'technical',
                'order': 11,
            },
            {
                'question': 'What are HTTP 400, 401, 403, 422, 429, and 503 error codes?',
                'answer': '400 means Bad Request; 401 requires signing in; 403 means Forbidden access; 422 indicates Unprocessable book metadata; 429 indicates rate limiting (too many requests); and 503 means the service or upstream book API is temporarily unavailable.',
                'category': 'technical',
                'order': 12,
            }
        ]

        for fdata in faqs_data:
            FAQ.objects.update_or_create(
                question=fdata['question'],
                defaults=fdata
            )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded with books, reviews, friends, shelves, and 12 FAQs!"))
