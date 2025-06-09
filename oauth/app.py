import os
from flask import Flask, jsonify, request, redirect
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

PORT = 9000
AUTHORIZED_REDIRECT_URLS = [
    "http://localhost:3000/api/auth/login/callback",
    "http://127.0.0.1:3000/api/auth/login/callback",
    "http://localhost:5001/api/auth/login/callback",
    "http://127.0.0.1:5001/api/auth/login/callback",
]


@app.route("/.well-known/openid-configuration")
def get_openid_config():
    """
    Mocks https://accounts.google.com/.well-known/openid-configuration.
    """
    app.logger.info("Retrieved OpenID config.")
    return {
        "issuer": "https://accounts.google.com",
        "authorization_endpoint": os.environ.get("AUTHORIZATION_URL")
        or f"http://localhost:{PORT}/auth",  # "https://accounts.google.com/o/oauth2/v2/auth"
        "device_authorization_endpoint": "https://oauth2.googleapis.com/device/code",
        "token_endpoint": os.environ.get("TOKEN_ENDPOINT")
        or f"http://localhost:{PORT}/token",  # "https://oauth2.googleapis.com/token"
        "userinfo_endpoint": os.environ.get("USERINFO_ENDPOINT")
        or f"http://localhost:{PORT}/userinfo",  # "https://openidconnect.googleapis.com/v1/userinfo"
        "revocation_endpoint": "https://oauth2.googleapis.com/revoke",
        "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
        "response_types_supported": [
            "code",
            "token",
            "id_token",
            "code token",
            "code id_token",
            "token id_token",
            "code token id_token",
            "none",
        ],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["RS256"],
        "scopes_supported": ["openid", "email", "profile"],
        "token_endpoint_auth_methods_supported": [
            "client_secret_post",
            "client_secret_basic",
        ],
        "claims_supported": [
            "aud",
            "email",
            "email_verified",
            "exp",
            "family_name",
            "given_name",
            "iat",
            "iss",
            "name",
            "picture",
            "sub",
        ],
        "code_challenge_methods_supported": ["plain", "S256"],
        "grant_types_supported": [
            "authorization_code",
            "refresh_token",
            "urn:ietf:params:oauth:grant-type:device_code",
            "urn:ietf:params:oauth:grant-type:jwt-bearer",
        ],
    }


@app.get("/auth")
def auth_endpoint():
    app.logger.info(f"Auth request received from {request.host}")
    app.logger.info(request.query_string)

    if not request.args.get("client_id"):
        return "Missing client_id", 400

    redirect_url = request.args.get("redirect_uri")
    app.logger.info(f"Redirect url {redirect_url}")
    if redirect_url not in AUTHORIZED_REDIRECT_URLS:
        return f"{redirect_url} not allowed. Make sure to 'register' it.", 400

    state = request.args.get("state", "")
    if state:
        state = "&state=" + state

    code = "?code=testcode"
    return redirect(redirect_url + code + state)


@app.post("/token")
def create_oauth_token():
    """
    'Creates' a mocked OAuth v2 token.
    Reference tokens taken from https://github.com/NewThingsCo/google-oauth-mock/blob/master/src/index.js.
    """
    app.logger.info("Retrieved OAuth2 token")
    return {
        "access_token": "1/fFAGRNJru1FTz70BzhT3Zg",
        "expires_in": 3920,
        "token_type": "Bearer",
        "refresh_token": "1/xEoDL4iW3cxlI7yDbSRFYNG01kVKM2C-259HOF2aQbI",
    }


@app.get("/userinfo")
def get_user_info():
    """
    Gets information about a user after OAuth flow completed.
    """
    app.logger.info("Retreieved user info")
    return {
        "sub": "108442171748001887974",
        "email": "test.user@newthings.co",
        "email_verified": True,
        "name": "Test User",
        "given_name": "User",
        "family_name": "Test",
        "picture": "https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg",
        "locale": "en",
        "hd": "newthings.co",
    }


@app.route("/<path:path>")
def catch_all(path):
    app.logger.error(f"{request.method} {path} not implemented!")
    return "Not implemented", 500


if __name__ == "__main__":
    app.run(port=PORT)
