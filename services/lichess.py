import re
import json
import uuid
import requests


LICHESS_BASE = "https://lichess.org/api"
CHESSCOM_BASE = "https://api.chess.com/pub"
HEADERS_CHESSCOM = {"User-Agent": "ChessLens/1.0"}


def get_games(username: str, max: int = 10) -> str:
    response = requests.get(
        f"{LICHESS_BASE}/games/user/{username}",
        params={"max": max, "moves": "true"},
        headers={"Accept": "application/x-ndjson"},
        timeout=15,
    )
    response.raise_for_status()
    return response.text


def get_games_chesscom(username: str, max: int = 10) -> str:
    archives_resp = requests.get(
        f"{CHESSCOM_BASE}/player/{username}/games/archives",
        headers=HEADERS_CHESSCOM,
        timeout=15,
    )
    archives_resp.raise_for_status()
    archives = archives_resp.json().get("archives", [])

    if not archives:
        return ""

    games_resp = requests.get(archives[-1], headers=HEADERS_CHESSCOM, timeout=15)
    games_resp.raise_for_status()
    games = list(reversed(games_resp.json().get("games", [])))[:max]

    ndjson = ""
    for game in games:
        white_result = (game.get("white") or {}).get("result", "")
        black_result = (game.get("black") or {}).get("result", "")
        if white_result == "win":
            winner = "white"
        elif black_result == "win":
            winner = "black"
        else:
            winner = "draw"

        ndjson += json.dumps({
            "id": game.get("uuid", str(uuid.uuid4())),
            "winner": winner,
            "moves": game.get("pgn", ""),
        }) + "\n"

    return ndjson


def import_game(pgn: str) -> str:
    """Import a PGN to Lichess and return the game URL for free analysis."""
    response = requests.post(
        "https://lichess.org/api/import",
        data={"pgn": pgn},
        headers={"Accept": "application/json", "User-Agent": "ChessLens/1.0"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["url"]


def parse_games(ndjson: str) -> list[dict]:
    games = []
    for line in ndjson.strip().splitlines():
        if not line:
            continue
        game = json.loads(line)
        if "moves" not in game:
            continue

        moves = game["moves"]
        moves = re.sub(r'\{[^}]*\}', '', moves)        # retire commentaires
        moves = re.sub(r'\[[^\]]*\]', '', moves)        # retire headers
        moves = re.sub(r'\d+\.{1,3}\s*', '', moves)    # retire numéros
        moves = re.sub(r'\s+', ' ', moves.strip())      # nettoie espaces
        moves = re.sub(r'1-0|0-1|1/2-1/2|\*', '', moves)  # retire résultat

        games.append({
            "id": game.get("id", ""),
            "winner": game.get("winner", "draw"),
            "moves": moves.strip() or game["moves"],
        })

    return games
