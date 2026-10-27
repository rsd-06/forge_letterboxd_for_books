import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from books.models import (
    Book, ReadList, ReadListItem, RatingReview, ReviewComment,
    Friendship, Activity, UserProfile, FAQ
)
from books.mongo_service import log_user_crud_to_mongo, log_book_crud_to_mongo


class Command(BaseCommand):
    help = "Seed initial books, demo users, reviews, reading lists, and FAQs"

    def handle(self, *args, **options):
        self.stdout.write("Seeding 22 curated books and community data...")

        # 1. 22 Curated Books with local verified covers
        all_books_data = [
            {
                'title': 'Dune',
                'author': 'Frank Herbert',
                'isbn': '9780441172719',
                'openlibrary_key': 'OL893415W',
                'cover_url': '/media/covers/dune.jpg',
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
                'cover_url': '/media/covers/project_hail_mary.jpg',
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
                'cover_url': '/media/covers/the_hobbit.jpg',
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
                'cover_url': '/media/covers/tomorrow_and_tomorrow_and_tomorrow.jpg',
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
                'cover_url': '/media/covers/1984.jpg',
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
                'cover_url': '/media/covers/pride_and_prejudice.jpg',
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
                'cover_url': '/media/covers/the_secret_history.jpg',
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
                'cover_url': '/media/covers/piranesi.jpg',
                'description': 'Piranesi lives in the House. Perhaps he always has. In his notebooks day after day he makes a clear and careful record of its wonders: the labyrinth of halls, the thousands upon thousands of statues, the tides that surge up staircases.',
                'first_publish_year': 2020,
                'genre': 'Fantasy Mystery',
                'page_count': 245,
            },
            {
                'title': 'The Name of the Wind',
                'author': 'Patrick Rothfuss',
                'isbn': '9780756404741',
                'openlibrary_key': 'OL8451877W',
                'cover_url': '/media/covers/the_name_of_the_wind.jpg',
                'description': 'Told in Kvothe\'s own voice, this is the tale of the magically gifted young man who grows to be the most notorious wizard his world has ever seen, from his childhood in a troupe of traveling players to his years as a near-feral orphan.',
                'first_publish_year': 2007,
                'genre': 'Epic Fantasy',
                'page_count': 662,
            },
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'isbn': '9780743273565',
                'openlibrary_key': 'OL69738W',
                'cover_url': '/media/covers/the_great_gatsby.jpg',
                'description': 'The story of the fabulously wealthy Jay Gatsby and his new love for the beautiful Daisy Buchanan, of lavish parties on Long Island at a time when The New York Times noted "gin was the national drink and sex the national obsession".',
                'first_publish_year': 1925,
                'genre': 'American Classics',
                'page_count': 180,
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'isbn': '9780060935467',
                'openlibrary_key': 'OL7353617W',
                'cover_url': '/media/covers/to_kill_a_mockingbird.jpg',
                'description': 'Compassionate, dramatic, and deeply moving, To Kill A Mockingbird takes readers to the roots of human behavior—to innocence and experience, kindness and cruelty, love and hatred, humor and pathos in the American South.',
                'first_publish_year': 1960,
                'genre': 'Historical Classics',
                'page_count': 336,
            },
            {
                'title': 'Babel',
                'author': 'R.F. Kuang',
                'isbn': '9780063021426',
                'openlibrary_key': 'OL25672950W',
                'cover_url': '/media/covers/babel.jpg',
                'description': 'An arcane historical fantasy about the power of language, the violence of empire, and the student revolution at the Oxford Royal Institute of Translation, known across the British Empire as Babel.',
                'first_publish_year': 2022,
                'genre': 'Dark Academia / Fantasy',
                'page_count': 544,
            },
            {
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'isbn': '9780735211292',
                'openlibrary_key': 'OL20150920W',
                'cover_url': '/media/covers/atomic_habits.jpg',
                'description': 'No matter your goals, Atomic Habits offers a proven framework for improving every day. James Clear, one of the world\'s leading experts on habit formation, reveals practical strategies to form good habits and break bad ones.',
                'first_publish_year': 2018,
                'genre': 'Personal Growth / Psychology',
                'page_count': 320,
            },
            {
                'title': 'Sapiens: A Brief History of Humankind',
                'author': 'Yuval Noah Harari',
                'isbn': '9780062316097',
                'openlibrary_key': 'OL17079549W',
                'cover_url': '/media/covers/sapiens.jpg',
                'description': 'From a renowned historian comes a groundbreaking narrative of humanity’s creation and evolution—a #1 international bestseller—that explores the ways in which biology and history have defined us and enhanced our understanding of what it means to be "human".',
                'first_publish_year': 2011,
                'genre': 'Anthropology / History',
                'page_count': 443,
            },
            {
                'title': 'The Silent Patient',
                'author': 'Alex Michaelides',
                'isbn': '9781250301697',
                'openlibrary_key': 'OL19732943W',
                'cover_url': '/media/covers/the_silent_patient.jpg',
                'description': 'Alicia Berenson’s life is seemingly perfect. A famous painter married to an in-demand fashion photographer, she lives in a grand house. Then one evening, she shoots her husband five times in the face, and never speaks another word.',
                'first_publish_year': 2019,
                'genre': 'Psychological Thriller',
                'page_count': 336,
            },
            {
                'title': 'Klara and the Sun',
                'author': 'Kazuo Ishiguro',
                'isbn': '9780593318171',
                'openlibrary_key': 'OL21175654W',
                'cover_url': '/media/covers/klara_and_the_sun.jpg',
                'description': 'From the bestselling author and Nobel laureate, a magnificent novel about Klara, an Artificial Friend with outstanding observational qualities, who, from her place in the store, watches carefully the behavior of those who come in to browse.',
                'first_publish_year': 2021,
                'genre': 'Speculative Fiction',
                'page_count': 303,
            },
            {
                'title': 'Crying in H Mart',
                'author': 'Michelle Zauner',
                'isbn': '9780525657743',
                'openlibrary_key': 'OL21689404W',
                'cover_url': '/media/covers/crying_in_h_mart.jpg',
                'description': 'A powerful, bittersweet memoir about family, food, grief, love, and growing up Korean American by the singer and guitarist of Japanese Breakfast.',
                'first_publish_year': 2021,
                'genre': 'Memoir / Biography',
                'page_count': 256,
            },
            {
                'title': 'Sea of Tranquility',
                'author': 'Emily St. John Mandel',
                'isbn': '9780593321447',
                'openlibrary_key': 'OL25672945W',
                'cover_url': '/media/covers/sea_of_tranquility.jpg',
                'description': 'A virtuoso performance that is as human and tender as it is intellectually playful, Sea of Tranquility is a novel of time travel and metaphysical suspense that precisely captures the reality of our current moment.',
                'first_publish_year': 2022,
                'genre': 'Science Fiction / Literary',
                'page_count': 272,
            },
            {
                'title': 'Good Omens',
                'author': 'Neil Gaiman & Terry Pratchett',
                'isbn': '9780060853983',
                'openlibrary_key': 'OL453936W',
                'cover_url': '/media/covers/good_omens.jpg',
                'description': 'According to The Nice and Accurate Prophecies of Agnes Nutter, Witch, the world will end on a Saturday. Next Saturday, in fact. Just before dinner. Which means an angel and a demon who enjoy living among mortals must find the misplaced Antichrist.',
                'first_publish_year': 1990,
                'genre': 'Fantasy Comedy',
                'page_count': 412,
            },
            {
                'title': 'Crime and Punishment',
                'author': 'Fyodor Dostoevsky',
                'isbn': '9780143058144',
                'openlibrary_key': 'OL1168007W',
                'cover_url': '/media/covers/crime_and_punishment.jpg',
                'description': 'Raskolnikov, a destitute and desperate former student, wanders through the slums of St Petersburg and commits a random murder without remorse or regret. He imagines himself to be an exceptional being above moral law.',
                'first_publish_year': 1866,
                'genre': 'Philosophical Classics',
                'page_count': 565,
            },
            {
                'title': 'Neuromancer',
                'author': 'William Gibson',
                'isbn': '9780441569595',
                'openlibrary_key': 'OL8451870W',
                'cover_url': '/media/covers/neuromancer.jpg',
                'description': 'Case had been the sharpest data-thief in the matrix—until he crossed the wrong people and they crippled his nervous system. Now a mysterious new employer recruits him for a high-risk run against an unthinkably powerful corporate artificial intelligence.',
                'first_publish_year': 1984,
                'genre': 'Cyberpunk / Sci-Fi',
                'page_count': 271,
            },
            {
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'isbn': '9780316769488',
                'openlibrary_key': 'OL1168003W',
                'cover_url': '/media/covers/the_catcher_in_the_rye.jpg',
                'description': 'The hero-narrator of The Catcher in the Rye is an ancient sixteen, a native New Yorker named Holden Caulfield. Through his distinctive voice, Salinger explores alienation, grief, and the search for authenticity.',
                'first_publish_year': 1951,
                'genre': 'American Modern Classics',
                'page_count': 234,
            }
        ]

        book_map = {}
        for bdata in all_books_data:
            book, _ = Book.objects.update_or_create(
                openlibrary_key=bdata['openlibrary_key'],
                defaults=bdata
            )
            book_map[book.title] = book

        # 2. Community User Personas
        community_users = [
            {
                'username': 'clara_reads',
                'email': 'clara@bookboxd.com',
                'bio': 'Literature nerd & tea enthusiast. Obsessed with sci-fi world-building, speculative fiction, and 19th-century prose.',
                'avatar_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250',
                'genres': 'Science Fiction, Dark Academia, Classic'
            },
            {
                'username': 'marcus_lit',
                'email': 'marcus@bookboxd.com',
                'bio': 'Letterboxd addict now logging 100 books a year. Give me high fantasy, grand space operas, and existential character studies.',
                'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=250',
                'genres': 'Fantasy, Speculative Fiction, Contemporary'
            },
            {
                'username': 'elena_pages',
                'email': 'elena@bookboxd.com',
                'bio': 'Always reading three books at once. Contemporary fiction, philosophical novels, and poignant memoirs.',
                'avatar_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&q=80&w=250',
                'genres': 'Contemporary Fiction, Literary, Mystery'
            },
            {
                'username': 'devon_scifi',
                'email': 'devon@bookboxd.com',
                'bio': 'Astrophysics PhD student by day, cyberpunk & space opera reader by night. Searching for the next Clarke, Gibson, or Weir.',
                'avatar_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=250',
                'genres': 'Science Fiction, Cyberpunk, Dystopian'
            },
            {
                'username': 'sophie_lit',
                'email': 'sophie@bookboxd.com',
                'bio': 'Comparative literature graduate student. Avid annotator of translated fiction, post-colonial literature, and modern classics.',
                'avatar_url': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&q=80&w=250',
                'genres': 'Classics, Dark Academia, Literary Fiction'
            },
            {
                'username': 'chloe_mystery',
                'email': 'chloe@bookboxd.com',
                'bio': 'Hooked on psychological thrillers, locked-room mysteries, and unreliable narrators. Will guess the twist by page 100.',
                'avatar_url': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&q=80&w=250',
                'genres': 'Psychological Thriller, Mystery, Crime'
            },
            {
                'username': 'alex_classics',
                'email': 'alex@bookboxd.com',
                'bio': 'On a lifelong quest through the Western and Eastern literary canons. Currently deep into Dostoevsky, Tolstoy, and Austen.',
                'avatar_url': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&q=80&w=250',
                'genres': 'Philosophical Classics, Romance / Classic, Historical'
            },
            {
                'username': 'maya_nonfiction',
                'email': 'maya@bookboxd.com',
                'bio': 'Science communicator and biographer. Loves books that dissect human behavior, neurobiology, and macro-history.',
                'avatar_url': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&q=80&w=250',
                'genres': 'Non-Fiction, Anthropology, Psychology, Memoir'
            },
            {
                'username': 'liam_fantasy',
                'email': 'liam@bookboxd.com',
                'bio': 'World-building enthusiast. Give me maps in the front cover, hard magic systems, and legendary character arcs.',
                'avatar_url': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&q=80&w=250',
                'genres': 'Epic Fantasy, High Fantasy, Mythology'
            }
        ]

        user_map = {}
        for udata in community_users:
            u, created = User.objects.get_or_create(
                username=udata['username'],
                defaults={'email': udata['email']}
            )
            if created:
                u.set_password('demo1234')
                u.save()
            profile = u.profile
            profile.bio = udata['bio']
            profile.avatar_url = udata['avatar_url']
            profile.favorite_genres = udata['genres']
            profile.save()
            user_map[u.username] = u

        # Integrate rsd-06 if present
        rsd_user = User.objects.filter(username='rsd-06').first()
        if rsd_user:
            user_map['rsd-06'] = rsd_user
            profile = rsd_user.profile
            if not profile.bio:
                profile.bio = "Curator & Bookboxd explorer. Building the ultimate library of fiction, science, and philosophy."
                profile.favorite_genres = "Science Fiction, Epic Fantasy, Dark Academia, Classics"
                profile.save()

        # 3. Friendships
        friendship_pairs = [
            ('clara_reads', 'marcus_lit'), ('marcus_lit', 'clara_reads'),
            ('clara_reads', 'elena_pages'), ('elena_pages', 'clara_reads'),
            ('devon_scifi', 'clara_reads'), ('clara_reads', 'devon_scifi'),
            ('devon_scifi', 'marcus_lit'), ('sophie_lit', 'elena_pages'),
            ('elena_pages', 'sophie_lit'), ('chloe_mystery', 'sophie_lit'),
            ('alex_classics', 'sophie_lit'), ('sophie_lit', 'alex_classics'),
            ('maya_nonfiction', 'devon_scifi'), ('liam_fantasy', 'marcus_lit'),
            ('marcus_lit', 'liam_fantasy'),
        ]
        if rsd_user:
            friendship_pairs.extend([
                ('clara_reads', 'rsd-06'), ('marcus_lit', 'rsd-06'),
                ('devon_scifi', 'rsd-06'), ('sophie_lit', 'rsd-06'),
                ('rsd-06', 'clara_reads'), ('rsd-06', 'marcus_lit'),
                ('rsd-06', 'elena_pages'), ('rsd-06', 'maya_nonfiction'),
            ])
        for f_from, f_to in friendship_pairs:
            u_from = user_map.get(f_from)
            u_to = user_map.get(f_to)
            if u_from and u_to:
                Friendship.objects.get_or_create(from_user=u_from, to_user=u_to)

        # 4. Detailed Reviews & Ratings
        reviews_data = [
            ('liam_fantasy', 'The Name of the Wind', Decimal('5.0'),
             "Patrick Rothfuss creates sheer musicality with language. Kvothe’s journey from the troupe of the Edema Ruh through the rooftops of Tarbean to the Arcanum is mesmerizing.", False),
            ('marcus_lit', 'The Name of the Wind', Decimal('4.5'),
             "The narrative framing device of the Waystone Inn is brilliant. When Bast warns Chronicler about Kvothe's true nature, you realize we are reading a tragedy disguised as an adventure.", True),
            ('alex_classics', 'The Great Gatsby', Decimal('5.0'),
             "Fitzgerald's sentences are pure poetry. The green light at the end of Daisy's dock remains the single greatest literary metaphor for the elusive American Dream.", False),
            ('sophie_lit', 'To Kill a Mockingbird', Decimal('5.0'),
             "Harper Lee captured the essence of moral courage through Atticus Finch. Scout's childhood perspective brings warmth and humor to a story confronting profound racial injustice.", False),
            ('sophie_lit', 'Babel', Decimal('5.0'),
             "R.F. Kuang delivers a profound masterpiece on translation, colonialism, and the cost of empire. The magic system based on silver-working is sheer genius.", False),
            ('maya_nonfiction', 'Atomic Habits', Decimal('5.0'),
             "The gold standard for behavioral psychology applied to daily life. The 1% compounding improvement concept completely changed how I organize my reading goals.", False),
            ('maya_nonfiction', 'Sapiens: A Brief History of Humankind', Decimal('5.0'),
             "Yuval Noah Harari connects biology, anthropology, and economics into a breathtaking panorama. Shared fictions define our civilization.", False),
            ('chloe_mystery', 'The Silent Patient', Decimal('5.0'),
             "Mind-blown. The blend of Greek tragedy (Alcestis) and psychotherapeutic tension makes this a five-star page-turner.", False),
            ('clara_reads', 'Klara and the Sun', Decimal('5.0'),
             "Kazuo Ishiguro's tenderness broke my heart. Seeing our fragile technological world through the observant, gentle gaze of an Artificial Friend asks what it truly means to love.", False),
            ('maya_nonfiction', 'Crying in H Mart', Decimal('5.0'),
             "Michelle Zauner writes about maternal love, identity, and grief with such raw vulnerability. Sensory descriptions of Korean home cooking honor her mother's memory.", False),
            ('devon_scifi', 'Sea of Tranquility', Decimal('5.0'),
             "Emily St. John Mandel weaves a tapestry spanning 1912 Vancouver, 2020 pandemic lockdowns, and 2401 moon colonies. Sublime metaphysical science fiction.", False),
            ('liam_fantasy', 'Good Omens', Decimal('5.0'),
             "The comedic alchemy of Terry Pratchett and Neil Gaiman is legendary. Crowley and Aziraphale enjoying tea while misplacing the Antichrist is comedy perfection.", False),
            ('alex_classics', 'Crime and Punishment', Decimal('5.0'),
             "The definitive psychological investigation into guilt, redemption, and pride. Porfiry Petrovich's cat-and-mouse interrogations are thrilling.", False),
            ('devon_scifi', 'Neuromancer', Decimal('5.0'),
             "The sky above the port was the color of television, tuned to a dead channel. Gibson defined cyberspace and cyberpunk in 1984.", False),
            ('elena_pages', 'The Catcher in the Rye', Decimal('4.0'),
             "Holden Caulfield's cynicism is a fragile armor protecting profound grief. Phoebe and the carousel scene is gorgeous.", False),
            ('clara_reads', 'Dune', Decimal('5.0'),
             "One of the greatest achievements in speculative fiction. The ecological world-building of Arrakis is peerless.", False),
            ('clara_reads', 'Project Hail Mary', Decimal('5.0'),
             "Andy Weir knocked this out of the park! The camaraderie between Ryland Grace and Rocky is pure joy. Fist my bump!", False)
        ]

        for uname, btitle, rating, text, has_sp in reviews_data:
            user = user_map.get(uname)
            book = book_map.get(btitle)
            if user and book:
                rev, _ = RatingReview.objects.update_or_create(
                    user=user,
                    book=book,
                    defaults={'rating': rating, 'review_text': text, 'contains_spoilers': has_sp}
                )
                Activity.objects.get_or_create(user=user, activity_type='reviewed', book=book, review=rev)

        # 5. Comments
        conv_list = [
            ('The Name of the Wind', 'liam_fantasy', 'marcus_lit', "Totally agree Liam! That passage describing the Chandrian gave me chills."),
            ('Babel', 'sophie_lit', 'elena_pages', "The footnotes alone read like a masterclass in historical linguistics."),
            ('Atomic Habits', 'maya_nonfiction', 'chloe_mystery', "The habit stacking trick works wonders! Paired reading with my evening tea.")
        ]
        for btitle, rev_author, comment_author, comment_text in conv_list:
            b = book_map.get(btitle)
            ru = user_map.get(rev_author)
            cu = user_map.get(comment_author)
            if b and ru and cu:
                rev = RatingReview.objects.filter(book=b, user=ru).first()
                if rev:
                    ReviewComment.objects.get_or_create(review=rev, user=cu, defaults={'comment_text': comment_text})

        # 6. Readlists
        curated_lists = [
            ('clara_reads', "Mind-Bending Sci-Fi & Space Operas", "Deep space, first contact, time paradoxes.", ['Dune', 'Project Hail Mary', 'Sea of Tranquility', 'Neuromancer']),
            ('sophie_lit', "Dark Academia & Campus Enigmas", "Eccentric scholars, collegiate secrets.", ['The Secret History', 'Babel', 'Piranesi']),
            ('alex_classics', "Pillars of World Literature", "Timeless classics that shaped literary tradition.", ['Crime and Punishment', 'The Great Gatsby', 'To Kill a Mockingbird', 'Pride and Prejudice', '1984'])
        ]
        for cname, lname, ldesc, btitles in curated_lists:
            c = user_map.get(cname)
            if c:
                rl, _ = ReadList.objects.get_or_create(user=c, name=lname, defaults={'description': ldesc, 'list_type': 'custom', 'is_public': True})
                for bt in btitles:
                    b = book_map.get(bt)
                    if b:
                        ReadListItem.objects.get_or_create(readlist=rl, book=b)

        # Update stats
        for b in Book.objects.all():
            b.update_rating_stats()

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

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {Book.objects.count()} books, {User.objects.count()} users, {RatingReview.objects.count()} reviews, and 12 FAQs!"))
