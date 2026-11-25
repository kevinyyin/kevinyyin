"""Pure calculations on data/contributions.json. Weeks run Sunday to Saturday."""
import math
from datetime import date, datetime, timedelta, timezone

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _sunday(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)


def fmt_date(iso: str, year: bool = False) -> str:
    d = date.fromisoformat(iso[:10])
    return f"{MONTHS[d.month - 1]} {d.day}" + (f", {d.year}" if year else "")


def grid(days: list[dict], today: date, weeks: int = 26) -> list[list[dict | None]]:
    by_date = {d["date"]: d for d in days}
    start = _sunday(today) - timedelta(weeks=weeks - 1)
    columns = []
    for w in range(weeks):
        col = []
        for i in range(7):
            day = start + timedelta(days=w * 7 + i)
            col.append(by_date.get(day.isoformat()) if day <= today else None)
        columns.append(col)
    return columns


def window_total(columns: list[list[dict | None]]) -> int:
    return sum(c["count"] for col in columns for c in col if c)


def month_labels(columns: list[list[dict | None]]) -> list[tuple[int, str]]:
    labels = []
    for i, col in enumerate(columns):
        for c in col:
            if c and c["date"][8:10] == "01":
                labels.append((i, MONTHS[int(c["date"][5:7]) - 1]))
    return labels


def shade(count: int) -> tuple[str, float]:
    if count <= 0:
        return ("ink", 0.07)
    if count >= 100:
        return ("accent", 1.0)
    return ("ink", min(1.0, 0.22 + 0.78 * math.sqrt(count / 75)))


def weekly_streak(days: list[dict], today: date) -> int:
    active = {_sunday(date.fromisoformat(d["date"])) for d in days if d["count"] > 0}
    week = _sunday(today)
    if week not in active:
        week -= timedelta(weeks=1)  # this week isn't over yet, don't break the streak on it
    n = 0
    while week in active:
        n += 1
        week -= timedelta(weeks=1)
    return n


def last_active(days: list[dict]) -> str | None:
    return max((d["date"] for d in days if d["count"] > 0), default=None)


def streak_caption(data: dict) -> str:
    cur, longest = data["current_streak"], data["longest_streak"]
    if not cur["length"]:
        last = last_active(data["days"])
        return f"last active {fmt_date(last)}" if last else "no activity yet"
    since = f"since {fmt_date(cur['start'])}"
    if cur["length"] >= longest["length"]:
        return f"{since} · your longest yet"
    return f"{since} · longest: {longest['length']} days"


def as_of(generated_at: str, now: datetime) -> str | None:
    made = datetime.strptime(generated_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    if now - made > timedelta(hours=48):
        return f"as of {fmt_date(generated_at)}"
    return None
