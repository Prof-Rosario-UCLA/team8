# Main Backend (Flask)

## Routing 
We use Flask Blueprints as our Express Router equivalent to handle route prefixes and routing.

We use appropriate status codes and HTTP methods for our requests and have auth middleware via flask login for maintaining user login sessions as well as OAuth for the actual Google Sign in.

# Auth 

We use flask login for auth middleware and maintaining the session of a user's login and getting the logged in user. 

We use OAuth for our actual login with Google Accounts.

On top of auth middleware, our routes do not support directly providing the user id, instead the user id is retrieved from the login session to only allow the logged in user to be used in DB accesses.

# SQLAlchemy

We use SQLAlchemy as our ORM to our PostgreSQL DB provided by Supabase. We define our models under `models` and use relations to have Resumes contain ResumeSections and those contain ResumeItems and serialization jsonifies the sub objects when serializing the full resume json.

# Alembic for Migrations
We use Alembic which helps to support migrations to propagate schema changes to the db without losing existing data.

# Compiler API + Gemini API

This also acts as our API gateway to access the compiler microservice found in `texify` and it supports the posting of new tasks to compile resumes and endpoints to support polling the compiler service for task completion.

We also interface with the GeminiAPI through the `ai` blueprint which uses the Google GenAI SDK to interface with the Gemini API and get ratings on resumes from the model.

# Caching

We implement caching via Flask caching on our endpoints as middleware and handle cache invalidation on logout and expirations to keep data relatively up to date.

# API 

As a group of 2, this project does not expose endpoints and we make use of the Gemini API instead.

However to document our main API gateway just for internally used endpoints:

`api` holds the main Flask Backend.

Within it we follow MVC structure and use SQLAlchemy as our ORM and library for model creation.

Our controllers implement some of the more detailed logic for creating and updating resumes.

Our main endpoints are related to auth, user info, and resume CRUD.

All routes are prefixed with `/api` and `/api` in the frontend proxies to the backend

## Resume View
url prefix: `/resume`

`api/views/resume.py`

`/resume/all` GET
retrieves all resumes

`/resume/<id>` GET
retrieves that resume id

Both of these endpoints require auth and `/all` is cached with Flask Cache

`/resume/create/<id>` POST
`/resume/delete/<id>` DELETE
`/resume/update/<id>` PUT
`/resume/<id>` GET

Crud operations, expects a serialized resume as in the `json()` method of the Resume model here:
`api/models/resume.py`

## User View

`api/views/user.py`

`/user/me` GET
retrieves the currently logged in user. It is protected and the login session is used to get the current user.

## Auth View

`api/views/auth.py`

`/auth/login` GET 

Login through OAuth redirect

`/auth/logout` POST 
Login required, logs user out

## Compiler View

For interfacing with Compiler microservice:
`api/views/compile.py`

`/compile/<resume_id>` POST
Creating a task with compiler microservice to compile the given resume. Protected by auth and requires user to own the resume.

Gets back the job id to poll with.

Polling the task status
`"/status/<job_id>"` GET
Polls the task status

returns status and URI if complete.

Note that our template endpoints are skeletoned for future-proofing if in the future custom templates would be supported. For now we support one template in our compiler service.

## AI View

api/views/ai.py
[route](api/views/ai.py)

`/ai/rate/<resume_id>`
Rates the resume id with the Gemini Python SDK, must provide an API key in the env variable.
