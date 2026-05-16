from flask import Blueprint, session, jsonify, Response, request
from ..services.moodle_service import fetch_assignments
from ..services.analytics_service import process_deadlines
from ..services.export_service import (
    export_txt, export_markdown, export_json,
    export_csv, export_ics, export_notes
)

export_bp = Blueprint('export', __name__)


def _get_deadlines():
    token = session.get('token')
    if not token:
        return None, ('Не авторизован', 401)
    try:
        courses = fetch_assignments(token)
        return process_deadlines(courses), None
    except Exception as e:
        return None, (str(e), 500)


@export_bp.route('/txt')
def to_txt():
    dl, err = _get_deadlines()
    if err:
        return jsonify({'error': err[0]}), err[1]
    return Response(export_txt(dl), mimetype='text/plain',
                    headers={'Content-Disposition': 'attachment; filename=deadlines.txt'})


@export_bp.route('/md')
def to_md():
    dl, err = _get_deadlines()
    if err:
        return jsonify({'error': err[0]}), err[1]
    return Response(export_markdown(dl), mimetype='text/markdown',
                    headers={'Content-Disposition': 'attachment; filename=deadlines.md'})


@export_bp.route('/json')
def to_json():
    dl, err = _get_deadlines()
    if err:
        return jsonify({'error': err[0]}), err[1]
    return Response(export_json(dl), mimetype='application/json',
                    headers={'Content-Disposition': 'attachment; filename=deadlines.json'})


@export_bp.route('/csv')
def to_csv():
    dl, err = _get_deadlines()
    if err:
        return jsonify({'error': err[0]}), err[1]
    return Response(export_csv(dl), mimetype='text/csv',
                    headers={'Content-Disposition': 'attachment; filename=deadlines.csv'})


@export_bp.route('/ics')
def to_ics():
    dl, err = _get_deadlines()
    if err:
        return jsonify({'error': err[0]}), err[1]
    return Response(export_ics(dl), mimetype='text/calendar',
                    headers={'Content-Disposition': 'attachment; filename=deadlines.ics'})


@export_bp.route('/notes')
def to_notes():
    dl, err = _get_deadlines()
    if err:
        return jsonify({'error': err[0]}), err[1]
    return Response(export_notes(dl), mimetype='text/plain',
                    headers={'Content-Disposition': 'attachment; filename=notes.txt'})
