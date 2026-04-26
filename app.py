import os
import streamlit as st
from dotenv import load_dotenv

from services.lichess import get_games, get_games_chesscom, parse_games, import_game
from services.claude_ai import analyze_games
from services import chesscom

load_dotenv()

st.set_page_config(
    page_title="ChessLens",
    page_icon="♟",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── DESIGN OBSIDIAN ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, .stApp {
    background: #0C0C0C !important;
    color: #EDECEA;
    font-family: 'Inter', sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }

/* Container */
.block-container {
    padding: 0 1.5rem 5rem 1.5rem !important;
    max-width: 860px !important;
}

/* Zoom base */
html { font-size: 17px; }

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    gap: 0 !important;
    margin-bottom: 2.5rem !important;
}
[data-baseweb="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 400 !important;
    color: rgba(255,255,255,0.28) !important;
    padding: 12px 22px !important;
    border-bottom: 1.5px solid transparent !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    background: transparent !important;
    transition: color 0.2s !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #C9913A !important;
    border-bottom-color: #C9913A !important;
}
[data-baseweb="tab"]:hover { color: rgba(255,255,255,0.55) !important; }
[data-baseweb="tab-panel"] { background: transparent !important; padding: 0 !important; }

/* ── Inputs ── */
.stTextInput label, .stSelectbox label, .stSlider label,
div[data-testid="stWidgetLabel"] > label {
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: rgba(255,255,255,0.55) !important;
}
.stTextInput input {
    background: #141414 !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 6px !important;
    color: #EDECEA !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    padding: 11px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus {
    border-color: #C9913A !important;
    box-shadow: 0 0 0 3px rgba(201,145,58,0.12) !important;
    outline: none !important;
}
.stTextInput input::placeholder { color: rgba(255,255,255,0.18) !important; }

