# 📝 prolio
![Prolio Home Page](readme_assets/prolio.png)

CS 144: Web Applications. Repository for Prolio, an interactive resume content management system!

# About 

Prolio is our web app for resume creation through a simple and intuitive ui, that supports injecting into internal LaTeX templates and compilation into a ATS-compatible PDF rendered from LaTeX for clean formatting. Users may also invite AI feedback as they work with the help of our AI reviewer built-on Gemini. 

We support drag and drop for ease of reordering resume elements within resume sections as well as geolocation for convenient location filling.

# Setup

To build and run the service do:
`docker-compose build && docker-compose up`

and the frontend should be default available at `localhost:3000`.

Note that you will need to provide a Gemini API key to make use of the api service which you can obtain currently for free from Google's AI Studio. See the instructions below. 

We have a mock OAuth flow and mock GCS bucket and SQLite for the DB by default but in our main deployment we use the actual services and our PostgreSQL DB is hosted on Supabase.

## Gemini API Key Setup 

Create a `.env` file in the root directory. There are defaults for all of these except for the `GEMINI_API_KEY` for which you may either provide a Gemini Key by following these steps or filling in an invalid key which will cause the rating endpoint to fail but allow the project to build.

1. Create an account in GCP, create a Project in Google Cloud.

2. Search for Gemini and click Gemini API
![Search For Gemini](readme_assets/GeminiAPISearch.png)

You may be asked to enable the Gemini API, press "Enable".

3. In the sidebar, navigate to "Credentials"

Click on Create Credentials.

Click on API Key, it will generate a key for you to copy.

![Create Key Instructions](readme_assets/CreateAPIKey.png)

4. Create a `.env` file, and put inside

```
GEMINI_API_KEY=<GEMINI_API_KEY>
``` 
where you should replace `<GEMINI_API_KEY>` with your generated key.

## Other Env Variable Configuration

The below are optional as the default build has mocks or local defaults for these but here is the full set of env variables.
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

![System Design](readme_assets/system-design.png)

`web` is NextJS which uses the App Router system to route via the directory structure. 
We use NextJS, React, Tailwind, Shadcn as our main libraries and frameworks for frontend styling, hooks, acessibility in component primitives, etc. 
We have response uis, accessibilities features, PWA and offline support via our manifest and service workers using Serwist.

`api` is our main Flask API gateway with a REST API that interfaces with our DB with auth middle ware for CRUD operations and handling serialization, interfacing with Gemini and our compiler microservice `texify`. We use SQLAlchemy as our ORM, Alembic for migrations, Supabase as our cloud provider for the PostgreSQL DB, Gemini for LLM services for rating resumes, and our own compiler service that uses Jinja2 to fill LaTeX templates from our structured resume JSON and compile to PDF in a storage bucket.

`texify` is the compiler microservice which handles a task queue using Redis and Celery. It converts resumes to LaTeX and compiles it to a PDF stored in the Google Storage Bucket where the URI may be returned for download and previewing via iframe.

`oauth` is OAuth mock when https is not present in local dev.

# API 

As a group of 2, this project does not expose endpoints and we make use of the Gemini API instead.

However to document our main API gateway just for internally used endpoints:

`api` holds the main Flask Backend.

Within it we follow MVC structure and use SQLAlchemy as our ORM and library for model creation.

Our controllers implement some of the more detailed logic for creating and updating resumes.

Our main endpoints are related to auth, user info, and resume CRUD.

All routes are prefixed with `/api` and `/api` in the frontend proxies to the backend

## Resume View
`api/views/resume.py`

`/resume/all` GET
retrieves all resumes

`/resume/<id>` GET
retrieves that resume id

Resume JSON example:
```json
{
    "created_at": "2025-06-11T19:16:53.842704+00:00",
    "email": "joebruin@ucla.edu",
    "github": "github.com/joebruin",
    "id": 34,
    "linkedin": "linkedin.com/joebruin",
    "name": "Joe Bruin",
    "phone": "999-999-9999",
    "resume_name": "Untitled Resume (2)",
    "sections": [
        {
            "display_order": 0,
            "id": 95,
            "items": [
                {
                    "description": "Degree description",
                    "display_order": 0,
                    "end_date": null,
                    "id": 110,
                    "location": "",
                    "organization": "University Name",
                    "section_id": 95,
                    "start_date": "2025-06-11T19:16:54.188231+00:00",
                    "title": "Degree",
                    "user_id": 5
                }
            ],
            "name": "Education",
            "resume_id": 34,
            "section_type": "education",
            "user_id": 5
        },
        {
            "display_order": 1,
            "id": 96,
            "items": [
                {
                    "description": "Job description",
                    "display_order": 0,
                    "end_date": null,
                    "id": 111,
                    "location": "",
                    "organization": "Company Name",
                    "section_id": 96,
                    "start_date": "2025-06-11T19:16:54.311986+00:00",
                    "title": "Job Title",
                    "user_id": 5
                }
            ],
            "name": "Experience",
            "resume_id": 34,
            "section_type": "experience",
            "user_id": 5
        },
        {
            "display_order": 2,
            "id": 97,
            "items": [
                {
                    "description": "Project description",
                    "display_order": 0,
                    "end_date": null,
                    "id": 112,
                    "location": "",
                    "organization": "",
                    "section_id": 97,
                    "start_date": "2025-06-11T19:16:54.429985+00:00",
                    "title": "Project Name",
                    "user_id": 5
                }
            ],
            "name": "Project",
            "resume_id": 34,
            "section_type": "project",
            "user_id": 5
        },
        {
            "display_order": 3,
            "id": 98,
            "items": [
                {
                    "description": "Resume-building, problem-solving, etc",
                    "display_order": 0,
                    "end_date": null,
                    "id": 113,
                    "location": "",
                    "organization": "",
                    "section_id": 98,
                    "start_date": "2025-06-11T19:16:54.548347+00:00",
                    "title": "Skill Category",
                    "user_id": 5
                }
            ],
            "name": "Technical Skills",
            "resume_id": 34,
            "section_type": "skill",
            "user_id": 5
        }
    ],
    "template_id": 2,
    "updated_at": "2025-06-11T19:16:53.842704+00:00",
    "user_id": 5,
    "website": ""
}
```

