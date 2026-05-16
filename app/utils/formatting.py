def get_status_info(days_left: int) -> dict:
    """Return visual and semantic info based on days remaining."""
    if days_left < 0:
        return {
            'emoji': '💀',
            'status': 'overdue',
            'color_class': 'overdue',
            'badge_class': 'badge-overdue',
            'priority': 0,
        }
    elif days_left == 0:
        return {
            'emoji': '🔥',
            'status': 'soon',
            'color_class': 'critical',
            'badge_class': 'badge-critical',
            'priority': 1,
        }
    elif days_left <= 2:
        return {
            'emoji': '🚨',
            'status': 'soon',
            'color_class': 'danger',
            'badge_class': 'badge-danger',
            'priority': 2,
        }
    elif days_left <= 7:
        return {
            'emoji': '⚠️',
            'status': 'soon',
            'color_class': 'warning',
            'badge_class': 'badge-warning',
            'priority': 3,
        }
    elif days_left <= 14:
        return {
            'emoji': '📅',
            'status': 'good',
            'color_class': 'info',
            'badge_class': 'badge-info',
            'priority': 4,
        }
    else:
        return {
            'emoji': '✅',
            'status': 'good',
            'color_class': 'safe',
            'badge_class': 'badge-safe',
            'priority': 5,
        }


# Overdue levels — humorous Russian academic scale
OVERDUE_LEVELS = [
    (0,   "Мамина радость",           "Сдал вовремя, бюджет в безопасности 🎉"),
    (-1,  "Ещё не всё потеряно",      "Препод ещё помнит твоё лицо 😬"),
    (-3,  "Начинаем нервничать",      "Время писать «я болел» 🤧"),
    (-7,  "Пора каяться",             "Объяснительная сама себя не напишет 📝"),
    (-14, "Зачётка рыдает",           "Она видела лучшие времена 😭"),
    (-21, "Деканат знает тебя в лицо","Ты уже легенда кафедры, но не в хорошем смысле 👀"),
    (-30, "Увидимся в академе",        "Академический отпуск машет рукой 👋"),
    (-45, "Призрак университета",      "Ты ещё числишься? Серьёзно? 👻"),
    (-60, "Удачи в следующей жизни",   "Диплом? Не, не слышал. Пока 🫡"),
]


def get_overdue_level(days_left: int) -> dict | None:
    """Return overdue level dict for negative days_left."""
    if days_left >= 0:
        return None
    result = None
    for threshold, title, subtitle in OVERDUE_LEVELS:
        if days_left <= threshold:
            result = {"title": title, "subtitle": subtitle, "days": abs(days_left)}
    return result