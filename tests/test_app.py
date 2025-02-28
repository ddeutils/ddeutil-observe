from fastapi.testclient import TestClient


def test_app(app):
    test_client = TestClient(app=app)
    print(test_client)
