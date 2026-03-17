import base64

import requests


MASTER_TOKEN = "test-admin"
HTTP = requests.Session()
HTTP.trust_env = False
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a6DMAAAAASUVORK5CYII="
)
TEXT_FILE_BYTES = b"test file payload"


def create_student(api, user_id="student-1", full_name="Student One"):
    response = api.post(
        "/master/user/create",
        json={
            "user_id": user_id,
            "full_name": full_name,
            "master_token": MASTER_TOKEN,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def upload_image(api, filename="image.png"):
    response = api.post(
        "/file/image",
        files={"image": (filename, PNG_BYTES, "image/png")},
    )
    assert response.status_code == 200, response.text
    return response.json()


def upload_file(api, filename="document.txt"):
    response = api.post(
        "/file/file",
        files={"file": (filename, TEXT_FILE_BYTES, "text/plain")},
    )
    assert response.status_code == 200, response.text
    return response.json()


def create_task(api, student_token, image_ids=None, file_ids=None):
    payload = {
        "title": "Task Title",
        "description": "Task Description",
        "master_token": MASTER_TOKEN,
        "user_id": student_token,
    }
    if image_ids:
        payload["image_ids"] = image_ids
    if file_ids:
        payload["file_ids"] = file_ids

    response = api.post("/master/task/create", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def create_answer(api, task_id, image_id=None):
    payload = {"task_id": task_id, "content": "Student answer"}
    if image_id is not None:
        payload["image_id"] = image_id

    response = api.post("/user/answer", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_auth_login_for_master_and_student(api):
    master_response = api.post("/auth/login", json={"token": MASTER_TOKEN})
    assert master_response.status_code == 200
    assert master_response.json()["user"]["type"] == "master"

    create_student(api, user_id="student-auth", full_name="Student Auth")
    student_response = api.post("/auth/login", json={"token": "student-auth"})
    assert student_response.status_code == 200
    assert student_response.json()["user"]["type"] == "student"


def test_master_user_routes_create_list_and_delete(api):
    create_response = create_student(api, user_id="student-manage", full_name="Student Manage")
    assert create_response["user_id"] == "student-manage"

    list_response = api.get("/master/students", params={"master_token": MASTER_TOKEN})
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert list_response.json()["students"][0]["user_id"] == "student-manage"

    delete_response = api.post(
        "/master/user/delete",
        json={"user_id": "student-manage", "master_token": MASTER_TOKEN},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "success"

    list_after_delete = api.get("/master/students", params={"master_token": MASTER_TOKEN})
    assert list_after_delete.status_code == 200
    assert list_after_delete.json()["count"] == 0


def test_image_routes_upload_and_delete_via_minio(api):
    upload_response = upload_image(api)
    assert upload_response["image_url"].startswith(f"{api.minio_public_url}/")

    minio_response = HTTP.get(upload_response["image_url"], timeout=20)
    assert minio_response.status_code == 200
    assert minio_response.content == PNG_BYTES

    delete_response = api.delete(
        "/file/image",
        json={"image_url": upload_response["image_url"]},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["image_url"] == upload_response["image_url"]

    minio_after_delete = HTTP.get(upload_response["image_url"], timeout=20)
    assert minio_after_delete.status_code == 404


def test_file_routes_upload_download_and_delete(api):
    upload_response = upload_file(api)
    file_name = upload_response["file_name"]

    download_response = api.get(f"/file/file/{file_name}")
    assert download_response.status_code == 200
    assert download_response.content == TEXT_FILE_BYTES

    delete_response = api.delete("/file/file", json={"file_name": file_name})
    assert delete_response.status_code == 200
    assert delete_response.json()["file_name"] == file_name

    download_after_delete = api.get(f"/file/file/{file_name}")
    assert download_after_delete.status_code == 404


def test_master_task_routes_create_read_update_and_delete(api):
    create_student(api, user_id="student-task", full_name="Student Task")
    image_response = upload_image(api)
    file_response = upload_file(api)

    task_response = create_task(
        api,
        "student-task",
        image_ids=[image_response["image_id"]],
        file_ids=[file_response["file_id"]],
    )
    task_id = task_response["task_id"]

    list_response = api.get("/master/task", params={"master_token": MASTER_TOKEN})
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1

    detail_response = api.get("/master/task", params={"master_token": MASTER_TOKEN, "task_id": task_id})
    assert detail_response.status_code == 200
    task_payload = detail_response.json()["task"]
    assert task_payload["images"][0]["image_url"] == image_response["image_url"]
    assert task_payload["files"][0]["file_name"] == file_response["file_name"]

    update_response = api.post(
        "/master/task/update",
        data={
            "task_id": str(task_id),
            "title": "Updated title",
            "description": "Updated description",
            "master_token": MASTER_TOKEN,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated title"

    delete_response = api.post(
        "/master/task/delete",
        data={"task_id": str(task_id), "master_token": MASTER_TOKEN},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["task_id"] == task_id

    after_delete = api.get("/master/task", params={"master_token": MASTER_TOKEN, "task_id": task_id})
    assert after_delete.status_code == 404


def test_user_task_route_returns_student_view(api):
    create_student(api, user_id="student-view", full_name="Student View")
    image_response = upload_image(api)
    file_response = upload_file(api)
    task_response = create_task(
        api,
        "student-view",
        image_ids=[image_response["image_id"]],
        file_ids=[file_response["file_id"]],
    )

    user_task_response = api.get(
        "/user/task",
        params={"user_token": "student-view", "task_id": task_response["task_id"]},
    )
    assert user_task_response.status_code == 200
    task_payload = user_task_response.json()["task"]
    assert task_payload["images"][0]["image_url"] == image_response["image_url"]
    assert task_payload["files"][0]["file_name"] == file_response["file_name"]


def test_user_answer_routes_create_read_update_and_delete(api):
    create_student(api, user_id="student-answer", full_name="Student Answer")
    task_response = create_task(api, "student-answer")
    answer_image_response = upload_image(api, filename="answer-image.png")

    create_answer_response = create_answer(
        api,
        task_response["task_id"],
        image_id=answer_image_response["image_id"],
    )
    answer_id = create_answer_response["answer_id"]

    read_response = api.get(
        "/user/answer",
        params={"master_token": MASTER_TOKEN, "task_id": task_response["task_id"]},
    )
    assert read_response.status_code == 200
    assert read_response.json()["answers"][0]["image"]["image_url"] == answer_image_response["image_url"]

    update_response = api.patch(
        "/user/answer",
        json={
            "answer_id": answer_id,
            "comment": "Reviewed",
            "comment_grade": 2,
            "master_token": MASTER_TOKEN,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["comment_grade"] == 2

    delete_response = api.delete(
        "/user/answer",
        json={"answer_id": answer_id, "master_token": MASTER_TOKEN},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["answer_id"] == answer_id

    read_after_delete = api.get(
        "/user/answer",
        params={"master_token": MASTER_TOKEN, "task_id": task_response["task_id"]},
    )
    assert read_after_delete.status_code == 200
    assert read_after_delete.json()["answers"] == []
