"""
Motor de Dosagem e Tecnologia do Concreto
Método ABCP/IPT, NBR 12655, NBR 6118, NBR 8953, NBR 7211 e NR-17
"""

import math
from typing import Dict, Any, List


class CalculadoraDosagem:
    # Parâmetros da Lei de Abrams por Tipo de Cimento (A e B da equação: fck = A / B^(a/c))
    PARAMETROS_ABRAMS = {
        "CP I": {"A": 98.0, "B": 12.5},
        "CP II": {"A": 102.0, "B": 13.0},
        "CP III": {"A": 92.0, "B": 11.5},
        "CP IV": {"A": 88.0, "B": 11.0},
        "CP V-ARI": {"A": 115.0, "B": 14.0}
    }

    # Densidades aparentes médias (kg/L ou t/m³)
    DENSIDADES = {
        "cimento": 1.20,
        "areia_fina": 1.42,
        "areia_media": 1.50,
        "areia_grossa": 1.55,
        "areia_britagem": 1.60,
        "brita_0": 1.30,
        "brita_1": 1.35,
        "brita_2": 1.40,
        "seixo_rolado": 1.50,
        "seixo_misto": 1.45
    }

    @staticmethod
    def obter_desvio_padrao(controle: str) -> float:
        controles = {
            "Classe A (Rigoroso - Central/Usina)": 4.0,
            "Classe B (Razoável - Canteiro Medido)": 5.5,
            "Classe C (Regular - Canteiro Manual)": 7.0
        }
        return controles.get(controle, 5.5)

    @classmethod
    def calcular_relacao_ac(cls, fck: float, sd: float, tipo_cimento: str, aditivo: str) -> float:
        fcm28 = fck + (1.65 * sd)
        params = cls.PARAMETROS_ABRAMS.get(tipo_cimento, cls.PARAMETROS_ABRAMS["CP II"])
        
        # Inversão da Lei de Abrams: a/c = log(A / fcm28) / log(B)
        relacao_ac_teorica = math.log(params["A"] / fcm28) / math.log(params["B"])
        
        # Ajustes por aditivo
        if aditivo == "Plastificante (-10% Água)":
            relacao_ac_teorica *= 0.90
        elif aditivo == "Superplastificante (-20% Água)":
            relacao_ac_teorica *= 0.80

        # Limites normativos NBR 6118 (Agressividade Ambiental)
        return max(0.30, min(0.65, round(relacao_ac_teorica, 3)))

    @classmethod
    def processar_dosagem(
        cls,
        fck: float,
        controle: str,
        tipo_cimento: str,
        tipo_areia: str,
        tipo_brita: str,
        slump: str,
        aditivo: str,
        umidade_areia_pct: float,
        inchamento_areia_pct: float,
        volume_m3: float = 1.0
    ) -> Dict[str, Any]:
        
        sd = cls.obter_desvio_padrao(controle)
        fcm28 = fck + (1.65 * sd)
        ac = cls.calcular_relacao_ac(fck, sd, tipo_cimento, aditivo)

        # Consumo aproximado de água por m³ conforme o Slump
        agua_base_m3 = 200.0  # Litros padrão para 100-120mm
        if "60-80" in slump:
            agua_base_m3 = 185.0
        elif "140-160" in slump:
            agua_base_m3 = 210.0
        elif "180-220" in slump:
            agua_base_m3 = 225.0

        if aditivo == "Plastificante (-10% Água)":
            agua_base_m3 *= 0.90
        elif aditivo == "Superplastificante (-20% Água)":
            agua_base_m3 *= 0.80

        # Consumo de cimento (kg/m³)
        cimento_kg_m3 = agua_base_m3 / ac

        # Proporção em massa de agregados (m = total agregados / cimento)
        # Estimativa empírica baseada na massa específica média do concreto (~2350 kg/m³)
        massa_agregados_total_m3 = 2350.0 - cimento_kg_m3 - agua_base_m3
        m_proporcao = massa_agregados_total_m3 / cimento_kg_m3

        # Teor de argamassa seco (alpha) ajustado pelo slump
        alpha_argamassa = 0.48
        if "60-80" in slump:
            alpha_argamassa = 0.45
        elif "140-160" in slump:
            alpha_argamassa = 0.52
        elif "180-220" in slump:
            alpha_argamassa = 0.55

        # Divisão do traço seco 1 : a : b
        a_areia = round(m_proporcao * alpha_argamassa, 2)
        b_brita = round(m_proporcao * (1.0 - alpha_argamassa), 2)

        # Consumos secos por m³
        areia_seca_kg_m3 = cimento_kg_m3 * a_areia
        brita_kg_m3 = cimento_kg_m3 * b_brita

        # Correção da umidade e inchaçamento na areia
        agua_presente_na_areia = areia_seca_kg_m3 * (umidade_areia_pct / 100.0)
        areia_umida_kg_m3 = areia_seca_kg_m3 + agua_presente_na_areia
        agua_efetiva_adicionar_m3 = agua_base_m3 - agua_presente_na_areia

        # Densidade aparente da areia para conversão em volume
        dens_areia = cls.DENSIDADES.get(tipo_areia, 1.50)
        dens_brita = cls.DENSIDADES.get(tipo_brita, 1.35)

        # Padiola Ergonômica NR-17 (36.2 Litros = 0.0362 m³)
        vol_padiola_m3 = 0.0362

        # Quantidades por saco de 50 kg de cimento
        areia_kg_por_saco_seco = 50.0 * a_areia
        brita_kg_por_saco = 50.0 * b_brita
        agua_litros_por_saco_corrigida = (50.0 * ac) - (areia_kg_por_saco_seco * (umidade_areia_pct / 100.0))

        # Volume de areia por saco considerando inchaçamento
        vol_areia_litros_saco = (areia_kg_por_saco_seco / dens_areia) * (1.0 + (inchamento_areia_pct / 100.0))
        vol_brita_litros_saco = (brita_kg_por_saco / dens_brita)

        padiolas_areia_saco = round(vol_areia_litros_saco / (vol_padiola_m3 * 1000.0), 1)
        padiolas_brita_saco = round(vol_brita_litros_saco / (vol_padiola_m3 * 1000.0), 1)

        # Diagnósticos e Alertas Técnicos de Engenharia
        alertas: List[str] = []
        if fck >= 35.0:
            alertas.append("⚠️ **Concreto de Alta Resistência (fck ≥ 35 MPa):** É altamente recomendado o uso de central de dosagem (concreto usinado). O preparo manual em canteiro não garante a homogeneidade e pode comprometer a segurança da estrutura.")
        if fck >= 40.0:
            alertas.append("🚨 **Alerta Normativo NBR 12655:** fck ≥ 40 MPa exige obrigatoriamente controle tecnológico Classe A e medição de agregados em massa. Uso indispensável de aditivos superplastificantes.")
        if "140-160" in slump or "180-220" in slump:
            alertas.append("🚛 **Bombeamento / Fluidez:** Verifique a curva granulométrica da areia. O excesso de brita sem finos adequados causará entupimento da tubulação de bombeamento.")
        if tipo_cimento == "CP III" or tipo_cimento == "CP IV":
            alertas.append("⏱️ **Tempo de Pega e Desforma:** Cimentos com adição de escória (CP III) ou pozolana (CP IV) possuem desenvolvimento de resistência inicial mais lento. Respeite os prazos de desforma.")

        return {
            "fck": fck,
            "sd": sd,
            "fcm28": round(fcm28, 2),
            "relacao_ac": ac,
            "traco_seco": f"1 : {a_areia} : {brita_kg_m3 / cimento_kg_m3:.2f}",
            "consumo_m3": {
                "cimento_kg": round(cimento_kg_m3 * volume_m3, 1),
                "sacos_cimento_50kg": round((cimento_kg_m3 * volume_m3) / 50.0, 1),
                "areia_seca_kg": round(areia_seca_kg_m3 * volume_m3, 1),
                "areia_umida_kg": round(areia_umida_kg_m3 * volume_m3, 1),
                "brita_kg": round(brita_kg_m3 * volume_m3, 1),
                "agua_litros": round(agua_efetiva_adicionar_m3 * volume_m3, 1),
                "areia_m3": round((areia_umida_kg_m3 * volume_m3) / (dens_areia * 1000.0), 2),
                "brita_m3": round((brita_kg_m3 * volume_m3) / (dens_brita * 1000.0), 2)
            },
            "dosagem_por_saco_50kg": {
                "padiolas_areia_nr17": padiolas_areia_saco,
                "padiolas_brita_nr17": padiolas_brita_saco,
                "agua_litros_balde": round(agua_litros_por_saco_corrigida, 1)
            },
            "alertas": alertas
        }
