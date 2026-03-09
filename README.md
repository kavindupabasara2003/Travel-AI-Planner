# 🌴 Travel AI Planner (Layla AI Theme)

[![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-Extension-blue)](#)
[![Ollama](https://img.shields.io/badge/Ollama-LLaMA_3.2-black)](#)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](#)

Welcome to the **Travel AI Planner**, a state-of-the-art, AI-powered travel itinerary generator and live assistant designed specifically for exploring the beautiful island of Sri Lanka. Built with a modern Vue 3 frontend, a robust Django REST Framework backend, and powered by locally-hosted Large Language Models (LLaMA 3.2 via Ollama), this application automates the complex process of travel planning. 

The system leverages cutting-edge Retrieval-Augmented Generation (RAG) and Semantic Vector Caching (`pgvector`) to deliver highly personalized, geographically logical, and real-time context-aware travel advice.

---

## 📖 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Key Features](#2-key-features)
3. [System Architecture & Tech Stack](#3-system-architecture--tech-stack)
4. [Core AI & RAG Pipeline Deep Dive](#4-core-ai--rag-pipeline-deep-dive)
5. [Database Schema & Data Models](#5-database-schema--data-models)
6. [API Reference & Authentication](#6-api-reference--authentication)
7. [Security & Protection](#7-security--protection)
8. [Prerequisites & Environment](#8-prerequisites--environment)
9. [Installation & Deployment](#9-installation--deployment)
10. [Testing Methodology](#10-testing-methodology)
11. [License & Contributing](#11-license--contributing)

---

## 1. Executive Summary

The Travel AI Planner was conceived to solve the overwhelming nature of vacation planning. Traditional travel planners offer static, generic templates. This application takes user preferences—such as duration (e.g., 7 days), starting location, group size (e.g., Couple, Solo), and trip style (e.g., Beach, Cultural, Adventure)—and generates a completely bespoke, JSON-structured daily itinerary.

What sets this project apart is its strict adherence to **Geographic Progression**. The LLM is explicitly constrained to move travelers logically across Sri Lanka (e.g., from Colombo down the South Coast to Galle and Mirissa) rather than aggressively looping them in a single city. Furthermore, the built-in AI Trip Assistant integrates live OpenMeteo weather data and the Sri Lankan native holiday calendar to provide critically timed advice, protecting users from booking outdoor hikes during severe thunderstorms or visiting crowded temples on sacred Poya days.

---

## 2. Key Features

- **Dynamic Itinerary Generation:** Generates comprehensive multi-day itineraries complete with daily themes, time-blocked activities, location constraints, suggested restaurants, and descriptive narratives.
- **Strict Geographic Progression:** Advanced prompt engineering forces the AI model to physically simulate travel, preventing users from staying in the exact same city for more than 2-3 days.
- **Intelligent Semantic Caching:** Utilizes PostgreSQL with the `pgvector` extension to convert user prompts into 768-dimensional mathematical vectors (`nomic-embed-text`). Semantically identical queries bypass the expensive LLM generation entirely, dropping response times from ~130 seconds down to ~2 seconds.
- **Real-Time RAG Trip Assistant:** An interactive chat wizard that intercepts user queries and enriches the AI's prompt with live data:
  - **Live Weather Integration:** Fetches real-time localized weather via the OpenMeteo API. Forbids outdoor activities during thunderstorms or heavy rains and pivots to indoor alternatives (like museums or temples).
  - **Holiday & Weekend Detection:** Synchronized strictly to the `Asia/Colombo` timezone. Detects Sri Lankan Public Holidays (like Madin Full Moon Poya Day) and weekends, warning users about massive crowds or mercantile closures.
- **Secure Authentication System:** JWT-based access tokens with strict Vue Router navigation guards.
- **Admin Dashboard:** A protected portal for system administrators to view deployed models, manage registered users, analyze saved trips, and monitor cache hit rates.

---

## 3. System Architecture & Tech Stack

This application utilizes a decoupled architecture, containerized via Docker Compose to ensure flawless parity between development and production environments.

### Frontend
- **Framework:** Vue.js 3 (Composition API)
- **Build Tool:** Vite
- **State Management:** Pinia
- **Routing:** Vue Router (with comprehensive authentication guards)
- **Styling:** Custom CSS implementing the sleek, white *Layla AI Theme*
- **Production Server:** Caddy (Reverse proxy and static file server)

### Backend API
- **Framework:** Django 4.2 & Django REST Framework (DRF)
- **Application Server:** Gunicorn (configured with elevated 300-second timeouts to accommodate heavy LLM processing)
- **Authentication:** `djangorestframework-simplejwt`
- **Integrations:** `requests` for internal Ollama HTTP API communication and external weather APIs.

### Database
- **Engine:** PostgreSQL 16
- **Extensions:** `pgvector` for storing and computing cosine distances on 768-dimensional embedding arrays.

### Artificial Intelligence
- **Platform:** Ollama (Hosted locally on the Docker host machine `host.docker.internal:11434`)
- **JSON Generator Model:** `llama3.2` (Selected for its unparalleled ability to strictly adhere to complex, multi-layered JSON schema constraints without aborting or hallucinating).
- **Embedding Model:** `nomic-embed-text`

---

## 4. Core AI & RAG Pipeline Deep Dive

### 4.1 Itinerary Generation Engine
When a user submits a trip request, the frontend constructs a highly explicit string:
`"Duration: 7 Days | Start Location: Colombo (CMB Airport) | Group: Couple | Style: Beach"`

This string is passed to `llama_service.py`. The backend utilizes a strict, multi-rule system prompt that forces `llama3.2` to output a deterministic JSON structure. To prevent the LLM from appending conversational fluff (e.g., *"Here is your itinerary..."*) which crashes standard decoders, the backend implements a highly resilient **stack-based bracket counting algorithm** that scans the raw streaming string, isolates the absolute outermost `{` and `}` brackets, and safely extracts the core JSON object.

### 4.2 Semantic Vector Caching (Tier 1 & Tier 2)
To save immense compute power, the application caches itineraries:
1. **Tier 1 (Exact Match):** The backend immediately checks if the exact query string exists in PostgreSQL. If found, it bypasses LLM generation.
2. **Tier 2 (Vector Similarity):** If an exact string match fails, the query is converted into a 768-dimensional vector via `nomic-embed-text`. PostgreSQL calculates the `CosineDistance`. If a previously generated itinerary has a distance of `<= 0.005`, the system investigates it. 
3. **False Positive Prevention:** It explicitly checks if the texts match to prevent semantic overlaps (e.g., an extra space) from returning the wrong trip.

### 4.3 Real-Time Contextual RAG
The `TripAssistantService` parses user questions (e.g., *"Should I visit Sigiriya Rock today?"*). 
1. It snaps the server clock to `ZoneInfo("Asia/Colombo")`.
2. It cross-references the current date against a local JSON database of Sri Lankan holidays.
3. It pings the exact GPS coordinates to OpenMeteo.
4. It synthesizes a hidden "Context Block" (e.g., *Holiday Status: Poya Day, Weather: Thunderstorms*) and forcefully instructs the LLM to read the context before advising the user.

---

## 5. Database Schema & Data Models

The PostgreSQL backend utilizes Django ORM to define the following primary structures:

### `User` (Django Native)
- Standard authentication model extended with `is_staff` and `is_superuser` to manage Admin route accessibility.

### `ItineraryCache`
The heart of the pgvector implementation.
- `id`: UUID Primary Key
- `query_text`: String (The exact prompt used)
- `embedding`: VectorField(dimensions=768) (The mathematical translation of the prompt)
- `itinerary_json`: JSONField (The saved LLM response)
- `created_at`: Datetime

### `SavedTrip`
Allows end-users to bookmark generated trips to their profile.
- `user`: ForeignKey to User
- `title`: String
- `trip_data`: JSONField

---

## 6. API Reference & Authentication

All endpoints are prefixed with `/api/v1/`.

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/token/` | POST | No | Exchanges `username` & `password` for `access` & `refresh` JWTs. |
| `/token/refresh/` | POST | No | Exchanges a valid `refresh` token for a new `access` token. |
| `/plan/` | POST | Yes | Initiates the Semantic Cache lookup or LLaMA generation pipeline. |
| `/chat/` | POST | Yes | Connects to the RAG Trip Assistant for real-time contextual advice. |

*Requests to protected routes must include the header: `Authorization: Bearer <access_token>`*

---

## 7. Security & Protection

### Frontend Vue Router Guards
The application implements strict client-side routing protection.
- Visitors attempting to access `/planner` or `/profile` without a token are forcefully redirected to the `/` root domain.
- Users who successfully authenticate but lack the `is_admin: true` flag in their decoded JWT are actively blocked from rendering `/admin` and its sub-routes, emitting an unauthorized warning to the console.

### Backend Data Integrity
- Django CORS headers are configured to prevent cross-origin scripting.
- PostgreSQL databases are completely hidden behind the Docker network bridge and are not directly exposed to the host machine.

---

## 8. Prerequisites & Environment

To run this project, your host machine must have the following installed:
- **Docker** and **Docker Compose**
- **Ollama** (Running natively on the host machine to access GPU hardware acceleration)
- LLaMA Models Pulled:
  - `ollama run llama3.2`
  - `ollama run nomic-embed-text`

### Environment Variables
Below are the critical environment variables automatically managed by Docker:
```env
# Backend / docker-compose.yml
DB_HOST=db
DB_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=travel_ai
OLLAMA_HOST=http://host.docker.internal:11434
```

---

## 9. Installation & Deployment

### Step 1: Clone the Repository
```bash
git clone https://github.com/kavindupabasara2003/Travel-AI-Planner.git
cd Travel-AI-Planner
```

### Step 2: Ensure Ollama is Running
Ensure your local Ollama instance is serving on port 11434.
```bash
ollama serve
```

### Step 3: Build and Spin Up Docker Compose
The `docker-compose.yml` file orchestration handles the PostgreSQL initialization, `pgvector` extension mounting, Django migrations, Gunicorn server execution, and Vite/Caddy static building.

```bash
docker-compose up -d --build
```

### Step 4: Verify Services
- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **Django API:** [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)
- **Database:** Internal Port 5432

---

## 10. Testing Methodology

The system has been rigorously tested against edge cases using Python, Bash, and Microsoft Playwright E2E browser tests.

- **TC-09 (Cache Hit):** Validated that identical prompts trigger an immediate 2-second response.
- **TC-10 (Vector False Positives):** Verified that adding invisible spaces tricks the vector math but is caught by strict string equivalence checks, forcing a safe cache-miss.
- **TC-13 (RAG Holiday Detection):** Python `datetime` mocks were used to inject "March 2, 2026" into the server, successfully forcing the AI to warn users to avoid temples due to "Madin Full Moon Poya Day" crowds.
- **TC-16 (RAG Weather Fallbacks):** OpenMeteo API interceptions successfully fed "Severe Thunderstorm" data into the pipeline. The AI actively blocked a user from climbing Sigiriya Rock and successfully routed them to the indoor Sigiriya Museum.
- **TC-29 & TC-30 (Route Guards):** Playwright automated scripts proved that anonymous users and standard users are aggressively redirected away from the Admin dashboards.

---

## 11. License & Contributing

This project is proprietary and built for demonstration, educational, and academic evaluation purposes. 

### Contributing
Given the complex nature of the AI orchestration and Semantic Vector Caching:
1. Ensure you have tested your structural LLaMA prompts heavily against `json.loads` prior to submitting Pull Requests.
2. If modifying backend time-based features, you **must** use `ZoneInfo("Asia/Colombo")` instead of naive system time to prevent container timezone drift.
3. Run `docker-compose down -v` to purge volumes if migrating database schemas.

---
*Powered by LLaMA 3.2, Vue.js, and Django.*
