from flask import Blueprint, request, redirect, url_for, current_app
from flask_login import current_user, login_user, login_required, logout_user

import os
import json
import base64
from urllib.parse import urlparse

from oauthlib.oauth2 import WebApplicationClient

from models.user import User
from db import db

import requests

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    os.environ.get("GOOGLE_DISCOVERY_URL", None)
    or "https://accounts.google.com/.well-known/openid-configuration"
)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

auth_view = Blueprint("auth_view", __name__, url_prefix="/auth")


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


# Google's OAuth2 protocol only supports passing a state parameter on
# the redirect to the callback containing a base64 encoded JSON.
# https://developers.google.com/identity/protocols/oauth2/web-server
def serialize_google_state(state: dict[str, str]) -> str | None:
    try:
        data = json.dumps(state).encode("utf-8")
        return base64.urlsafe_b64encode(data).decode("utf-8")
    except Exception as e:
        print(e)
        return None


def deserialize_google_state(state: str) -> dict[str, str] | None:
    try:
        data = base64.urlsafe_b64decode(state).decode("utf-8")
        return json.loads(data)
    except Exception as e:
        print(e)
        return None


def is_safe_url(url: str) -> bool:
    """
    URL validation to prevent open redirects.
    """
    u = urlparse(url)
    # Only allow relative URLs
    if u.scheme or u.netloc:
        return False
    return url.startswith("/")


# Following code referenced from https://realpython.com/flask-google-login/


# TODO, move the entire flask routes to under /api prefix (proxied from frontend /api to backend as /api as well so redirects are consistent and less prefix jank, don't reroute through X-Forwarded-Host, since now the paths are the same and will automatically be proxied to backend if appropriate or otherwise stay on frontend)


# Testing shim
@auth_view.route("/shim")
def index():
    next_url = request.args.get("next")
    if next_url and is_safe_url(next_url):
        next_params = "?next=" + next_url
    else:
        next_params = ""

    # TODO: remove this hot garbage later
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/api/auth/logout">Logout</a>'.format(
                current_user.name,
                current_user.email,
                current_user.profile_picture,
            )
        )
    else:
        # Hotfix(bliutech): Temporary primitive XSS sanitization
        next_params = next_params.replace('"', "")
        return f'<a class="button" href="/api/auth/login{next_params}">Google Login</a>'


@auth_view.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Save optional redirect after authentication
    state = serialize_google_state({"next": request.args.get("next")}) or ""

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    base_url = request.base_url
    if request.headers.get("X-Forwarded-Host"):
        base_url = "http://" + request.headers.get("X-Forwarded-Host") + request.path
    # TODO(bliutech): add some more checks here to prevent open redirect
    if request.headers.get("Referer"):
        base_url = request.headers.get("Referer") + request.path
    current_app.logger.debug(base_url)
    current_app.logger.debug(request.headers)
    current_app.logger.debug(request.headers.get("X-Forwarded-Host"))
    current_app.logger.debug(request.headers.get("Referer"))
    if not os.environ.get("GOOGLE_DISCOVERY_URL"):
        base_url = base_url.replace("http://", "https://")
        base_url = base_url.replace("api-dot-prolio-resume", "prolio-resume")
    current_app.logger.debug(base_url)
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=base_url + "/callback",
        scope=["openid", "email", "profile"],
        state=state,
    )
    return redirect(request_uri)


@auth_view.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    current_app.logger.debug(code)

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    AUTHORIZATION_URL = request.url
    current_app.logger.debug("AUTHORIZATION_URL " + AUTHORIZATION_URL)
    REDIRECT_URL = request.base_url
    current_app.logger.debug("REDIRECT_URL " + REDIRECT_URL)
    current_app.logger.debug(request.headers.get("X-Forwarded-Host"))
    current_app.logger.debug(request.base_url)
    if request.headers.get("X-Forwarded-Host"):
        REDIRECT_URL = "http://" + request.headers.get("X-Forwarded-Host")
        # AUTHORIZATION_URL = AUTHORIZATION_URL.replace(request.base_url, REDIRECT_URL)
    if request.headers.get("Referer"):
        REDIRECT_URL = (
            os.environ.get("CLIENT_ORIGIN", "http://localhost:3000") + request.path
        )
        AUTHORIZATION_URL = AUTHORIZATION_URL.replace(request.base_url, REDIRECT_URL)

    if not os.environ.get("GOOGLE_DISCOVERY_URL"):
        AUTHORIZATION_URL = AUTHORIZATION_URL.replace("http://", "https://")
        REDIRECT_URL = REDIRECT_URL.replace("http://", "https://")

    current_app.logger.debug("AUTHORIZATION_URL " + AUTHORIZATION_URL)
    current_app.logger.debug("REDIRECT_URL " + REDIRECT_URL)
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=AUTHORIZATION_URL,
        redirect_url=REDIRECT_URL,
        code=code,
    )
    current_app.logger.debug(token_url)
    current_app.logger.debug(headers)
    current_app.logger.debug(body)
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    res = json.dumps(token_response.json())
    current_app.logger.debug(res)
    client.parse_request_body_response(res)

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    res = userinfo_response.json()
    current_app.logger.debug(res)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if res.get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = db.session.execute(db.select(User).filter_by(google_id=unique_id)).fetchone()

    # Doesn't exist? Add it to the database.
    if not user:
        user = User(
            google_id=unique_id,
            name=users_name,
            email=users_email,
            profile_picture=picture,
        )
        user.save_to_db()
    else:
        user = user[0]

    # Begin user session by logging the user in
    login_user(user)

    # Redirect user to path set at ?next=<path>
    state = request.args.get("state")
    next_url = None
    if state:
        state = deserialize_google_state(state)
    if state:
        next_url = state.get("next")

    # TODO: check if we need a 307 redirect instead
    # https://stackoverflow.com/questions/32133910/how-redirect-with-args-for-view-function-without-query-string-on-flask
    if next_url and is_safe_url(next_url):
        return redirect(next_url)

    # Send user back to homepage
    base = "/api" if request.headers.get("X-Forwarded-Host") else ""
    return redirect(base + url_for("main_view.auth_view.index"))


@auth_view.route("/logout")
@login_required
def logout():
    logout_user()
    base = "/api" if request.headers.get("X-Forwarded-Host") else ""
    return redirect(base + url_for("main_view.auth_view.index"))
