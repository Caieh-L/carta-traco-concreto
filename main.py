"""
Interface Web de Alto Desempenho - Sistema Profissional de Dosagem de Concreto
Compatível com NBR 12655, NBR 6118, NBR 8953, NBR 7211 e NR-17
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

from src.dosagem import CalculadoraDosagem
from src.relatorios import gerar_pdf_canteiro, gerar_pdf_tecnico

# 1. Configuração da Página
st.set_page_config(
    page_title="DOSACON | Sistema Especialista de Concreto",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilização CSS Customizada (Aparência de Software Comercial)
st.markdown("""
<style>
    /* Fundo e Container Principal */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Cartões Módulo */
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #38BDF8;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Dicas didáticas */
    .info-box {
        background-color: #1E293B;
        border-left: 4px solid #38BDF8;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 10px 0;
        font-size: 0.9rem;
        color: #E2E8F0;
    }

    /* Ocultar elementos desnecessários */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Cabeçalho Principal
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    st.markdown("🏽‍🏗️", unsafe_allow_html=True)
with col_titulo:
    st.title("DOSACON — Tecnologia e Dosagem de Concreto")
    st.caption("Plataforma de Dosagem Científica e Operação de Canteiro | NBR 12655 & NBR 6118")

st.divider()

# 4. Painel Lateral de Entrada de Dados (Sidebar)
st.sidebar.header("⚙️ Parâmetros de Dosagem")

# Finalidade Estrutural e "Testinho Explicativo"
finalidade = st.sidebar.selectbox(
    "Finalidade da Estrutura",
    [
        "Lastro / Concreto Magro",
        "Calçadas e Pisos Leves",
        "Lajes e Vigas Convencionais",
        "Pilares e Muros de Arrimo (Alta Responsabilidade)",
        "Obras Especiais / Pontes / Reserva Hídrica"
    ]
)

# Textos Explicativos Contextuais baseados na Finalidade
EXPLICACOES_FINALIDADE = {
    "Lastro / Concreto Magro": "💡 **Concreto Magro:** Função de regularização de solo e proteção das armaduras. Baixe consumo de cimento e sem função estrutural direta.",
    "Calçadas e Pisos Leves": "💡 **Pisos de Pedestres:** Exige resistência ao desgaste superficial. Atenção ao acabamento e controle de água para evitar esfarinhamento.",
    "Lajes e Vigas Convencionais": "💡 **Elementos Curvados/Flexão:** Exige boa trabalhabilidade para cobrir armaduras sem criar vazios de concretagem.",
    "Pilares e Muros de Arrimo (Alta Responsabilidade)": "⚠️ **Alta Responsabilidade:** Muros de arrimo e pilares possuem alta densidade de aço. Exigem adensamento rigoroso e excelente fluidez para evitar bocheiras (nichos).",
    "Obras Especiais / Pontes / Reserva Hídrica": "🚨 **Obras Especiais:** Baixa permeabilidade e elevada durabilidade contra ataque químico. Exige controle rigoroso da relação água/cimento."
}

st.sidebar.info(EXPLICACOES_FINALIDADE[finalidade])

fck = st.sidebar.select_slider(
    "Resistência Projetada fck (MPa)",
    options=[15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0],
    value=25.0
)

controle = st.sidebar.selectbox(
    "Controle Tecnológico em Obra",
    [
        "Classe A (Rigoroso - Central/Usina)",
        "Classe B (Razoável - Canteiro Medido)",
        "Classe C (Regular - Canteiro Manual)"
    ]
)

tipo_cimento = st.sidebar.selectbox(
    "Tipo de Cimento",
    ["CP I", "CP II", "CP III", "CP IV", "CP V-ARI"]
)

