from app import app


def test_health():
    reply = app.test_client().get("/health")
    assert reply.status_code == 200
    assert reply.data == b"OK"
