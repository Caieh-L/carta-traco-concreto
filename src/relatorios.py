"""
Módulo de Geração de Relatórios Técnicos e Fichas Operacionais em PDF
"""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def gerar_pdf_canteiro(dados: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    elements = []

    # Título Principal
    titulo_style = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#1E3A8A'), alignment=1)
    elements.append(Paragraph("🏗️ FICHA OPERACIONAL DE CANTEIRO - DOSAGEM", titulo_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1E3A8A')))
    elements.append(Spacer(1, 15))

    # Tabela de Mistura por Saco de Cimento
    sub_style = ParagraphStyle('Sub', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F172A'))
    elements.append(Paragraph("📋 Receita Prática por Saco de Cimento (50 kg)", sub_style))
    elements.append(Spacer(1, 8))

    dosagem_saco = dados["dosagem_por_saco_50kg"]
    tabela_data = [
        ["Material", "Quantidade Operacional", "Recipiente Padronizado"],
        ["Cimento Portland", "1 Saco (50 kg)", "Saco Fechado"],
        ["Areia Lavada", f"{dosagem_saco['padiolas_areia_nr17']} Padiolas", "Padiola NR-17 (36.2 Litros)"],
        ["Brita / Seixo", f"{dosagem_saco['padiolas_brita_nr17']} Padiolas", "Padiola NR-17 (36.2 Litros)"],
        ["Água Limpa a Adicionar", f"{dosagem_saco['agua_litros_balde']} Litros", "Balde Graduado (Corrigido por Umidade)"]
    ]

    t = Table(tabela_data, colWidths=[180, 160, 180])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563EB')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Recomendações do Canteiro
    elements.append(Paragraph("⚠️ Orientações de Aplicação e Cura", sub_style))
    elements.append(Spacer(1, 8))

    dicas = [
        "<b>Ordem de Colocação na Betoneira:</b> 1º Toda a água e aditivo -> 2º Todo o agregado graúdo (brita) -> 3º Todo o cimento -> 4º Por último, a areia aos poucos.",
        "<b>Tempo de Mistura:</b> Manter a betoneira girando por no mínimo 3 minutos após a inserção do último componente.",
        "<b>Cura Hidráulica:</b> Iniciar a molhagem contínua da peça 2 horas após a concretagem e manter por pelo menos 7 dias consecutivos."
    ]

    for dica in dicas:
        elements.append(Paragraph(f"• {dica}", styles['BodyText']))
        elements.append(Spacer(1, 5))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def gerar_pdf_tecnico(dados: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    elements = []

    # Título do Relatório
    titulo_style = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#0F172A'), alignment=0)
    elements.append(Paragraph("DOSSIÊ TÉCNICO DE DOSAGEM DE CONCRETO", titulo_style))
    elements.append(Paragraph("MEMORIAL DE CÁLCULO E ESPECIFICAÇÃO NORMATIVA", ParagraphStyle('Subhead', parent=styles['Normal'], textColor=colors.HexColor('#64748B'))))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0F172A')))
    elements.append(Spacer(1, 15))

    # Tabela de Parâmetros Normativos
    elements.append(Paragraph("1. Parâmetros do Projeto e Dosagem Científica", styles['Heading2']))
    elements.append(Spacer(1, 8))

    param_data = [
        ["Parâmetro Normativo", "Valor Especificado", "Referência / Norma"],
        ["Resistência Característica (fck)", f"{dados['fck']} MPa", "NBR 6118"],
        ["Desvio Padrão de Dosagem (sd)", f"{dados['sd']} MPa", "NBR 12655"],
        ["Resistência Média aos 28 dias (fcm28)", f"{dados['fcm28']} MPa", "Lei de Abrams"],
        ["Relação Água / Cimento (a/c)", f"{dados['relacao_ac']}", "Durabilidade NBR 6118"],
        ["Traço Seco em Massa (1 : a : b)", f"{dados['traco_seco']}", "Método ABCP/IPT"]
    ]

    t = Table(param_data, colWidths=[200, 140, 180])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Consumo Consolidado por m³
    elements.append(Paragraph("2. Consumo de Materiais por Metro Cúbico (m³)", styles['Heading2']))
    elements.append(Spacer(1, 8))

    consumo = dados["consumo_m3"]
    consumo_data = [
        ["Insumo", "Massa Seca / Volume", "Massa Corrigida / Depósito"],
        ["Cimento Portland", f"{consumo['cimento_kg']} kg", f"{consumo['sacos_cimento_50kg']} Sacos (50 kg)"],
        ["Agregado Miúdo (Areia)", f"{consumo['areia_seca_kg']} kg", f"{consumo['areia_umida_kg']} kg ({consumo['areia_m3']} m³)"],
        ["Agregado Graúdo (Brita)", f"{consumo['brita_kg']} kg", f"{consumo['brita_kg']} kg ({consumo['brita_m3']} m³)"],
        ["Água Efetiva", f"{consumo['agua_litros']} Litros", f"{consumo['agua_litros']} Litros"]
    ]

    t2 = Table(consumo_data, colWidths=[180, 170, 170])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 20))

    # Diagnósticos de Engenharia
    if dados["alertas"]:
        elements.append(Paragraph("3. Diagnóstico de Segurança e Diretrizes de Execução", styles['Heading2']))
        elements.append(Spacer(1, 8))
        for alerta in dados["alertas"]:
            # Remover tags markdown para exibição no PDF
            alerta_limpo = alerta.replace("**", "").replace("⚠️ ", "").replace("🚨 ", "").replace("🚛 ", "").replace("⏱️ ", "")
            elements.append(Paragraph(f"• {alerta_limpo}", styles['BodyText']))
            elements.append(Spacer(1, 4))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
