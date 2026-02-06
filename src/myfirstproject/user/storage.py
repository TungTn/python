import json
from pathlib import Path
from myfirstproject.user.models import User

def save_users_to_json(users: list[User], file_path: str) -> None:
    data = [u.__dict__ for u in users]
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def load_users_from_json(file_path: str) -> list[User]:
    path = Path(file_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    users: list[User] = []
    for item in data:
      users.append(User(**item))
    return users