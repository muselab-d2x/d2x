import os
import requests
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHMAC
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF
from cryptography.hazmat.primitives.kdf.kbkdf import KBKDFHMAC, KBKDFCMAC
from cryptography.hazmat.primitives.kdf.kbkdf import CounterLocation
from cryptography.hazmat.primitives.kdf.kbkdf import Mode


def set_environment_variable(env_name: str, var_name: str, var_value: str) -> None:
    """Set a variable in a GitHub Environment"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/environments/{env_name}/variables/{var_name}"
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

    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/environments/{env_name}/variables/{var_name}"
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

    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/environments/{env_name}/secrets/{secret_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"encrypted_value": secret_value}

    response = requests.put(url, headers=headers, json(data))
    response.raise_for_status()


def get_environment_secret(env_name: str, secret_name: str) -> str:
    """Get a secret from a GitHub Environment"""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/environments/{env_name}/secrets/{secret_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()["encrypted_value"]
