import os
import socket
import subprocess
import time
from pathlib import Path

import pytest
import requests


ROOT_DIR = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT_DIR / "docker-compose.test.yml"
PROJECT_NAME = "edtask-api-tests"
MASTER_TOKEN = "test-admin"
HTTP = requests.Session()
HTTP.trust_env = False


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


TEST_BACKEND_PORT = _get_free_port()
TEST_MINIO_PORT = _get_free_port()
BASE_URL = f"http://127.0.0.1:{TEST_BACKEND_PORT}"
MINIO_PUBLIC_URL = f"http://127.0.0.1:{TEST_MINIO_PORT}"
COMPOSE_ENV = {
    **os.environ,
    "TEST_BACKEND_PORT": str(TEST_BACKEND_PORT),
    "TEST_MINIO_PORT": str(TEST_MINIO_PORT),
}


def compose(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "-p", PROJECT_NAME, *args],
        cwd=ROOT_DIR,
        env=COMPOSE_ENV,
        check=True,
        text=True,
        capture_output=True,
    )


def wait_for_backend(timeout: int = 120) -> None:
    deadline = time.time() + timeout
    last_error = None

    while time.time() < deadline:
        try:
            response = HTTP.get(f"{BASE_URL}/openapi.json", timeout=5)
            if response.status_code == 200:
                return
        except requests.RequestException as exc:  # pragma: no cover - diagnostic path
            last_error = exc
        time.sleep(2)

    raise RuntimeError("Backend did not become ready in time") from last_error


def exec_backend_python(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            str(COMPOSE_FILE),
            "-p",
            PROJECT_NAME,
            "exec",
            "-T",
            "backend",
            "python",
            "-c",
            script,
        ],
        cwd=ROOT_DIR,
        env=COMPOSE_ENV,
        check=True,
        text=True,
        capture_output=True,
    )


@pytest.fixture(scope="session", autouse=True)
def docker_test_stack():
    compose("down", "-v")
    compose("up", "-d", "--build")
    wait_for_backend()
    yield
    compose("down", "-v")


@pytest.fixture(autouse=True)
def reset_test_state(docker_test_stack):
    script = """
from pathlib import Path
import shutil
from data.data import Base, engine, ensure_bootstrap_master
from media import get_minio_bucket, get_minio_client

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
ensure_bootstrap_master()

files_dir = Path("data/files")
files_dir.mkdir(parents=True, exist_ok=True)
for entry in files_dir.iterdir():
    if entry.name == ".gitkeep":
        continue
    if entry.is_dir():
        shutil.rmtree(entry)
    else:
        entry.unlink()

client = get_minio_client()
bucket = get_minio_bucket()
for obj in client.list_objects(bucket, recursive=True):
    client.remove_object(bucket, obj.object_name)
"""
    exec_backend_python(script)
    yield


@pytest.fixture
def api():
    session = requests.Session()
    session.trust_env = False

    class ApiClient:
        base_url = BASE_URL
        master_token = MASTER_TOKEN
        minio_public_url = MINIO_PUBLIC_URL

        def request(self, method: str, path: str, **kwargs):
            return session.request(method, f"{BASE_URL}{path}", timeout=20, **kwargs)

        def get(self, path: str, **kwargs):
            return self.request("GET", path, **kwargs)

        def post(self, path: str, **kwargs):
            return self.request("POST", path, **kwargs)

        def patch(self, path: str, **kwargs):
            return self.request("PATCH", path, **kwargs)

        def delete(self, path: str, **kwargs):
            return self.request("DELETE", path, **kwargs)

    return ApiClient()
