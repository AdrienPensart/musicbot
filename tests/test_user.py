from musicbot.lib import user


def test_register():
    email = "test@test.com"
    password = "test_test"
    u = user.User.register(graphql=user.DEFAULT_GRAPHQL, first_name="first_test", last_name="last_test", email=email, password=password)
    assert u.authenticated

    same = user.User(email=email, password=password)
    assert same.authenticated

    assert u.token == same.token

    same2 = user.User(token=same.token)
    assert same2.authenticated

    assert u.unregister()
