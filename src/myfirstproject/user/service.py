from myfirstproject.user.models import User

def is_dev(user: User) -> bool:
    return user.is_dev

def sort_by_age_desc(users: list[User]) -> list[User]:
    return sorted(users, key=lambda u: u.age, reverse=True)

def split_by_dev(users: list[User]) -> tuple[list[User], list[User]]:
    devs = [u for u in users if is_dev(u)]
    non_devs = [u for u in users if not is_dev(u)]
    return devs, non_devs