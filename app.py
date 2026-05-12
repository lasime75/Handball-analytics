import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── CONFIG PAGE ────────────────────────────────────────────
st.set_page_config(
    page_title="Handball Analytics",
    page_icon="🤾",
    layout="wide"
)

# ── CSS CUSTOM ─────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1446; }
    .stApp { background-color: #0f1446; }
    h1, h2, h3, p, div { color: white !important; }
    .metric-card {
        background: #1a2460;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2a3480;
    }
    .metric-value { font-size: 2.5rem; font-weight: bold; color: #4A74F3 !important; }
    .metric-label { font-size: 0.9rem; color: #aaaaaa !important; }
</style>
""", unsafe_allow_html=True)

# ── DONNÉES ────────────────────────────────────────────────
EUROPEENS = {
    "Denmark","Norway","Sweden","Germany","France","Spain","Italy",
    "Slovenia","Hungary","Serbia","Czech Republic","Croatia","Portugal",
    "Latvia","Russia","Austria","Bosnia-Herzegovina","Poland","Switzerland",
    "Romania","Slovakia","Finland","Netherlands","Belgium","Greece",
    "Iceland","Faroe Islands","Montenegro","Macedonia","Ukraine",
    "Belarus","Estonia","Lithuania","Georgia","Azerbaijan","Turkey",
    "Albania","Kosovo","Bulgaria","Cyprus","Luxembourg","Ireland",
    "Great Britain","North Macedonia"
}

@st.cache_data
def load_data():
    df = pd.read_csv("handball_clean.csv")
    df["continent"] = df["nationalite"].apply(
        lambda x: "Europe" if x in EUROPEENS else "Hors-Europe"
    )
    return df

df = load_data()

# ── HEADER ─────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 30px 0 10px 0'>
    <h1 style='font-size:2.8rem; color:#4A74F3 !important;'>🤾 Handball Analytics</h1>
    <p style='color:#aaaaaa; font-size:1.1rem;'>
        Analyse de l'internationalisation du handball mondial
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── KPIs ───────────────────────────────────────────────────
total       = len(df)
nb_europe   = len(df[df["continent"] == "Europe"])
nb_hors     = len(df[df["continent"] == "Hors-Europe"])
nb_nations  = df["nationalite"].nunique()
nb_clubs    = df["club"].nunique()
pct_europe  = round(nb_europe / total * 100, 1)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{total:,}</div>
        <div class='metric-label'>Joueurs analysés</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{pct_europe}%</div>
        <div class='metric-label'>Joueurs européens</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{nb_hors}</div>
        <div class='metric-label'>Joueurs hors-Europe</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{nb_nations}</div>
        <div class='metric-label'>Nationalités</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{nb_clubs}</div>
        <div class='metric-label'>Clubs</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── VIZ ROW 1 ──────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.markdown("### 🌍 Europe vs Reste du Monde")
    fig_donut = go.Figure(go.Pie(
        labels=["🇪🇺 Europe", "🌍 Hors-Europe"],
        values=[nb_europe, nb_hors],
        hole=0.6,
        marker=dict(colors=["#4A74F3", "#FF6B6B"],
                    line=dict(color="#0f1446", width=3)),
        textfont=dict(size=14, color="white"),
        hovertemplate="%{label}<br>%{value} joueurs<br>%{percent}<extra></extra>"
    ))
    fig_donut.add_annotation(
        text=f"<b>{pct_europe}%</b><br>européens",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="white"),
        align="center"
    )
    fig_donut.update_layout(
        paper_bgcolor="#0f1446", plot_bgcolor="#0f1446",
        font=dict(color="white"),
        legend=dict(font=dict(color="white"), bgcolor="#1a2460"),
        margin=dict(t=20, b=20, l=20, r=20),
        height=350
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_right:
    st.markdown("### 🏆 Top 20 Nationalités")
    top20 = df["nationalite"].value_counts().head(20).reset_index()
    top20.columns = ["nationalite", "count"]
    top20["couleur"] = top20["nationalite"].apply(
        lambda x: "#4A74F3" if x in EUROPEENS else "#FF6B6B"
    )
    fig_bar = px.bar(
        top20, x="count", y="nationalite",
        orientation="h",
        color="couleur",
        color_discrete_map="identity",
        labels={"count": "Joueurs", "nationalite": ""}
    )
    fig_bar.update_layout(
        paper_bgcolor="#0f1446", plot_bgcolor="#0f1446",
        font=dict(color="white"),
        showlegend=False,
        yaxis=dict(autorange="reversed", tickfont=dict(color="white")),
        xaxis=dict(tickfont=dict(color="white")),
        margin=dict(t=20, b=20, l=20, r=20),
        height=400
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── VIZ ROW 2 ──────────────────────────────────────────────
st.markdown("### 🌐 Carte Mondiale des Joueurs")

map_data = df.groupby("nationalite").size().reset_index(name="joueurs")

fig_map = px.choropleth(
    map_data,
    locations="nationalite",
    locationmode="country names",
    color="joueurs",
    color_continuous_scale=[[0, "#1a2460"], [0.3, "#4A74F3"], [1, "#FF6B6B"]],
    labels={"joueurs": "Nb joueurs"},
    hover_name="nationalite",
    hover_data={"joueurs": True}
)
fig_map.update_layout(
    paper_bgcolor="#0f1446",
    geo=dict(
        bgcolor="#0f1446",
        showframe=False,
        showcoastlines=True,
        coastlinecolor="#333366",
        showland=True, landcolor="#1a2460",
        showocean=True, oceancolor="#0a0e2e",
        showlakes=False,
        projection_type="natural earth"
    ),
    coloraxis_colorbar=dict(
        tickfont=dict(color="white"),
        title=dict(text="Joueurs", font=dict(color="white"))
    ),
    margin=dict(t=10, b=10, l=0, r=0),
    height=450
)
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ── EXPLORER LES DONNÉES ───────────────────────────────────
st.markdown("### 🔍 Explorer les Joueurs")

col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    filtre_continent = st.selectbox(
        "Continent", ["Tous", "Europe", "Hors-Europe"]
    )
with col_f2:
    nations_dispo = ["Toutes"] + sorted(df["nationalite"].dropna().unique().tolist())
    filtre_nation = st.selectbox("Nationalité", nations_dispo)
with col_f3:
    postes_dispo = ["Tous"] + sorted(df["poste"].dropna().unique().tolist())
    filtre_poste = st.selectbox("Poste", postes_dispo)

df_filtered = df.copy()
if filtre_continent != "Tous":
    df_filtered = df_filtered[df_filtered["continent"] == filtre_continent]
if filtre_nation != "Toutes":
    df_filtered = df_filtered[df_filtered["nationalite"] == filtre_nation]
if filtre_poste != "Tous":
    df_filtered = df_filtered[df_filtered["poste"] == filtre_poste]

st.markdown(f"**{len(df_filtered)} joueurs trouvés**")

st.dataframe(
    df_filtered[["nom", "nationalite", "continent", "poste", "club", "statut"]]
    .reset_index(drop=True),
    use_container_width=True,
    height=400
)

# ── FOOTER ─────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#666; font-size:0.85rem; padding:10px'>
    🤾 Handball Analytics • Données : handball-base.com • 
    Projet data open-source
</div>
""", unsafe_allow_html=True)
