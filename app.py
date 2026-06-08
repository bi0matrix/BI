"""
biomatrix BI-demo — versie 2.2
================================
Wijzigingen t.o.v. v2.1:
  - Data inladen via Parquet i.p.v. CSV (NDFF_gecombineerd_mini.parquet)
  - Kolommen Stadium en Gedrag verwijderd uit Browser-weergave (niet in mini-parquet)

Vereisten:
    pip install streamlit pandas plotly requests pyarrow

Starten:
    streamlit run app.py
"""

import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# ──────────────────────────────────────────────────────────────
# PAGINACONFIGURATIE
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="biomatrix BI-demo",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# GRAFIEK-ACHTERGRONDKLEUR  (donker groen-tint)
# ──────────────────────────────────────────────────────────────
PLOT_BG    = "#071a0f"
PAPER_BG   = "#071a0f"
GRID_COLOR = "#0f2d18"

# ──────────────────────────────────────────────────────────────
# GLOBALE CSS
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000000 0%, #021a09 60%, #000000 100%) !important;
    }
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    .logo-wrap {
        padding: 6px 20px 0px 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .logo-wrap img { max-width: 50%; height: auto; }
    .bm-slogan {
        color: #ffffff !important;
        font-size: 0.52rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        text-align: center;
        margin: 8px 0 2px 0;
        opacity: 0.55;
    }
    [data-testid="stSidebar"] .stRadio > label {
        display: none;
    }
    .nav-link {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 7px 8px;
        border-radius: 7px;
        text-decoration: none;
        font-size: 0.86rem;
        color: #ffffff !important;
        font-weight: 400;
        cursor: pointer;
        margin-bottom: 2px;
        transition: background 0.15s;
    }
    .nav-link:hover { background: rgba(255,255,255,0.06); }
    .nav-link.active {
        color: #00FF41 !important;
        font-weight: 700;
        background: rgba(0,255,65,0.07);
    }
    .nav-link svg { flex-shrink: 0; }
    .nav-link.active svg { stroke: #00FF41 !important; }
    [data-testid="stSidebar"] hr {
        border-color: #1a3320 !important;
        margin: 10px 0;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        background-color: #0a1f0f !important;
        border-color: #1a3320 !important;
        color: #e0e0e0 !important;
    }
    h1 { font-size:1.45rem !important; font-weight:700 !important;
         letter-spacing:-0.01em !important; margin:0.2rem 0 !important; }
    h2 { font-size:1.05rem !important; font-weight:600 !important;
         margin:1.2rem 0 0.3rem 0 !important; }
    h3 { font-size:0.92rem !important; font-weight:600 !important;
         margin:0.8rem 0 0 0 !important; }
    .kpi-card {
        background: #071a0f;
        border: 1px solid #0f3020;
        border-radius: 10px;
        padding: 18px 22px 14px 22px;
        text-align: center;
        min-height: 100px;
    }
    .kpi-label { font-size:0.72rem; text-transform:uppercase;
                 letter-spacing:0.08em; color:#558866; margin-bottom:6px; }
    .kpi-value { font-size:2.1rem; font-weight:800; color:#00FF41; line-height:1; }
    .kpi-sub   { font-size:0.70rem; color:#3a5c45; margin-top:4px; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00FF41 !important; font-weight:800 !important;
    }
    .bm-divider { border:none; border-top:1px solid #0f2d18; margin:1rem 0; }
    .soort-card {
        background: #071a0f;
        border: 1px solid #0f3020;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .soort-naam { font-size:1.1rem; font-weight:700; color:#00FF41; }
    .soort-latijn { font-size:0.82rem; color:#558866; font-style:italic; margin-top:2px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# AUTHENTICATIE
# ──────────────────────────────────────────────────────────────
def _check_login() -> bool:
    try:
        correct_pw = st.secrets["auth"]["password"]
    except Exception:
        correct_pw = "natuurlijk!"

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "login_error" not in st.session_state:
        st.session_state["login_error"] = False

    if st.session_state["authenticated"]:
        return True

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"]          { display: none !important; }
        [data-testid="stToolbar"]          { display: none !important; }
        [data-testid="stDecoration"]       { display: none !important; }
        [data-testid="stStatusWidget"]     { display: none !important; }
        header[data-testid="stHeader"]     { display: none !important; }
        #MainMenu                          { display: none !important; }
        footer                             { display: none !important; }
        [data-testid="stAppViewContainer"] { background: #050f08 !important; }
        [data-testid="block-container"]    { padding-top: 0 !important; }
        .login-wrap {
            max-width: 360px;
            margin: 60px auto 0 auto;
            background: #0a0a0a;
            border: 1px solid #0f3020;
            border-radius: 14px;
            padding: 36px 32px 12px 32px;
            text-align: center;
        }
        .login-logo-box {
            display: inline-block;
            margin-bottom: 20px;
        }
        .login-logo-box img {
            filter: drop-shadow(0 0 6px rgba(0,255,65,0.25));
        }
        .login-title {
            font-size: 0.95rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 16px;
            text-align: center;
        }
        .login-slogan {
            font-size: 0.55rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: #ffffff;
            opacity: 0.45;
            margin: 0 0 24px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    import base64, pathlib
    def _login_logo(pad: str, w: str = "140px") -> str:
        try:
            data = pathlib.Path(pad).read_bytes()
            b64  = base64.b64encode(data).decode()
            return (
                f'<div class="login-logo-box">'
                f'<img src="data:image/png;base64,{b64}" '
                f'style="width:{w};height:auto;display:block;">'
                f'</div>'
            )
        except Exception:
            return "<span style='color:#00FF41;font-weight:900;font-size:1.3rem;'>biomatrix</span>"

    st.markdown(
        f'<div class="login-wrap">'
        f'{_login_logo("BM_LOGO_TRANSP.png")}'
        f'<p class="login-title">Inloggen</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        wachtwoord = st.text_input(
            "Wachtwoord",
            type="password",
            placeholder="Voer wachtwoord in…",
            label_visibility="collapsed",
        )
        if st.button("→  Inloggen", use_container_width=True):
            if wachtwoord == correct_pw:
                st.session_state["authenticated"] = True
                st.session_state["login_error"] = False
                st.rerun()
            else:
                st.session_state["login_error"] = True

        if st.session_state["login_error"]:
            st.markdown(
                "<p style='color:#ff4444;font-size:0.78rem;margin-top:8px;'>"
                "Onjuist wachtwoord. Probeer opnieuw.</p>",
                unsafe_allow_html=True,
            )

    st.stop()


_check_login()

# ──────────────────────────────────────────────────────────────
# DATA INLADEN  ← v2.2: Parquet i.p.v. CSV
# ──────────────────────────────────────────────────────────────
@st.cache_data
def laad_data(pad: str) -> pd.DataFrame:
    df = pd.read_parquet(pad)
    df["periode_start"] = pd.to_datetime(
        df["Periode start"], format="%d-%m-%y %H:%M", errors="coerce"
    )
    df["Jaar"] = df["periode_start"].dt.year.astype("Int64")
    return df


df_raw = laad_data("NDFF_gecombineerd_mini.parquet")

UITGESLOTEN_JAREN = [2021, 2026]
df_raw = df_raw[~df_raw["Jaar"].isin(UITGESLOTEN_JAREN)].copy()


@st.cache_data
def laad_ndvi(pad: str) -> pd.DataFrame:
    raw = pd.read_csv(pad)
    ndvi_cols = [c for c in raw.columns if c.startswith("NDVI_")]
    long = raw[["label"] + ndvi_cols].melt(
        id_vars="label", var_name="ndvi_col", value_name="NDVI"
    )
    long["Jaar"] = long["ndvi_col"].str.extract(r"(\d{4})").astype(int)
    long = long.drop(columns="ndvi_col").rename(columns={"label": "Hoknummer"})
    long["NDVI"] = long["NDVI"].round(4)
    long = long[long["Jaar"].between(2022, 2025)]
    return long.sort_values(["Hoknummer", "Jaar"]).reset_index(drop=True)


df_ndvi_raw = laad_ndvi("ndff_unmerged_ndvi_2020_2026.csv")

# ──────────────────────────────────────────────────────────────
# AFBEELDING OPHALEN via Wikipedia
# ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def zoek_afbeelding(latijnse_naam: str) -> str | None:
    if not latijnse_naam or pd.isna(latijnse_naam):
        return None

    naam = str(latijnse_naam).strip()
    naam_encoded = naam.replace(" ", "_")
    headers = {"User-Agent": "biomatrix-BI-demo/2.2 (contact@biomatrix.nl)"}

    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{naam_encoded}",
            timeout=5, headers=headers,
        )
        if r.status_code == 200:
            thumb = r.json().get("thumbnail", {}).get("source")
            if thumb:
                return thumb
    except Exception:
        pass

    try:
        r2 = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "titles": naam_encoded,
                "prop": "pageimages", "format": "json",
                "pithumbsize": 400,
            },
            timeout=5, headers=headers,
        )
        if r2.status_code == 200:
            pages = r2.json().get("query", {}).get("pages", {})
            for page in pages.values():
                thumb = page.get("thumbnail", {}).get("source")
                if thumb:
                    return thumb
    except Exception:
        pass

    try:
        r3 = requests.get(
            "https://api.inaturalist.org/v1/taxa",
            params={"q": naam, "per_page": 1, "rank": "species"},
            timeout=5, headers=headers,
        )
        if r3.status_code == 200:
            results = r3.json().get("results", [])
            if results:
                foto = results[0].get("default_photo", {}).get("medium_url")
                if foto:
                    return foto
    except Exception:
        pass

    return None

# ──────────────────────────────────────────────────────────────
# ZIJBALK
# ──────────────────────────────────────────────────────────────
with st.sidebar:

    import base64, pathlib

    def _logo_html(pad: str, max_w: str = "50%") -> str:
        try:
            data = pathlib.Path(pad).read_bytes()
            b64  = base64.b64encode(data).decode()
            ext  = pathlib.Path(pad).suffix.lstrip(".")
            mime = "image/png" if ext in ("png", "") else f"image/{ext}"
            return (
                f'<div style="padding:8px 12px 0 12px;">'
                f'<img src="data:{mime};base64,{b64}" id="bm-logo" '
                f'style="max-width:{max_w};width:{max_w};height:auto;display:block;">'
                f'<p style="font-size:0.50rem;letter-spacing:0.14em;text-transform:uppercase;'
                f'color:#ffffff;opacity:0.50;margin:3px 0 0 0;padding:0;'
                f'text-align:left;">Numbers for nature</p>'
                f'</div>'
            )
        except Exception:
            return (
                "<div style='padding:8px 12px 0 12px;'>"
                "<span style='color:#00FF41;font-weight:900;font-size:1.2rem;"
                "letter-spacing:0.05em;'>biomatrix</span>"
                "<p style='font-size:0.50rem;color:#fff;opacity:0.50;"
                "margin:3px 0 0 1px;letter-spacing:0.16em;text-align:left;'>Numbers for nature</p></div>"
            )

    st.markdown(_logo_html("BM_LOGO_TRANSP.png", max_w="50%"), unsafe_allow_html=True)
    st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)

    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "Home"

    PAGINA_OPTIES = ["Home", "Browser", "Analyser", "Reports"]

    def _nav_icon(naam, kleur):
        icons = {
            "Home":     f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{kleur}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/><path d="M9 21V12h6v9"/></svg>',
            "Browser":  f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{kleur}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>',
            "Analyser": f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{kleur}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
            "Reports":  f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{kleur}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
        }
        return icons[naam]

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
            position: absolute !important;
            opacity: 0 !important;
            height: 36px !important;
            margin-top: -36px !important;
            cursor: pointer !important;
            z-index: 10 !important;
            padding: 0 !important;
            min-height: 0 !important;
        }
        [data-testid="stSidebar"] div:has(> [data-testid="stBaseButton-secondary"]) {
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p,
        [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] span {
            color: transparent !important;
            font-size: 0 !important;
        }
        [data-testid="stSidebar"] div.nav-active span {
            color: #00FF41 !important;
        }
        [data-testid="stSidebar"] div.nav-inactive span {
            color: #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.65rem;letter-spacing:0.12em;color:#2a5c38;"
        "margin:0 0 4px 4px;'>NAVIGATIE</p>",
        unsafe_allow_html=True,
    )

    for p in PAGINA_OPTIES:
        actief  = st.session_state["pagina"] == p
        kleur   = "#00FF41" if actief else "#ffffff"
        gewicht = "700" if actief else "400"
        bg      = "rgba(0,255,65,0.08)" if actief else "transparent"
        css_cls = "nav-active" if actief else "nav-inactive"
        icoon   = _nav_icon(p, kleur)
        st.markdown(
            f'<div class="{css_cls}" style="display:flex;align-items:center;gap:10px;'
            f'padding:7px 8px;border-radius:7px;background:{bg};margin-bottom:2px;'
            f'pointer-events:none;">'
            f'{icoon}'
            f'<span style="font-size:0.88rem;font-weight:{gewicht};">{p}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state["pagina"] = p
            st.rerun()

    pagina = st.session_state["pagina"]

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:0.65rem;letter-spacing:0.12em;color:#2a5c38;"
        "margin:0 0 4px 4px;'>LOCATIE</p>",
        unsafe_allow_html=True,
    )
    alle_hokken = sorted(df_raw["Hoknummer"].dropna().unique())
    gekozen_locatie = st.selectbox(
        label="locatie",
        options=["Alle locaties"] + alle_hokken,
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.62rem;color:#1a3320;text-align:center;margin-top:8px;'>"
        "biomatrix BI-demo v2.2</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:6px;'>", unsafe_allow_html=True)
    if st.button("↩  Uitloggen", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Globaal locatiefilter toepassen
df = df_raw.copy() if gekozen_locatie == "Alle locaties" \
    else df_raw[df_raw["Hoknummer"] == gekozen_locatie].copy()

ndvi_hokken = df["Hoknummer"].dropna().unique()
df_ndvi = df_ndvi_raw[df_ndvi_raw["Hoknummer"].isin(ndvi_hokken)].copy()

GROEN_PALET = ["#00FF41", "#32a852", "#007a2f"]

# ──────────────────────────────────────────────────────────────
# HULPFUNCTIES
# ──────────────────────────────────────────────────────────────
def kpi(label: str, waarde: str, sub: str = "") -> str:
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{waarde}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f"</div>"
    )

def groene_layout(fig, height: int = 300, **kwargs):
    fig.update_layout(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font_color="#cccccc",
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        margin=dict(t=14, b=10, l=0, r=0),
        height=height,
        **kwargs,
    )
    return fig


# ══════════════════════════════════════════════════════════════
# PAGINA 1 — HOME
# ══════════════════════════════════════════════════════════════
if pagina == "Home":

    st.markdown("## Biomatrix Biodiversiteit dashboard")
    st.markdown(
        f"<p style='color:#2a5c38;font-size:0.85rem;margin-top:-4px;'>"
        f"Biodiversiteits­monitoring · selectie: "
        f"<strong style='color:#00FF41'>{gekozen_locatie}</strong></p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(kpi("Totaal records", f"{len(df):,}", "waarnemingen"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("Actieve locaties", str(df["Hoknummer"].nunique()), "hoknummers"), unsafe_allow_html=True)
    with c3:
        ndvi_jaren_sorted = sorted(df_ndvi["Jaar"].unique())
        default_jaar = 2025 if 2025 in ndvi_jaren_sorted else ndvi_jaren_sorted[-1]
        default_index = ndvi_jaren_sorted.index(default_jaar)
        huidig_jaar = st.session_state.get("ndvi_jaar", default_jaar)
        ndvi_jaar_val = df_ndvi[df_ndvi["Jaar"] == huidig_jaar]["NDVI"].mean()
        ndvi_jaar_str = f"{ndvi_jaar_val:.3f}" if not pd.isna(ndvi_jaar_val) else "–"
        st.markdown(
            kpi(f"Gem. NDVI {huidig_jaar}", ndvi_jaar_str, "kies jaar hieronder"),
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <style>
            [data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"],
            div[data-testid="stRadio"] div[role="radiogroup"] {
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: 6px !important;
                padding: 4px 0 !important;
            }
            [data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] > label,
            div[data-testid="stRadio"] div[role="radiogroup"] > label {
                border: 1px solid #777777 !important;
                border-radius: 20px !important;
                padding: 3px 11px !important;
                font-size: 0.72rem !important;
                color: #bbbbbb !important;
                background: transparent !important;
                cursor: pointer !important;
                white-space: nowrap !important;
            }
            [data-testid="stMain"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked),
            div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
                border-color: #00FF41 !important;
                color: #00FF41 !important;
                font-weight: 700 !important;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) p,
            div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) span,
            div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) div {
                color: #00FF41 !important;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
                display: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        gekozen_ndvi_jaar = st.radio(
            "NDVI jaar",
            options=ndvi_jaren_sorted,
            index=default_index,
            horizontal=True,
            label_visibility="collapsed",
            key="ndvi_jaar",
        )

    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        if gekozen_locatie != "Alle locaties":
            st.markdown("#### Top 10 soorten")
            top10_soort = (
                df.groupby("Naam soort").size()
                .reset_index(name="Records")
                .sort_values("Records", ascending=False)
                .head(10)
            )
            fig_top10 = px.bar(
                top10_soort, x="Records", y="Naam soort",
                orientation="h",
                color="Records",
                color_continuous_scale=["#007a2f", "#00FF41"],
                text_auto=True,
            )
            fig_top10.update_layout(yaxis={"categoryorder": "total ascending"},
                                    coloraxis_showscale=False)
            groene_layout(fig_top10, height=280)
            st.plotly_chart(fig_top10, use_container_width=True)
        else:
            st.markdown("#### Records per locatie")
            hok_counts = df.groupby("Hoknummer").size().reset_index(name="Records").sort_values("Hoknummer")
            fig_hok = px.bar(hok_counts, x="Hoknummer", y="Records",
                             color="Hoknummer", color_discrete_sequence=GROEN_PALET, text_auto=True)
            fig_hok.update_traces(marker_line_width=0)
            groene_layout(fig_hok, height=280, showlegend=False)
            st.plotly_chart(fig_hok, use_container_width=True)

    with col_r:
        st.markdown("#### Top 8 soortgroepen")
        top_sg = (df.groupby("Soortgroep").size().reset_index(name="Records")
                  .sort_values("Records", ascending=False).head(8))
        fig_sg = px.bar(top_sg, x="Records", y="Soortgroep", orientation="h",
                        color="Records", color_continuous_scale=["#007a2f", "#00FF41"])
        fig_sg.update_layout(yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
        groene_layout(fig_sg, height=280)
        st.plotly_chart(fig_sg, use_container_width=True)

    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)
    st.markdown("#### Gemiddelde NDVI-score per jaar")
    st.caption("NDVI (Normalized Difference Vegetation Index) — hogere waarde = meer vegetatie. "
               "Gemiddelde over alle geselecteerde locaties.")

    ndvi_gem = (
        df_ndvi.groupby("Jaar")["NDVI"]
        .mean()
        .reset_index()
        .rename(columns={"NDVI": "Gem. NDVI"})
    )
    ndvi_gem["Gem. NDVI"] = ndvi_gem["Gem. NDVI"].round(3)

    fig_ndvi_home = px.bar(
        ndvi_gem, x="Jaar", y="Gem. NDVI",
        color_discrete_sequence=["#00FF41"],
        text="Gem. NDVI",
    )
    fig_ndvi_home.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside",
        textfont=dict(color="#cccccc", size=11),
        marker_line_width=0,
        hovertemplate="Jaar: %{x}<br>Gem. NDVI: %{y:.3f}<extra></extra>",
    )
    fig_ndvi_home.update_layout(
        plot_bgcolor="#3a3a3a",
        paper_bgcolor=PAPER_BG,
        font_color="#cccccc",
        height=240,
        hovermode="x unified",
        margin=dict(t=28, b=10, l=0, r=0),
        xaxis=dict(tickmode="linear", dtick=1, gridcolor="#555555", zerolinecolor="#555555"),
        yaxis=dict(range=[0, 1.05], gridcolor="#555555", zerolinecolor="#555555"),
    )
    st.plotly_chart(fig_ndvi_home, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PAGINA 2 — BROWSER
# ══════════════════════════════════════════════════════════════
elif pagina == "Browser":

    st.markdown("## Data Browser")
    st.markdown(
        f"<p style='color:#2a5c38;font-size:0.85rem;margin-top:-4px;'>"
        f"Ruwe data verkenner · biomatrix · selectie: "
        f"<strong style='color:#00FF41'>{gekozen_locatie}</strong></p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)

    bf1, bf2 = st.columns(2)

    with bf1:
        sg_opties = ["Alle soortgroepen"] + sorted(df["Soortgroep"].dropna().unique())
        gekozen_sg = st.selectbox("Soortgroep", options=sg_opties, key="browser_sg")
    df_sg_filtered = df.copy() if gekozen_sg == "Alle soortgroepen" \
        else df[df["Soortgroep"] == gekozen_sg].copy()

    with bf2:
        soort_df = (
            df_sg_filtered[["Naam soort", "Wetenschappelijke naam"]]
            .drop_duplicates()
            .sort_values("Naam soort")
        )
        def soort_label(row):
            lat = row["Wetenschappelijke naam"]
            if pd.notna(lat) and str(lat).strip():
                return f"{row['Naam soort']}  ({str(lat).strip()})"
            return row["Naam soort"]
        soort_df["label"] = soort_df.apply(soort_label, axis=1)
        soort_opties = ["Alle soorten"] + soort_df["label"].tolist()
        gekozen_soort_label = st.selectbox("Soort", options=soort_opties, key="browser_soort")

    if gekozen_soort_label == "Alle soorten":
        df_browser = df_sg_filtered.copy()
        gekozen_latijn = None
        gekozen_soort_naam = None
    else:
        gekozen_soort_naam = gekozen_soort_label.split("  (")[0]
        df_browser = df_sg_filtered[df_sg_filtered["Naam soort"] == gekozen_soort_naam].copy()
        rij = soort_df[soort_df["Naam soort"] == gekozen_soort_naam]
        gekozen_latijn = rij["Wetenschappelijke naam"].iloc[0] if not rij.empty else None

    if gekozen_soort_naam and gekozen_latijn:
        img_col, info_col = st.columns([1, 3])

        with img_col:
            with st.spinner("Afbeelding laden…"):
                img_url = zoek_afbeelding(str(gekozen_latijn))
            if img_url:
                st.markdown(
                    f"""
                    <div style="height:220px;border-radius:10px;overflow:hidden;
                                border:1px solid #0f3020;">
                      <img src="{img_url}"
                           alt="{gekozen_latijn}"
                           style="width:100%;height:100%;object-fit:cover;display:block;">
                    </div>
                    <p style="font-size:0.65rem;color:#2a5c38;
                               text-align:center;margin:4px 0 0 0;
                               font-style:italic;">{gekozen_latijn}</p>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div style='height:220px;background:#071a0f;border:1px solid #0f3020;"
                    "border-radius:10px;display:flex;align-items:center;justify-content:center;"
                    "color:#2a5c38;font-size:0.78rem;'>Geen afbeelding gevonden</div>",
                    unsafe_allow_html=True,
                )

        with info_col:
            records_soort = len(df_browser)
            jaren = sorted(df_browser["Jaar"].dropna().unique().astype(int))
            jaar_str = f"{min(jaren)} – {max(jaren)}" if jaren else "–"
            st.markdown(
                f"""
                <div class="soort-card" style="height:220px;box-sizing:border-box;">
                  <div class="soort-naam">{gekozen_soort_naam}</div>
                  <div class="soort-latijn">{gekozen_latijn}</div>
                  <hr style="border-color:#0f3020;margin:10px 0;">
                  <table style="font-size:0.82rem;color:#aaaaaa;width:100%;border-collapse:collapse;">
                    <tr><td style="color:#558866;padding-right:20px;">Records</td>
                        <td style="color:#00FF41;font-weight:700;">{records_soort:,}</td></tr>
                    <tr><td style="color:#558866;">Soortgroep</td>
                        <td>{gekozen_sg if gekozen_sg != "Alle soortgroepen" else "–"}</td></tr>
                    <tr><td style="color:#558866;">Periode</td>
                        <td>{jaar_str}</td></tr>
                    <tr><td style="color:#558866;">Locatie</td>
                        <td>{gekozen_locatie}</td></tr>
                  </table>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)

    st.markdown(
        f"<p style='font-size:0.8rem;color:#2a5c38;'>"
        f"{len(df_browser):,} records na filter</p>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Record count per soort")
    records_per_soort = (
        df_browser.groupby(["Soortgroep", "Naam soort", "Wetenschappelijke naam"])
        .size()
        .reset_index(name="Record count")
        .sort_values("Record count", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(records_per_soort, use_container_width=True, height=240, hide_index=True)

    # ── Ruwe data  ← v2.2: Stadium en Gedrag verwijderd (niet in mini-parquet)
    st.markdown("#### Ruwe data")
    weergave_kolommen = [
        "Hoknummer", "Soortgroep", "Naam soort", "Wetenschappelijke naam",
        "periode_start", "Jaar", "Aantal", "Bronhouder", "Protocol",
    ]
    weergave_kolommen = [k for k in weergave_kolommen if k in df_browser.columns]
    st.dataframe(df_browser[weergave_kolommen], use_container_width=True, height=360, hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGINA 3 — ANALYSER
# ══════════════════════════════════════════════════════════════
elif pagina == "Analyser":

    hdr_col, thumb_col = st.columns([4, 1])
    with hdr_col:
        st.markdown("## Analyser — Jaartrend per hoknummer")
        st.markdown(
            f"<p style='color:#2a5c38;font-size:0.85rem;margin-top:-4px;'>"
            f"Records per jaar per locatie · biomatrix · "
            f"selectie: <strong style='color:#00FF41'>{gekozen_locatie}</strong></p>",
            unsafe_allow_html=True,
        )
    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)

    df_jaar_basis = df.dropna(subset=["Jaar"]).copy()
    df_jaar_basis["Jaar"] = df_jaar_basis["Jaar"].astype(int)

    fcol1, fcol2 = st.columns(2)

    with fcol1:
        sg_opties_analyser = ["Alle soortgroepen"] + sorted(
            df_jaar_basis["Soortgroep"].dropna().unique()
        )
        gekozen_sg_analyser = st.selectbox(
            "Soortgroep", options=sg_opties_analyser, index=0, key="analyser_sg",
        )
        if gekozen_sg_analyser != "Alle soortgroepen":
            df_jaar_basis = df_jaar_basis[df_jaar_basis["Soortgroep"] == gekozen_sg_analyser]

    with fcol2:
        soort_opties_analyser = ["Alle soorten"] + sorted(
            df_jaar_basis["Naam soort"].dropna().unique()
        )
        gekozen_soort_analyser = st.selectbox(
            "Soort", options=soort_opties_analyser, index=0, key="analyser_soort",
        )
        if gekozen_soort_analyser != "Alle soorten":
            df_jaar_basis = df_jaar_basis[df_jaar_basis["Naam soort"] == gekozen_soort_analyser]

    if gekozen_soort_analyser != "Alle soorten":
        lat_rij = df_jaar_basis[df_jaar_basis["Naam soort"] == gekozen_soort_analyser][
            "Wetenschappelijke naam"
        ].dropna()
        lat_naam_analyser = lat_rij.iloc[0] if not lat_rij.empty else None
        with thumb_col:
            if lat_naam_analyser:
                with st.spinner(""):
                    img_url_a = zoek_afbeelding(str(lat_naam_analyser))
                if img_url_a:
                    st.markdown(
                        f"""
                        <div style="border:1px solid #0f3020;border-radius:8px;
                                    overflow:hidden;margin-top:4px;">
                          <img src="{img_url_a}"
                               style="width:100%;height:80px;object-fit:cover;display:block;">
                        </div>
                        <p style="font-size:0.6rem;color:#2a5c38;text-align:center;
                                  margin:2px 0;font-style:italic;">{lat_naam_analyser}</p>
                        """,
                        unsafe_allow_html=True,
                    )

    df_jaar = (
        df_jaar_basis
        .groupby(["Jaar", "Hoknummer"])
        .size()
        .reset_index(name="Aantal records")
        .sort_values("Jaar")
    )

    if df_jaar.empty:
        st.warning("Geen data beschikbaar voor de huidige selectie.")
    else:
        unieke_hokken = sorted(df_jaar["Hoknummer"].unique())
        kleur_map = {hok: GROEN_PALET[i % len(GROEN_PALET)] for i, hok in enumerate(unieke_hokken)}

        fig_lijn = px.line(
            df_jaar, x="Jaar", y="Aantal records",
            color="Hoknummer", markers=True,
            color_discrete_map=kleur_map,
        )
        fig_lijn.update_traces(line_width=2.5, marker_size=9)
        LICHT_GROEN_BG   = "#0e3320"
        LICHT_GROEN_GRID = "#1a5035"
        groene_layout(
            fig_lijn, height=420,
            hovermode="x unified",
            legend=dict(bgcolor=LICHT_GROEN_BG, bordercolor=LICHT_GROEN_GRID, borderwidth=1,
                        font=dict(color="#cccccc"), title=dict(font=dict(color="#00FF41"))),
        )
        fig_lijn.update_layout(
            plot_bgcolor=LICHT_GROEN_BG,
            xaxis=dict(tickmode="linear", dtick=1, gridcolor=LICHT_GROEN_GRID,
                       zerolinecolor=LICHT_GROEN_GRID, color="#cccccc"),
            yaxis=dict(gridcolor=LICHT_GROEN_GRID, zerolinecolor=LICHT_GROEN_GRID,
                       color="#cccccc"),
            font_color="#cccccc",
        )
        st.plotly_chart(fig_lijn, use_container_width=True)

        pivot_label = (
            f"#### Onderliggende data ({gekozen_soort_analyser})"
            if gekozen_soort_analyser != "Alle soorten"
            else "#### Onderliggende data"
        )
        st.markdown(pivot_label)
        pivot = (
            df_jaar.pivot(index="Jaar", columns="Hoknummer", values="Aantal records")
            .fillna(0).astype(int)
        )
        pivot["Totaal"] = pivot.sum(axis=1)

        def style_totaal(df_s):
            styles = pd.DataFrame("", index=df_s.index, columns=df_s.columns)
            if "Totaal" in df_s.columns:
                styles["Totaal"] = "color: #888888;"
            return styles

        st.dataframe(
            pivot.style.apply(style_totaal, axis=None),
            use_container_width=True,
        )

    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)
    st.markdown("#### NDVI per locatie per jaar")
    st.caption("Normalized Difference Vegetation Index (0–1). "
               "Elke lijn = één hoknummer. Hogere waarde = meer vegetatiebedekking.")

    if df_ndvi.empty:
        st.info("Geen NDVI-data beschikbaar voor de huidige locatieselectie.")
    else:
        unieke_hokken_ndvi = sorted(df_ndvi["Hoknummer"].unique())
        kleur_map_ndvi = {
            hok: GROEN_PALET[i % len(GROEN_PALET)]
            for i, hok in enumerate(unieke_hokken_ndvi)
        }

        fig_ndvi = px.line(
            df_ndvi, x="Jaar", y="NDVI",
            color="Hoknummer", markers=True,
            color_discrete_map=kleur_map_ndvi,
            labels={"NDVI": "NDVI-score", "Jaar": "Jaar"},
        )
        fig_ndvi.update_traces(line_width=2.5, marker_size=9)
        groene_layout(
            fig_ndvi, height=380,
            hovermode="x unified",
            legend=dict(bgcolor=PLOT_BG, bordercolor=GRID_COLOR, borderwidth=1,
                        font=dict(color="#cccccc"), title=dict(font=dict(color="#00FF41"))),
        )
        fig_ndvi.update_layout(
            xaxis=dict(tickmode="linear", dtick=1, gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
            yaxis=dict(range=[0, 1], gridcolor=GRID_COLOR, tickformat=".2f"),
        )
        st.plotly_chart(fig_ndvi, use_container_width=True)

        st.markdown("#### Records vs NDVI — gecombineerde weergave")
        st.caption("Lijndiagram: aantal records (links, per hoknummer) "
                   "en NDVI-score (rechts, gestippeld) op een gedeelde tijdlijn.")

        from plotly.subplots import make_subplots
        import plotly.graph_objects as go

        fig_combo = make_subplots(specs=[[{"secondary_y": True}]])

        for i, hok in enumerate(unieke_hokken_ndvi):
            kleur = GROEN_PALET[i % len(GROEN_PALET)]
            rec_data = df_jaar[df_jaar["Hoknummer"] == hok]
            fig_combo.add_trace(
                go.Scatter(
                    x=rec_data["Jaar"], y=rec_data["Aantal records"],
                    mode="lines+markers", name=f"{hok} records",
                    line=dict(color=kleur, width=2),
                    marker=dict(size=7),
                ),
                secondary_y=False,
            )
            ndvi_data = df_ndvi[df_ndvi["Hoknummer"] == hok]
            fig_combo.add_trace(
                go.Scatter(
                    x=ndvi_data["Jaar"], y=ndvi_data["NDVI"],
                    mode="lines+markers", name=f"{hok} NDVI",
                    line=dict(color=kleur, width=1.5, dash="dot"),
                    marker=dict(size=6, symbol="diamond"),
                    opacity=0.75,
                ),
                secondary_y=True,
            )

        fig_combo.update_layout(
            plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
            font_color="#cccccc", height=420,
            hovermode="x unified",
            margin=dict(t=14, b=10, l=0, r=0),
            legend=dict(bgcolor=PLOT_BG, bordercolor=GRID_COLOR, borderwidth=1,
                        font=dict(color="#cccccc")),
            xaxis=dict(tickmode="linear", dtick=1, gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        )
        fig_combo.update_yaxes(
            title_text="Aantal records", secondary_y=False,
            gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR,
        )
        fig_combo.update_yaxes(
            title_text="NDVI-score (0–1)", secondary_y=True,
            range=[0, 1], tickformat=".2f",
            gridcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_combo, use_container_width=True)

        st.markdown("#### NDVI-waarden per locatie per jaar")
        ndvi_pivot = (
            df_ndvi.pivot(index="Jaar", columns="Hoknummer", values="NDVI")
            .round(4)
        )
        ndvi_pivot.index.name = "Jaar"
        st.dataframe(ndvi_pivot, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# PAGINA 4 — REPORTS
# ══════════════════════════════════════════════════════════════
elif pagina == "Reports":

    st.markdown("## Rapportage")
    st.markdown(
        f"<p style='color:#2a5c38;font-size:0.85rem;margin-top:-4px;'>"
        f"Samenvatting &amp; trendanalyse · biomatrix · "
        f"selectie: <strong style='color:#00FF41'>{gekozen_locatie}</strong></p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)

    if df.empty:
        st.warning("Geen data beschikbaar voor de huidige selectie.")
        st.stop()

    trend = (
        df.dropna(subset=["Jaar"])
        .groupby("Jaar")
        .agg(
            Records=("Naam soort", "count"),
            Unieke_soorten=("Naam soort", "nunique"),
            Soortgroepen=("Soortgroep", "nunique"),
            Bronhouders=("Bronhouder", "nunique"),
        )
        .reset_index()
        .sort_values("Jaar")
        .rename(columns={"Unieke_soorten": "Unieke soorten"})
    )
    trend["Jaar"] = trend["Jaar"].astype(int)
    trend["Groei (%)"] = trend["Records"].pct_change().mul(100).round(1).fillna(0)

    st.markdown("#### Jaarlijkse trendtabel")
    st.dataframe(trend.set_index("Jaar"), use_container_width=True, hide_index=False)

    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)
    st.markdown("#### Recordvolume & soortenrijkdom per jaar")

    col_l, col_r = st.columns(2)

    with col_l:
        fig_vol = px.bar(trend, x="Jaar", y="Records",
                         color="Records", color_continuous_scale=["#007a2f", "#00FF41"],
                         text_auto=True)
        fig_vol.add_scatter(
            x=trend["Jaar"], y=trend["Records"], mode="lines+markers",
            name="Trend", line=dict(color="#ffffff", width=1.5, dash="dot"),
            marker=dict(size=6, color="#00FF41"),
        )
        groene_layout(fig_vol, height=300,
                      coloraxis_showscale=False, showlegend=False)
        fig_vol.update_layout(xaxis=dict(tickmode="linear", dtick=1, gridcolor=GRID_COLOR))
        st.plotly_chart(fig_vol, use_container_width=True)

    with col_r:
        fig_div = px.line(trend, x="Jaar", y="Unieke soorten",
                          markers=True, color_discrete_sequence=["#00FF41"])
        fig_div.update_traces(line_width=2.5, marker_size=9)
        groene_layout(fig_div, height=300)
        fig_div.update_layout(xaxis=dict(tickmode="linear", dtick=1, gridcolor=GRID_COLOR))
        st.plotly_chart(fig_div, use_container_width=True)

    st.markdown("<hr class='bm-divider'>", unsafe_allow_html=True)

    jaar_max_rec = int(trend.loc[trend["Records"].idxmax(), "Jaar"])
    jaar_max_div = int(trend.loc[trend["Unieke soorten"].idxmax(), "Jaar"])
    totaal        = int(trend["Records"].sum())
    max_soorten   = int(trend["Unieke soorten"].max())

    st.markdown("#### Conclusie")
    st.markdown(
        f"""
        <div style="background:#071a0f;border:1px solid #0f3020;border-radius:8px;
                    padding:16px 20px;font-size:0.86rem;line-height:1.7;color:#cccccc;">
        Het biomatrix-monitoringssysteem registreerde in totaal
        <strong style="color:#00FF41">{totaal:,} records</strong>
        voor de selectie <em>{gekozen_locatie}</em>.<br>
        Het piekjaar qua volume was <strong style="color:#00FF41">{jaar_max_rec}</strong>,
        terwijl de hoogste soortenrijkdom werd behaald in
        <strong style="color:#00FF41">{jaar_max_div}</strong>
        met <strong style="color:#00FF41">{max_soorten:,}</strong> unieke soorten.<br>
        Alle data is afkomstig uit het biomatrix-inzamelsysteem en omvat
        <strong style="color:#00FF41">{df["Bronhouder"].nunique()}</strong> actieve bronhouders.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='font-size:0.65rem;color:#1a3320;margin-top:16px;'>"
        f"biomatrix BI-demo v2.2 · data t/m "
        f"{df['periode_start'].max().date()}</p>",
        unsafe_allow_html=True,
    )
