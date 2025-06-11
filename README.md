# prolio
CS 144: Web Applications. Repository for Prolio, an interactive resume content management system!

# About 

Prolio is our web app for resume creation through a simple and intuitive ui, that supports injecting into internal LaTeX templates and compilation into a ATS-compatible PDF rendered from LaTeX for clean formatting. Users may also invite AI feedback as they work with the help of our AI reviewer built-on Gemini. 

We support drag and drop for ease of reordering resume elements within resume sections as well as geolocation for convenient location filling.

## Setup

To build and run the service do:
`docker-compose build && docker-compose up`

and the frontend should be default available at `localhost:3000`.

Note that you will need to provide a Gemini API key to make use of the api service which you can obtain currently for free from Google's AI Studio. 

We have a mock OAuth flow and mock GCS bucket and SQLite for the DB by default but in our main deployment we use the actual services and our PostgreSQL DB is hosted on Supabase.

# ENV Variable Setup

Env variable setup

```
GOOGLE_CLIENT_ID=<OAUTH_GOOGLE_CLIENT_ID>
GOOGLE_CLIENT_SECRET=<OAUTH_GOOGLE_CLIENT_SECRET>

DATABASE_URL=<DATABASE_URL>

GEMINI_API_KEY=<GEMINI_API_KEY>

GCS_BUCKET_NAME=<GCS_BUCKET_NAME>

REDIS_IP=<REDIS_IP>

TEXIFY_URL=<COMPILER_SERVICE_URL>
CLIENT_ORIGIN=<FRONTEND_SERVER_URL>
SERVER_URL=<API_URL>
```

# Repo Organization

`web` is NextJS which uses the App Router system to route via the directory structure. 
We use NextJS, React, Tailwind, Shadcn as our main libraries and frameworks for frontend styling, hooks, acessibility in component primitives, etc.
We have response uis, accessibilities features, PWA and offline support via our manifest and service workers using Serwist.

`api` is our main Flask API gateway with a REST API that interfaces with our DB with auth middle ware for CRUD operations and handling serialization, interfacing with Gemini and our compiler microservice `texify`. We use SQLAlchemy as our ORM, Alembic for migrations, Supabase as our cloud provider for the PostgreSQL DB, Gemini for LLM services for rating resumes, and our own compiler service that uses Jinja2 to fill LaTeX templates from our structured resume JSON and compile to PDF in a storage bucket.

`texify` is the compiler microservice which handles a task queue using Redis and Celery. It converts resumes to LaTeX and compiles it to a PDF stored in the Google Storage Bucket where the URI may be returned for download and previewing via iframe.

`oauth` is OAuth mock when https is not present in local dev.


