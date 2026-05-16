import json
import csv
import io
from datetime import datetime, timezone


# ──────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────

def _group_by_course(deadlines: list) -> dict:
    """Return OrderedDict-like dict: course → [deadlines], sorted by due_timestamp."""
    groups: dict = {}
    for d in deadlines:
        if d.get('deleted'):
            continue
        groups.setdefault(d['course'], []).append(d)
    # Sort each group internally by date
    for items in groups.values():
        items.sort(key=lambda x: x.get('due_timestamp', 0))
    return groups


def _overdue_label(d: dict) -> str:
    """Return human-readable overdue label if applicable."""
    ol = d.get('overdue_level')
    if ol and isinstance(ol, dict):
        return ol.get('title', '')
    return ''


def _status_ru(d: dict) -> str:
    label = _overdue_label(d)
    if label:
        return label
    return d.get('time_left', '—')


def _ics_escape(text: str) -> str:
    return (text
            .replace('\\', '\\\\')
            .replace('\n', '\\n')
            .replace(',', '\\,')
            .replace(';', '\\;'))


# ──────────────────────────────────────────
#  EXPORT FUNCTIONS
# ──────────────────────────────────────────

def export_txt(deadlines: list) -> str:
    now = datetime.now().strftime('%d.%m.%Y %H:%M')
    groups = _group_by_course(deadlines)
    total = sum(len(v) for v in groups.values())

    lines = [
        "╔══════════════════════════════════════╗",
        "║       ДЕДЛАЙНЫ MOODLE — МИСИС        ║",
        "╚══════════════════════════════════════╝",
        f"  Экспорт: {now}",
        f"  Всего задач: {total}",
        "",
    ]

    for course, items in groups.items():
        lines.append(f"┌─ 📚 {course} ({len(items)} задан.)")
        for d in items:
            status = _status_ru(d)
            overdue_sub = ''
            ol = d.get('overdue_level')
            if ol and isinstance(ol, dict):
                overdue_sub = f"\n  │    └─ {ol.get('subtitle', '')}"
            lines.append(f"  ├─ {d['emoji']}  {d['task']}")
            lines.append(f"  │    Дедлайн: {d['due_date']}  ·  {status}{overdue_sub}")
        lines.append("  └─" + "─" * 38)
        lines.append("")

    return "\n".join(lines)


def export_markdown(deadlines: list) -> str:
    now = datetime.now().strftime('%d.%m.%Y %H:%M')
    groups = _group_by_course(deadlines)
    total = sum(len(v) for v in groups.values())

    lines = [
        "# 🎯 Дедлайны Moodle",
        f"*Экспорт: {now} · Всего задач: {total}*",
        "",
    ]

    for course, items in groups.items():
        lines.append(f"## 📚 {course}")
        lines.append("")
        lines.append("| # | Задание | Дедлайн | Осталось / Статус | Уровень просрочки |")
        lines.append("|---|---------|---------|-------------------|-------------------|")
        for i, d in enumerate(items, 1):
            ol = d.get('overdue_level')
            overdue_title = ol.get('title', '—') if isinstance(ol, dict) else '—'
            status = d['time_left']
            lines.append(
                f"| {i} | {d['emoji']} {d['task']} "
                f"| {d['due_date']} "
                f"| {status} "
                f"| {overdue_title} |"
            )
        lines.append("")

    return "\n".join(lines)


def export_json(deadlines: list) -> str:
    groups = _group_by_course(deadlines)
    output = {
        "exported_at": datetime.now().isoformat(),
        "total": sum(len(v) for v in groups.values()),
        "courses": {}
    }

    for course, items in groups.items():
        output["courses"][course] = [
            {
                "task": d["task"],
                "due_date": d["due_date"],
                "due_timestamp": d["due_timestamp"],
                "days_left": d["days_left"],
                "time_left": d["time_left"],
                "status": d["status"],
                "emoji": d["emoji"],
                "overdue_level": d.get("overdue_level"),
            }
            for d in items
        ]

    return json.dumps(output, ensure_ascii=False, indent=2)


def export_csv(deadlines: list) -> str:
    groups = _group_by_course(deadlines)
    output = io.StringIO()
    fieldnames = ['course', 'task', 'due_date', 'days_left', 'time_left', 'status', 'overdue_title', 'overdue_subtitle']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for course, items in groups.items():
        for d in items:
            ol = d.get('overdue_level')
            writer.writerow({
                'course':           d['course'],
                'task':             d['task'],
                'due_date':         d['due_date'],
                'days_left':        d['days_left'],
                'time_left':        d['time_left'],
                'status':           d['status'],
                'overdue_title':    ol.get('title', '') if isinstance(ol, dict) else '',
                'overdue_subtitle': ol.get('subtitle', '') if isinstance(ol, dict) else '',
            })

    return output.getvalue()


def export_ics(deadlines: list) -> str:
    """Generate iCalendar (.ics) file — one event per deadline, grouped description."""
    groups = _group_by_course(deadlines)
    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Moodle Tracker//RU",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    idx = 0
    for course, items in groups.items():
        for d in items:
            try:
                due_dt = datetime.fromtimestamp(d['due_timestamp'], tz=timezone.utc)
                dtstart = due_dt.strftime("%Y%m%dT%H%M%SZ")
                summary = f"{d['emoji']} {d['task']}"
                ol = d.get('overdue_level')
                desc_parts = [f"Предмет: {course}", f"Осталось: {d['time_left']}"]
                if isinstance(ol, dict):
                    desc_parts.append(f"Статус: {ol.get('title','')} — {ol.get('subtitle','')}")
                description = " | ".join(desc_parts)
                uid = f"moodle-{d['due_timestamp']}-{idx}@tracker"
                lines += [
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{now_stamp}",
                    f"DTSTART:{dtstart}",
                    f"DTEND:{dtstart}",
                    f"SUMMARY:{_ics_escape(summary)}",
                    f"DESCRIPTION:{_ics_escape(description)}",
                    f"CATEGORIES:{_ics_escape(course)}",
                    "END:VEVENT",
                ]
                idx += 1
            except Exception:
                continue

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def export_notes(deadlines: list) -> str:
    """Grouped plain text for copy-paste into Notes / Telegram / anything."""
    now = datetime.now().strftime('%d.%m.%Y')
    groups = _group_by_course(deadlines)
    total = sum(len(v) for v in groups.values())

    lines = [
        f"📋 Дедлайны Moodle · {now}",
        f"Всего задач: {total}",
        "",
    ]

    for course, items in groups.items():
        lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"📚 {course}")
        lines.append("")
        for d in items:
            ol = d.get('overdue_level')
            status = _status_ru(d)
            lines.append(f"  {d['emoji']} {d['task']}")
            lines.append(f"     📅 {d['due_date']}  ·  {status}")
            if isinstance(ol, dict):
                lines.append(f"     ☠️  {ol.get('subtitle', '')}")
            lines.append("")

    return "\n".join(lines)