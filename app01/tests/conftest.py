import pytest
from django.test.client import Client
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def api_client():
    return APIClient()
