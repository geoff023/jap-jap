DEFAULT_PASSWORD = "supersecret1"


async def _register(client, email="alice@example.com", password=DEFAULT_PASSWORD):
    return await client.post("/api/auth/register", json={"email": email, "password": password})


async def test_register_creates_user_and_returns_token(client):
    response = await _register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "alice@example.com"
    assert "access_token" in body
    assert "hashed_password" not in body["user"]
    assert "password" not in body["user"]


async def test_register_rejects_duplicate_email(client):
    await _register(client, email="bob@example.com")
    response = await _register(client, email="bob@example.com")

    assert response.status_code == 409


async def test_register_rejects_password_below_minimum_length(client):
    response = await client.post(
        "/api/auth/register", json={"email": "carol@example.com", "password": "short"}
    )

    assert response.status_code == 422


async def test_login_with_valid_credentials_succeeds(client):
    await _register(client, email="dave@example.com")

    response = await client.post(
        "/api/auth/login", json={"email": "dave@example.com", "password": DEFAULT_PASSWORD}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_with_wrong_password_fails(client):
    await _register(client, email="erin@example.com")

    response = await client.post(
        "/api/auth/login", json={"email": "erin@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401


async def test_login_with_unknown_email_fails(client):
    response = await client.post(
        "/api/auth/login", json={"email": "ghost@example.com", "password": DEFAULT_PASSWORD}
    )

    assert response.status_code == 401


async def test_protected_endpoint_requires_a_token(client):
    response = await client.get("/api/users/me")

    assert response.status_code == 401


async def test_protected_endpoint_rejects_an_invalid_token(client):
    response = await client.get(
        "/api/users/me", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


async def test_protected_endpoint_returns_the_current_user(client):
    register_response = await _register(client, email="frank@example.com")
    token = register_response.json()["access_token"]

    response = await client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == "frank@example.com"


async def test_logout_requires_authentication(client):
    response = await client.post("/api/auth/logout")

    assert response.status_code == 401


async def test_logout_succeeds_when_authenticated(client):
    register_response = await _register(client, email="grace@example.com")
    token = register_response.json()["access_token"]

    response = await client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 204
