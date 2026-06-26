def _register(client, name="Test User", email="test@example.com", password="password123"):
    return client.post(
        "/register",
        data={"name": name, "email": email, "password": password},
        follow_redirects=False,
    )


def test_register_get(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_register_success(client):
    response = _register(client)
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert "user_id" in sess
        assert isinstance(sess["user_id"], int)


def test_register_duplicate_email(client):
    _register(client)
    with client.session_transaction() as sess:
        sess.clear()
    response = _register(client, name="Other User")
    assert response.status_code == 200
    assert b"already exists" in response.data


def test_register_short_password(client):
    response = _register(client, password="short")
    assert response.status_code == 200
    assert b"8 characters" in response.data


def test_register_missing_name(client):
    response = _register(client, name="")
    assert response.status_code == 200
    assert b"Name is required" in response.data


def test_register_missing_email(client):
    response = _register(client, email="")
    assert response.status_code == 200
    assert b"Email is required" in response.data


def test_register_sticky_fields(client):
    response = _register(client, name="Sticky Name", email="sticky@example.com", password="short")
    assert response.status_code == 200
    assert b"Sticky Name" in response.data
    assert b"sticky@example.com" in response.data


def test_password_not_stored_plain(client):
    _register(client, email="hash@example.com", password="mysecurepassword")
    from database.db import get_db
    conn = get_db()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE email = ?", ("hash@example.com",)
    ).fetchone()
    conn.close()
    assert row["password_hash"] != "mysecurepassword"
