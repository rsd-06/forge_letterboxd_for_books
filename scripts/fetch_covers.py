import requests

titles = [
    ('Dune', 'Frank Herbert'),
    ('Project Hail Mary', 'Andy Weir'),
    ('The Hobbit', 'Tolkien'),
    ('1984', 'George Orwell'),
    ('Pride and Prejudice', 'Jane Austen'),
    ('The Secret History', 'Donna Tartt'),
    ('Piranesi', 'Susanna Clarke'),
    ('Tomorrow, and Tomorrow, and Tomorrow', 'Gabrielle Zevin')
]

for title, author in titles:
    try:
        url = f"https://openlibrary.org/search.json?title={requests.utils.quote(title)}&author={requests.utils.quote(author)}&limit=5"
        res = requests.get(url, timeout=10)
        data = res.json()
        print(f"=== {title} by {author} ===")
        for doc in data.get('docs', [])[:3]:
            cover_i = doc.get('cover_i')
            t = doc.get('title')
            authors = doc.get('author_name', [])
            isbns = doc.get('isbn', [])
            first_isbn = isbns[0] if isbns else None
            print(f"  Title: {t} | Cover ID: {cover_i} | ISBN: {first_isbn}")
            if cover_i:
                print(f"  -> Cover URL: https://covers.openlibrary.org/b/id/{cover_i}-L.jpg")
    except Exception as e:
        print(f"Error fetching {title}: {e}")
