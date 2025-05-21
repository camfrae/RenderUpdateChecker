import time

def get_uptime_minutes(start_timestamp):
    """
    Возвращает количество минут с момента запуска мониторинга,
    округлённое вверх при любом неполном интервале.
    """
    return int((time.time() - start_timestamp + 59) // 60)

def format_idle_duration(seconds):
    """
    Форматирует продолжительность бездействия в виде:
    - 0 мин. 34 сек.
    - 5 мин. 12 сек.
    - 1 час. 3 мин. 5 сек.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours:
        parts.append(f"{hours} час." if hours == 1 else f"{hours} ч.")
    parts.append(f"{minutes} мин.")
    parts.append(f"{secs} сек.")

    return " ".join(parts)
