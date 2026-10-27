import urllib.request
import json
import os
from PIL import Image

MEDIA_COVERS_DIR = os.path.join(os.getcwd(), 'media', 'covers')
os.makedirs(MEDIA_COVERS_DIR, exist_ok=True)

# Curated list of 14 new books with search query and fallback known cover IDs or Open Library work keys
NEW_BOOKS = [
    {
        'title': 'The Name of the Wind',
        'author': 'Patrick Rothfuss',
        'slug': 'the_name_of_the_wind',
        'isbn': '9780756404741',
        'ol_key': 'OL8451877W',
        'preferred_cover_id': 8547468  # Iconic hooded figure green/gold
    },
    {
        'title': 'The Great Gatsby',
        'author': 'F. Scott Fitzgerald',
        'slug': 'the_great_gatsby',
        'isbn': '9780743273565',
        'ol_key': 'OL69738W',
        'preferred_cover_id': 8432047  # Iconic blue celestial eyes
    },
    {
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'slug': 'to_kill_a_mockingbird',
        'isbn': '9780060935467',
        'ol_key': 'OL7353617W',
        'preferred_cover_id': 8225261  # Iconic tree silhouette / brown cover
    },
    {
        'title': 'Babel',
        'author': 'R.F. Kuang',
        'slug': 'babel',
        'isbn': '9780063021426',
        'ol_key': 'OL25672950W',
        'preferred_cover_id': 12891395 # Babel tower silver/black
    },
    {
        'title': 'Atomic Habits',
        'author': 'James Clear',
        'slug': 'atomic_habits',
        'isbn': '9780735211292',
        'ol_key': 'OL20150920W',
        'preferred_cover_id': 12843588 # Official white/gold dots cover
    },
    {
        'title': 'Sapiens: A Brief History of Humankind',
        'author': 'Yuval Noah Harari',
        'slug': 'sapiens',
        'isbn': '9780062316097',
        'ol_key': 'OL17079549W',
        'preferred_cover_id': 8231990  # Iconic fingerprint/white cover
    },
    {
        'title': 'The Silent Patient',
        'author': 'Alex Michaelides',
        'slug': 'the_silent_patient',
        'isbn': '9781250301697',
        'ol_key': 'OL19732943W',
        'preferred_cover_id': 10582963 # Iconic Greek statue eye tear / white cover
    },
    {
        'title': 'Klara and the Sun',
        'author': 'Kazuo Ishiguro',
        'slug': 'klara_and_the_sun',
        'isbn': '9780593318171',
        'ol_key': 'OL21175654W',
        'preferred_cover_id': 11181285 # Iconic orange/yellow geometric sun
    },
    {
        'title': 'Crying in H Mart',
        'author': 'Michelle Zauner',
        'slug': 'crying_in_h_mart',
        'isbn': '9780525657743',
        'ol_key': 'OL21689404W',
        'preferred_cover_id': 10959441 # Iconic red/yellow noodle chopsticks
    },
    {
        'title': 'Sea of Tranquility',
        'author': 'Emily St. John Mandel',
        'slug': 'sea_of_tranquility',
        'isbn': '9780593321447',
        'ol_key': 'OL25672945W',
        'preferred_cover_id': 12644265 # Forest canopy / moon
    },
    {
        'title': 'Good Omens',
        'author': 'Neil Gaiman & Terry Pratchett',
        'slug': 'good_omens',
        'isbn': '9780060853983',
        'ol_key': 'OL27482W',
        'preferred_cover_id': 8234388  # Iconic red/black silhouettes Crowley & Aziraphale
    },
    {
        'title': 'Crime and Punishment',
        'author': 'Fyodor Dostoevsky',
        'slug': 'crime_and_punishment',
        'isbn': '9780143058144',
        'ol_key': 'OL1168007W',
        'preferred_cover_id': 8231856  # Penguin classic edition
    },
    {
        'title': 'Neuromancer',
        'author': 'William Gibson',
        'slug': 'neuromancer',
        'isbn': '9780441569595',
        'ol_key': 'OL8451870W',
        'preferred_cover_id': 8235114  # Classic neon grid matrix
    },
    {
        'title': 'The Catcher in the Rye',
        'author': 'J.D. Salinger',
        'slug': 'the_catcher_in_the_rye',
        'isbn': '9780316769488',
        'ol_key': 'OL1168003W',
        'preferred_cover_id': 8228691  # Iconic red carousel horse
    }
]

def download_and_verify(book):
    slug = book['slug']
    target_path = os.path.join(MEDIA_COVERS_DIR, f"{slug}.jpg")
    
    # Try preferred cover id first
    cid = book.get('preferred_cover_id')
    headers = {'User-Agent': 'Bookboxd/1.0 (educational book platform)'}
    
    urls_to_try = []
    if cid:
        urls_to_try.append(f"https://covers.openlibrary.org/b/id/{cid}-L.jpg")
    if book.get('isbn'):
        urls_to_try.append(f"https://covers.openlibrary.org/b/isbn/{book['isbn']}-L.jpg")
    if book.get('ol_key'):
        urls_to_try.append(f"https://covers.openlibrary.org/b/olid/{book['ol_key']}-L.jpg")

    for url in urls_to_try:
        try:
            print(f"Trying {book['title']} from {url}...")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read()
                # Check size - Open Library returns a 1x1 807-byte GIF/JPEG for misses
                if len(content) > 3000:
                    with open(target_path, 'wb') as f:
                        f.write(content)
                    # Verify with PIL
                    with Image.open(target_path) as im:
                        im.verify()
                    print(f"SUCCESS: {book['title']} ({len(content)} bytes) -> {target_path}")
                    return True
                else:
                    print(f"Small file ({len(content)} bytes), skipping...")
        except Exception as e:
            print(f"Failed {url}: {e}")
    
    print(f"FAILED to download {book['title']}")
    return False

if __name__ == '__main__':
    results = {}
    for b in NEW_BOOKS:
        results[b['title']] = download_and_verify(b)
    print("\nSummary:")
    for t, ok in results.items():
        print(f" - {t}: {'OK' if ok else 'FAILED'}")
