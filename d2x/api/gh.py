import os
import requests

GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY")


def get_github_token() -> str:
    """Get the GitHub token from the environment"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    return token


def get_repo_full_name() -> str:
    """Get the full name of the GitHub repository"""
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo:
        raise ValueError("GITHUB_REPOSITORY environment variable not set")
    return repo


def set_environment_variable(env_name: str, var_name: str, var_value: str) -> None:
    """Set a variable in a GitHub Environment"""
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/environments/{env_name}/variables/{var_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"name": var_name, "value": var_value}

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()


def get_environment_variable(env_name: str, var_name: str) -> str:
    """Get a variable from a GitHub Environment"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/environments/{env_name}/variables/{var_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["value"]


def set_environment_secret(env_name: str, secret_name: str, secret_value: str) -> None:
    """Set a secret in a GitHub Environment"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/environments/{env_name}/secrets/{secret_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"encrypted_value": secret_value}

    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()


def get_environment_secret(env_name: str, secret_name: str) -> str:
    """Get a secret from a GitHub Environment"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/environments/{env_name}/secrets/{secret_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["encrypted_value"]
