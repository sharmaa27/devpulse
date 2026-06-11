import pytest
from fastapi.testclient import TestClient

from app import main
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_store():
    main.tasks.clear()
    main.next_id = 1


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_get_task():
    r = client.post("/tasks", json={"title": "learn actions"})
    assert r.status_code == 201
    task_id = r.json()["id"]
    r = client.get(f"/tasks/{task_id}")
    assert r.json()["title"] == "learn actions"


def test_get_missing_task():
    assert client.get("/tasks/999").status_code == 404


def test_delete_task():
    task_id = client.post("/tasks", json={"title": "x"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_stats():
    client.post("/tasks", json={"title": "a", "done": True})
    client.post("/tasks", json={"title": "b"})
    assert client.get("/stats").json() == {"total": 2, "done": 1, "pending": 1}