# Textos explicativos sobre cimentos
EXPLICACOES_CIMENTO = {
    "CP I": "Cimento comum sem aditivos. Uso geral em obras sem exposição agressiva.",
    "CP II": "Cimento composto versátil. Baixo calor de hidratação, excelente para a maioria das obras.",
    "CP III": "Cimento de Alto Forno. Altíssima durabilidade contra sulfatos e água do mar. Ganho de resistência inicial mais lento.",
    "CP IV": "Cimento Pozolânico. Indicado para obras hidráulicas, pilares densos e regiões litorâneas.",
    "CP V-ARI": "Alta Resistência Inicial. Atinge alta resistência em poucos dias. Ideal para rápida desforma."
}
st.sidebar.caption(f"ℹ️ **{tipo_cimento}:** {EXPLICACOES_CIMENTO[tipo_cimento]}")

st.sidebar.subheader("🧱 Agregados e Consistência")
tipo_areia = st.sidebar.selectbox("Tipo de Areia", ["areia_fina", "areia_media", "areia_grossa", "areia_britagem"])
tipo_brita = st.sidebar.selectbox("Tipo de Brita", ["brita_0", "brita_1", "brita_2", "seixo_rolado", "seixo_misto"])

slump = st.sidebar.selectbox(
    "Abatimento (Slump Test)",
    [
        "60-80 mm (Manual / Peças Simples)",
        "100-120 mm (Vigas e Lajes Densas)",
        "140-160 mm (Fluido / Bombeável)",
        "180-220 mm (Auto-adensável)"
    ]
)

aditivo = st.sidebar.selectbox("Aditivos Químicos", ["Nenhum (Sem aditivo)", "Plastificante (-10% Água)", "Superplastificante (-20% Água)"])

st.sidebar.subheader("🌧️ Condições do Canteiro")
umidade_areia = st.sidebar.slider("Umidade da Areia (%)", 0.0, 10.0, 4.0, 0.5)
inchamento_areia = st.sidebar.slider("Inchaçamento da Areia (%)", 0.0, 30.0, 20.0, 1.0)

# Cubagem da Peça
st.sidebar.subheader("📐 Geometria para Cálculo de Volume")
comp = st.sidebar.number_input("Comprimento (m)", value=5.0, step=0.5)
larg = st.sidebar.number_input("Largura (m)", value=0.3, step=0.05)
alt = st.sidebar.number_input("Altura / Espessura (m)", value=0.4, step=0.05)
perda = st.sidebar.selectbox("Margem de Perda (%)", [0, 5, 10, 15], index=2)

vol_bruto = comp * larg * alt
vol_total = vol_bruto * (1.0 + (perda / 100.0))

# Cálculo dos Dados via Motor
res = CalculadoraDosagem.processar_dosagem(
    fck=fck,
    controle=controle,
    tipo_cimento=tipo_cimento,
    tipo_areia=tipo_areia,
    tipo_brita=tipo_brita,
    slump=slump,
    aditivo=aditivo,
    umidade_areia_pct=umidade_areia,
    inchamento_areia_pct=inchamento_areia,
    volume_m3=vol_total
)

# 5. Dashboard Principal (Abas)
tab_painel, tab_abrams, tab_canteiro, tab_pdf = st.tabs([
    "📊 Painel Principal", 
    "📈 Curva de Abrams", 
    "👷 Receita de Canteiro (NR-17)", 
    "📑 Relatórios PDF"
])

