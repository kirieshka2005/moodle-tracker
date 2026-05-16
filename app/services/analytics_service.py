from datetime import datetime, timedelta
from ..utils.date_utils import days_between, get_week_range
from ..utils.formatting import get_status_info, get_overdue_level


def process_deadlines(courses: list) -> list:
    """Convert raw Moodle course data into enriched deadline dicts."""
    deadlines = []
    now = datetime.now()

    for course in courses:
        course_name = course.get('fullname') or course.get('shortname', 'Без названия')
        for assign in course.get('assignments', []):
            duedate = assign.get('duedate', 0)
            if duedate <= 0:
                continue

            due = datetime.fromtimestamp(duedate)
            diff = due - now
            days_left = diff.days
            hours_left = int(diff.total_seconds() // 3600)

            # Skip very old deadlines
            if days_left < -60:
                continue

            status_info = get_status_info(days_left)
            overdue_level = get_overdue_level(days_left) if days_left < 0 else None

            deadlines.append({
                "course": course_name,
                "task": assign.get('name', 'Без названия'),
                "due_date": due.strftime("%d.%m.%Y %H:%M"),
                "due_timestamp": duedate,
                "days_left": days_left,
                "hours_left": hours_left,
                "time_left": _format_time_left(days_left, hours_left),
                "emoji": status_info['emoji'],
                "status": status_info['status'],
                "color_class": status_info['color_class'],
                "badge_class": status_info['badge_class'],
                "priority": status_info['priority'],
                "overdue_level": overdue_level,
                "deleted": False,
                "manual_priority": None,  # for user override
            })

    # Sort by due date ascending (soonest first)
    deadlines.sort(key=lambda x: x['due_timestamp'])
    return deadlines


def get_stats(deadlines: list) -> dict:
    """Compute summary statistics for the dashboard."""
    active = [d for d in deadlines if not d['deleted']]
    total = len(active)
    overdue = len([d for d in active if d['status'] == 'overdue'])
    soon = len([d for d in active if d['status'] == 'soon'])
    good = len([d for d in active if d['status'] == 'good'])

    now = datetime.now()
    week_start, week_end = get_week_range(now, offset_weeks=1)
    next_week = [
        d for d in active
        if week_start <= datetime.fromtimestamp(d['due_timestamp']) <= week_end
    ]

    done_pct = 0  # Will be updated client-side from localStorage
    return {
        "total": total,
        "overdue": overdue,
        "soon": soon,
        "good": good,
        "next_week_count": len(next_week),
        "next_week_deadlines": next_week,
    }


def group_by_course(deadlines: list) -> dict:
    """Group active deadlines by course name."""
    groups = {}
    for d in deadlines:
        if d['deleted']:
            continue
        course = d['course']
        if course not in groups:
            groups[course] = []
        groups[course].append(d)
    return groups


def _format_time_left(days_left: int, hours_left: int) -> str:
    if days_left < 0:
        days_ago = abs(days_left)
        return f"{days_ago} дн. назад"
    elif days_left == 0:
        h = hours_left
        if h <= 0:
            return "Истекает сейчас"
        return f"~{h} ч."
    elif days_left == 1:
        return "Завтра"
    else:
        return f"{days_left} дн."
