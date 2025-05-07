import pytest
import requests
import uuid

BASE_URL = "https://todo.pixegami.io"

@pytest.fixture
def user_id():
    """
    Fixture care generează un user_id unic pentru fiecare test.
    """
    return str(uuid.uuid4())


@pytest.fixture
def sample_task(user_id):
    """
    Creează un task de testare și îl returnează.
    """
    task_data = {
        "user_id": user_id,
        "content": "Sample task content",
        "is_done": False
    }
    response = requests.put(f"{BASE_URL}/create-task", json=task_data)
    assert response.status_code == 200
    return response.json()["task"]


# ======================
# EXERCIȚII
# ======================

def test_create_task(user_id):
    """
    Testează crearea unui task nou.

    Pași:
    1. Trimite un request PUT către /create-task cu date valide.
    2. Verifică răspunsul (status 200).
    3. Extrage task_id și folosește-l pentru a face un GET.
    4. Verifică dacă datele returnate corespund celor introduse.

    Hint: În răspunsul de la /get-task nu vei mai avea `user_id`, deci verifică doar ce este disponibil.
    """
    content = "content"
    is_done = False

    create_payload = {
        "user_id": user_id,
        "content": content,
        "is_done": is_done
    }

    put_resp = requests.put(f"{BASE_URL}/create-task", json=create_payload)
    assert put_resp.status_code == 200

    task_id = put_resp.json()["task"]["task_id"]
    get_resp = requests.get(f"{BASE_URL}/get-task/{task_id}")
    assert get_resp.status_code == 200

    task = get_resp.json()["task"]
    assert task["user_id"] == user_id
    assert task["content"] == content
    assert task["is_done"] == is_done

    #pass


def test_update_task(sample_task):
    """
    Testează actualizarea unui task existent.

    Pași:
    1. Creează un task.
    2. Trimite un PUT către /update-task cu modificări.
    3. Verifică status code-ul (200).
    4. Fă un GET pentru acel task și asigură-te că modificările sunt prezente.

    Hint: În răspunsul de la /update-task primești doar `updated_task_id`.
    """
    new_content = "Updated content"
    new_is_done = True

    update_payload = {
        "user_id": sample_task["user_id"],
        "task_id": sample_task["task_id"],
        "content": new_content,
        "is_done": new_is_done
    }

    update_resp = requests.put(f"{BASE_URL}/update-task", json=update_payload)
    assert update_resp.status_code == 200
    assert "updated_task_id" in update_resp.json()

    get_resp = requests.get(f"{BASE_URL}/get-task/{sample_task['task_id']}")
    assert get_resp.status_code == 200
    updated_task = get_resp.json()["task"]
    assert updated_task["content"] == new_content
    assert updated_task["is_done"] == new_is_done

    #pass


def test_list_multiple_tasks(user_id):
    """
    Testează listarea task-urilor pentru un user.

    Pași:
    1. Creează 3 task-uri pentru același user_id.
    2. Trimite un GET către /list-tasks/{user_id}.
    3. Verifică dacă sunt exact 3 task-uri returnate.

    Hint: Folosește un user_id unic pentru a evita datele altor colegi.
    """
    for i in range(3):
        requests.put(f"{BASE_URL}/create-task", json={
            "user_id": user_id,
            "content": f"Task {i}",
            "is_done": False
        })

    list_resp = requests.get(f"{BASE_URL}/list-tasks/{user_id}")
    assert list_resp.status_code == 200

    tasks = list_resp.json()["tasks"]
    assert len(tasks) == 3
    for task in tasks:
        assert task["user_id"] == user_id

    #pass


def test_delete_task(sample_task):
    """
    Testează ștergerea unui task.

    Pași:
    1. Creează un task.
    2. Trimite un DELETE către /delete-task/{task_id}.
    3. Verifică status-ul (200).
    4. Încearcă să faci GET pe acel task și verifică că primești 404.
    """
    delete_resp = requests.delete(f"{BASE_URL}/delete-task/{sample_task['task_id']}")
    assert delete_resp.status_code == 200

    get_resp = requests.get(f"{BASE_URL}/get-task/{sample_task['task_id']}")
    assert get_resp.status_code == 404

    #pass


def test_get_nonexistent_task():
    """
    Testează obținerea unui task inexistent.

    Pași:
    1. Generează un UUID aleator ca task_id.
    2. Trimite GET pe acel id.
    3. Verifică dacă primești status 404.

    Hint: Nu este nevoie să creezi nimic, doar folosește un id invalid (unic).
    """
    fake_task_id = str(uuid.uuid4())

    get_resp = requests.get(f"{BASE_URL}/get-task/{fake_task_id}")
    assert get_resp.status_code == 404

    #pass


def test_update_nonexistent_task(user_id):
    """
    Testează actualizarea unui task care nu există.

    Pași:
    1. Generează un UUID aleator ca task_id.
    2. Trimite PUT pe /update-task cu acel id.
    3. Verifică dacă primești eroare sau operația se execută cu succes.

    Hint: Dacă operația se execută cu succes, puteți face verificarea folosind GET.
    """
    fake_task_id = str(uuid.uuid4())

    update_payload = {
        "user_id": user_id,
        "task_id": fake_task_id,
        "content": "Created via update",
        "is_done": True
    }

    update_resp = requests.put(f"{BASE_URL}/update-task", json=update_payload)
    assert update_resp.status_code == 200

    get_resp = requests.get(f"{BASE_URL}/get-task/{fake_task_id}")
    assert get_resp.status_code == 200
    task = get_resp.json()["task"]
    assert task["task_id"] == fake_task_id
    assert task["content"] == "Created via update"
    assert task["is_done"] is True

    #pass


def test_delete_nonexistent_task():
    """
    Testează ștergerea unui task inexistent.

    Pași:
    1. Generează un UUID aleator ca task_id.
    2. Trimite DELETE pe acel id.
    3. Verifică statusul.

    Hint: Validează că operația e "safe", adică nu aruncă excepție.
    """
    fake_task_id = str(uuid.uuid4())

    delete_resp = requests.delete(f"{BASE_URL}/delete-task/{fake_task_id}")
    assert delete_resp.status_code == 404

    #pass

def test_create_task_invalid_data():
    """
    Testează crearea unui task cu date invalide.

    Pași:
    1. Trimite un request cu date invalide (ex: is_done="some_string").
    2. Verifică statusul și mesajul de eroare.
    """
    invalid_payload = {
        "user_id": str(uuid.uuid4()),
        "content": "Invalid is_done field",
        "is_done": "not-a-boolean"
    }

    resp = requests.put(f"{BASE_URL}/create-task", json=invalid_payload)
    assert resp.status_code == 422

    #pass

