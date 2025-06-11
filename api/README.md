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