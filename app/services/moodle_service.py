import requests
from flask import current_app


MOODLE_BASE_URL = "https://newlms.misis.ru"


def get_token(username: str, password: str) -> str:
    """Authenticate with Moodle and return token. Password is NOT stored."""
    payload = {
        'username': username,
        'password': password,
        'service': 'moodle_mobile_app'
    }
    response = requests.post(
        f"{MOODLE_BASE_URL}/login/token.php",
        data=payload,
        timeout=15
    )
    data = response.json()
    if 'token' not in data:
        raise ValueError(data.get('error', 'Неверный логин или пароль'))
    return data['token']


def fetch_assignments(token: str) -> list:
    """Fetch all assignments from Moodle using token."""
    params = {
        'wstoken': token,
        'wsfunction': 'mod_assign_get_assignments',
        'moodlewsrestformat': 'json'
    }
    response = requests.get(
        f"{MOODLE_BASE_URL}/webservice/rest/server.php",
        params=params,
        timeout=15
    )
    data = response.json()
    if 'exception' in data:
        raise ValueError(data.get('message', 'Ошибка получения заданий'))
    return data.get('courses', [])