`sections` and `items` are populated from their own tables where our one to many hierarchy looks like a tree of Resumes having many ResumeSections having many ResuemItems. Our backend routes support updating the resume on the granularity of passing the full resume where the section and item objects will be handled by creating or updating them appropriately based on whether they exist at that id and are owned by the user and are valid.

Both of these endpoints require auth and `/all` is cached with Flask Cache

`/resume/create/<id>` POST
`/resume/delete/<id>` DELETE
`/resume/update/<id>` PUT
`/resume/<id>` GET

CRUD operations, expects a serialized resume as in the `json()` method of the Resume model here:
`api/models/resume.py`

`update` returns the updated JSON on success and `create` will return the JSON of the newly created resume. `delete` returns a success message on success.

We perform some validation on updating in that we enforce that all sections are present and that all sections contain at least one item for compatibility with the compiler. The frontend also does this validation. 

## User View

`api/views/user.py`

`/user/me` GET
retrieves the currently logged in user. It is protected and the login session is used to get the current user.

```JSON
{
    "email": "joebruin@ucla.edu",
    "github": "github.com/joebruin",
    "google_id": "110192453484285413348",
    "id": 5,
    "linkedin": "linkedin.com/joebruin",
    "name": "Joe Bruin",
    "phone": "999-999-9999",
    "profile_picture": "https://lh3.googleusercontent.com/a/ACg8ocJp0tLlnGyJk5iYGTuBLzoC7cQfOTdPALIN4X-H6TvKdUFDXQ=s96-c",
    "website": ""
}
```

## Auth View

`api/views/auth.py`

`/auth/login` GET 

Login through OAuth redirect.

`/auth/logout` POST 

Login required, logs user out.

## Compiler View

For interfacing with Compiler microservice:
`api/views/compile.py`

`/compile/<resume_id>` POST
Creating a task with compiler microservice to compile the given resume. Protected by auth and requires user to own the resume and the resume must exist.

Gets back the job id to poll with.

```JSON
{"task_id":"52bf4f0b-dba5-4775-951f-7b45ca03b82d"}
```

Polling the task status
`"/status/<job_id>"` GET
Polls the task status

returns status and URI if complete.

Example:
```JSON
{
    "status": "done",
    "url": "https://storage.googleapis.com/prolio-resume/52bf4f0b-dba5-4775-951f-7b45ca03b82d.pdf?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=github-actions-deployer%40prolio-resume.iam.gserviceaccount.com%2F20250611%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20250611T235409Z&X-Goog-Expires=3600&X-Goog-SignedHeaders=host&X-Goog-Signature=85e8cfc9390bf1e78024397d732f53d5046dc124ddf2a50f67d336423ed8a4c50a17cd72f3cdd4ffa0b466668a70b025246f5069f4faa4aecf495ec4407b5268c9cf4665c4bff6bc2b45a620aeb1224b0095b5e05c2c352f8adbb9c30844e12df6cfd986f17e78a4fd042481ef81490c67a6c0c13942ff14eaa3cac4e7f3e86869a8a01dbb134e561deff7dff3ed0eb2e32e760a8e6a9255e80f6790cac9c5b540d1d814a079d75e472bd8853c6fd6dd19a2c899ec8912fbd4d38840f0e3c30a6c1cdf9f6f5ea7fc22314fe50920bd192afc61d1d00f7b9730eb51f469101468d333ff388d060082f3dd226a99761e056d555de95d7889fea808537073132572"
}
```

Note that our template endpoints are skeletoned for future-proofing if in the future custom templates would be supported. For now we support one template in our compiler service.

## AI View

api/views/ai.py
[route](api/views/ai.py)

`/ai/rate/<resume_id>`
Rates the resume id with the Gemini Python SDK, must provide an API key in the env variable.

```JSON
{
    "rating": 3.0,
    "reasoning": "The resume is a good start but needs significant improvement ... [shortened] ... will greatly enhance your resume's effectiveness."
}
```