from functools import wraps
from flask_caching import Cache
from flask import current_app, request
from flask_login import current_user
from threading import Lock

# Cache singleton
cache = None

# cache mutex
mu = Lock()


# Initialize the cache
def init_cache(app):
    global cache

    # Don't need to init cache if it already exists
    if cache:
        return

    cache = Cache(
        app,
        config={
            "CACHE_TYPE": "FileSystemCache",
            "CACHE_DIR": "/tmp/flask_cache",
            "CACHE_DEFAULT_TIMEOUT": 60,
            "CACHE_THRESHOLD": 1000,
            "CACHE_MODE": 0o600,
        },
    )


# Cache key based on current user and request path
def make_cache_key(path: str = None) -> str:
    if not path:
        with current_app.app_context():
            path = request.path

    # Build a unique cache key per user and path
    user_id = current_user.id if current_user.is_authenticated else "anon"
    key = f"response_cache:{user_id}:{path}"
    return key


CACHED_ROUTES_KEY = "cached_routes"


# Keep track of cached routes for garbage collection
# Precondition: caller has acquired the mutex
def cache_route(path: str):
    val = cache.get(f"{CACHED_ROUTES_KEY}:{current_user.id}")
    if not val:
        val = set()
    val.add(path)
    cache.set(f"{CACHED_ROUTES_KEY}:{current_user.id}", val)


# Custom decorator to cache responses
def cache_response(fn):
    mu.acquire()

    @wraps(fn)
    def wrapper(*args, **kwargs):
        key = make_cache_key()

        # Try to get cached result
        cached_result = cache.get(key)
        if cached_result is not None:
            return cached_result

        # Otherwise, call the function and cache the result
        result = fn(*args, **kwargs)
        cache.set(key, result)

        with current_app.app_context():
            cache_route(request.path)

        return result

    mu.release()
    return wrapper


# Delete all cache entries for a user
def invalidate_cache():
    mu.acquire()

    cached_routes = cache.get(f"{CACHED_ROUTES_KEY}:{current_user.id}") or set()
    for route in cached_routes:
        key = make_cache_key(route)
        cache.delete(key)

    cache.delete(f"{CACHED_ROUTES_KEY}:{current_user.id}")

    mu.release()
