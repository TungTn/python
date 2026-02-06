from myfirstproject.user import User, is_dev, split_by_dev, sort_by_age_desc


def test_is_dev():
    u1 = User(name="A", age=20, is_dev=True)
    u2 = User(name="B", age=20)

    assert is_dev(u1) is True
    assert is_dev(u2) is False


def test_split_by_dev():
    users = [
        User(name="A", age=30, is_dev=True),
        User(name="B", age=20),
        User(name="C", age=25, is_dev=True),
    ]

    devs, non_devs = split_by_dev(users)

    assert len(devs) == 2
    assert len(non_devs) == 1


def test_sort_by_age_desc():
    users = [
        User(name="A", age=20),
        User(name="B", age=30),
        User(name="C", age=25),
    ]

    sorted_users = sort_by_age_desc(users)

    assert [u.age for u in sorted_users] == [30, 25, 20]