import os
import requests
from PIL import Image, ImageDraw, ImageFont

MEDIA_DIR = os.path.join(os.getcwd(), "media", "covers")
os.makedirs(MEDIA_DIR, exist_ok=True)

# Accurate Open Library cover IDs discovered from direct work lookup:
# Dune (OL893415W): 11481354
# Project Hail Mary (OL20150917W): 11200092
# The Hobbit (OL262758W): 8406766
# 1984 (OL1168007W): 7222246
# Pride and Prejudice (OL1599723W): 13148521
# The Secret History (OL338274W): 744854
# Piranesi (OL20875323W): 10226290
# Tomorrow, and Tomorrow, and Tomorrow (OL25672935W): 12859975

books_covers = [
    {
        'slug': 'dune',
        'title': 'Dune',
        'author': 'Frank Herbert',
        'ol_id': '11481354',
        'theme_color': (184, 115, 51), # Rich spiced desert sand
        'accent_color': (245, 197, 66),
    },
    {
        'slug': 'project_hail_mary',
        'title': 'Project Hail Mary',
        'author': 'Andy Weir',
        'ol_id': '11200092',
        'theme_color': (20, 24, 38), # Deep space cosmic blue
        'accent_color': (235, 175, 40),
    },
    {
        'slug': 'the_hobbit',
        'title': 'The Hobbit',
        'author': 'J.R.R. Tolkien',
        'ol_id': '8406766',
        'theme_color': (34, 76, 56), # Shire forest emerald
        'accent_color': (212, 175, 55),
    },
    {
        'slug': '1984',
        'title': '1984',
        'author': 'George Orwell',
        'ol_id': '7222246',
        'theme_color': (140, 29, 29), # Dystopian stark crimson
        'accent_color': (240, 230, 210),
    },
    {
        'slug': 'pride_and_prejudice',
        'title': 'Pride and Prejudice',
        'author': 'Jane Austen',
        'ol_id': '13148521',
        'theme_color': (100, 70, 95), # Regency mauve / plum
        'accent_color': (230, 215, 195),
    },
    {
        'slug': 'the_secret_history',
        'title': 'The Secret History',
        'author': 'Donna Tartt',
        'ol_id': '744854',
        'theme_color': (28, 43, 40), # Dark academia deep ivy
        'accent_color': (218, 165, 32),
    },
    {
        'slug': 'piranesi',
        'title': 'Piranesi',
        'author': 'Susanna Clarke',
        'ol_id': '10226290',
        'theme_color': (45, 65, 80), # Marble labyrinth sea mist
        'accent_color': (210, 220, 230),
    },
    {
        'slug': 'tomorrow_and_tomorrow_and_tomorrow',
        'title': 'Tomorrow, and Tomorrow, and Tomorrow',
        'author': 'Gabrielle Zevin',
        'ol_id': '12859975',
        'theme_color': (200, 60, 50), # Great Wave vivid vermilion
        'accent_color': (255, 230, 150),
    },
]

print("Downloading and verifying book covers from Open Library...", flush=True)

headers = {'User-Agent': 'Bookboxd/1.0 (Educational Book Diary Webapp)'}

for b in books_covers:
    filepath = os.path.join(MEDIA_DIR, f"{b['slug']}.jpg")
    url = f"https://covers.openlibrary.org/b/id/{b['ol_id']}-L.jpg"
    success = False
    try:
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f"Downloaded Open Library cover for {b['title']}: {filepath} ({len(r.content)} bytes)")
            success = True
    except Exception as e:
        print(f"Failed to fetch OL cover for {b['title']}: {e}")

    # If Open Library fails or is unavailable, create a pristine typographic book cover
    if not success or not os.path.exists(filepath):
        print(f"Generating high-res typography cover for {b['title']}...")
        w, h = 600, 900
        img = Image.new('RGB', (w, h), color=b['theme_color'])
        draw = ImageDraw.Draw(img)

        # Draw decorative inner border
        draw.rectangle([25, 25, w-25, h-25], outline=b['accent_color'], width=3)
        draw.rectangle([35, 35, w-35, h-35], outline=(255, 255, 255, 60), width=1)

        # Book title text
        draw.text((w/2, 380), b['title'].upper(), fill=(255, 255, 255), anchor="mm")
        draw.text((w/2, 480), f"by {b['author']}", fill=b['accent_color'], anchor="mm")
        img.save(filepath, "JPEG", quality=95)
