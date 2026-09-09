"""
Módulo de Impressão PDF - Fichas Operacionais e Dossiê Técnico
Com alinhamento rigoroso e Bloco de Assinatura do Responsável Técnico
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def criar_bloco_assinatura(dados_obra: dict, styles) -> List:
    elementos = []
    elementos.append(Spacer(1, 15))
    elementos.append(Paragraph("<b>4. Responsabilidade Técnica e Identificação da Obra</b>", styles['Heading2']))
    elementos.append(Spacer(1, 8))

    obra = dados_obra.get("nome_obra", "Não Informada")
    prop = dados_obra.get("proprietario", "Não Informado")
    resp = dados_obra.get("responsavel_tecnico", "Engenheiro / Arquiteto Responsável")
    crea = dados_obra.get("registro_prof", "CREA/CAU N° ---")
    art = dados_obra.get("art_rrt", "ART/RRT N° ---")

    t_data = [
        [Paragraph(f"<b>Obra:</b> {obra}", styles['Normal']), Paragraph(f"<b>Proprietário:</b> {prop}", styles['Normal'])],
        [Paragraph(f"<b>Responsável Técnico:</b> {resp}", styles['Normal']), Paragraph(f"<b>Registro:</b> {crea}", styles['Normal'])],
        [Paragraph(f"<b>ART/RRT:</b> {art}", styles['Normal']), Paragraph("<b>Data:</b> ____/____/2026", styles['Normal'])]
    ]

    t_info = Table(t_data, colWidths=[270, 270])
    t_info.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elementos.append(t_info)
    elementos.append(Spacer(1, 25))

    # Campo de Assinatura
    t_sig = Table([
        ["__________________________________________________", "__________________________________________________"],
        [f"{resp}", "Fiscalização / Controle Tecnológico"],
        [f"{crea} | ART: {art}", "Visto do Responsável da Obra"]
    ], colWidths=[270, 270])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#334155')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elementos.append(t_sig)
    return elementos

def gerar_pdf_canteiro(dados: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    elements = []

    title_style = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#1E3A8A'), alignment=0)
    elements.append(Paragraph("FICHA OPERACIONAL DE CANTEIRO — MISTURA DE CONCRETO", title_style))
    elements.append(Paragraph("Orientações Práticas de Dosagem | Conforme NBR 12655 e NR-17", ParagraphStyle('Sub', parent=styles['Normal'], textColor=colors.HexColor('#64748B'))))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A')))
    elements.append(Spacer(1, 12))

    saco = dados["dosagem_saco_50kg"]
    t_data = [
        [Paragraph("<b>Componente</b>", styles['Normal']), Paragraph("<b>Quantidade por Saco de Cimento (50 kg)</b>", styles['Normal']), Paragraph("<b>Recipiente Medidor</b>", styles['Normal'])],
        [Paragraph("Cimento Portland", styles['Normal']), Paragraph("1 Saco Fechado (50 kg)", styles['Normal']), Paragraph("Embalagem de Fábrica", styles['Normal'])],
        [Paragraph("Areia Lavada", styles['Normal']), Paragraph(f"<b>{saco['padiolas_areia']} Padiolas</b>", styles['Normal']), Paragraph("Padiola NR-17 (36.2 Litros)", styles['Normal'])],
        [Paragraph("Brita / Seixo", styles['Normal']), Paragraph(f"<b>{saco['padiolas_brita']} Padiolas</b>", styles['Normal']), Paragraph("Padiola NR-17 (36.2 Litros)", styles['Normal'])],
        [Paragraph("Água Limpa Efetiva", styles['Normal']), Paragraph(f"<b>{saco['agua_litros']} Litros</b>", styles['Normal']), Paragraph("Balde Graduado (Já descontada a chuva)", styles['Normal'])]
    ]

    t = Table(t_data, colWidths=[150, 190, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>Procedimento de Mistura na Betoneira:</b>", styles['Heading2']))
    recom = [
        "1. Adicionar 80% da água limpa e todo o aditivo (se especificado).",
        "2. Adicionar 100% da brita/seixo e girar a betoneira por 1 minuto para lavar as pás.",
        "3. Adicionar 100% do cimento Portland.",
        "4. Adicionar 100% da areia aos poucos e completar com o restante da água.",
        "5. Manter a betoneira girando por no mínimo 3 minutos antes de descarregar."
    ]
    for r in recom:
        elements.append(Paragraph(r, styles['Normal']))
        elements.append(Spacer(1, 3))

    elements.extend(criar_bloco_assinatura(dados.get("dados_obra", {}), styles))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def gerar_pdf_tecnico(dados: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    elements = []

    title_style = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0F172A'), alignment=0)
    elements.append(Paragraph("DOSSIÊ TÉCNICO DE DOSAGEM DE CONCRETO E PROJETO", title_style))
    elements.append(Paragraph("Memorial de Cálculo Científico — NBR 6118, NBR 12655 e NBR 8953", ParagraphStyle('Sub', parent=styles['Normal'], textColor=colors.HexColor('#64748B'))))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0F172A')))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>1. Parâmetros de Projeto e Correlações Normativas</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))

    p_data = [
        [Paragraph("<b>Parâmetro</b>", styles['Normal']), Paragraph("<b>Valor Especificado</b>", styles['Normal']), Paragraph("<b>Fundamento Normativo</b>", styles['Normal'])],
        [Paragraph("Resistência Característica (fck)", styles['Normal']), Paragraph(f"{dados['fck']} MPa", styles['Normal']), Paragraph("NBR 8953 / NBR 6118", styles['Normal'])],
        [Paragraph("Desvio Padrão de Dosagem (sd)", styles['Normal']), Paragraph(f"{dados['sd']} MPa", styles['Normal']), Paragraph("NBR 12655", styles['Normal'])],
        [Paragraph("Resistência Média aos 28 Dias (fcm28)", styles['Normal']), Paragraph(f"{dados['fcm28']} MPa", styles['Normal']), Paragraph("Lei de Abrams (fcm = fck + 1.65*sd)", styles['Normal'])],
        [Paragraph("Relação Água / Cimento (a/c)", styles['Normal']), Paragraph(f"{dados['relacao_ac']}", styles['Normal']), Paragraph("Durabilidade e Agressividade NBR 6118", styles['Normal'])],
        [Paragraph("Traço Seco em Massa", styles['Normal']), Paragraph(f"{dados['traco_seco']}", styles['Normal']), Paragraph("Método ABCP / IPT", styles['Normal'])]
    ]

    t_p = Table(p_data, colWidths=[180, 160, 200])
    t_p.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_p)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>2. Consumo Consolidado de Materiais por Metro Cúbico (m³)</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))

    c = dados["consumo_m3"]
    c_data = [
        [Paragraph("<b>Insumo</b>", styles['Normal']), Paragraph("<b>Massa Seca / Vol.</b>", styles['Normal']), Paragraph("<b>Massa Úmida / Embalagem</b>", styles['Normal'])],
        [Paragraph("Cimento Portland", styles['Normal']), Paragraph(f"{c['cimento_kg']} kg", styles['Normal']), Paragraph(f"{c['sacos_cimento_50kg']} Sacos (50 kg)", styles['Normal'])],
        [Paragraph("Areia (Agregado Miúdo)", styles['Normal']), Paragraph(f"{c['areia_seca_kg']} kg", styles['Normal']), Paragraph(f"{c['areia_umida_kg']} kg ({c['areia_m3']} m³)", styles['Normal'])],
        [Paragraph("Brita / Seixo (Agregado Graúdo)", styles['Normal']), Paragraph(f"{c['brita_kg']} kg", styles['Normal']), Paragraph(f"{c['brita_kg']} kg ({c['brita_m3']} m³)", styles['Normal'])],
        [Paragraph("Água Efetiva a Adicionar", styles['Normal']), Paragraph(f"{c['agua_litros']} Litros", styles['Normal']), Paragraph(f"{c['agua_litros']} Litros", styles['Normal'])]
    ]

    t_c = Table(c_data, colWidths=[180, 160, 200])
    t_c.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_c)
    elements.append(Spacer(1, 12))

    if dados["alertas"]:
        elements.append(Paragraph("<b>3. Parecer Tecnológico e Advertências Normativas</b>", styles['Heading2']))
        elements.append(Spacer(1, 6))
        for alt in dados["alertas"]:
            clean_alt = alt.replace("**", "").replace("🚨 ", "").replace("⚠️ ", "").replace("🏗️ ", "")
            elements.append(Paragraph(f"• {clean_alt}", styles['Normal']))
            elements.append(Spacer(1, 3))

    elements.extend(criar_bloco_assinatura(dados.get("dados_obra", {}), styles))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
