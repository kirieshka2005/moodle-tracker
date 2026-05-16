from flask import Blueprint, render_template, session, jsonify, request
from ..services.moodle_service import get_token, fetch_assignments
from ..services.analytics_service import process_deadlines, get_stats, group_by_course
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user, store only token in session (never the password)."""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Введите логин и пароль'}), 400

    try:
        token = get_token(username, password)
        # Store ONLY token and username — password is discarded immediately
        session['token'] = token
        session['username'] = username
        session.permanent = True
        return jsonify({'ok': True, 'username': username})
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Ошибка соединения: {str(e)}'}), 500


@main_bp.route('/deadlines', methods=['GET'])
def deadlines():
    """Return processed deadlines for the logged-in user."""
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Не авторизован'}), 401

    try:
        courses = fetch_assignments(token)
        dl = process_deadlines(courses)
        stats = get_stats(dl)
        groups = group_by_course(dl)

        return jsonify({
            'deadlines': dl,
            'stats': stats,
            'groups': {k: v for k, v in groups.items()},
            'update_time': datetime.now().strftime("%d.%m.%Y %H:%M"),
        })
    except ValueError as e:
        session.clear()
        return jsonify({'error': str(e), 'reauth': True}), 401
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500


@main_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})


@main_bp.route('/session', methods=['GET'])
def check_session():
    """Check if user has a valid session (token present)."""
    if session.get('token'):
        return jsonify({'authenticated': True, 'username': session.get('username', '')})
    return jsonify({'authenticated': False})
