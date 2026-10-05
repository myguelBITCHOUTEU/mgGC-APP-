import streamlit as st
import pandas as pd
import math, os
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm

# Configuration de la page
st.set_page_config(page_title="mgGCAPP Express", page_icon="🏗️", layout="wide")

# 1. EN-TÊTE ET SALUTATION
heure = datetime.now().hour
salut = "Bonjour Monsieur" if 5 <= heure < 18 else "Bonsoir Monsieur"

st.title("🏗️ mgGCAPP — Devis Express BTP")
st.caption(f"✨ {salut}, bienvenue ! Obtenez une estimation rapide des matériaux pour votre projet de construction.")

st.divider()

# 2. SECTION AIDE & SUPPORT (HELP)
with st.expander("❓ **Besoin d'aide ou problème sur le site ? (Aide / Help)**"):
    col_faq, col_contact = st.columns([2, 1], gap="medium")
    
    with col_faq:
        st.markdown("##### 📌 Foire Aux Questions (FAQ)")
        st.markdown("""
        - **Comment sont calculés les matériaux ?** Les quantités sont estimées selon les normes de calcul BTP et Eurocode 2 adaptées à la superficie et au nombre de pièces.
        - **Le devis est-il définitif ?** C'est un devis estimatif rapide pour vous donner une idée globale du budget matériaux.
        - **Problème de téléchargement PDF ?** Vérifiez que votre navigateur ne bloque pas les fenêtres surgissantes ou réessayez en cliquant à nouveau sur le bouton.
        """)
    
    with col_contact:
        st.markdown("##### 📞 Assistance Directe")
        st.write("Une difficulté ? Un problème technique ?")
        
        # Lien direct WhatsApp
        whatsapp_url = "https://wa.me/237696073121?text=Bonjour,%20j'ai%20besoin%20d'aide%20sur%20le%20site%20mgGCAPP."
        st.markdown(f'''
            <a href="{whatsapp_url}" target="_blank">
                <button style="background-color:#25D366; color:white; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; font-weight:bold; width:100%;">
                    💬 Discuter sur WhatsApp (696073121)
                </button>
            </a>
        ''', unsafe_allow_html=True)
        
        st.caption("Disponible 7j/7 pour vous accompagner.")

st.divider()

# 3. PARCOURS UTILISATEUR : QUESTIONS STRUCTURÉES
st.subheader("📋 Vos informations & Détails du projet")

col_a, col_b = st.columns([1, 2], gap="large")

with col_a:
    st.markdown("#### 1️⃣ Vos Coordonnées")
    nom = st.text_input("Nom & Prénom", value="Client")
    tel = st.text_input("Téléphone / WhatsApp", placeholder="+237...")

    # Enregistrement discret des visiteurs
    if nom != "Client" and tel:
        fichier_csv = "visiteurs.csv"
        hdr = not os.path.exists(fichier_csv)
        pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Nom": nom, "Tel": tel}]).to_csv(
            fichier_csv, mode="a", header=hdr, index=False
        )

with col_b:
    st.markdown("#### 2️⃣ Caractéristiques du Bâtiment")
    c_proj, c_surf = st.columns(2)
    with c_proj:
        type_projet = st.selectbox("Type d'ouvrage", ["Plain-pied (RDC)", "R+1", "R+2", "R+2-1"])
    with c_surf:
        surf = st.number_input("Superficie au sol (m²)", min_value=30, max_value=1500, value=100, step=10)

    st.markdown("#### 3️⃣ Répartition des Pièces")
    cp1, cp2, cp3, cp4, cp5 = st.columns(5)
    with cp1:
        nb_chambres = st.number_input("Chambres", min_value=1, max_value=20, value=3)
    with cp2:
        nb_salons = st.number_input("Salons", min_value=1, max_value=5, value=1)
    with cp3:
        nb_cuisines = st.number_input("Cuisines", min_value=1, max_value=5, value=1)
    with cp4:
        nb_wc = st.number_input("SDB / WC", min_value=1, max_value=10, value=2)
    with cp5:
        nb_verandas = st.number_input("Vérandas", min_value=0, max_value=10, value=1)

# Options avancées / Préférences
with st.expander("⚙️ Préférences techniques et devises (Optionnel)"):
    co1, co2 = st.columns(2)
    with co1:
        dosage = st.selectbox("Dosage du Béton", [300, 350, 400, 450], index=1, format_func=lambda x: f"{x} kg/m³")
    with co2:
        devise = st.selectbox("Devise d'affichage", ["FCFA", "EUR (€)", "USD ($)"])

# 4. CALCULS TECHNIQUE (EUROCODE 2)
niveaux_dict = {"Plain-pied (RDC)": 1, "R+1": 2, "R+2": 3, "R+2-1": 2.5}
niveaux = niveaux_dict[type_projet]
surf_tot = surf * niveaux
perim = 4 * math.sqrt(surf) * 1.3

# Prise en compte du cloisonnement selon le nombre de pièces
ratio_cloison = 1.0 + ((nb_chambres + nb_salons + nb_cuisines + nb_wc) * 0.05)
perim_effectif = perim * ratio_cloison

