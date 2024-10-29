import os


def get_login_url_and_token(access_token: str | None = None) -> tuple[str, str]:
    from_env = False
    if not access_token:
        access_token = os.getenv("ACCESS_TOKEN")
        from_env = True
    if not access_token:
        raise ValueError(" environment variable not set")

    return login_url, access_token
