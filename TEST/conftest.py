import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--host", action="store", default="localhost:8080", help="Exist fdsn host"
    )


@pytest.fixture
def host(request):
    return request.config.getoption("--host")
