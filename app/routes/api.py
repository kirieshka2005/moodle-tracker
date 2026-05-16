from flask import Blueprint, jsonify, session

api_bp = Blueprint('api', __name__)


@api_bp.route('/ping')
def ping():
    return jsonify({'status': 'ok'})


@api_bp.route('/me')
def me():
    if session.get('token'):
        return jsonify({'username': session.get('username', ''), 'authenticated': True})
    return jsonify({'authenticated': False}), 401
