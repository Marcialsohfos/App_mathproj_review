import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

class ProjectionDemographique:
    def __init__(self):
        self.resultats = {}
    
    def calculer_coefficients(self, m0, m1, m2):
        c = m0
        b = (4 * m1 - m2 - 3 * m0) / 4
        a = (m2 - 2 * m1 + m0) / 8
        return a, b, c
    
    def calculer_population(self, a, b, c, t):
        return a * (t ** 2) + b * t + c
    
    def effectuer_projection(self, nom_ville, population_2016, population_2018, population_2020):
        a, b, c = self.calculer_coefficients(population_2016, population_2018, population_2020)
        
        projections = {}
        projections[2016] = population_2016
        projections[2018] = population_2018
        projections[2020] = population_2020
        projections[2023] = self.calculer_population(a, b, c, 7)
        projections[2024] = self.calculer_population(a, b, c, 8)
        projections[2025] = self.calculer_population(a, b, c, 9)
        projections[2026] = self.calculer_population(a, b, c, 10)
        
        resultat_ville = {
            'coefficients': {'a': a, 'b': b, 'c': c},
            'projections': projections
        }
        
        self.resultats[nom_ville] = resultat_ville
        return resultat_ville
    
    def exporter_excel(self):
        if not self.resultats:
            return None
        
        donnees_export = []
        for ville, data in self.resultats.items():
            ligne = {'Ville': ville}
            ligne.update(data['projections'])
            ligne.update({
                'Coefficient a': data['coefficients']['a'],
                'Coefficient b': data['coefficients']['b'],
                'Coefficient c': data['coefficients']['c']
            })
            donnees_export.append(ligne)
        
        df = pd.DataFrame(donnees_export)
        return df

# Initialisation du modèle dans session_state
if 'modele' not in st.session_state:
    st.session_state.modele = ProjectionDemographique()