[data-baseweb="select"] > div:first-child {
    background: #141414 !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 6px !important;
    color: #EDECEA !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
}
[data-baseweb="popover"] { background: #1A1A1A !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 8px !important; }
[data-baseweb="menu"] { background: #1A1A1A !important; }
[data-baseweb="menu-item"] { color: #EDECEA !important; font-family: 'Inter', sans-serif !important; }
[data-baseweb="menu-item"]:hover { background: rgba(255,255,255,0.06) !important; }

/* Slider */
[data-testid="stSlider"] [data-testid="stTickBar"] { display: none !important; }
[data-testid="stSlider"] > div > div > div > div { background: #C9913A !important; }
[data-testid="stSlider"] > div > div > div { background: rgba(255,255,255,0.1) !important; }

/* ── Buttons ── */
.stButton > button, .stFormSubmitButton > button {
    background: #C9913A !important;
    color: #0C0C0C !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    padding: 13px 24px !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
    cursor: pointer !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    opacity: 0.85 !important;
    transform: translateY(-1px) !important;
}

/* Link button */
.stLinkButton > a {
    background: transparent !important;
    border: 1px solid #C9913A !important;
    color: #C9913A !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    text-decoration: none !important;
    padding: 10px 18px !important;
    display: inline-flex !important;
    align-items: center !important;
    width: 100% !important;
    justify-content: center !important;
    transition: background 0.2s, color 0.2s !important;
}
.stLinkButton > a:hover { background: #C9913A !important; color: #0C0C0C !important; }

/* ── Alerts ── */
div[data-testid="stNotification"], .stAlert {
    background: #141414 !important;
    border-radius: 6px !important;
    border-color: rgba(255,255,255,0.1) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #C9913A !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #141414 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 6px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #C9913A; }

/* ── Custom components ── */

.ob-header {
    padding: 4rem 0 3rem;
    text-align: center;
}
.ob-logo {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.6rem;
    font-weight: 300;
    color: #EDECEA;
    letter-spacing: 0.04em;
    line-height: 1;
}
.ob-logo b { color: #C9913A; font-weight: 600; }
.ob-tagline {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: rgba(255,255,255,0.25);
    letter-spacing: 0.35em;
    text-transform: uppercase;
    margin-top: 12px;
}
.ob-line {
    width: 32px;
    height: 1px;
    background: #C9913A;
    margin: 16px auto 0;
    opacity: 0.6;
}

.ob-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #C9913A;
    margin-bottom: 1.25rem;
    opacity: 0.8;
}

.ob-quote {
    margin: 2rem 0;
    padding: 2.4rem 2.5rem;
    background: #111111;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.06);
    text-align: center;
}
.ob-quote-text {
    font-family: 'Inter', sans-serif;
    font-size: 1.2rem;
    font-style: normal;
    font-weight: 500;
    color: #EDECEA;
    line-height: 1.75;
    max-width: 640px;
    margin: 0 auto;
}
.ob-quote-text::before {
    content: '\201C';
    color: #C9913A;
    font-size: 1.6rem;
    line-height: 0;
    vertical-align: -0.35rem;
    margin-right: 4px;
    opacity: 0.9;
}
.ob-quote-text::after {
    content: '\201D';
    color: #C9913A;
    font-size: 1.6rem;
    line-height: 0;
    vertical-align: -0.35rem;
    margin-left: 4px;
    opacity: 0.9;
}

.ob-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 1.5rem 0;
}

.ob-card {
    background: #111111;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1.4rem 1.5rem;
    transition: border-color 0.2s;
}
.ob-card:hover { border-color: rgba(201,145,58,0.25); }
.ob-card-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    margin-bottom: 0.65rem;
}
.ob-card-body {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-style: normal;
    font-weight: 400;
    color: rgba(255,255,255,0.88);
    line-height: 1.7;
}

.ob-advice {
    background: linear-gradient(135deg, rgba(201,145,58,0.1), rgba(201,145,58,0.04));
    border: 1px solid rgba(201,145,58,0.25);
    border-radius: 10px;
    padding: 1.8rem 2rem;
    margin: 0.5rem 0 2rem;
    text-align: center;
}
.ob-advice-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #C9913A;
    margin-bottom: 0.75rem;
    opacity: 1;
}
.ob-advice-text {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 500;
    font-style: normal;
    color: #EDECEA;
    line-height: 1.7;
}

.ob-sep {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0;
    color: rgba(255,255,255,0.08);
    font-size: 0.9rem;
    letter-spacing: 0.5rem;
}
.ob-sep::before, .ob-sep::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* Game cards */
.ob-game {
    display: flex;
    align-items: stretch;
    gap: 0;
    background: #111111;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    margin-bottom: 10px;
    overflow: hidden;
    transition: border-color 0.2s;
}
.ob-game:hover { border-color: rgba(255,255,255,0.12); }
.ob-game-stripe {
    width: 3px;
    flex-shrink: 0;
}
.ob-game-stripe.win  { background: #30D158; }
.ob-game-stripe.loss { background: #FF453A; }
.ob-game-stripe.draw { background: rgba(255,255,255,0.2); }
.ob-game-body { padding: 1rem 1.25rem; flex: 1; }
.ob-game-top {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.4rem;
}
.ob-badge {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 4px;
    font-weight: 500;
}
.ob-badge.win  { background: rgba(48,209,88,0.12);  color: #30D158; }
.ob-badge.loss { background: rgba(255,69,58,0.12);   color: #FF453A; }
.ob-badge.draw { background: rgba(255,255,255,0.07); color: rgba(255,255,255,0.4); }
.ob-game-opp {
    font-size: 15px;
    font-weight: 500;
    color: #EDECEA;
}
.ob-game-opp span { color: rgba(255,255,255,0.3); font-weight: 300; margin-right: 4px; font-size: 13px; }
.ob-game-rating {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: rgba(255,255,255,0.5);
    margin-left: auto;
}
.ob-game-meta {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 400;
    color: rgba(255,255,255,0.5);
    letter-spacing: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 0.4rem;
}
.ob-acc { color: #C9913A !important; }

.ob-info-box {
    background: #111;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    margin-top: 2rem;
}
.ob-info-box p {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: rgba(255,255,255,0.2);
    letter-spacing: 0.1em;
    line-height: 1.8;
}
.ob-info-box b { color: #C9913A; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ob-header">
    <div class="ob-logo">Chess<b>Lens</b></div>
    <div class="ob-tagline">Analyse d'échecs par Intelligence artificielle</div>
    <div class="ob-line"></div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Analyse IA", "Ouvrir sur Lichess", "Comment ça marche"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Analyse IA
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:

    with st.form("analyze_form"):
        username = st.text_input("Pseudo du joueur", max_chars=30, placeholder="ex: MagnusCarlsen")
        col1, col2 = st.columns(2)
        with col1:
            platform = st.selectbox(
                "Plateforme",
                ["lichess", "chesscom"],
                format_func=lambda x: "Lichess" if x == "lichess" else "Chess.com",
            )
        with col2:
            games_count = st.selectbox("Parties analysées", options=[5, 10, 20], index=1)
        submitted = st.form_submit_button("Lancer l'analyse")

    if submitted:
        username = username.strip()
        if len(username) < 2:
            st.error("Le pseudo doit faire au moins 2 caractères.")
        elif not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Variable ANTHROPIC_API_KEY manquante dans .env")
        else:
            try:
                platform_label = "Lichess" if platform == "lichess" else "Chess.com"
                with st.spinner(f"Chargement des parties de {username}…"):
                    raw = get_games(username, max=games_count) if platform == "lichess" \
                          else get_games_chesscom(username, max=games_count)

                if not raw.strip():
                    st.error(f"Aucune partie trouvée pour **{username}**.")
                    st.stop()

                games_data = parse_games(raw)
                if not games_data:
                    st.error("Impossible de lire les parties récupérées.")
                    st.stop()

                with st.spinner("Claude analyse…"):
                    result = analyze_games(username, games_data)

                # Roast
                st.markdown(f"""
<div class="ob-quote">
    <div class="ob-quote-text">{result.get("roast", "—")}</div>
</div>
""", unsafe_allow_html=True)

                # Stats header
                st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
    <div class="ob-label" style="margin:0">Analyse de {username}</div>
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,0.2);">
        {len(games_data)} parties
    </div>
</div>
""", unsafe_allow_html=True)

                # 4 cards grid
                st.markdown(f"""
<div class="ob-grid">
    <div class="ob-card">
        <div class="ob-card-label">♟ Style</div>
        <div class="ob-card-body">{result.get("style","—")}</div>
    </div>
    <div class="ob-card">
        <div class="ob-card-label">↑ Points forts</div>
        <div class="ob-card-body">{result.get("strengths","—")}</div>
    </div>
    <div class="ob-card">
        <div class="ob-card-label">↓ Points faibles</div>
        <div class="ob-card-body">{result.get("weaknesses","—")}</div>
    </div>
    <div class="ob-card">
        <div class="ob-card-label">♞ Ouvertures</div>
        <div class="ob-card-body">{result.get("openings","—")}</div>
    </div>
</div>
""", unsafe_allow_html=True)

                # Advice
                st.markdown(f"""
<div class="ob-advice">
    <div class="ob-advice-label">♛ Conseil du coach</div>
    <div class="ob-advice-text">{result.get("advice","—")}</div>
</div>
""", unsafe_allow_html=True)

            except Exception as e:
                err = str(e)
                if "404" in err or "Not Found" in err:
                    st.error(f"Joueur **{username}** introuvable sur {platform_label}.")
                elif "401" in err or "403" in err:
                    st.error("Clé API Anthropic invalide.")
                else:
                    st.error(f"Erreur : {err}")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Ouvrir sur Lichess
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:

    with st.form("browser_form"):
        cc_username = st.text_input("Pseudo Chess.com", max_chars=30, placeholder="ex: hikaru")
        cc_count = st.selectbox("Nombre de parties", options=[5, 10, 20], index=1)
        load_btn = st.form_submit_button("♟  Charger les parties")

    if load_btn:
        cc_username = cc_username.strip()
        if len(cc_username) < 2:
            st.error("Le pseudo doit faire au moins 2 caractères.")
        else:
            try:
                with st.spinner(f"Chargement des parties de {cc_username}…"):
                    games_list = chesscom.get_player_games(cc_username, count=cc_count)
                if not games_list:
                    st.error(f"Aucune partie trouvée pour **{cc_username}** sur Chess.com.")
                    st.stop()
                st.session_state["cc_games"] = games_list
                st.session_state["cc_user"] = cc_username
                st.session_state.pop("lichess_urls", None)
            except Exception as e:
                err = str(e)
                if "404" in err or "Not Found" in err:
                    st.error(f"Joueur **{cc_username}** introuvable sur Chess.com.")
                else:
                    st.error(f"Erreur : {err}")

    if "cc_games" in st.session_state:
        games_list: list[dict] = st.session_state["cc_games"]
        cc_user: str = st.session_state.get("cc_user", "")

        if "lichess_urls" not in st.session_state:
            st.session_state["lichess_urls"] = {}

        outcome_labels = {"win": "Victoire", "loss": "Défaite", "draw": "Nulle"}
        color_icons    = {"white": "♔", "black": "♚"}

        st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem;">
    <div class="ob-label" style="margin:0">{len(games_list)} parties de {cc_user}</div>
    <div style="font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,0.2);">
        Chess.com → Lichess
    </div>
</div>
""", unsafe_allow_html=True)

        for i, g in enumerate(games_list):
            outcome   = g["outcome"]
            icon      = color_icons.get(g.get("my_color", "white"), "♟")
            acc_part  = f' · <span class="ob-acc">{g["accuracy"]}%</span>' if g["accuracy"] else ""

            meta = (
                f'⏱ {g["time_control"]} &nbsp;·&nbsp; '
                f'📅 {g["date"]} &nbsp;·&nbsp; '
                f'🎯 {g["opening"]}'
                f'{acc_part}'
            )

            card_html = (
                f'<div class="ob-game">'
                f'<div class="ob-game-stripe {outcome}"></div>'
                f'<div class="ob-game-body">'
                f'<div class="ob-game-top">'
                f'<span class="ob-badge {outcome}">{outcome_labels[outcome]}</span>'
                f'<span class="ob-game-opp"><span>vs</span>{g["opponent"]}</span>'
                f'<span class="ob-game-rating">{icon} {g["my_rating"]} · {g["opponent_rating"]}</span>'
                f'</div>'
                f'<div class="ob-game-meta">{meta}</div>'
                f'</div>'
                f'</div>'
            )

            col_card, col_btn = st.columns([3, 1])
            with col_card:
                st.markdown(card_html, unsafe_allow_html=True)

            with col_btn:
                lichess_url = st.session_state["lichess_urls"].get(i)
                st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                if lichess_url:
                    st.link_button("Ouvrir ↗", lichess_url, use_container_width=True)
                else:
                    if st.button("Analyser", key=f"import_{i}", use_container_width=True):
                        pgn = g.get("pgn", "")
                        if not pgn:
                            st.error("PGN manquant.")
                        else:
                            try:
                                with st.spinner("Import…"):
                                    url = import_game(pgn)
                                st.session_state["lichess_urls"][i] = url
                                st.rerun()
                            except Exception as e:
                                st.error(f"Import échoué : {e}")
                                with st.expander("PGN — coller sur lichess.org/paste"):
                                    st.code(pgn, language=None)

        st.markdown("""
<div class="ob-info-box">
    <p>♟ &nbsp;L'analyse <b>Stockfish</b> sur Lichess est entièrement <b>gratuite</b><br>
    contrairement à Chess.com qui la réserve aux abonnés Premium</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Comment ça marche
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="ob-label">C\'est quoi ChessLens ?</div>', unsafe_allow_html=True)
    st.markdown(
        "ChessLens est un outil gratuit qui analyse vos parties d'échecs avec l'intelligence artificielle "
        "et vous permet de les rejouer coup par coup avec un moteur d'analyse de niveau grandmaster — "
        "sans abonnement payant."
    )

    st.markdown("")
    st.markdown('<div class="ob-label">Comment ça marche — en 3 étapes</div>', unsafe_allow_html=True)
    st.markdown("")

    steps = [
        (
            "1",
            "Vous entrez votre pseudo",
            "Chess.com et Lichess sont deux plateformes en ligne où des millions de personnes jouent aux échecs. "
            "Il suffit d'entrer votre nom d'utilisateur — ChessLens récupère automatiquement vos dernières parties.",
        ),
        (
            "2",
            "L'IA analyse votre jeu",
            "Claude (une IA d'Anthropic, similaire à ChatGPT) lit vos parties et identifie votre style, "
            "vos forces, vos erreurs récurrentes, et vous donne un conseil concret pour progresser.",
        ),
        (
            "3",
            "Vous rejouez chaque partie avec un moteur d'analyse",
            "Stockfish est le programme d'échecs le plus fort du monde. Il montre, coup par coup, "
            "les erreurs commises et les meilleurs coups possibles. "
            "Sur Lichess cette analyse est **100 % gratuite** — Chess.com la réserve à ses abonnés payants. "
            "ChessLens fait le pont entre les deux.",
        ),
    ]

    for num, title, body in steps:
        st.markdown(
            f'<div style="display:flex;gap:1.25rem;align-items:flex-start;margin-bottom:1.5rem;">'
            f'<div style="min-width:36px;height:36px;border-radius:50%;background:#C9913A;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-family:Inter,sans-serif;font-size:15px;font-weight:700;color:#0a0a0a;flex-shrink:0;">{num}</div>'
            f'<div style="padding-top:4px;">'
            f'<div style="font-family:Inter,sans-serif;color:#fff;font-size:16px;font-weight:600;margin-bottom:6px;">{title}</div>'
            f'<div style="font-family:Inter,sans-serif;color:rgba(255,255,255,0.7);font-size:14px;font-weight:400;line-height:1.75;">{body}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("""
<div style="background:#111;border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:1.5rem 1.75rem;margin-top:0.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:13px;font-weight:400;color:rgba(255,255,255,0.45);line-height:2.2;">
        ♟ &nbsp;Aucune inscription requise &nbsp;·&nbsp; Vos données ne sont pas stockées<br>
        ♟ &nbsp;Fonctionne avec <b style="color:#C9913A;font-weight:600;">Chess.com</b> et <b style="color:#C9913A;font-weight:600;">Lichess</b><br>
        ♟ &nbsp;Analyse IA propulsée par <b style="color:#C9913A;font-weight:600;">Claude · Anthropic</b>
    </div>
</div>
""", unsafe_allow_html=True)
