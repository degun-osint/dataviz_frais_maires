"""
Dataviz - Frais de représentation des maires
Analyse des dépenses par commune à l'approche des municipales 2026
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import numpy as np


def fmt_fr(num, decimals=0):
    """Formate un nombre au format français: 1 234 567,89"""
    if decimals > 0:
        formatted = f"{num:,.{decimals}f}"
    else:
        formatted = f"{num:,.0f}"
    return formatted.replace(',', ' ').replace('.', ',')


# Configuration de la page
st.set_page_config(
    page_title="Frais de représentation des maires",
    page_icon="🏛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS flat & minimaliste
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/iconoir-icons/iconoir@main/css/iconoir.css">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', -apple-system, sans-serif;
        background: #fafafa;
    }

    /* Header clean */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #111;
        text-align: center;
        margin-bottom: 0.25rem;
    }

    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* Cards métriques flat */
    [data-testid="stMetric"] {
        background: #fff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e5e5;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        color: #111;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        font-weight: 500;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }

    /* Tabs flat */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f0f0f0;
        padding: 4px;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        color: #666;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: #111 !important;
        color: #fff !important;
    }

    /* Icônes dans les tabs via CSS */
    .stTabs [data-baseweb="tab"]:nth-child(1)::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 6px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' fill='none' stroke='currentColor' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 9.5 12 4l7 5.5V20H5V9.5Z'/%3E%3Cpath d='m5 9.5 7-5.5 7 5.5M12 20v-7h4v7'/%3E%3C/svg%3E") center/contain no-repeat;
        vertical-align: middle;
        opacity: 0.6;
    }
    .stTabs [data-baseweb="tab"]:nth-child(2)::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 6px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' fill='none' stroke='currentColor' stroke-width='1.5'%3E%3Cpath d='M3 12h18M3 6h18M3 18h18'/%3E%3C/svg%3E") center/contain no-repeat;
        vertical-align: middle;
        opacity: 0.6;
    }
    .stTabs [data-baseweb="tab"]:nth-child(3)::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 6px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' fill='none' stroke='currentColor' stroke-width='1.5'%3E%3Cpath d='M3 21h18M3 21V9l4-1 4 3 4-4 4 2v12'/%3E%3C/svg%3E") center/contain no-repeat;
        vertical-align: middle;
        opacity: 0.6;
    }
    .stTabs [data-baseweb="tab"]:nth-child(4)::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 6px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' fill='none' stroke='currentColor' stroke-width='1.5'%3E%3Cpath d='M6 9h2v12H6z M10 3h4v18h-4z M16 7h2v14h-2z'/%3E%3C/svg%3E") center/contain no-repeat;
        vertical-align: middle;
        opacity: 0.6;
    }
    .stTabs [data-baseweb="tab"]:nth-child(5)::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 6px;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' fill='none' stroke='currentColor' stroke-width='1.5'%3E%3Cpath d='M19 11V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2h4'/%3E%3Cpath d='M14 15h6v6h-6z'/%3E%3Cpath d='M9 9h6M9 13h3'/%3E%3C/svg%3E") center/contain no-repeat;
        vertical-align: middle;
        opacity: 0.6;
    }
    .stTabs [aria-selected="true"]::before {
        filter: invert(1);
        opacity: 1;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #fff;
        border-right: 1px solid #e5e5e5;
    }

    /* Boutons flat */
    .stDownloadButton button {
        background: #111;
        color: #fff;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
    }

    .stDownloadButton button:hover {
        background: #333;
    }

    /* Tables */
    .stDataFrame {
        border-radius: 8px;
        border: 1px solid #e5e5e5;
        overflow: hidden;
    }

    /* Radio & inputs */
    .stRadio > div {
        background: #fff;
        padding: 0.75rem;
        border-radius: 6px;
        border: 1px solid #e5e5e5;
    }

    /* Sources footer */
    .sources-container {
        background: #fff;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 2rem;
        border: 1px solid #e5e5e5;
    }

    .sources-title {
        color: #111;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .source-item {
        background: #fafafa;
        padding: 0.6rem 0.8rem;
        border-radius: 6px;
        margin-bottom: 0.4rem;
        border-left: 2px solid #ddd;
    }

    .source-item:hover {
        border-left-color: #111;
    }

    .source-title {
        font-weight: 500;
        color: #333;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .source-desc {
        font-size: 0.75rem;
        color: #888;
        margin-top: 0.2rem;
    }

    .sources-container a {
        color: #666;
        text-decoration: none;
        font-family: monospace;
        font-size: 0.7rem;
    }

    .sources-container a:hover {
        color: #111;
    }

    hr {
        border: none;
        height: 1px;
        background: #e5e5e5;
        margin: 1.5rem 0;
    }

    /* Iconoir inline */
    .icon {
        width: 18px;
        height: 18px;
        display: inline-block;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Charge et prépare les données"""
    df = pd.read_csv(
        "data/donnees_analyse.csv",
        dtype={'CODE_COMMUNE': str, 'DEPARTEMENT': str},
        na_values=['#N/D', '#N/A', 'N/A', '', ' ']
    )

    # Nettoyage des colonnes numériques (virgule -> point)
    numeric_cols = ['FRAIS_REPRESENTATION', 'EUR_PAR_HAB', 'TOTAL_CHARGES',
                    'CHARGES_PERSONNEL', 'ACHATS_SERVICES', 'CHARGES_FINANCIERES',
                    'CHARGES_EXCEPT', 'AUTRES_CHARGES_GESTION', 'RATIO_FRAIS_REP']
    for col in numeric_cols:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Nettoyage population
    df['POP_2022'] = pd.to_numeric(
        df['POP_2022'].astype(str).str.replace(' ', '').str.replace(',', '.'),
        errors='coerce'
    ).fillna(0).astype(int)

    # Nettoyage coordonnées (convertir en numérique, remplacer invalides par NaN)
    for col in ['LATITUDE', 'LONGITUDE']:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(',', '.'),
            errors='coerce'
        )

    # Nettoyage couleur politique
    df['COUL_POL'] = df['COUL_POL'].fillna('Non classé')
    df['COUL_POL'] = df['COUL_POL'].replace('', 'Non classé')
    df['COUL_POL'] = df['COUL_POL'].replace('#N/D', 'Non classé')

    # Catégories de population
    df['CATEGORIE_POP'] = pd.cut(
        df['POP_2022'],
        bins=[0, 500, 2000, 10000, 50000, float('inf')],
        labels=['< 500 hab', '500-2000', '2000-10000', '10000-50000', '> 50000']
    )

    return df


