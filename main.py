import streamlit as st
from src.dosagem import calcular_traco_seco, consumo_materiais_m3
from src.utils import converter_para_canteiro

st.set_page_config(page_title="Carta Traço de Concreto", page_icon="🏗️", layout="centered")

st.title("🏗️ Carta Traço de Concreto")
st.write("Calculadora interativa de dosagem e conversão para canteiro de obras.")

st.sidebar.header("Parâmetros de Entrada")
fck_projeto = st.sidebar.number_input("fck especificado (MPa)", value=20.0, step=1.0)
controle = st.sidebar.selectbox("Controle Tecnológico", ["Rigoroso", "Razoável", "Regular"])
m_agregados = st.sidebar.number_input("Proporção agregados/cimento (m)", value=4.22, step=0.01)
alpha_argamassa = st.sidebar.number_input("Teor de argamassa (α)", value=0.474, step=0.001)
relacao_ac = st.sidebar.number_input("Relação Água/Cimento (a/c)", value=0.47, step=0.01)

def obter_desvio_padrao(nivel: str) -> float:
    controles = {"rigoroso": 4.0, "razoavel": 5.5, "regular": 7.0}
    return controles.get(nivel.lower(), 5.5)

sd = obter_desvio_padrao(controle)
fcm28 = fck_projeto + (1.65 * sd)

traco_seco = calcular_traco_seco(m_agregados, alpha_argamassa, relacao_ac)
consumo = consumo_materiais_m3(traco_seco)
canteiro = converter_para_canteiro(consumo)

st.subheader("📊 Resultados da Dosagem")

col1, col2 = st.columns(2)
col1.metric("Resistência fcm28", f"{fcm28:.2f} MPa")
col2.metric("Desvio Padrão (sd)", f"{sd:.1f} MPa")

st.info(f"**Traço Seco em Massa:** 1 : {traco_seco['areia']} : {traco_seco['brita']} (a/c = {traco_seco['agua']})")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### Consumo por m³")
    st.write(f"- **Cimento:** {consumo['cimento_kg']} kg")
    st.write(f"- **Areia:** {consumo['areia_kg']} kg")
    st.write(f"- **Brita:** {consumo['brita_kg']} kg")
    st.write(f"- **Água:** {consumo['agua_litros']} L")

with col_b:
    st.markdown("### Por Saco de Cimento (50 kg)")
    st.write(f"- **Areia:** {canteiro['areia_latas_18l']} latas de 18L")
    st.write(f"- **Brita:** {canteiro['brita_latas_18l']} latas de 18L")
    st.write(f"- **Água:** {canteiro['agua_latas_18l']} latas ({canteiro['agua_litros_saco']} L)")