# Configuration de la page
st.set_page_config(
    page_title="Projection Démographique - Lab_math_RMT",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .city-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .success-alert {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-alert {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# En-tête
st.markdown("""
<div class="main-header">
    <h1>📊 Application de Projection Démographique</h1>
    <p>Modèle polynomial pour l'évolution démographique des villes</p>
    <p><small>Power by Lab_math_RMT and CIE 2025</small></p>
</div>
""", unsafe_allow_html=True)

# Sidebar pour les informations
with st.sidebar:
    st.markdown("## ℹ️ À propos")
    st.info(
        """
        Cette application utilise un modèle polynomial quadratique 
        pour projeter l'évolution démographique des villes.
        
        **Formule:** p(t) = at² + bt + c
        
        **Paramètres:**
        - t = 0 pour l'année 2016
        - t = 2 pour l'année 2018
        - t = 4 pour l'année 2020
        
        **Projections:** 2023, 2024, 2025, 2026
        """
    )
    
    st.markdown("---")
    st.markdown("### 📈 Statistiques")
    
    if st.session_state.modele.resultats:
        nb_villes = len(st.session_state.modele.resultats)
        st.metric("🏙️ Villes analysées", nb_villes)
        
        total_pop_2026 = sum(data['projections'][2026] 
                              for data in st.session_state.modele.resultats.values())
        st.metric("👥 Population totale 2026", f"{int(total_pop_2026):,}")
        
        st.metric("📊 Projections totales", nb_villes * 4)

# Zone principale - Deux colonnes
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("## ➕ Ajouter une nouvelle ville")
    
    with st.form(key="add_city_form"):
        nom_ville = st.text_input("🏙️ Nom de la ville", placeholder="Entrez le nom de la ville")
        
        st.markdown("### 📅 Populations de référence")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            pop_2016 = st.number_input("Population 2016", min_value=0, step=1000, value=0)
        with col_b:
            pop_2018 = st.number_input("Population 2018", min_value=0, step=1000, value=0)
        with col_c:
            pop_2020 = st.number_input("Population 2020", min_value=0, step=1000, value=0)
        
        submitted = st.form_submit_button("🚀 Calculer les projections")
        
        if submitted:
            if not nom_ville:
                st.markdown('<div class="error-alert">❌ Veuillez entrer un nom de ville</div>', 
                           unsafe_allow_html=True)
            elif pop_2016 <= 0 or pop_2018 <= 0 or pop_2020 <= 0:
                st.markdown('<div class="error-alert">❌ Les populations doivent être supérieures à 0</div>', 
                           unsafe_allow_html=True)
            else:
                try:
                    resultat = st.session_state.modele.effectuer_projection(
                        nom_ville, pop_2016, pop_2018, pop_2020
                    )
                    st.markdown(f"""
                    <div class="success-alert">
                        ✅ Projections calculées avec succès pour {nom_ville}!
                    </div>
                    """, unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="error-alert">❌ Erreur: {str(e)}</div>', 
                               unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📂 Charger des exemples")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🏙️ NGAOUNDÉRÉ I", use_container_width=True):
            st.session_state.modele.effectuer_projection("NGAOUNDÉRÉ I", 109423, 115772, 122282)
            st.success("✅ NGAOUNDÉRÉ I ajoutée avec succès!")
            st.rerun()
    
    with col_btn2:
        if st.button("🏛️ YAOUNDE 1", use_container_width=True):
            st.session_state.modele.effectuer_projection("YAOUNDE 1", 429252, 461134, 494353)
            st.success("✅ YAOUNDE 1 ajoutée avec succès!")
            st.rerun()
    
    with col_btn3:
        if st.button("📦 Tous les exemples", use_container_width=True):
            exemples = {
                "NGAOUNDÉRÉ I": [109423, 115772, 122282],
                "NGAOUNDÉRÉ II": [118764, 125655, 132721],
                "NGAOUNDÉRÉ III": [24501, 25923, 27380],
                "YAOUNDE 1": [429252, 461134, 494353],
                "YAOUNDE 2": [361606, 388463, 416448],
            }
            for ville, pops in exemples.items():
                st.session_state.modele.effectuer_projection(ville, pops[0], pops[1], pops[2])
            st.success(f"✅ {len(exemples)} villes chargées avec succès!")
            st.rerun()

with col2:
    st.markdown("## 📊 Résultats des projections")
    
    if st.session_state.modele.resultats:
        # Actions
        col_action1, col_action2 = st.columns(2)
        with col_action1:
            if st.button("📥 Exporter vers Excel", use_container_width=True):
                df = st.session_state.modele.exporter_excel()
                if df is not None:
                    # Convertir en Excel
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Projections', index=False)
                    output.seek(0)
                    
                    st.download_button(
                        label="📊 Télécharger Excel",
                        data=output,
                        file_name=f"projections_demographiques_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        with col_action2:
            if st.button("🗑️ Réinitialiser tout", use_container_width=True):
                st.session_state.modele.resultats = {}
                st.success("✅ Toutes les données ont été réinitialisées!")
                st.rerun()
        
        # Affichage des résultats
        for ville, data in st.session_state.modele.resultats.items():
            with st.container():
                st.markdown(f"""
                <div class="city-card">
                    <h3>{ville}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Coefficients
                col_coef1, col_coef2, col_coef3 = st.columns(3)
                with col_coef1:
                    st.metric("Coefficient a", f"{data['coefficients']['a']:.4f}")
                with col_coef2:
                    st.metric("Coefficient b", f"{data['coefficients']['b']:.4f}")
                with col_coef3:
                    st.metric("Coefficient c", f"{data['coefficients']['c']:.4f}")
                
                # Tableau des projections
                df_projections = pd.DataFrame([
                    {"Année": annee, "Population": int(pop), 
                     "Évolution (%)": f"{((pop - list(data['projections'].values())[i-1]) / list(data['projections'].values())[i-1] * 100):.1f}%" 
                     if i > 0 else "-"}
                    for i, (annee, pop) in enumerate(data['projections'].items())
                ])
                
                st.dataframe(df_projections, use_container_width=True, hide_index=True)
                
                # Graphique
                fig = go.Figure()
                
                annees_historiques = [2016, 2018, 2020]
                pops_historiques = [data['projections'][2016], data['projections'][2018], data['projections'][2020]]
                
                annees_projection = [2023, 2024, 2025, 2026]
                pops_projection = [data['projections'][2023], data['projections'][2024], 
                                  data['projections'][2025], data['projections'][2026]]
                
                fig.add_trace(go.Scatter(
                    x=annees_historiques, y=pops_historiques,
                    mode='markers+lines', name='Données historiques',
                    line=dict(color='blue', width=3),
                    marker=dict(size=10, color='blue')
                ))
                
                fig.add_trace(go.Scatter(
                    x=annees_projection, y=pops_projection,
                    mode='markers+lines', name='Projections',
                    line=dict(color='red', width=3, dash='dash'),
                    marker=dict(size=10, color='red')
                ))
                
                fig.update_layout(
                    title=f"Évolution démographique - {ville}",
                    xaxis_title="Année",
                    yaxis_title="Population",
                    hovermode='x unified',
                    showlegend=True,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("---")
    else:
        st.info("👈 Ajoutez une ville à gauche pour commencer les projections")

# Pied de page
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-top: 2rem;">
    <p style="font-size: 1.1rem;">Power by Lab_math_RMT and CIE 2025</p>
    <p style="font-size: 0.9rem;">Application de projection démographique avancée</p>
    <p style="font-size: 0.8rem;">Modèle polynomial: p(t) = at² + bt + c (avec t=0 pour l'année 2016)</p>
</div>
""", unsafe_allow_html=True)