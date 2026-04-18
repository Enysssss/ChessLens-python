import os
import anthropic


def analyze_games(username: str, games: list[dict]) -> dict:
    games_text = ""
    for i, game in enumerate(games, 1):
        games_text += f"Partie {i} (résultat: {game['winner']}) : {game['moves']}\n\n"

    prompt = f"""Tu es un coach d'échecs qui a un sens de l'humour acéré. Voici les dernières parties de "{username}" sur Lichess.

{games_text}

Réponds en JSON strict, sans markdown, sans backticks, exactement ce format :
{{
  "roast": "Un roast drôle, un peu méchant mais pas vulgaire, de 2-3 phrases maximum sur son style de jeu. Style tweet viral. Ne mentionne pas les numéros de parties. Parle de son comportement général.",
  "style": "Son style général en 1-2 phrases directes.",
  "strengths": "Ses vrais points forts, basés sur l'ensemble des parties, sans mentionner de numéros de partie.",
  "weaknesses": "Ses vrais défauts récurrents, sans mentionner de numéros de partie.",
  "openings": "Ce qu'il joue en ouverture de manière générale.",
  "advice": "Un conseil principal concret, direct, actionnable."
}}"""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    import json, re
    text = message.content[0].text
    text = re.sub(r'```json|```', '', text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "roast": "", "style": text,
            "strengths": "", "weaknesses": "",
            "openings": "", "advice": "",
        }
