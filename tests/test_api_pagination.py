import sqlite3
from fastapi.testclient import TestClient

from myfirstproject.main import app
from myfirstproject.db import get_db, init_db

client = TestClient(app)

def override_get_db():
  conn = sqlite3.connect(":memory:")
  conn.row_factory = sqlite3.Row
  init_db(conn)
  try:
    yield conn
  finally:
    conn.close()

app.dependency_overrides[get_db] = override_get_db

def seed_users():
  for i in range(1, 26):
    client.post("/users", json={
      "name": f"User{i}",
      "age": i,
      "is_dev": (i % 2 == 0),
      "email": f"user{i}@ex.com"
    })

def test_pagination_and_filter():
  seed_users()

  # page 1 size 10
  r = client.get("/users?page=1&page_size=10")
  assert r.status_code == 200
  data = r.json()
  assert data["total"] == 25
  assert len(data["items"]) == 10

  # page 3 size 10 => còn 5
  r2 = client.get("/users?page=3&page_size=10")
  assert r2.status_code == 200
  data2 = r2.json()
  assert len(data2["items"]) == 5

  # filter is_dev=true => các user tuổi chẵn => 12 (2..24)
  r3 = client.get("/users?is_dev=true&page=1&page_size=50")
  assert r3.status_code == 200
  data3 = r3.json()
  assert data3["total"] == 12

  # search q
  r4 = client.get("/users?q=User2&page=1&page_size=50")
  assert r4.status_code == 200
  data4 = r4.json()
  assert data4["total"] >= 1