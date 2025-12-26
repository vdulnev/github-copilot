from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of initial state and restore after each test
    original = {k: {**v} for k, v in activities.items()}
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_delete_participant():
    client = TestClient(app)
    activity = "Programming Class"
    email = "newstudent@mergington.edu"

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")
    assert any(p.lower() == email for p in activities[activity]["participants"])

    # Duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400

    # Delete participant
    del_resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert del_resp.status_code == 200
    assert not any(p.lower() == email for p in activities[activity]["participants"])


def test_delete_nonexistent_participant():
    client = TestClient(app)
    activity = "Gym Class"
    email = "doesnotexist@mergington.edu"
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404


def test_signup_unknown_activity():
    client = TestClient(app)
    resp = client.post("/activities/NoSuchActivity/signup?email=test@x.com")
    assert resp.status_code == 404
