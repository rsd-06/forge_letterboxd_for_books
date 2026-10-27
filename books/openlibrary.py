import logging
import requests
from django.core.cache import cache
from .models import Book

logger = logging.getLogger(__name__)

OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
OPEN_LIBRARY_WORKS_URL = "https://openlibrary.org/works"
COVERS_URL = "https://covers.openlibrary.org/b/id"


def search_open_library(query, limit=20):
    """
    Search Open Library API for books matching query.
    Returns list of parsed dicts.
    """
    if not query or not query.strip():
        return []

    cache_key = f"ol_search_{query.strip().lower()}_{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    params = {
        'q': query.strip(),
        'limit': limit,
        'fields': 'key,title,author_name,cover_i,first_publish_year,isbn,subject,number_of_pages_median,ratings_average,ratings_count'
    }

    try:
        response = requests.get(OPEN_LIBRARY_SEARCH_URL, params=params, timeout=6)
        if response.status_code == 200:
            data = response.json()
            docs = data.get('docs', [])
            results = []
            for doc in docs:
                work_key = doc.get('key', '').replace('/works/', '')
                if not work_key:
                    continue

                cover_id = doc.get('cover_i')
                cover_url = f"{COVERS_URL}/{cover_id}-L.jpg" if cover_id else None
                authors = doc.get('author_name', ['Unknown Author'])
                author_str = ', '.join(authors[:2])
                subjects = doc.get('subject', [])
                genre = ', '.join(subjects[:3]) if subjects else 'Fiction'
                isbn_list = doc.get('isbn', [])
                first_isbn = isbn_list[0] if isbn_list else None

                results.append({
                    'openlibrary_key': work_key,
                    'title': doc.get('title', 'Untitled'),
                    'author': author_str,
                    'cover_url': cover_url,
                    'first_publish_year': doc.get('first_publish_year'),
                    'genre': genre,
                    'isbn': first_isbn,
                    'page_count': doc.get('number_of_pages_median'),
                })
            cache.set(cache_key, results, timeout=600)  # cache 10 mins
            return results
    except Exception as e:
        logger.warning(f"Error querying Open Library: {e}")

    return []


def get_or_create_book_from_ol(work_key, fallback_doc=None):
    """
    Given an Open Library work key (e.g. 'OL45804W'),
    find or create the Book in the local DB.
    """
    clean_key = work_key.replace('/works/', '').strip()
    book = Book.objects.filter(openlibrary_key=clean_key).first()
    if book:
        return book

    # Try fetching details from Open Library works endpoint if details needed
    title = "Unknown Book"
    author = "Unknown Author"
    description = ""
    cover_url = None
    first_publish_year = None
    genre = "Fiction"
    page_count = None
    isbn = None

    if fallback_doc:
        title = fallback_doc.get('title') or title
        author = fallback_doc.get('author') or author
        cover_url = fallback_doc.get('cover_url') or cover_url
        first_publish_year = fallback_doc.get('first_publish_year')
        genre = fallback_doc.get('genre') or genre
        isbn = fallback_doc.get('isbn')
        page_count = fallback_doc.get('page_count')

    try:
        url = f"{OPEN_LIBRARY_WORKS_URL}/{clean_key}.json"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            work_data = res.json()
            title = work_data.get('title', title)
            desc_val = work_data.get('description', '')
            if isinstance(desc_val, dict):
                description = desc_val.get('value', '')
            elif isinstance(desc_val, str):
                description = desc_val

            covers = work_data.get('covers', [])
            if covers and not cover_url:
                cover_url = f"{COVERS_URL}/{covers[0]}-L.jpg"

            subjects = work_data.get('subjects', [])
            if subjects:
                genre = ', '.join(subjects[:3])
    except Exception as e:
        logger.warning(f"Failed to fetch detailed work info for {clean_key}: {e}")

    book, _ = Book.objects.get_or_create(
        openlibrary_key=clean_key,
        defaults={
            'title': title,
            'author': author,
            'description': description or f"A celebrated work by {author}.",
            'cover_url': cover_url,
            'first_publish_year': first_publish_year,
            'genre': genre,
            'page_count': page_count,
            'isbn': isbn,
        }
    )
    return book
