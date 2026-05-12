import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── CONFIG ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Handball Analytics",
    page_icon="🤾",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1446; }
    h1, h2, h3, p, label, div { color: white !important; }
    .metric-card {
        background: #1a2460;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2a3480;
        margin: 5px;
    }
    .metric-value { font-size: 2.2rem; font-weight: bold; color: #4A74F3 !important; }
    .metric-label { font-size: 0.85rem; color: #aaaaaa !important; margin-top: 5px; }
    .stSelectbox > div { background-color: #1a2460 !important; }
    .stDataFrame { background-color: #1a2460 !important; }
</style>
""", unsafe_allow_html=True)

# ── DATA ───────────────────────────────────────────────────
EUROPEENS = {
    "Denmark","Norway","Sweden","Germany","France","Spain","Italy",
    "Slovenia","Hungary","Serbia","Czech Republic","Croatia","Portugal",
    "Latvia","Russia","Austria","Bosnia-Herzegovina","Poland","Switzerland",
    "Romania","Slovakia","Finland","Netherlands","Belgium","Greece",
    "Iceland","Faroe Islands","Montenegro","Macedonia","Ukraine",
    "Belarus","Estonia","Lithuania","Georgia","Azerbaijan","Turkey",
    "Albania","Kosovo","Bulgaria","Cyprus","Luxembourg","Ireland",
    "Great Britain","North Macedonia","Moldova","Bosnia & Herzegovina"
}

@st.cache_data
def load_data():
    df = pd.read_csv("handball_clubs_players.csv")
    df["continent"] = df["nationalite"].apply(
        lambda x: "Europe" if x in EUROPEENS else "Hors-Europe"
    )
    df["est_etranger"] = df["nationalite"] != df["pays_club"]
    return df

df = load_data()

# ── HEADER ─────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding:30px 0 10px 0'>
    <h1 style='font-size:2.8rem; color:#4A74F3 !important;'>
        🤾 Handball Analytics
    </h1>
    <p style='color:#aaaaaa; font-size:1.1rem;'>
        Analyse de l'internationalisation du handball mondial
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── KPIs ───────────────────────────────────────────────────
total      = len(df)
nb_europe  = len(df[df["continent"] == "Europe"])
nb_hors    = len(df[df["continent"] == "Hors-Europe"])
nb_etrangers = df["est_etranger"].sum()
pct_europe = round(nb_europe / total * 100, 1)
pct_etrangers = round(nb_etrangers / total * 100, 1)

c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (f"{total:,}",         "Joueurs analysés"),
    (f"{pct_europe}%",     "Joueurs européens"),
    (f"{pct_etrangers}%",  "Joueurs expatriés"),
    (f"{df['nationalite'].nunique()}", "Nationalités"),
    (f"{df['ligue'].nunique()}",       "Ligues"),
]
for col, (val, label) in zip([c1,c2,c3,c4,c5], kpis):
    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{val}</div>
            <div class='metric-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── VIZ 1 : Donut + Bar ────────────────────────────────────
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### 🌍 Europe vs Reste du Monde")
    fig = go.Figure(go.Pie(
        labels=["🇪🇺 Europe", "🌍 Hors-Europe"],
        values=[nb_europe, nb_hors],
        hole=0.6,
        marker=dict(colors=["#4A74F3","#FF6B6B"],
                    line=dict(color="#0f1446", width=3)),
        textfont=dict(size=14, color="white"),
        hovertemplate="%{label}<br>%{value} joueurs<br>%{percent}<extra></extra>"
    ))
    fig.add_annotation(
        text=f"<b>{pct_europe}%</b><br>européens",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color="white"), align="center"
    )
    fig.update_layout(
        paper_bgcolor="#0f1446", plot_bgcolor="#0f1446",
        font=dict(color="white"),
        legend=dict(font=dict(color="white"), bgcolor="#1a2460"),
        margin=dict(t=20,b=20,l=20,r=20), height=320
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 🏆 Top 20 Nationalités")
    top20 = df["nationalite"].value_counts().head(20).reset_index()
    top20.columns = ["nationalite","count"]
    top20["couleur"] = top20["nationalite"].apply(
        lambda x: "#4A74F3" if x in EUROPEENS else "#FF6B6B"
    )
    fig2 = px.bar(top20, x="count", y="nationalite", orientation="h",
                  color="couleur", color_discrete_map="identity",
                  labels={"count":"Joueurs","nationalite":""})
    fig2.update_layout(
        paper_bgcolor="#0f1446", plot_bgcolor="#0f1446",
        font=dict(color="white"), showlegend=False,
        yaxis=dict(autorange="reversed", tickfont=dict(color="white")),
        xaxis=dict(tickfont=dict(color="white")),
        margin=dict(t=20,b=20,l=20,r=20), height=420
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── VIZ 2 : % Étrangers par championnat ───────────────────
st.markdown("### 🏅 % de Joueurs Étrangers par Championnat")

ligue_stats = df.groupby(["ligue","pays_club"]).agg(
    total=("nom","count"),
    etrangers=("est_etranger","sum")
).reset_index()
ligue_stats["pct"] = (ligue_stats["etrangers"] / ligue_stats["total"] * 100).round(1)
ligue_stats = ligue_stats[ligue_stats["total"] >= 15].sort_values("pct", ascending=False).head(25)

fig3 = px.bar(
    ligue_stats, x="pct", y="ligue", orientation="h",
    color="pct",
    color_continuous_scale=[[0,"#1a2460"],[0.5,"#4A74F3"],[1,"#FF6B6B"]],
    text="pct",
    labels={"pct":"% étrangers","ligue":""}
)
fig3.update_traces(texttemplate="%{text}%", textposition="outside",
                   textfont=dict(color="white"))
fig3.update_layout(
    paper_bgcolor="#0f1446", plot_bgcolor="#0f1446",
    font=dict(color="white"),
    yaxis=dict(autorange="reversed", tickfont=dict(color="white", size=10)),
    xaxis=dict(tickfont=dict(color="white")),
    coloraxis_showscale=False,
    margin=dict(t=20,b=20,l=20,r=20), height=600
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── VIZ 3 : Carte mondiale ─────────────────────────────────
st.markdown("### 🗺 Carte Mondiale des Joueurs")

map_data = df.groupby("nationalite").size().reset_index(name="joueurs")
fig4 = px.choropleth(
    map_data, locations="nationalite", locationmode="country names",
    color="joueurs",
    color_continuous_scale=[[0,"#1a2460"],[0.3,"#4A74F3"],[1,"#FF6B6B"]],
    labels={"joueurs":"Nb joueurs"},
    hover_name="nationalite"
)
fig4.update_layout(
    paper_bgcolor="#0f1446",
    geo=dict(bgcolor="#0f1446", showframe=False,
             showland=True, landcolor="#1a2460",
             showocean=True, oceancolor="#0a0e2e",
             coastlinecolor="#333366",
             projection_type="natural earth"),
    coloraxis_colorbar=dict(tickfont=dict(color="white"),
                            title=dict(text="Joueurs",font=dict(color="white"))),
    margin=dict(t=10,b=10,l=0,r=0), height=420
)
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── VIZ 4 : Flux nationalité → pays du club ───────────────
st.markdown("### 🔄 Flux des Joueurs Expatriés")

flux = df[df["est_etranger"]].groupby(
    ["nationalite","pays_club"]
).size().reset_index(name="count")
flux = flux[flux["count"] >= 3].sort_values("count", ascending=False).head(30)

fig5 = px.bar(flux, x="count", y="nationalite",
              color="pays_club", orientation="h",
              labels={"count":"Joueurs","nationalite":"Nationalité","pays_club":"Pays du club"},
              color_discrete_sequence=px.colors.qualitative.Set3)
fig5.update_layout(
    paper_bgcolor="#0f1446", plot_bgcolor="#0f1446",
    font=dict(color="white"),
    yaxis=dict(autorange="reversed", tickfont=dict(color="white")),
    xaxis=dict(tickfont=dict(color="white")),
    legend=dict(font=dict(color="white"), bgcolor="#1a2460"),
    margin=dict(t=20,b=20,l=20,r=20), height=500
)
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ── EXPLORER ───────────────────────────────────────────────
st.markdown("### 🔍 Explorer les Joueurs")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)
with col_f1:
    f_continent = st.selectbox("Continent", ["Tous","Europe","Hors-Europe"])
with col_f2:
    pays_list = ["Tous"] + sorted(df["pays_club"].dropna().unique().tolist())
    f_pays = st.selectbox("Pays du championnat", pays_list)
with col_f3:
    nat_list = ["Toutes"] + sorted(df["nationalite"].dropna().unique().tolist())
    f_nat = st.selectbox("Nationalité", nat_list)
with col_f4:
    f_etranger = st.selectbox("Statut", ["Tous","Expatriés uniquement","Locaux uniquement"])

df_f = df.copy()
if f_continent != "Tous":
    df_f = df_f[df_f["continent"] == f_continent]
if f_pays != "Tous":
    df_f = df_f[df_f["pays_club"] == f_pays]
if f_nat != "Toutes":
    df_f = df_f[df_f["nationalite"] == f_nat]
if f_etranger == "Expatriés uniquement":
    df_f = df_f[df_f["est_etranger"] == True]
elif f_etranger == "Locaux uniquement":
    df_f = df_f[df_f["est_etranger"] == False]

st.markdown(f"**{len(df_f)} joueurs trouvés**")
st.dataframe(
    df_f[["nom","nationalite","continent","poste","club","ligue","pays_club","est_etranger"]]
    .rename(columns={"est_etranger":"expatrié"})
    .reset_index(drop=True),
    use_container_width=True, height=400
)

# ── FOOTER ─────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#666; font-size:0.85rem; padding:10px'>
    🤾 Handball Analytics • Données : handball-base.com •
    Projet data open-source
</div>
""", unsafe_allow_html=True)
