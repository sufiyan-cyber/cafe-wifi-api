# ☕ Café Radar — Bangalore Café Discovery API

> A production-grade REST API for discovering cafés across Bangalore. Built with Flask and PostgreSQL, deployed on AWS with a full CI/CD pipeline.

**🌐 Live:** [cafe.sufiyan.co.in](http://cafe.sufiyan.co.in) &nbsp;|&nbsp; **📄 API Docs:** [Postman Documentation](https://documenter.getpostman.com/view/52395039/2sBXcBo3HV)

![CI/CD](https://github.com/sufiyan-cyber/cafe-wifi-api/actions/workflows/deploy.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![AWS](https://img.shields.io/badge/AWS-Elastic%20Beanstalk-orange)

---

## Architecture

```
                        ┌─────────────────────┐
                        │   Custom Domain      │
                        │  cafe.sufiyan.co.in  │
                        └────────┬────────────┘
                                 │ CNAME
                        ┌────────▼────────────┐
                        │  Elastic Beanstalk   │
                        │   Flask + Gunicorn   │
                        │    (4 workers)       │
                        └────────┬────────────┘
                                 │
                        ┌────────▼────────────┐
                        │    AWS RDS           │
                        │  PostgreSQL 16       │
                        │  (db.t3.micro)       │
                        └─────────────────────┘

         GitHub Push → GitHub Actions → Run Tests → Deploy to EB
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.0 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 16 (AWS RDS) |
| Deployment | AWS Elastic Beanstalk |
| Web Server | Gunicorn |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Auth | Bearer Token (admin routes) |
| DNS | GoDaddy CNAME → EB endpoint |

---

## Dataset

- **Source:** Zomato Bangalore dataset (Kaggle)
- **Size:** 2,067 café entries across 46 locations
- **Cleaning pipeline:**
  - Removed nulls — filled non-critical columns, dropped only where critical fields missing
  - Converted `Yes/No` strings → PostgreSQL booleans
  - Cleaned cost column — stripped commas, converted to integer, filled nulls with median
  - Renamed columns for API consistency (`listed_in(type)` → `listed_in_type`)
  - Deduplication handled at query level using `DISTINCT ON (name, location)` — preserves raw data integrity while preventing duplicate results in API responses

---

## API Endpoints

### Public Routes

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/all` | Paginated list of all cafés |
| GET | `/random` | One randomly selected café |
| GET | `/search` | Filter by location, rating, cost, online order |
| GET | `/locations` | All unique locations for dropdown population |

### Admin Routes (Bearer Token required)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/add` | Add a new café |
| PATCH | `/update-price/<id>` | Update café cost |
| DELETE | `/report-closed/<id>` | Remove a café |

### Example Requests

```bash
# Get all cafés — page 2, 18 per page
GET /all?page=2&per_page=18

# Filter cafés in Koramangala with rating ≥ 4.2 and cost ≤ ₹800
GET /search?location=Koramangala&min_rate=4.2&max_cost=800&online_order=true

# Admin — delete a café
DELETE /report-closed/42
Authorization: Bearer <api_key>
```

### Response Shape

```json
{
  "cafes": [
    {
      "id": 1,
      "name": "Third Wave Coffee",
      "address": "14, 80 Feet Road, Koramangala",
      "location": "Koramangala",
      "rate": 4.5,
      "votes": 1200,
      "online_order": true,
      "book_table": false,
      "approx_cost": 600,
      "rest_type": ["Café", "Quick Bites"],
      "cuisines": ["Coffee", "Continental", "Beverages"],
      "dish_liked": ["Cold Brew", "Croissant", "Avocado Toast"],
      "listed_in_type": "Cafes",
      "listed_in_city": "Koramangala"
    }
  ],
  "total": 2067,
  "page": 1,
  "pages": 115,
  "per_page": 18
}
```

---

## Key Engineering Decisions

**Why DISTINCT at query level instead of deleting duplicates?**
The source dataset lists the same café under multiple categories (Cafes, Buffet, Drinks & Nightlife). Rather than deleting 1,700+ rows and losing categorical data, duplicates are handled using PostgreSQL's `DISTINCT ON (name, location)` at query time. Raw data stays intact for potential analytics use cases.

**Why Elastic Beanstalk over EC2?**
EB manages the underlying EC2 instance, load balancer, and auto-scaling automatically. For a single-service API this is the right tradeoff — operational overhead is low while still being a genuine AWS deployment with full control over environment config.

**Why Bearer token over session auth for admin routes?**
Admin operations (add, update, delete) are not exposed on the frontend at all — they're exclusively for internal use via Postman or CLI. Bearer token over Authorization header is the correct pattern for this use case and avoids session management complexity.

**Why Gunicorn with 4 sync workers?**
On a `t3.micro` instance (2 vCPU), 4 workers follows the standard `(2 × CPUs) + 1` formula. Each sync worker handles one request at a time — appropriate for a database-bound API with no long-running async operations.

---

## CI/CD Pipeline

Every push to `main` triggers the GitHub Actions workflow:

```
git push → GitHub Actions triggered
              │
              ▼
         ┌─────────────────────────┐
         │  Job 1: Run Tests        │
         │  • Fresh Ubuntu runner   │
         │  • Install dependencies  │
         │  • pytest (14 tests)     │
         │  • SQLite in-memory DB   │
         └────────────┬────────────┘
                      │ tests pass
                      ▼
         ┌─────────────────────────┐
         │  Job 2: Deploy to EB    │
         │  • Zip application      │
         │  • Upload to S3         │
         │  • Create EB version    │
         │  • Trigger deployment   │
         └─────────────────────────┘
                      │ tests fail
                      ▼
                 Deploy blocked
```

Broken code never reaches production.

---

## Test Coverage

```bash
pytest test_main.py -v
```

```
test_home                          PASSED
test_get_all_cafes_empty           PASSED
test_get_all_cafes_pagination      PASSED
test_random_cafe_empty_db          PASSED
test_search_no_results             PASSED
test_locations_empty               PASSED
test_add_cafe_no_auth              PASSED
test_delete_no_auth                PASSED
test_update_price_no_auth          PASSED
test_add_cafe_with_auth            PASSED
test_delete_nonexistent_cafe       PASSED
test_update_price_nonexistent      PASSED
test_add_then_delete               PASSED
test_add_missing_required_fields   PASSED

14 passed in 0.95s
```

Tests cover public routes, auth protection, CRUD operations, edge cases, and pagination.

---

## Local Development

### Prerequisites
- Python 3.11
- PostgreSQL
- Docker (optional)

### Setup

```bash
# Clone the repo
git clone https://github.com/sufiyan-cyber/cafe-wifi-api.git
cd cafe-wifi-api

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your DB credentials
```

### Environment Variables

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/cafes_db
API_KEY=yoursecretkey
```

### Run locally

```bash
python main.py
```

### Run with Docker

```bash
docker build -t cafe-radar .
docker run --env-file .env -p 5000:5000 cafe-radar
```

### Run tests

```bash
pytest test_main.py -v
```

---

## Project Structure

```
cafe-wifi-api/
├── main.py              # Flask app — routes, model, API logic
├── test_main.py         # pytest test suite (14 tests)
├── requirements.txt     # Python dependencies
├── Procfile             # Gunicorn config for Elastic Beanstalk
├── Dockerfile           # Container definition for local dev
├── .dockerignore        # Docker build exclusions
├── .ebignore            # EB deployment exclusions
├── templates/
│   └── index.html       # Frontend entry point
├── static/
│   ├── style.css        # Styling
│   └── script.js        # Frontend API calls
└── .github/
    └── workflows/
        └── deploy.yml   # GitHub Actions CI/CD pipeline
```

---

## Future Improvements

- AWS Cognito authentication for user login/signup
- Redis caching for frequently queried locations
- Rate limiting on public endpoints
- AI-powered café recommendations using AWS Bedrock

---

## Author

**Sufiyan Khan S** — Information Science & Engineering, The Oxford College of Engineering, Bangalore

[![GitHub](https://img.shields.io/badge/GitHub-sufiyan--cyber-black)](https://github.com/sufiyan-cyber)
