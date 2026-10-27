# Bookboxd — Letterboxd for Books 📚

A social diary, review platform, and recommendation network for bibliophiles. Inspired by the sleek social tracking of **Letterboxd** and styled with the warm, bookish aesthetic of **Goodreads**.

---

## 🌟 Live Demo & Local Quickstart

- **Repository**: [https://github.com/rsd-06/forge_letterboxd_for_books](https://github.com/rsd-06/forge_letterboxd_for_books)
- **Local URL**: `http://127.0.0.1:8000`

### Quick Setup:

```bash
# 1. Activate virtual environment
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate  # macOS/Linux

# 2. Run database migrations
python manage.py migrate

# 3. Seed initial books, demo users, shelves, and 12 FAQs
python manage.py seed_books

# 4. Start local development server
python manage.py runserver
```

---

## 🚀 Key Features

### 1. 5-Star Rating System & Spoiler-Protected Reviews
- Rate any book on a **1.0 to 5.0 star scale** with 0.5 half-star precision.
- Write reviews with a **"Contains spoilers" toggle**: reviews are masked with a blur effect and a click-to-reveal button so fellow readers are never spoiled.
- Rating distribution visual breakdown (1★ through 5★) on every book page.

### 2. Friends Network & Live Activity Feed
- Follow and add fellow readers as friends.
- Home dashboard features a **Letterboxd-style live activity feed** displaying recent ratings, reviews, and shelf additions from your network.
- Comment on any community member's review to spark literary discussions.

### 3. Multiple Custom Readlists & Default Shelves
- Three default shelves initialized for every user: **Want to Read**, **Currently Reading**, and **Read**.
- Create **unlimited custom readlists** (e.g. *"Best Sci-Fi of 2024"*, *"Cozy Autumn Mysteries"*) with descriptions and public/private visibility.

### 4. Free Open Library Internet Database Integration
- Live search queries millions of global titles, editions, and authors from the free [Open Library REST API](https://openlibrary.org/).
- **Resilient 3.0s Timeout with Local Fallback**: If Open Library times out or is unreachable, the system seamlessly serves local curated masterpieces and cached records.

### 5. Google Gemini AI Assistant & Profile Recommendations
- **The Bibliophile**: An interactive AI chat companion embedded on every page (and dedicated at `/ai-assistant/`) answering literary questions, summarizing tropes, explaining features, and recommending books.
- **AI Curator on User Profiles**: Personalized reading recommendations analyzing the user's high-rated books, reading habits, and preferred genres.
- **Automated Support Ticket Filing**: When the AI cannot resolve an inquiry or upon user request, it automatically creates a SQL support ticket with a unique reference code (`TKT-XXXX`).

### 6. Dual-Database Architecture: SQL & MongoDB
- **SQL Database (SQLite / PostgreSQL)**: Stores primary relational data (Users, Profiles, Books, Shelves, Ratings, Reviews, Comments, 12 FAQs, and Support Tickets).
- **MongoDB NoSQL Database**: Stores conversation chat logs (`chat_logs`), user feedback ratings (`chat_feedback`), HTTP request metrics (`request_logs`), and user/book CRUD audit trails (`user_crud_logs`, `book_crud_logs`).
- **Resilient Fallback**: If MongoDB is not configured or offline, local fallback logging keeps the entire platform functional without interruptions.

### 7. Minimum 10 FAQs in Database
- 12 comprehensive FAQs covering ratings, spoilers, shelves, Gemini AI, error codes, and support tickets.
- Displayed on the dedicated `/faq/` knowledge base page AND directly on the Home / Landing page.

### 8. Minimum 8 Error Codes Handled & Custom Error Pages
- Handles and explains 8 error codes:
  - `400 Bad Request`
  - `401 Unauthorized`
  - `403 Forbidden`
  - `404 Not Found` (Custom page with **"Ask the Assistant"** option)
  - `422 Unprocessable Book Metadata` (Site-specific code)
  - `429 Too Many Requests`
  - `500 Internal Server Error` (Custom page with **"Ask the Assistant"** option)
  - `503 Service Unavailable`
- Test all 8 codes live at `/errors/`.

### 9. Request Logging & System Health Check
- Custom middleware logs all incoming HTTP requests, response status codes, IP addresses, and execution latency.
- Live `/health/` telemetry page (and `/health/?format=json`) reporting SQL database health, MongoDB status, Gemini AI status, and Open Library 3rd-party API latency.

---

## 🔑 Environment Variables & How to Get Free API Keys

All confidential credentials are kept strictly in `.env` (which is git-ignored):

```env
DJANGO_SECRET_KEY=your-django-secret-key
DJANGO_DEBUG=True

# 1. Google Gemini API Key (100% Free)
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# 2. MongoDB Atlas Connection URI (100% Free M0 Cluster)
MONGODB_URI=
MONGODB_NAME=bookboxd
```

### How to Get Your Free Google Gemini API Key:
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** and then **"Create API key in new project"**.
4. Copy the generated key and paste it as `GEMINI_API_KEY=` in your `.env` file.

### How to Get Your Free MongoDB Atlas URI:
1. Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and register for a free account.
2. Create a free **M0 Shared Cluster**.
3. Under **Database Access**, create a database username and password.
4. Under **Network Access**, click **Add IP Address** and select `0.0.0.0/0` (Allow Access from Anywhere) or add your current IP.
5. In your cluster dashboard, click **Connect** > **Drivers** > **Python**.
6. Copy the connection string (e.g., `mongodb+srv://<username>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority`) and paste it as `MONGODB_URI=` in `.env`.

*(Note: If you leave `GEMINI_API_KEY` or `MONGODB_URI` blank, Bookboxd automatically activates its built-in smart heuristic recommendations and local audit logging, so the entire site runs completely out of the box!)*

---

## 🧪 Playwright Automated Verification

A full Playwright end-to-end test suite is included in `tests/test_webapp_playwright.py`:

```bash
# Run the test suite
pytest tests/test_webapp_playwright.py -v
```

### Verified Test Cases:
1. **Desktop Viewport**: Tests Goodreads-themed header, poster carousel, activity feed, and floating chat widget.
2. **Mobile Device Viewport (iPhone 13)**: Verifies responsive rendering, hamburger navigation drawer, and mobile chat button.
3. **Custom 404 Page**: Verifies invalid routes return HTTP 404 with custom literary template and interactive "Ask the Assistant" option.
4. **FAQ Verification**: Verifies minimum 10 FAQs stored in SQL database and displayed on `/faq/` and the home page.
5. **8 Error Codes**: Verifies all 8 codes (400, 401, 403, 404, 422, 429, 500, 503) are handled and documented.
6. **Book Detail & Spoilers**: Verifies 5-star rating display and click-to-reveal spoiler toggle.
7. **Health Check**: Verifies `/health/` telemetry endpoint and 3rd-party API 3.0s timeout with fallback.

---

## 💡 Proposed Improvement

**Real-Time Book Club Reading Rooms & Vector Similarity Shelf Search:**
- **Feature**: Integrate Django Channels / WebSockets to enable live "Buddy Reads" and book club group discussions where friends reading the same book can comment in real-time chapter threads with synchronized spoiler checkpoints.
- **AI Vector Search**: Generate text embeddings (using Gemini or Vertex AI embeddings) for book themes and user reading tastes to enable semantic search (e.g. searching *"melancholy sci-fi novels set on ocean planets"* and instantly retrieving accurate matches even if those exact words do not appear in the title).
