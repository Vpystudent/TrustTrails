import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    
def test_bad_address():
    response = client.get("/report?address=0x123&chains=ethereum")
    assert response.status_code == 400
    
@patch('backend.main.analyze')
def test_mocked_e2e(mock_analyze):
    mock_analyze.return_value = {"mock": "data", "cache": {"hit": False}}
    response = client.get("/report?address=0x1234567890123456789012345678901234567890&chains=ethereum")
    assert response.status_code == 200
    assert response.json() == {"mock": "data", "cache": {"hit": False}}
