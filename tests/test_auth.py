import re
import pytest
from pydantic import ValidationError
from d2x.models.sf.auth import LoginUrlModel, SfdxAuthUrlModel


def test_login_url_model():
    model = LoginUrlModel(access_token="test_token", login_url="https://example.com")
    login_url, token = model.get_login_url_and_token()
    assert login_url == "https://example.com/secur/frontdoor.jsp?sid=test_token&retURL=%2F"
    assert token == "test_token"


def test_login_url_model_with_ret_url():
    model = LoginUrlModel(access_token="test_token", login_url="https://example.com", ret_url="/home")
    login_url, token = model.get_login_url_and_token()
    assert login_url == "https://example.com/secur/frontdoor.jsp?sid=test_token&retURL=%2Fhome"
    assert token == "test_token"


def test_login_url_model_missing_access_token():
    with pytest.raises(ValidationError):
        LoginUrlModel(login_url="https://example.com")


def test_login_url_model_missing_login_url():
    with pytest.raises(ValidationError):
        LoginUrlModel(access_token="test_token")


def test_sfdx_auth_url_model():
    auth_url = "force://PlatformCLI::token123@https://mycompany.my.salesforce.com"
    model = SfdxAuthUrlModel(auth_url=auth_url)
    org_info = model.parse_sfdx_auth_url()
    assert org_info["auth_info"].client_id == "PlatformCLI"
    assert org_info["auth_info"].refresh_token == "token123"
    assert org_info["auth_info"].instance_url == "https://mycompany.my.salesforce.com"
    assert org_info["org_type"] == "production"
    assert org_info["domain_type"] == "my"
    assert org_info["full_domain"] == "https://mycompany.my.salesforce.com"


def test_sfdx_auth_url_model_invalid_url():
    auth_url = "invalid_url"
    model = SfdxAuthUrlModel(auth_url=auth_url)
    with pytest.raises(ValueError):
        model.parse_sfdx_auth_url()
