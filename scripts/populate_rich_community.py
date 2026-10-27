import os
import sys
from decimal import Decimal
import django
from datetime import datetime, timezone, timedelta

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from books.models import (
    Book, UserProfile, Friendship, ReadList, ReadListItem,
    RatingReview, ReviewComment, Activity
)
from books.mongo_service import log_user_crud_to_mongo, log_book_crud_to_mongo


def run_seeding():
    print("=== Populating Rich Books, Community Users, Reviews, & Comments ===")

    # 1. Comprehensive list of 22 books (8 existing + 14 new)
    all_books_data = [
        # Existing 8
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

        # 14 New Verified Additions
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
        book, created = Book.objects.update_or_create(
            openlibrary_key=bdata['openlibrary_key'],
            defaults=bdata
        )
        book_map[book.title] = book
        if created:
            print(f" [+] Added Book: {book.title} ({book.author})")
        else:
            print(f" [~] Updated Book: {book.title}")
    
    print(f"\nTotal Books in Catalog: {Book.objects.count()}")

    # 2. Rich User Personas (including existing rsd-06)
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
            print(f" [+] Created Community User: {u.username}")
        profile = u.profile
        profile.bio = udata['bio']
        profile.avatar_url = udata['avatar_url']
        profile.favorite_genres = udata['genres']
        profile.save()
        user_map[u.username] = u
        log_user_crud_to_mongo('SEED_USER', {'username': u.username, 'email': u.email})

    # Include rsd-06 if present
    rsd_user = User.objects.filter(username='rsd-06').first()
    if rsd_user:
        user_map['rsd-06'] = rsd_user
        profile = rsd_user.profile
        if not profile.bio:
            profile.bio = "Curator & Bookboxd explorer. Building the ultimate library of fiction, science, and philosophy."
            profile.favorite_genres = "Science Fiction, Epic Fantasy, Dark Academia, Classics"
            profile.save()
        print(" [+] Integrated user 'rsd-06' into social graph")

    # 3. Social Friendship Graph
    friendship_pairs = [
        ('clara_reads', 'marcus_lit'),
        ('marcus_lit', 'clara_reads'),
        ('clara_reads', 'elena_pages'),
        ('elena_pages', 'clara_reads'),
        ('devon_scifi', 'clara_reads'),
        ('clara_reads', 'devon_scifi'),
        ('devon_scifi', 'marcus_lit'),
        ('sophie_lit', 'elena_pages'),
        ('elena_pages', 'sophie_lit'),
        ('chloe_mystery', 'sophie_lit'),
        ('alex_classics', 'sophie_lit'),
        ('sophie_lit', 'alex_classics'),
        ('maya_nonfiction', 'devon_scifi'),
        ('liam_fantasy', 'marcus_lit'),
        ('marcus_lit', 'liam_fantasy'),
    ]
    # Connect friends to rsd-06 so user has active feed!
    if rsd_user:
        friendship_pairs.extend([
            ('clara_reads', 'rsd-06'),
            ('marcus_lit', 'rsd-06'),
            ('devon_scifi', 'rsd-06'),
            ('sophie_lit', 'rsd-06'),
            ('rsd-06', 'clara_reads'),
            ('rsd-06', 'marcus_lit'),
            ('rsd-06', 'elena_pages'),
            ('rsd-06', 'maya_nonfiction'),
        ])

    for f_from, f_to in friendship_pairs:
        u_from = user_map.get(f_from)
        u_to = user_map.get(f_to)
        if u_from and u_to:
            Friendship.objects.get_or_create(from_user=u_from, to_user=u_to)

    print(f" [+] Established {Friendship.objects.count()} social connections in community")

    # 4. Rich In-Depth Reviews & Ratings (Spanning All Books)
    detailed_reviews = [
        # The Name of the Wind
        (
            'liam_fantasy', 'The Name of the Wind', Decimal('5.0'),
            "Patrick Rothfuss creates sheer musicality with language. Kvothe’s journey from the troupe of the Edema Ruh through the rooftops of Tarbean to the Arcanum is mesmerizing. The magic system of Sympathy is one of the most logically sound in all of fantasy. An absolute masterpiece of the genre.",
            False
        ),
        (
            'marcus_lit', 'The Name of the Wind', Decimal('4.5'),
            "The narrative framing device of the Waystone Inn is brilliant. When Bast warns Chronicler about Kvothe's true nature, you realize we are reading a tragedy disguised as an adventure. Can't wait for The Doors of Stone.",
            True
        ),
        (
            'sophie_lit', 'The Name of the Wind', Decimal('4.0'),
            "Immensely readable with poetic sentence structure. While Kvothe can occasionally lean into the 'prodigy who is good at everything' trope, the world-building and lore of the Chandrian kept me completely hooked.",
            False
        ),

        # The Great Gatsby
        (
            'alex_classics', 'The Great Gatsby', Decimal('5.0'),
            "Fitzgerald's sentences are pure poetry. The green light at the end of Daisy's dock remains the single greatest literary metaphor for the elusive American Dream. Nick Carraway's unreliable observation makes every reread richer.",
            False
        ),
        (
            'elena_pages', 'The Great Gatsby', Decimal('4.5'),
            "The tragedy of Jay Gatsby is that he tried to repeat a past that only ever existed in his longing. The scene in the Plaza Hotel where Tom strips away his facade is heart-wrenching.",
            True
        ),

        # To Kill a Mockingbird
        (
            'sophie_lit', 'To Kill a Mockingbird', Decimal('5.0'),
            "Harper Lee captured the essence of moral courage through Atticus Finch. Scout's childhood perspective brings warmth and humor to a story confronting profound racial injustice in 1930s Alabama. Essential reading for every generation.",
            False
        ),
        (
            'alex_classics', 'To Kill a Mockingbird', Decimal('5.0'),
            "Atticus standing guard outside the jailhouse and the courtroom scene where the balcony stands for him as he exits are forever etched into literature. A timeless, towering classic.",
            False
        ),

        # Babel
        (
            'sophie_lit', 'Babel', Decimal('5.0'),
            "R.F. Kuang delivers a profound masterpiece on translation, colonialism, and the cost of empire. The magic system based on silver-working and translation loss (the meaning that is lost between languages) is sheer genius. Heartbreaking and intellectually electrifying.",
            False
        ),
        (
            'elena_pages', 'Babel', Decimal('4.5'),
            "The dark academia setting of 19th-century Oxford turns into a revolutionary pressure cooker. When Robin Swift confronts Professor Lovell and realizes Babel's wealth comes from global exploitation, the stakes reach a devastating peak.",
            True
        ),

        # Atomic Habits
        (
            'maya_nonfiction', 'Atomic Habits', Decimal('5.0'),
            "The gold standard for behavioral psychology applied to daily life. James Clear distills habit loops into four simple laws: make it obvious, attractive, easy, and satisfying. The 1% compounding improvement concept completely changed how I organize my reading goals.",
            False
        ),
        (
            'devon_scifi', 'Atomic Habits', Decimal('4.5'),
            "Systems over goals! Highly practical with zero fluff. Tracking my reading habit using Clear's two-minute rule helped me log 40 books this year alone.",
            False
        ),

        # Sapiens
        (
            'maya_nonfiction', 'Sapiens: A Brief History of Humankind', Decimal('5.0'),
            "Yuval Noah Harari connects biology, anthropology, and economics into a breathtaking panorama. His thesis that Homo sapiens conquered the globe through shared fictions (money, religions, nations, corporations) is dazzling and paradigm-shifting.",
            False
        ),
        (
            'alex_classics', 'Sapiens: A Brief History of Humankind', Decimal('4.5'),
            "Provocative and endlessly thought-provoking. The chapter on the Agricultural Revolution being 'history's biggest fraud' will completely reframe how you look at modern civilization.",
            False
        ),

        # The Silent Patient
        (
            'chloe_mystery', 'The Silent Patient', Decimal('5.0'),
            "Mind-blown. I pride myself on predicting thriller plot twists, but Alex Michaelides totally caught me off guard. The blend of Greek tragedy (Alcestis) and psychotherapeutic tension makes this a five-star page-turner.",
            False
        ),
        (
            'elena_pages', 'The Silent Patient', Decimal('4.0'),
            "The dual timeline reveal between Theo Faber's personal diary and Alicia's silence at The Grove is executed with surgical precision. The final revelation of why she shot Gabriel sent chills down my spine.",
            True
        ),

        # Klara and the Sun
        (
            'clara_reads', 'Klara and the Sun', Decimal('5.0'),
            "Kazuo Ishiguro's tenderness broke my heart. Seeing our fragile, technological world through the observant, gentle gaze of an Artificial Friend asks what it truly means to love and whether a human heart can ever be replicated.",
            False
        ),
        (
            'devon_scifi', 'Klara and the Sun', Decimal('4.5'),
            "A quieter, more melancholic sci-fi than what I normally read, but so deeply resonant. The ending where Klara looks back on her life in the yard will stay with me forever.",
            True
        ),

        # Crying in H Mart
        (
            'maya_nonfiction', 'Crying in H Mart', Decimal('5.0'),
            "Michelle Zauner writes about maternal love, identity, and grief with such raw vulnerability. The sensory descriptions of Korean home cooking—kimchi jjigae, tteokbokki, banchan—become the vessels through which she honors her mother's memory.",
            False
        ),
        (
            'elena_pages', 'Crying in H Mart', Decimal('4.5'),
            "Prepare a box of tissues. An intimate exploration of what remains of our cultural heritage and identity when the person who anchored it passes away.",
            False
        ),

        # Sea of Tranquility
        (
            'devon_scifi', 'Sea of Tranquility', Decimal('5.0'),
            "Emily St. John Mandel weaves a tapestry spanning 1912 Vancouver, 2020 pandemic lockdowns, and 2401 moon colonies. The violin anomaly in the forest echoing across centuries is sublime metaphysical science fiction.",
            False
        ),
        (
            'clara_reads', 'Sea of Tranquility', Decimal('4.5'),
            "Gaspary-Jacques Roberts is such a compassionate protagonist. Mandel proves once again that time travel novels can be intimate human meditations rather than mere puzzle boxes.",
            True
        ),

        # Good Omens
        (
            'liam_fantasy', 'Good Omens', Decimal('5.0'),
            "The comedic alchemy of Terry Pratchett and Neil Gaiman is legendary. Crowley the demon and Aziraphale the angel enjoying sushi, tea, and Queen's Greatest Hits while accidentally misplacing the Antichrist is pure comedic perfection.",
            False
        ),
        (
            'marcus_lit', 'Good Omens', Decimal('4.5'),
            "Endlessly quotable, witty, and heartwarming. The Them and Adam Young standing down the Four Horsemen of the Apocalypse in Tadfield is peak British fantasy satire.",
            False
        ),

        # Crime and Punishment
        (
            'alex_classics', 'Crime and Punishment', Decimal('5.0'),
            "The definitive psychological investigation into guilt, redemption, and pride. Dostoevsky puts Raskolnikov's feverish, rationalized guilt under a psychological microscope. Porfiry Petrovich's cat-and-mouse interrogations are thrilling.",
            False
        ),
        (
            'sophie_lit', 'Crime and Punishment', Decimal('4.5'),
            "Sonia Marmeladov represents selfless grace against Raskolnikov's cold intellectual nihilism. The Siberia epilogue shows the difficult, honest road to moral resurrection.",
            True
        ),

        # Neuromancer
        (
            'devon_scifi', 'Neuromancer', Decimal('5.0'),
            "The sky above the port was the color of television, tuned to a dead channel. William Gibson practically invented cyberspace and cyberpunk aesthetics in 1984. Case, Molly Millions, and Wintermute defined a generation of sci-fi.",
            False
        ),
        (
            'clara_reads', 'Neuromancer', Decimal('4.0'),
            "Dense, neon-drenched prose that hits like a shot of adrenaline. The sensory overload of Chiba City and the matrix run on Villa Straylight is visionary.",
            False
        ),

        # The Catcher in the Rye
        (
            'elena_pages', 'The Catcher in the Rye', Decimal('4.0'),
            "Holden Caulfield's voice is unforgettable. Reading it as an adult, his cynicism reveals itself as a fragile armor protecting profound grief over the death of his brother Allie. Phoebe and the carousel scene is gorgeous.",
            False
        ),
        (
            'alex_classics', 'The Catcher in the Rye', Decimal('4.0'),
            "A masterclass in voice and modern alienation. Holden wanting to be the catcher in the rye to keep children from falling off the cliff of innocence into the phoniness of adulthood is profoundly moving.",
            False
        )
    ]

    created_reviews = []
    for uname, btitle, rating, text, has_sp in detailed_reviews:
        user = user_map.get(uname)
        book = book_map.get(btitle)
        if not user or not book:
            continue
        
        rev, created = RatingReview.objects.update_or_create(
            user=user,
            book=book,
            defaults={
                'rating': rating,
                'review_text': text,
                'contains_spoilers': has_sp
            }
        )
        created_reviews.append(rev)

        # Create Activity
        Activity.objects.get_or_create(
            user=user,
            activity_type='reviewed',
            book=book,
            review=rev
        )
        log_book_crud_to_mongo('RATE_REVIEW', {
            'username': user.username,
            'book_title': book.title,
            'rating': float(rating),
            'has_spoiler': has_sp
        })

    print(f" [+] Added / verified {len(created_reviews)} detailed community reviews")

    # 5. Review Likes (Social validation)
    all_users_list = list(user_map.values())
    for rev in RatingReview.objects.all()[:15]:
        # Add 2 to 4 likes to each review
        likers = [u for u in all_users_list if u != rev.user][:3]
        for l in likers:
            rev.likes.add(l)

    # 6. Interactive Review Comments (Conversations)
    conversation_data = [
        (
            'The Name of the Wind', 'liam_fantasy', 'marcus_lit',
            "Totally agree Liam! That passage describing the Chandrian's blue fire and the pottery vase gave me chills."
        ),
        (
            'The Name of the Wind', 'liam_fantasy', 'devon_scifi',
            "The Sympathy system is so cool—especially the Law of Consanguinity and Conservation of Energy. Felt like real thermodynamic physics!"
        ),
        (
            'Babel', 'sophie_lit', 'elena_pages',
            "R.F. Kuang did so much archival research for this. The footnotes alone read like a masterclass in historical linguistics."
        ),
        (
            'Atomic Habits', 'maya_nonfiction', 'chloe_mystery',
            "The habit stacking trick works wonders! I paired my evening reading habit with my post-dinner tea routine."
        ),
        (
            'The Silent Patient', 'chloe_mystery', 'sophie_lit',
            "The Alcestis myth parallel was my favorite part! Did you figure out the timeline before Theo met Alicia's neighbor?"
        ),
        (
            'Sea of Tranquility', 'devon_scifi', 'clara_reads',
            "The connection to Station Eleven and The Glass Hotel made it feel like part of an interconnected multiverse. Mandel is a genius."
        ),
        (
            'Crime and Punishment', 'alex_classics', 'sophie_lit',
            "Porfiry Petrovich's dialogues remind me so much of modern detective fiction like Columbo. The psychological interrogation was brilliant."
        ),
        (
            'Project Hail Mary', 'clara_reads', 'marcus_lit',
            "Fist my bump! Best sci-fi duo since Han and Chewie. Rocky made me cry happy tears."
        )
    ]

    for btitle, rev_author, comment_author, comment_text in conversation_data:
        target_book = book_map.get(btitle)
        target_rev_user = user_map.get(rev_author)
        commenter = user_map.get(comment_author)
        if target_book and target_rev_user and commenter:
            review = RatingReview.objects.filter(book=target_book, user=target_rev_user).first()
            if review:
                ReviewComment.objects.get_or_create(
                    review=review,
                    user=commenter,
                    defaults={'comment_text': comment_text}
                )
                log_book_crud_to_mongo('ADD_COMMENT', {
                    'username': commenter.username,
                    'book_title': target_book.title,
                    'comment': comment_text[:50]
                })

    print(f" [+] Added {ReviewComment.objects.count()} community discussion comments")

    # 7. Custom Themed Readlists (Shelves)
    curated_lists = [
        (
            'clara_reads', "Mind-Bending Sci-Fi & Space Operas",
            "Novels exploring deep space, first contact, time paradoxes, and the limits of the human mind.",
            ['Dune', 'Project Hail Mary', 'Sea of Tranquility', 'Neuromancer']
        ),
        (
            'sophie_lit', "Dark Academia & Campus Enigmas",
            "Eccentric scholars, Greek tragedies, collegiate secrets, and the dangerous pursuit of esoteric knowledge.",
            ['The Secret History', 'Babel', 'Piranesi']
        ),
        (
            'alex_classics', "Pillars of World Literature",
            "Timeless classics that shaped literary tradition, moral philosophy, and human storytelling across the centuries.",
            ['Crime and Punishment', 'The Great Gatsby', 'To Kill a Mockingbird', 'Pride and Prejudice', '1984']
        ),
        (
            'maya_nonfiction', "Mind-Expanding Psychology & Human History",
            "Non-fiction works that deconstruct habit formation, macro-anthropology, and the architecture of the modern mind.",
            ['Atomic Habits', 'Sapiens: A Brief History of Humankind', 'Crying in H Mart']
        ),
        (
            'liam_fantasy', "Legendary High Fantasy & Mythic Quests",
            "Grand landscapes, epic magic systems, legendary heroes, and unforgettable world-building.",
            ['The Name of the Wind', 'The Hobbit', 'Good Omens']
        ),
        (
            'chloe_mystery', "Unreliable Narrators & Psychological Twists",
            "Books where every chapter makes you doubt what you know, packed with relentless suspense and stunning revelations.",
            ['The Silent Patient', 'Piranesi', 'The Secret History']
        )
    ]

    for creator_name, list_name, list_desc, book_titles in curated_lists:
        creator = user_map.get(creator_name)
        if not creator:
            continue
        readlist, _ = ReadList.objects.get_or_create(
            user=creator,
            name=list_name,
            defaults={
                'description': list_desc,
                'list_type': 'custom',
                'is_public': True
            }
        )
        for bt in book_titles:
            b = book_map.get(bt)
            if b:
                ReadListItem.objects.get_or_create(readlist=readlist, book=b)

    # Also populate default shelves for all users
    shelf_distribution = [
        ('Read', ['Dune', 'The Hobbit', '1984', 'Project Hail Mary', 'The Name of the Wind', 'Babel', 'Atomic Habits']),
        ('Currently Reading', ['Sea of Tranquility', 'Klara and the Sun', 'The Silent Patient', 'Tomorrow, and Tomorrow, and Tomorrow']),
        ('Want to Read', ['Crime and Punishment', 'Sapiens: A Brief History of Humankind', 'Neuromancer', 'The Great Gatsby'])
    ]

    for u in all_users_list:
        for shelf_name, b_titles in shelf_distribution:
            shelf = ReadList.objects.filter(user=u, name=shelf_name).first()
            if shelf:
                # Add 2-3 books to each user's default shelf
                import random
                assigned = random.sample(b_titles, min(len(b_titles), 2))
                for title in assigned:
                    b = book_map.get(title)
                    if b:
                        ReadListItem.objects.get_or_create(readlist=shelf, book=b)

    print(f" [+] Configured {ReadList.objects.count()} custom & default shelves with {ReadListItem.objects.count()} shelved items")

    # Update all books' rating statistics
    for b in Book.objects.all():
        b.update_rating_stats()

    print("\n=== SUCCESS: Community data enrichment completed! ===")
    print(f"Books: {Book.objects.count()}")
    print(f"Users: {User.objects.count()}")
    print(f"Reviews: {RatingReview.objects.count()}")
    print(f"Comments: {ReviewComment.objects.count()}")
    print(f"Shelves: {ReadList.objects.count()}")
    print(f"Shelved Books: {ReadListItem.objects.count()}")
    print(f"Friendships: {Friendship.objects.count()}")


if __name__ == '__main__':
    run_seeding()