with tab_painel:
    # Exibição de Alertas
    if res["alertas"]:
        for alt_msg in res["alertas"]:
            st.warning(alt_msg)

    # Cartões de Resumo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">fck Projetado</div><div class="metric-value">{res["fck"]} MPa</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">fcm28 (Alvo)</div><div class="metric-value">{res["fcm28"]} MPa</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Relação A/C</div><div class="metric-value">{res["relacao_ac"]}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Volume Total</div><div class="metric-value">{vol_total:.2f} m³</div></div>', unsafe_allow_html=True)

    st.markdown("### 📝 Traço Seco em Massa")
    st.info(f"**Traço Padronizado:** `{res['traco_seco']}` (Cimento : Areia : Brita)")

    st.markdown("### 📦 Consumo de Materiais para a Obra")
    c_m3 = res["consumo_m3"]
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.write(f"• **Cimento Portland:** `{c_m3['cimento_kg']} kg` ({c_m3['sacos_cimento_50kg']} sacos de 50kg)")
        st.write(f"• **Areia Úmida:** `{c_m3['areia_umida_kg']} kg` ({c_m3['areia_m3']} m³)")
    with col_c2:
        st.write(f"• **Brita / Seixo:** `{c_m3['brita_kg']} kg` ({c_m3['brita_m3']} m³)")
        st.write(f"• **Água Efetiva:** `{c_m3['agua_litros']} Litros` *(já corrigido pelo inchaçamento)*")

with tab_abrams:
    st.subheader("Análise Gráfica da Lei de Abrams")
    
    ac_eixo = np.linspace(0.30, 0.70, 50)
    params = CalculadoraDosagem.PARAMETROS_ABRAMS[tipo_cimento]
    fcm_eixo = params["A"] / (params["B"] ** ac_eixo)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ac_eixo, y=fcm_eixo, 
        mode='lines', 
        name=f'Curva Teórica ({tipo_cimento})',
        line=dict(color='#38BDF8', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=[res['relacao_ac']], y=[res['fcm28']], 
        mode='markers+text', 
        name='Ponto de Operação',
        text=[f"  fcm28 = {res['fcm28']} MPa"], 
        textposition="top right",
        marker=dict(color='#EF4444', size=14)
    ))

    fig.update_layout(
        title="Relação Água/Cimento vs Resistência Média (fcm28)",
        xaxis_title="Relação Água / Cimento (a/c)",
        yaxis_title="Resistência Média aos 28 Dias (MPa)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,23,42,0.8)',
        font=dict(color='#F8FAFC')
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_canteiro:
    st.subheader("Receita Operacional por Saco de Cimento (50 kg)")
    saco = res["dosagem_por_saco_50kg"]
    
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Cimento</div><div class="metric-value">1 Saco</div><div>50 kg</div></div>', unsafe_allow_html=True)
    with c_s2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Areia (Padiola NR-17)</div><div class="metric-value">{saco["padiolas_areia_nr17"]}</div><div>Padiolas Padronizadas</div></div>', unsafe_allow_html=True)
    with c_s3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Brita (Padiola NR-17)</div><div class="metric-value">{saco["padiolas_brita_nr17"]}</div><div>Padiolas Padronizadas</div></div>', unsafe_allow_html=True)

    st.markdown(f"🪣 **Água Limpa a Adicionar:** `{saco['agua_litros_balde']} Litros` por saco de cimento.")
    st.caption("📏 Padiola NR-17 Padronizada: 45 x 35 x 23 cm (Volume = 36.2 Litros). Peso limitado a ~27 kg para ergometria de dois trabalhadores.")

with tab_pdf:
    st.subheader("Emissão de Fichas e Dossiês Técnicos")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("#### Ficha Operacional de Canteiro")
        st.write("Relatório em linguagem acessível voltado para pedreiros e mestres de obras com a contagem exata de padiolas e cuidados na cura.")
        pdf_c = gerar_pdf_canteiro(res)
        st.download_button("📄 Baixar Ficha de Canteiro (PDF)", data=pdf_c, file_name="ficha_canteiro.pdf", mime="application/pdf")

    with col_p2:
        st.markdown("#### Dossiê Técnico de Engenharia")
        st.write("Memorial de cálculo detalhado para engenheiros, arquitetos e fiscalização, com registro de premissas NBR 12655 e Lei de Abrams.")
        pdf_t = gerar_pdf_tecnico(res)
        st.download_button("📑 Baixar Dossiê Técnico (PDF)", data=pdf_t, file_name="dossie_tecnico.pdf", mime="application/pdf")