vol_beton = round((surf * 0.12) + (surf_tot * 0.05) + ((niveaux - 1) * surf * 0.15) + (perim_effectif * 0.45 * 0.45), 1)
sacs_ciment = math.ceil((vol_beton * dosage) / 50)
sable = round(vol_beton * 0.45, 1)
gravier = round(vol_beton * 0.82, 1)
acier_kg = math.ceil(vol_beton * (75 if niveaux <= 2 else 95))
agglos = math.ceil(perim_effectif * 3.0 * niveaux * 9)

is_fcfa = (devise == "FCFA")
pu = {
    "Ciment": 4800 if is_fcfa else 8,
    "Sable": 9000 if is_fcfa else 35,
    "Gravier": 14000 if is_fcfa else 45,
    "Acier": 750 if is_fcfa else 1.6,
    "Agglos": 320 if is_fcfa else 1.2
}

data = [
    {"Matériau": f"Ciment CPJ (Dosage {dosage} kg/m³)", "Unité": "Sacs 50kg", "Qté": sacs_ciment, "P.U": pu["Ciment"], "Total": int(sacs_ciment * pu["Ciment"])},
    {"Matériau": "Sable propre (0/4)", "Unité": "m³", "Qté": sable, "P.U": pu["Sable"], "Total": int(round(sable * pu["Sable"]))},
    {"Matériau": "Gravier concassé (5/25)", "Unité": "m³", "Qté": gravier, "P.U": pu["Gravier"], "Total": int(round(gravier * pu["Gravier"]))},
    {"Matériau": "Aciers Haute Adhérence FeE500", "Unité": "Kg", "Qté": acier_kg, "P.U": pu["Acier"], "Total": int(acier_kg * pu["Acier"])},
    {"Matériau": "Agglos creux vibrés", "Unité": "Unités", "Qté": agglos, "P.U": pu["Agglos"], "Total": int(agglos * pu["Agglos"])},
]

df = pd.DataFrame(data)
total_ht = int(df["Total"].sum())

# 5. PRÉSENTATION DES RÉSULTATS
st.divider()
st.subheader("📊 Résultat du Devis Estimatif")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Béton Total", f"{vol_beton} m³")
m2.metric("Ciment Requis", f"{sacs_ciment} sacs")
m3.metric("Aciers", f"{acier_kg} kg")
m4.metric("TOTAL ESTIMÉ", f"{total_ht:,.0f} {devise}".replace(",", " "))

st.dataframe(df, use_container_width=True)

# 6. GÉNÉRATION DU PDF EN CACHE
@st.cache_data(show_spinner=False)
def generate_pdf_bytes(nom_c, tel_c, proj, surface_t, dos, data_list, tot_ht, dev, ch, sal, cuis, wc, ver):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    
    story = [
        Paragraph("<b>mgGCAPP — DEVIS ESTIMATIF RAPIDE</b>", styles['Heading1']),
        Paragraph(f"Client : <b>{nom_c}</b> | Tél : {tel_c} | Projet : <b>{proj} ({surface_t} m²)</b>", styles['Normal']),
        Paragraph(f"Distribution : <b>{ch} Ch. | {sal} Salon(s) | {cuis} Cuis. | {wc} WC | {ver} Véranda(s)</b>", styles['Normal']),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=15)
    ]
    
    t_data = [["Matériau", "Unité", "Quantité", "P.U", "Total HT"]]
    for r in data_list:
        t_data.append([
            r["Matériau"], 
            r["Unité"], 
            str(r["Qté"]), 
            f"{r['P.U']:,.0f}".replace(",", " "), 
            f"{r['Total']:,.0f}".replace(",", " ")
        ])
    
    t_data.append(["TOTAL GÉNÉRAL", "", "", "", f"{tot_ht:,.0f} {dev}".replace(",", " ")])
    
    t = Table(t_data, colWidths=[7*cm, 2.5*cm, 2.5*cm, 2.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#F1F5F9'))
    ]))
    
    story.append(t)
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Besoin d'un plan de distribution sur mesure ?</b> Contactez-nous au <b>+237 696 07 31 21</b>", styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>Merci d’avoir visité mgGCAPP, {nom_c} !</b>", styles['Normal']))
    
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

pdf_bytes = generate_pdf_bytes(
    nom, tel, type_projet, surf_tot, dosage, data, total_ht, devise,
    nb_chambres, nb_salons, nb_cuisines, nb_wc, nb_verandas
)

# 7. ACTION & CONTACT FINAUX
col_dl, col_info = st.columns([1, 2])

with col_dl:
    st.download_button(
        label="📥 TÉLÉCHARGER LE DEVIS (PDF)",
        data=pdf_bytes,
        file_name=f"Devis_{nom}_{type_projet}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with col_info:
    st.info("📐 **Vous souhaitez un plan de distribution personnalisé pour votre projet ?**\n\nContactez notre architecte au **696073121** (Appel / WhatsApp).")

st.markdown("---")
st.success(f"🤝 **Merci pour votre confiance, {nom} !** Bon succès dans la réalisation de votre ouvrage.")