def create_map(df_filtered, color_by='EUR_PAR_HAB'):
    """Crée la carte Folium interactive"""

    # Centre de la France
    m = folium.Map(
        location=[46.603354, 1.888334],
        zoom_start=6,
        tiles='cartodbpositron'
    )

    # Taille fixe des marqueurs
    MARKER_RADIUS = 6

    # Palette de couleurs selon le critère
    if color_by in ['EUR_PAR_HAB', 'FRAIS_REPRESENTATION', 'RATIO_FRAIS_REP']:
        # Échelle de couleurs pour la valeur choisie
        if color_by == 'RATIO_FRAIS_REP':
            # Pour le ratio, on exclut les 0 du calcul du percentile
            max_val = df_filtered[df_filtered[color_by] > 0][color_by].quantile(0.95)
        else:
            max_val = df_filtered[color_by].quantile(0.95)  # Cap à 95e percentile

        for _, row in df_filtered.iterrows():
            # Vérifier que les coordonnées sont valides (numériques et dans les bornes)
            try:
                lat = float(row['LATITUDE'])
                lon = float(row['LONGITUDE'])
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue
            except (ValueError, TypeError):
                continue

            # Couleur selon la valeur (vert -> orange -> rouge)
            ratio = min(row[color_by] / max_val, 1) if max_val > 0 else 0
            if ratio < 0.33:
                color = '#2ecc71'  # Vert
            elif ratio < 0.66:
                color = '#f39c12'  # Orange
            else:
                color = '#e74c3c'  # Rouge

            # Tooltip selon le mode
            if color_by == 'EUR_PAR_HAB':
                tooltip_text = f"{row['NOM_COMMUNE']}: {fmt_fr(row['EUR_PAR_HAB'], 2)} €/hab"
            elif color_by == 'RATIO_FRAIS_REP':
                tooltip_text = f"{row['NOM_COMMUNE']}: {fmt_fr(row['RATIO_FRAIS_REP'], 2)} %"
            else:
                tooltip_text = f"{row['NOM_COMMUNE']}: {fmt_fr(row['FRAIS_REPRESENTATION'])} €"

            popup_html = f"""
            <b>{row['NOM_COMMUNE']}</b><br>
            Département: {row['DEPARTEMENT']}<br>
            Population: {fmt_fr(row['POP_2022'])}<br>
            Frais: {fmt_fr(row['FRAIS_REPRESENTATION'], 2)} €<br>
            EUR/hab: {fmt_fr(row['EUR_PAR_HAB'], 2)} €<br>
            Ratio: {fmt_fr(row.get('RATIO_FRAIS_REP', 0), 2)} %<br>
            Politique: {row['COUL_POL']}
            """

            folium.CircleMarker(
                location=[lat, lon],
                radius=MARKER_RADIUS,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=tooltip_text
            ).add_to(m)

    else:  # Couleur politique
        color_map = {
            'Gauche': '#e74c3c',
            'Droite': '#3498db',
            'Centre': '#f39c12',
            'Extrême droite': '#1a1a2e',
            'Courants politiques divers': '#9b59b6',
            'Non classé': '#95a5a6',
                    }

        for _, row in df_filtered.iterrows():
            # Vérifier que les coordonnées sont valides
            try:
                lat = float(row['LATITUDE'])
                lon = float(row['LONGITUDE'])
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    continue
            except (ValueError, TypeError):
                continue

            color = color_map.get(row['COUL_POL'], '#95a5a6')

            popup_html = f"""
            <b>{row['NOM_COMMUNE']}</b><br>
            Département: {row['DEPARTEMENT']}<br>
            Population: {fmt_fr(row['POP_2022'])}<br>
            Frais: {fmt_fr(row['FRAIS_REPRESENTATION'], 2)} €<br>
            EUR/hab: {fmt_fr(row['EUR_PAR_HAB'], 2)} €<br>
            <b>Politique: {row['COUL_POL']}</b>
            """

            folium.CircleMarker(
                location=[lat, lon],
                radius=MARKER_RADIUS,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{row['NOM_COMMUNE']}: {row['COUL_POL']}"
            ).add_to(m)

    return m


