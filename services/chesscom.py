import re
import requests
from datetime import datetime

HEADERS = {"User-Agent": "ChessLens/1.0"}
BASE = "https://api.chess.com/pub"


def get_player_games(username: str, count: int = 10) -> list[dict]:
    archives = _get_archives(username)
    if not archives:
        return []

    raw_games: list[dict] = []
    for archive_url in reversed(archives):
        resp = requests.get(archive_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        month = list(reversed(resp.json().get("games", [])))
        raw_games.extend(month)
        if len(raw_games) >= count:
            break

    return _format_games(username.lower(), raw_games[:count])


def _get_archives(username: str) -> list[str]:
    resp = requests.get(f"{BASE}/player/{username}/games/archives", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json().get("archives", [])


def _format_games(username_lower: str, games: list[dict]) -> list[dict]:
    result = []
    for g in games:
        white = g.get("white") or {}
        black = g.get("black") or {}

        is_white = white.get("username", "").lower() == username_lower
        my = white if is_white else black
        opp = black if is_white else white

        my_result = my.get("result", "")
        if my_result == "win":
            outcome = "win"
        elif my_result in ("checkmated", "resigned", "timeout", "abandoned", "lose"):
            outcome = "loss"
        else:
            outcome = "draw"

        pgn = g.get("pgn", "")
        eco_url = _extract_pgn_header(pgn, "ECOUrl")
        opening = eco_url.split("/")[-1].replace("-", " ").title() if eco_url else (
            _extract_pgn_header(pgn, "Opening") or "—"
        )

        end_time = g.get("end_time")
        date_str = datetime.fromtimestamp(end_time).strftime("%d %b %Y") if end_time else "—"

        accuracies = g.get("accuracies") or {}
        my_color_key = "white" if is_white else "black"
        acc = accuracies.get(my_color_key)

        result.append({
            "pgn": pgn,
            "outcome": outcome,
            "opponent": opp.get("username", "?"),
            "opponent_rating": opp.get("rating", "?"),
            "my_rating": my.get("rating", "?"),
            "my_color": my_color_key,
            "date": date_str,
            "time_control": _format_time_control(g.get("time_control", "")),
            "opening": opening,
            "accuracy": round(acc, 1) if acc else None,
        })

    return result


def _extract_pgn_header(pgn: str, key: str) -> str:
    m = re.search(rf'\[{key} "([^"]+)"\]', pgn)
    return m.group(1) if m else ""


def _format_time_control(tc: str) -> str:
    if not tc:
        return "—"
    try:
        if "+" in tc:
            base, inc = tc.split("+", 1)
            base, inc = int(base), int(inc)
        else:
            base, inc = int(tc), 0

        if base >= 1500:
            label = f"Classique {base // 60}"
        elif base >= 600:
            label = f"Rapide {base // 60}"
        elif base >= 180:
            label = f"Blitz {base // 60}"
        else:
            label = f"Bullet {base // 60}"

        return f"{label}+{inc}min" if inc else f"{label}min"
    except (ValueError, AttributeError):
        return tc
