def _register(client, name="Test User", email="test@example.com", password="password123"):
    return client.post(
        "/register",
        data={"name": name, "email": email, "password": password},
        follow_redirects=False,
    )


def _login(client, email="test@example.com", password="password123"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_success(client):
    _register(client)
    response = _login(client)
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert "user_id" in sess
        assert isinstance(sess["user_id"], int)


def test_login_wrong_password(client):
    _register(client)
    response = _login(client, password="wrongpassword")
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_login_unknown_email(client):
    response = _login(client, email="nobody@example.com")
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_login_missing_email(client):
    response = _login(client, email="")
    assert response.status_code == 200
    assert b"Email is required" in response.data


def test_login_missing_password(client):
    response = _login(client, password="")
    assert response.status_code == 200
    assert b"Password is required" in response.data


def test_login_sticky_email(client):
    response = _login(client, email="sticky@example.com", password="wrongpassword")
    assert response.status_code == 200
    assert b"sticky@example.com" in response.data


def test_logout(client):
    _register(client)
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith("/")
    with client.session_transaction() as sess:
        assert "user_id" not in sess
