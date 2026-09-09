"""
DOSACON — Interface Web Corporativa de Tecnologia do Concreto
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

from src.dosagem import CalculadoraDosagem
from src.relatorios import gerar_pdf_canteiro, gerar_pdf_tecnico

st.set_page_config(
    page_title="DOSACON | Sistema Especialista de Concreto",
    page_icon="🏗️",
    layout="wide"
)

# Estilização Profissional Clean (Tema Claro Corporativo)
st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    .main-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #2563EB;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h2 style="margin:0;">🏗️ DOSACON — Sistema Especialista de Dosagem de Concreto</h2>
    <p style="margin:0; font-size:0.9rem; opacity:0.9;">
        Tecnologia do Concreto em Conformidade com NBR 6118, NBR 12655, NBR 8953, NBR 7211 e NR-17
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Entradas
st.sidebar.header("📋 Dados da Obra & Identificação")
nome_obra = st.sidebar.text_input("Nome da Obra / Projeto", "Residencial Modelo")
proprietario = st.sidebar.text_input("Proprietário / Cliente", "Cliente Exemplo")
resp_tecnico = st.sidebar.text_input("Responsável Técnico", "Eng. Alex Mário Sales")
registro_prof = st.sidebar.text_input("Registro (CREA/CAU)", "CREA/MS 123456")
art_rrt = st.sidebar.text_input("ART / RRT N°", "ART-2026-98765")

st.sidebar.divider()
st.sidebar.header("⚙️ Parâmetros do Concreto")

# Finalidade com Sugestão de fck
finalidades = {
    "Calçadas e Lastros (C15 - C20)": {"fck": 20.0, "slump": "60-80 mm (Manual / Peças Simples)", "info": "Indicado para peças sem responsabilidade estrutural direta."},
    "Lajes, Vigas e Pisos (C25 - C30)": {"fck": 25.0, "slump": "100-120 mm (Vigas e Lajes Densas)", "info": "Padrão para estruturas residenciais e comerciais."},
    "Pilares e Muros de Arrimo (C35 - C40)": {"fck": 35.0, "slump": "140-160 mm (Fluido / Bombeável)", "info": "Alta responsabilidade estrutural e elevada densidade de aço."},
    "Obras Especiais e Pontes (C45 - C60)": {"fck": 50.0, "slump": "180-220 mm (Auto-adensável)", "info": "Exige controle Classe A e central de dosagem usinada."}
}

finalidade_sel = st.sidebar.selectbox("Finalidade Estrutural", list(finalidades.keys()))
st.sidebar.caption(f"💡 **Diretriz:** {finalidades[finalidade_sel]['info']}")

# Botões de fck por Classe Normativa (NBR 8953)
st.sidebar.subheader("Resistência Característica fck (MPa)")
fck_opcao = st.sidebar.radio(
    "Classe de Resistência (NBR 8953)",
    [15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0],
    index=2,
    horizontal=True
)

controle = st.sidebar.selectbox(
    "Controle Tecnológico (NBR 12655)",
    [
        "Classe A (Central / Usinado - Medição em Massa)",
        "Classe B (Canteiro Medido em Massa)",
        "Classe C (Canteiro Manual / Volumétrico)"
    ]
)

tipo_cimento = st.sidebar.selectbox(
    "Tipo de Cimento Portland (NBR 16697)",
    ["CP I", "CP II-E", "CP II-F", "CP II-Z", "CP III", "CP IV", "CP V-ARI"]
)

st.sidebar.subheader("🧱 Agregados & Trabalhabilidade")
tipo_areia = st.sidebar.selectbox("Agregado Miúdo (Areia)", ["areia_fina", "areia_media", "areia_grossa", "areia_britagem", "areia_industrial"])
tipo_brita = st.sidebar.selectbox("Agregado Graúdo (Brita/Seixo)", ["brita_0", "brita_1", "brita_2", "brita_3", "seixo_rolado", "seixo_misto"])

slump = st.sidebar.selectbox(
    "Consistência / Slump Test (NBR 16889)",
    [
        "60-80 mm (Manual / Peças Simples)",
        "100-120 mm (Vigas e Lajes Densas)",
        "140-160 mm (Fluido / Bombeável)",
        "180-220 mm (Auto-adensável)"
    ],
    index=1
)

aditivo = st.sidebar.selectbox("Aditivos Químicos", ["Nenhum (Sem aditivo)", "Plastificante (-10% Água)", "Superplastificante (-20% Água)"])

st.sidebar.subheader("🌧️ Estado da Areia no Canteiro")
estado_areia = st.sidebar.radio(
    "Umidade da Areia",
    ["Seca (0%)", "Pouco Úmida (3%)", "Úmida / Padrão (5%)", "Encharcada (8%)", "Personalizado"],
    index=2
)

if estado_areia == "Seca (0%)": umidade_val, incham_val = 0.0, 0.0
elif estado_areia == "Pouco Úmida (3%)": umidade_val, incham_val = 3.0, 15.0
elif estado_areia == "Úmida / Padrão (5%)": umidade_val, incham_val = 5.0, 22.0
elif estado_areia == "Encharcada (8%)": umidade_val, incham_val = 8.0, 28.0
else:
    umidade_val = st.sidebar.slider("Umidade Medida (%)", 0.0, 10.0, 5.0)
    incham_val = st.sidebar.slider("Inchaçamento Medido (%)", 0.0, 30.0, 22.0)

# Geometria e Cubagem
st.sidebar.subheader("📐 Geometria para Cubagem")
tipo_elemento = st.sidebar.radio("Tipo de Peça", ["Placa (Laje, Piso, Calçada)", "Barra (Viga, Pilar, Muro)"])

if "Placa" in tipo_elemento:
    comp = st.sidebar.number_input("Comprimento (m)", value=6.0, step=0.5)
    larg = st.sidebar.number_input("Largura (m)", value=4.0, step=0.5)
    esp = st.sidebar.number_input("Espessura (cm)", value=12.0, step=1.0) / 100.0
    qtd = st.sidebar.number_input("Quantidade de Peças", value=1, step=1)
    vol_bruto = comp * larg * esp * qtd
else:
    b = st.sidebar.number_input("Largura da Seção b (cm)", value=20.0, step=5.0) / 100.0
    h = st.sidebar.number_input("Altura da Seção h (cm)", value=40.0, step=5.0) / 100.0
    comprimento_peça = st.sidebar.number_input("Comprimento / Altura (m)", value=3.0, step=0.5)
    qtd = st.sidebar.number_input("Quantidade de Peças", value=4, step=1)
    vol_bruto = b * h * comprimento_peça * qtd

perda = st.sidebar.selectbox("Margem de Perda (%)", [0, 5, 10, 15], index=2)
vol_total = vol_bruto * (1.0 + (perda / 100.0))

dados_obra_dict = {
    "nome_obra": nome_obra,
    "proprietario": proprietario,
    "responsavel_tecnico": resp_tecnico,
    "registro_prof": registro_prof,
    "art_rrt": art_rrt
}

res = CalculadoraDosagem.processar_dosagem(
    fck=fck_opcao,
    controle=controle,
    tipo_cimento=tipo_cimento,
    tipo_areia=tipo_areia,
    tipo_brita=tipo_brita,
    slump=slump,
    aditivo=aditivo,
    umidade_areia_pct=umidade_val,
    inchamento_areia_pct=incham_val,
    volume_m3=vol_total,
    dados_obra=dados_obra_dict
)

# Conteúdo Principal
tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumo da Dosagem", "📈 Curva de Abrams", "👷 Receita de Canteiro", "📄 Exportar PDF"])

with tab1:
    if res["alertas"]:
        for alt in res["alertas"]:
            st.error(alt)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">fck Projetado</div><div class="metric-value">{res["fck"]} MPa</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">fcm28 (Resistência Média)</div><div class="metric-value">{res["fcm28"]} MPa</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Relação Água/Cimento</div><div class="metric-value">{res["relacao_ac"]}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Volume Com Perda</div><div class="metric-value">{vol_total:.2f} m³</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 📝 Traço Seco em Massa: `{res['traco_seco']}` *(Cimento : Areia : Brita)*")

    st.markdown("### 📦 Materiais Totais para a Obra")
    c = res["consumo_m3"]
    ca, cb = st.columns(2)
    with ca:
        st.write(f"• **Cimento Portland ({tipo_cimento}):** `{c['cimento_kg']} kg` ({c['sacos_cimento_50kg']} sacos de 50 kg)")
        st.write(f"• **Areia Úmida ({tipo_areia}):** `{c['areia_umida_kg']} kg` ({c['areia_m3']} m³)")
    with cb:
        st.write(f"• **Brita / Seixo ({tipo_brita}):** `{c['brita_kg']} kg` ({c['brita_m3']} m³)")
        st.write(f"• **Água Efetiva:** `{c['agua_litros']} Litros` *(descontada umidade da areia)*")

with tab2:
    st.subheader("Curva Teórica de Abrams vs Ponto de Operação")
    ac_eixo = np.linspace(0.30, 0.70, 50)
    params = CalculadoraDosagem.PARAMETROS_ABRAMS[tipo_cimento]
    fcm_eixo = params["A"] / (params["B"] ** ac_eixo)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ac_eixo, y=fcm_eixo, mode='lines', name=f'Curva {tipo_cimento}', line=dict(color='#2563EB', width=3)))
    fig.add_trace(go.Scatter(x=[res['relacao_ac']], y=[res['fcm28']], mode='markers+text', name='Dosagem Atual',
                             text=[f"  fcm28 = {res['fcm28']} MPa"], textposition="top right", marker=dict(color='#DC2626', size=12)))

    fig.update_layout(title="Resistência Média aos 28 Dias (fcm28) vs Relação a/c", xaxis_title="Relação Água / Cimento (a/c)", yaxis_title="fcm28 (MPa)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Receita de Canteiro por Saco de Cimento (50 kg)")
    saco = res["dosagem_saco_50kg"]
    
    cs1, cs2, cs3 = st.columns(3)
    with cs1:
        st.markdown('<div class="metric-card"><div class="metric-title">Cimento</div><div class="metric-value">1 Saco</div><div>50 kg</div></div>', unsafe_allow_html=True)
    with cs2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Areia (Padiola NR-17)</div><div class="metric-value">{saco["padiolas_areia"]}</div><div>Padiolas Padronizadas</div></div>', unsafe_allow_html=True)
    with cs3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Brita (Padiola NR-17)</div><div class="metric-value">{saco["padiolas_brita"]}</div><div>Padiolas Padronizadas</div></div>', unsafe_allow_html=True)

    st.markdown(f"🪣 **Água a Adicionar na Betoneira:** `{saco['agua_litros']} Litros` por saco de cimento.")
    st.caption("📏 Padiola NR-17 Padronizada: Dimensões 45 x 35 x 23 cm (Volume = 36.2 Litros). Ergonomia limitada a dois operadores.")

with tab4:
    st.subheader("Gerar Documentos Técnicos com Assinatura")
    
    cp1, cp2 = st.columns(2)
    with cp1:
        st.markdown("#### Ficha Operacional de Canteiro")
        st.write("Ficha simplificada para mestre de obras e pedreiros com dosagem de padiolas, sequência de mistura e bloco de visto.")
        pdf_cant = gerar_pdf_canteiro(res)
        st.download_button("📄 Baixar Ficha de Canteiro (PDF)", data=pdf_cant, file_name=f"ficha_canteiro_{nome_obra}.pdf", mime="application/pdf")

    with cp2:
        st.markdown("#### Dossiê Técnico de Engenharia")
        st.write("Memorial de cálculo completo contendo parâmetros NBR, análise de Abrams, consumo específico e bloco de assinatura para ART/RRT.")
        pdf_tec = gerar_pdf_tecnico(res)
        st.download_button("📑 Baixar Dossiê Técnico (PDF)", data=pdf_tec, file_name=f"dossie_tecnico_{nome_obra}.pdf", mime="application/pdf")
