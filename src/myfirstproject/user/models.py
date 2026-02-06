from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    name: str
    age: int
    is_dev: bool = False
    email: str = ""
    phone_number: Optional[str] = None

    def __post_init__(self):
      if not self.name or not self.name.strip():
        raise ValueError("Tên không được để trống")

      if self.age <= 0:
        raise ValueError("Tuổi không hợp lệ")