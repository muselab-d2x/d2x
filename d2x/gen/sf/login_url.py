import os
import urllib.parse

StartJarUrl = "{login_url}/secur/frontdoor.jsp?sid={access_token}&retURL={ret_url}"


def get_login_url_and_token(
    access_token: str | None = None, login_url: str | None = None, ret_url: str = "/"
) -> tuple[str, str]:
    if not access_token:
        access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        raise ValueError("ACCESS_TOKEN environment variable not set")
    if not login_url:
        login_url = os.getenv("LOGIN_URL")
    if not login_url:
        raise ValueError("LOGIN_URL environment variable not set")

    # URL-encode the ret_url parameter
    ret_url_encoded = urllib.parse.quote(ret_url)

    # Format the login URL
    login_url_formatted = StartJarUrl.format(
        login_url=login_url, access_token=access_token, ret_url=ret_url_encoded
    )

    return login_url_formatted, access_token
