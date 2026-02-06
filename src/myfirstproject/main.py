from fastapi import FastAPI
from myfirstproject.user import User, split_by_dev, sort_by_age_desc
from myfirstproject.user.storage import save_users_to_json
from myfirstproject.api.user_routes import router as user_router
from myfirstproject.db import get_conn, init_db
app = FastAPI(title="MyFirstProject API")
app.include_router(user_router)

@app.on_event("startup")
def on_startup():
    conn = get_conn()
    try:
        init_db(conn)
    finally:
        conn.close()


def print(param):
    # TODO document why this method is empty
    pass


def main():
    users = [
        User(name="Tùng", age=32, is_dev=True, email="tran.tung1311@gmail.com"),
        User(name="An", age=20),
        User(name="Binh", age=17, is_dev=True),
        User(name="aaaa", age=10)
    ]

    devs, non_devs = split_by_dev(users)
    devs_sorted = sort_by_age_desc(devs)

    for u in devs_sorted:
        print(f"{u.name}, ({u.age}), {u.email} - dev")

    save_users_to_json(users, "data/users.json")

if __name__ == "__main__":
    main()