def main():
    # Header
    st.markdown('<p class="main-header"><i class="iconoir-city"></i> Frais de représentation des maires</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyse des dépenses en frais de representation par commune en ayant déclaré sur leur budget 2024</p>', unsafe_allow_html=True)

    # Chargement des données
    df = load_data()

    # Sidebar - Filtres
    st.sidebar.header("Filtres")

    # Filtre département
    departements = ['Tous'] + sorted(df['DEPARTEMENT'].unique().tolist())
    dept_selection = st.sidebar.selectbox("Département", departements)

    # Filtre population
    pop_min, pop_max = st.sidebar.slider(
        "Population",
        min_value=0,
        max_value=int(df['POP_2022'].max()),
        value=(0, int(df['POP_2022'].max())),
        step=100
    )

    # Filtre EUR/hab
    eur_min, eur_max = st.sidebar.slider(
        "EUR par habitant",
        min_value=0.0,
        max_value=float(df['EUR_PAR_HAB'].max()),
        value=(0.0, float(df['EUR_PAR_HAB'].max())),
        step=0.1
    )

    # Filtre couleur politique
    couleurs_pol = ['Toutes'] + sorted(df['COUL_POL'].unique().tolist())
    coul_selection = st.sidebar.multiselect(
        "Couleur politique",
        options=df['COUL_POL'].unique().tolist(),
        default=df['COUL_POL'].unique().tolist()
    )

    # Application des filtres
    df_filtered = df.copy()

    if dept_selection != 'Tous':
        df_filtered = df_filtered[df_filtered['DEPARTEMENT'] == dept_selection]

    df_filtered = df_filtered[
        (df_filtered['POP_2022'] >= pop_min) &
        (df_filtered['POP_2022'] <= pop_max) &
        (df_filtered['EUR_PAR_HAB'] >= eur_min) &
        (df_filtered['EUR_PAR_HAB'] <= eur_max) &
        (df_filtered['COUL_POL'].isin(coul_selection))
    ]

    # Métriques clés
    st.markdown('<h3><i class="iconoir-stats-report"></i> Chiffres clés</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Communes", fmt_fr(len(df_filtered)))
    with col2:
        st.metric("Total frais", f"{fmt_fr(df_filtered['FRAIS_REPRESENTATION'].sum())} €")
    with col3:
        st.metric("Moyenne EUR/hab", f"{fmt_fr(df_filtered['EUR_PAR_HAB'].mean(), 2)} €")
    with col4:
        st.metric("Médiane EUR/hab", f"{fmt_fr(df_filtered['EUR_PAR_HAB'].median(), 2)} €")
    with col5:
        st.metric("Max EUR/hab", f"{fmt_fr(df_filtered['EUR_PAR_HAB'].max(), 2)} €")

    st.markdown("---")

    # Onglets principaux
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Carte", "Tableau", "Analyses", "Palmarès", "Budget"])

    # TAB 1 - CARTE
    with tab1:
        st.markdown('<h3><i class="iconoir-map"></i> Carte interactive</h3>', unsafe_allow_html=True)

        col_map1, col_map2 = st.columns([3, 1])

        with col_map2:
            color_option = st.radio(
                "Colorier par :",
                ['EUR/habitant', 'Frais totaux', 'Ratio budget', 'Couleur politique'],
                index=0
            )

            if color_option == 'EUR/habitant':
                max_val = df_filtered['EUR_PAR_HAB'].quantile(0.95)
                seuil_vert = max_val * 0.33
                seuil_orange = max_val * 0.66
                st.markdown(f"""
**Légende**

<span style="color:#2ecc71">●</span> < {fmt_fr(seuil_vert, 2)} €/hab<br>
<span style="color:#f39c12">●</span> {fmt_fr(seuil_vert, 2)} – {fmt_fr(seuil_orange, 2)} €/hab<br>
<span style="color:#e74c3c">●</span> > {fmt_fr(seuil_orange, 2)} €/hab

*95e percentile*
                """, unsafe_allow_html=True)
            elif color_option == 'Frais totaux':
                max_val = df_filtered['FRAIS_REPRESENTATION'].quantile(0.95)
                seuil_vert = max_val * 0.33
                seuil_orange = max_val * 0.66
                st.markdown(f"""
**Légende**

<span style="color:#2ecc71">●</span> < {fmt_fr(seuil_vert)} €<br>
<span style="color:#f39c12">●</span> {fmt_fr(seuil_vert)} – {fmt_fr(seuil_orange)} €<br>
<span style="color:#e74c3c">●</span> > {fmt_fr(seuil_orange)} €

*95e percentile*
                """, unsafe_allow_html=True)
            elif color_option == 'Ratio budget':
                max_val = df_filtered[df_filtered['RATIO_FRAIS_REP'] > 0]['RATIO_FRAIS_REP'].quantile(0.95)
                seuil_vert = max_val * 0.33
                seuil_orange = max_val * 0.66
                st.markdown(f"""
**Légende**

<span style="color:#2ecc71">●</span> < {fmt_fr(seuil_vert, 2)} %<br>
<span style="color:#f39c12">●</span> {fmt_fr(seuil_vert, 2)} – {fmt_fr(seuil_orange, 2)} %<br>
<span style="color:#e74c3c">●</span> > {fmt_fr(seuil_orange, 2)} %

*Ratio frais rep. / charges totales*
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
**Légende**

<span style="color:#e74c3c">●</span> Gauche<br>
<span style="color:#3498db">●</span> Droite<br>
<span style="color:#f39c12">●</span> Centre<br>
<span style="color:#1a1a2e">●</span> Extrême droite<br>
<span style="color:#9b59b6">●</span> Divers<br>
<span style="color:#95a5a6">●</span> Non classé
                """, unsafe_allow_html=True)

        with col_map1:
            if color_option == 'EUR/habitant':
                color_by = 'EUR_PAR_HAB'
            elif color_option == 'Frais totaux':
                color_by = 'FRAIS_REPRESENTATION'
            elif color_option == 'Ratio budget':
                color_by = 'RATIO_FRAIS_REP'
            else:
                color_by = 'COUL_POL'
            m = create_map(df_filtered, color_by=color_by)
            st_folium(m, width=800, height=500)

    # TAB 2 - TABLEAU
    with tab2:
        st.markdown('<h3><i class="iconoir-table-rows"></i> Données détaillées</h3>', unsafe_allow_html=True)

        # Filtres du tableau
        with st.expander("🔍 Filtres avancés", expanded=False):
            col_f1, col_f2 = st.columns(2)

            with col_f1:
                # Recherche par nom
                search_commune = st.text_input(
                    "Rechercher une commune",
                    placeholder="Tapez un nom de commune...",
                    key="search_commune"
                )

                # Filtre EUR/hab
                eur_range = st.slider(
                    "EUR par habitant",
                    min_value=0.0,
                    max_value=float(df_filtered['EUR_PAR_HAB'].max()),
                    value=(0.0, float(df_filtered['EUR_PAR_HAB'].max())),
                    step=0.1,
                    key="table_eur_range"
                )

            with col_f2:
                # Filtre Frais totaux
                frais_range = st.slider(
                    "Frais totaux (€)",
                    min_value=0.0,
                    max_value=float(df_filtered['FRAIS_REPRESENTATION'].max()),
                    value=(0.0, float(df_filtered['FRAIS_REPRESENTATION'].max())),
                    step=100.0,
                    key="table_frais_range"
                )

                # Filtre Ratio si disponible
                if 'RATIO_FRAIS_REP' in df_filtered.columns:
                    ratio_range = st.slider(
                        "Ratio budget (%)",
                        min_value=0.0,
                        max_value=float(df_filtered['RATIO_FRAIS_REP'].max()),
                        value=(0.0, float(df_filtered['RATIO_FRAIS_REP'].max())),
                        step=0.01,
                        key="table_ratio_range"
                    )
                else:
                    ratio_range = None

        # Appliquer les filtres du tableau
        df_table = df_filtered.copy()

        if search_commune:
            df_table = df_table[df_table['NOM_COMMUNE'].str.contains(search_commune, case=False, na=False)]

        df_table = df_table[
            (df_table['EUR_PAR_HAB'] >= eur_range[0]) &
            (df_table['EUR_PAR_HAB'] <= eur_range[1]) &
            (df_table['FRAIS_REPRESENTATION'] >= frais_range[0]) &
            (df_table['FRAIS_REPRESENTATION'] <= frais_range[1])
        ]

        if ratio_range is not None:
            df_table = df_table[
                (df_table['RATIO_FRAIS_REP'] >= ratio_range[0]) &
                (df_table['RATIO_FRAIS_REP'] <= ratio_range[1])
            ]

        st.caption(f"{len(df_table)} communes après filtres")

        # Option pour afficher les colonnes budget
        show_budget = st.checkbox("Afficher les données budgétaires", value=False)

        # Colonnes à afficher
        columns_display = ['CODE_COMMUNE', 'NOM_COMMUNE', 'DEPARTEMENT', 'POP_2022',
                          'FRAIS_REPRESENTATION', 'EUR_PAR_HAB', 'COUL_POL']

        if show_budget and 'TOTAL_CHARGES' in df_table.columns:
            columns_display.extend(['TOTAL_CHARGES', 'CHARGES_PERSONNEL', 'RATIO_FRAIS_REP'])

        # Options de tri
        sort_options = ['EUR_PAR_HAB', 'FRAIS_REPRESENTATION', 'POP_2022', 'NOM_COMMUNE']
        if show_budget and 'TOTAL_CHARGES' in df_table.columns:
            sort_options.extend(['TOTAL_CHARGES', 'CHARGES_PERSONNEL', 'RATIO_FRAIS_REP'])

        sort_col = st.selectbox(
            "Trier par :",
            options=sort_options,
            format_func=lambda x: {
                'EUR_PAR_HAB': 'EUR par habitant',
                'FRAIS_REPRESENTATION': 'Frais totaux',
                'POP_2022': 'Population',
                'NOM_COMMUNE': 'Nom commune',
                'TOTAL_CHARGES': 'Charges totales',
                'CHARGES_PERSONNEL': 'Charges personnel',
                'RATIO_FRAIS_REP': 'Ratio frais rep.'
            }.get(x, x)
        )

        sort_order = st.checkbox("Ordre décroissant", value=True)

        df_display = df_table[columns_display].sort_values(
            by=sort_col,
            ascending=not sort_order
        )

        # Renommer les colonnes pour l'affichage
        col_names = ['INSEE', 'Commune', 'Dépt', 'Population', 'Frais (€)', 'EUR/hab', 'Politique']
        if show_budget and 'TOTAL_CHARGES' in df_table.columns:
            col_names.extend(['Charges tot. (€)', 'Personnel (€)', 'Ratio (%)'])
        df_display.columns = col_names

        # Formatage français des colonnes numériques
        df_display['Population'] = df_display['Population'].apply(lambda x: fmt_fr(x))
        df_display['Frais (€)'] = df_display['Frais (€)'].apply(lambda x: fmt_fr(x, 2))
        df_display['EUR/hab'] = df_display['EUR/hab'].apply(lambda x: fmt_fr(x, 2))

        if show_budget and 'Charges tot. (€)' in df_display.columns:
            df_display['Charges tot. (€)'] = df_display['Charges tot. (€)'].apply(lambda x: fmt_fr(x))
            df_display['Personnel (€)'] = df_display['Personnel (€)'].apply(lambda x: fmt_fr(x))
            df_display['Ratio (%)'] = df_display['Ratio (%)'].apply(lambda x: fmt_fr(x, 3))

        st.dataframe(
            df_display,
            use_container_width=True,
            height=500,
            hide_index=True
        )

        # Export CSV
        csv = df_table.to_csv(index=False, sep=';', decimal=',')
        st.download_button(
            label="Télécharger les données filtrées (CSV)",
            data=csv,
            file_name="frais_representation_filtrees.csv",
            mime="text/csv"
        )

    # TAB 3 - ANALYSES
    with tab3:
        st.markdown('<h3><i class="iconoir-graph-up"></i> Analyses graphiques</h3>', unsafe_allow_html=True)

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            # Boxplot par couleur politique
            st.markdown("#### EUR/hab par couleur politique")
            fig_box = px.box(
                df_filtered[df_filtered['COUL_POL'].isin(['Gauche', 'Droite', 'Centre', 'Extrême droite'])],
                x='COUL_POL',
                y='EUR_PAR_HAB',
                color='COUL_POL',
                color_discrete_map={
                    'Gauche': '#e74c3c',
                    'Droite': '#3498db',
                    'Centre': '#f39c12',
                    'Extrême droite': '#1a1a2e'
                }
            )
            fig_box.update_layout(
                showlegend=False,
                xaxis_title="",
                yaxis_title="EUR par habitant",
                separators=", "
            )
            st.plotly_chart(fig_box, use_container_width=True)

        with col_g2:
            # Scatter population vs EUR/hab
            st.markdown("#### Population vs EUR/hab")
            fig_scatter = px.scatter(
                df_filtered,
                x='POP_2022',
                y='EUR_PAR_HAB',
                color='COUL_POL',
                hover_name='NOM_COMMUNE',
                hover_data=['DEPARTEMENT', 'FRAIS_REPRESENTATION'],
                opacity=0.6,
                color_discrete_map={
                    'Gauche': '#e74c3c',
                    'Droite': '#3498db',
                    'Centre': '#f39c12',
                    'Extrême droite': '#1a1a2e',
                    'Courants politiques divers': '#9b59b6',
                    'Non classé': '#95a5a6',
                                    }
            )
            fig_scatter.update_layout(
                xaxis_title="Population",
                yaxis_title="EUR par habitant",
                xaxis_type="log",
                separators=", "
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Histogramme distribution
        st.markdown("#### Distribution des EUR/hab")
        fig_hist = px.histogram(
            df_filtered,
            x='EUR_PAR_HAB',
            nbins=50,
            color='COUL_POL',
            marginal='box',
            color_discrete_map={
                'Gauche': '#e74c3c',
                'Droite': '#3498db',
                'Centre': '#f39c12',
                'Extrême droite': '#1a1a2e',
                'Courants politiques divers': '#9b59b6',
                'Non classé': '#95a5a6',
                            }
        )
        fig_hist.update_layout(
            xaxis_title="EUR par habitant",
            yaxis_title="Nombre de communes",
            separators=", "
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # Moyennes par catégorie
        st.markdown("#### Moyenne EUR/hab par catégorie de population")
        df_cat = df_filtered.groupby('CATEGORIE_POP', observed=True)['EUR_PAR_HAB'].agg(['mean', 'median', 'count']).reset_index()
        df_cat.columns = ['Catégorie', 'Moyenne', 'Médiane', 'Nb communes']

        fig_bar = px.bar(
            df_cat,
            x='Catégorie',
            y=['Moyenne', 'Médiane'],
            barmode='group',
            text_auto='.2f'
        )
        fig_bar.update_layout(
            xaxis_title="",
            yaxis_title="EUR par habitant",
            legend_title="",
            separators=", "
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # TAB 4 - PALMARÈS
    with tab4:
        st.markdown('<h3><i class="iconoir-trophy"></i> Palmarès</h3>', unsafe_allow_html=True)

        # Filtres spécifiques au palmarès
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            cat_pop_options = ['Toutes'] + ['< 500 hab', '500-2000', '2000-10000', '10000-50000', '> 50000']
            cat_pop_palmares = st.selectbox("Catégorie de population", cat_pop_options, key="palmares_cat")
        with col_f2:
            nb_resultats = st.selectbox("Nombre de résultats", [10, 20, 50, 100], index=1, key="palmares_nb")
        with col_f3:
            coul_pol_options = ['Toutes'] + sorted(df_filtered['COUL_POL'].unique().tolist())
            coul_pol_palmares = st.selectbox("Couleur politique", coul_pol_options, key="palmares_coul")

        # Appliquer les filtres du palmarès
        df_palmares = df_filtered.copy()
        if cat_pop_palmares != 'Toutes':
            df_palmares = df_palmares[df_palmares['CATEGORIE_POP'] == cat_pop_palmares]
        if coul_pol_palmares != 'Toutes':
            df_palmares = df_palmares[df_palmares['COUL_POL'] == coul_pol_palmares]

        st.markdown("---")

        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.markdown(f'<h4><i class="iconoir-arrow-up"></i> Top {nb_resultats} - Plus dépensiers (EUR/hab)</h4>', unsafe_allow_html=True)
            top_n = df_palmares.nlargest(nb_resultats, 'EUR_PAR_HAB')[
                ['NOM_COMMUNE', 'DEPARTEMENT', 'POP_2022', 'EUR_PAR_HAB', 'TOTAL_CHARGES', 'RATIO_FRAIS_REP', 'COUL_POL']
            ].reset_index(drop=True)
            top_n.columns = ['Commune', 'Dépt', 'Pop.', 'EUR/hab', 'Budget (€)', 'Ratio (%)', 'Politique']
            top_n['Pop.'] = top_n['Pop.'].apply(lambda x: fmt_fr(x))
            top_n['EUR/hab'] = top_n['EUR/hab'].apply(lambda x: fmt_fr(x, 2))
            top_n['Budget (€)'] = top_n['Budget (€)'].apply(lambda x: fmt_fr(x))
            top_n['Ratio (%)'] = top_n['Ratio (%)'].apply(lambda x: fmt_fr(x, 2))
            st.dataframe(top_n, use_container_width=True, hide_index=True)

        with col_p2:
            st.markdown(f'<h4><i class="iconoir-arrow-down"></i> Top {nb_resultats} - Communes à 0€</h4>', unsafe_allow_html=True)
            zero_frais = df_palmares[df_palmares['FRAIS_REPRESENTATION'] == 0].nlargest(nb_resultats, 'POP_2022')[
                ['NOM_COMMUNE', 'DEPARTEMENT', 'POP_2022', 'EUR_PAR_HAB', 'TOTAL_CHARGES', 'COUL_POL']
            ].reset_index(drop=True)
            zero_frais.columns = ['Commune', 'Dépt', 'Pop.', 'EUR/hab', 'Budget (€)', 'Politique']
            zero_frais['Pop.'] = zero_frais['Pop.'].apply(lambda x: fmt_fr(x))
            zero_frais['EUR/hab'] = zero_frais['EUR/hab'].apply(lambda x: fmt_fr(x, 2))
            zero_frais['Budget (€)'] = zero_frais['Budget (€)'].apply(lambda x: fmt_fr(x))
            st.dataframe(zero_frais, use_container_width=True, hide_index=True)

        # Stats par couleur politique
        st.markdown('<h4><i class="iconoir-percentage"></i> Statistiques par couleur politique</h4>', unsafe_allow_html=True)
        stats_pol = df_palmares.groupby('COUL_POL').agg({
            'EUR_PAR_HAB': ['mean', 'median', 'std'],
            'FRAIS_REPRESENTATION': 'sum',
            'NOM_COMMUNE': 'count'
        }).round(2)
        stats_pol.columns = ['Moyenne EUR/hab', 'Médiane EUR/hab', 'Écart-type', 'Total frais (€)', 'Nb communes']
        stats_pol = stats_pol.sort_values('Moyenne EUR/hab', ascending=False)
        # Formatage français
        stats_pol['Moyenne EUR/hab'] = stats_pol['Moyenne EUR/hab'].apply(lambda x: fmt_fr(x, 2))
        stats_pol['Médiane EUR/hab'] = stats_pol['Médiane EUR/hab'].apply(lambda x: fmt_fr(x, 2))
        stats_pol['Écart-type'] = stats_pol['Écart-type'].apply(lambda x: fmt_fr(x, 2))
        stats_pol['Total frais (€)'] = stats_pol['Total frais (€)'].apply(lambda x: fmt_fr(x))
        stats_pol['Nb communes'] = stats_pol['Nb communes'].apply(lambda x: fmt_fr(x))
        st.dataframe(stats_pol, use_container_width=True)

    # TAB 5 - BUDGET
    with tab5:
        st.markdown('<h3><i class="iconoir-wallet"></i> Analyse budgétaire</h3>', unsafe_allow_html=True)
        st.markdown("Comparaison des frais de représentation avec le budget global des communes")

        # Vérifier que les colonnes budget existent
        if 'TOTAL_CHARGES' in df_filtered.columns and df_filtered['TOTAL_CHARGES'].sum() > 0:

            # Métriques budget
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1:
                total_charges = df_filtered['TOTAL_CHARGES'].sum()
                st.metric("Total charges", f"{fmt_fr(total_charges / 1e9, 2)} Mds €")
            with col_b2:
                total_personnel = df_filtered['CHARGES_PERSONNEL'].sum()
                st.metric("Charges personnel", f"{fmt_fr(total_personnel / 1e9, 2)} Mds €")
            with col_b3:
                ratio_moy = df_filtered[df_filtered['RATIO_FRAIS_REP'] > 0]['RATIO_FRAIS_REP'].mean()
                st.metric("Ratio frais rep. moyen", f"{fmt_fr(ratio_moy, 3)} %")
            with col_b4:
                ratio_max = df_filtered['RATIO_FRAIS_REP'].max()
                st.metric("Ratio frais rep. max", f"{fmt_fr(ratio_max, 2)} %")

            st.markdown("---")

            col_bg1, col_bg2 = st.columns(2)

            with col_bg1:
                # Répartition des charges (top 10 communes)
                st.markdown("#### Répartition des charges (Top 10 communes)")
                top10_budget = df_filtered.nlargest(10, 'TOTAL_CHARGES')

                # Préparer les données pour le graphique empilé
                budget_data = []
                for _, row in top10_budget.iterrows():
                    budget_data.append({
                        'Commune': row['NOM_COMMUNE'][:15],
                        'Personnel': row['CHARGES_PERSONNEL'] / 1e6,
                        'Achats/Services': row['ACHATS_SERVICES'] / 1e6,
                        'Autres gestion': row['AUTRES_CHARGES_GESTION'] / 1e6,
                        'Financières': row['CHARGES_FINANCIERES'] / 1e6,
                        'Exceptionnelles': row['CHARGES_EXCEPT'] / 1e6
                    })

                df_budget = pd.DataFrame(budget_data)
                fig_budget = px.bar(
                    df_budget,
                    x='Commune',
                    y=['Personnel', 'Achats/Services', 'Autres gestion', 'Financières', 'Exceptionnelles'],
                    title="",
                    labels={'value': 'Millions €', 'variable': 'Type de charge'},
                    color_discrete_sequence=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']
                )
                fig_budget.update_layout(
                    xaxis_title="",
                    yaxis_title="Millions €",
                    legend_title="",
                    barmode='stack',
                    separators=", "
                )
                st.plotly_chart(fig_budget, use_container_width=True)

            with col_bg2:
                # Scatter : Charges totales vs Frais de représentation
                st.markdown("#### Charges totales vs Frais de représentation")
                fig_scatter_budget = px.scatter(
                    df_filtered[df_filtered['TOTAL_CHARGES'] > 0],
                    x='TOTAL_CHARGES',
                    y='FRAIS_REPRESENTATION',
                    color='COUL_POL',
                    hover_name='NOM_COMMUNE',
                    hover_data=['POP_2022', 'RATIO_FRAIS_REP'],
                    opacity=0.6,
                    color_discrete_map={
                        'Gauche': '#e74c3c',
                        'Droite': '#3498db',
                        'Centre': '#f39c12',
                        'Extrême droite': '#1a1a2e',
                        'Courants politiques divers': '#9b59b6',
                        'Non classé': '#95a5a6',
                    }
                )
                fig_scatter_budget.update_layout(
                    xaxis_title="Charges totales (€)",
                    yaxis_title="Frais de représentation (€)",
                    xaxis_type="log",
                    yaxis_type="log",
                    separators=", "
                )
                st.plotly_chart(fig_scatter_budget, use_container_width=True)

            # Distribution du ratio frais de représentation
            st.markdown("#### Distribution du ratio frais de représentation / charges totales")
            df_ratio = df_filtered[df_filtered['RATIO_FRAIS_REP'] > 0].copy()
            df_ratio['RATIO_PERCENT'] = df_ratio['RATIO_FRAIS_REP']

            fig_ratio = px.histogram(
                df_ratio,
                x='RATIO_PERCENT',
                nbins=50,
                color='COUL_POL',
                marginal='box',
                color_discrete_map={
                    'Gauche': '#e74c3c',
                    'Droite': '#3498db',
                    'Centre': '#f39c12',
                    'Extrême droite': '#1a1a2e',
                    'Courants politiques divers': '#9b59b6',
                    'Non classé': '#95a5a6',
                }
            )
            fig_ratio.update_layout(
                xaxis_title="Ratio frais représentation / charges totales (%)",
                yaxis_title="Nombre de communes",
                separators=", "
            )
            st.plotly_chart(fig_ratio, use_container_width=True)

            # Top communes par ratio
            st.markdown("#### Top 20 communes avec le plus haut ratio frais de représentation")
            top_ratio = df_filtered[df_filtered['RATIO_FRAIS_REP'] > 0].nlargest(20, 'RATIO_FRAIS_REP')[
                ['NOM_COMMUNE', 'DEPARTEMENT', 'POP_2022', 'FRAIS_REPRESENTATION',
                 'TOTAL_CHARGES', 'RATIO_FRAIS_REP', 'COUL_POL']
            ].reset_index(drop=True)
            top_ratio.columns = ['Commune', 'Dépt', 'Pop.', 'Frais rep. (€)', 'Charges totales (€)', 'Ratio (%)', 'Politique']
            top_ratio['Pop.'] = top_ratio['Pop.'].apply(lambda x: fmt_fr(x))
            top_ratio['Frais rep. (€)'] = top_ratio['Frais rep. (€)'].apply(lambda x: fmt_fr(x, 2))
            top_ratio['Charges totales (€)'] = top_ratio['Charges totales (€)'].apply(lambda x: fmt_fr(x))
            top_ratio['Ratio (%)'] = top_ratio['Ratio (%)'].apply(lambda x: fmt_fr(x, 3))
            st.dataframe(top_ratio, use_container_width=True, hide_index=True)

        else:
            st.warning("Les données budgétaires ne sont pas disponibles pour cette sélection.")

    # Section méthodologie
    st.markdown("---")
    with st.expander("📋 Méthodologie - Traitement des données"):
        st.markdown("""
### Méthodologie de traitement : 

Cette visualisation a été réalisée pour illustrer la **phase de traitement** du cycle du renseignement OSINT,
où les données brutes collectées sont transformées en informations exploitables.

---

#### 1. Frais de représentation des maires

**Source** : Balances comptables des communes 2024 (data.gouv.fr)

**Compte comptable** : `65316` - *Frais de représentation du maire*

Ce compte enregistre les dépenses liées aux fonctions de représentation du maire :
réceptions officielles, cérémonies, déplacements protocolaires, etc.

**Extraction** : Filtrage des lignes où `COMPTE = '65316'` dans la balance comptable,
puis agrégation par SIREN de commune.

---

#### 2. Dépenses globales des communes

**Méthode** : Agrégation de tous les comptes de **classe 6** (charges) de la balance comptable.

| Catégorie | Comptes | Description |
|-----------|---------|-------------|
| **Personnel** | 64* | Rémunérations, charges sociales |
| **Achats/Services** | 60*, 61*, 62* | Fournitures, prestations, sous-traitance |
| **Autres gestion** | 65* | Dont frais de représentation (65316) |
| **Financières** | 66* | Intérêts d'emprunts |
| **Exceptionnelles** | 67* | Charges non récurrentes |
| **Amortissements** | 68* | Dotations aux amortissements |

**Colonne utilisée** : `OBNETDEB` (Opérations Budgétaires Nettes - Débit)

---

#### 3. Ratio frais de représentation

```
RATIO = FRAIS_REPRESENTATION / TOTAL_CHARGES × 100
```

Ce ratio permet de comparer les communes entre elles indépendamment de leur taille budgétaire.

---

#### 4. Jointure des données

Les trois sources (balances comptables, nuances politiques, population INSEE) sont
fusionnées via le **code INSEE** de chaque commune, garantissant l'unicité des correspondances.
Dans le fichier des balances comptables, il a fallu reconstituer le code INSEE à partir de 2 colonnes.
**Communes analysées** : 1 208 communes de France Métropolitaine ayant déclaré des frais de représentation en 2024.
        """)

    # Footer avec sources
    st.markdown("---")
    footer_html = """<div class="sources-container">
<div class="sources-title"><i class="iconoir-book"></i> Sources des données</div>
<div class="source-item">
<div class="source-title"><i class="iconoir-coins"></i> Frais de représentation des maires</div>
<div class="source-desc">Balances comptables des communes 2024 — Compte 65316<br>
<a href="https://www.data.gouv.fr/datasets/balances-comptables-des-communes-en-2024/" target="_blank">data.gouv.fr → balances-comptables-communes-2024</a></div>
</div>
<div class="source-item">
<div class="source-title"><i class="iconoir-community"></i> Étiquette politique du maire</div>
<div class="source-desc">Nuance politique — Résultats des élections municipales<br>
<a href="https://www.data.gouv.fr/datasets/communes-enrichies-avec-la-nuance-politique-france/" target="_blank">data.gouv.fr → communes-nuance-politique</a></div>
</div>
<div class="source-item">
<div class="source-title"><i class="iconoir-group"></i> Population des communes</div>
<div class="source-desc">Recensement de la population 2022<br>
<a href="https://www.insee.fr/fr/statistiques/8581696" target="_blank">insee.fr → statistiques/8581696</a></div>
</div>
<div style="text-align: center; margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid #eee; color: #999; font-size: 0.75rem;">
Réalisé par <strong style="color: #666;">Degun</strong> — <a href="https://manufacture-osint.fr" target="_blank" style="color: #888;">Manufacture Française d'OSINT</a>
</div>
</div>"""
    st.markdown(footer_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
