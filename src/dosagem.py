"""
Motor Especialista de Dosagem e Tecnologia do Concreto
Atende NBR 12655, NBR 6118, NBR 8953, NBR 7211, NBR 16697 e NR-17
"""

import math
from typing import Dict, Any, List

class CalculadoraDosagem:
    PARAMETROS_ABRAMS = {
        "CP I": {"A": 98.0, "B": 12.5},
        "CP II-E": {"A": 102.0, "B": 13.0},
        "CP II-F": {"A": 100.0, "B": 12.8},
        "CP II-Z": {"A": 99.0, "B": 12.6},
        "CP III": {"A": 92.0, "B": 11.5},
        "CP IV": {"A": 88.0, "B": 11.0},
        "CP V-ARI": {"A": 118.0, "B": 14.2}
    }

    DENSIDADES = {
        "areia_fina": 1.42,
        "areia_media": 1.50,
        "areia_grossa": 1.55,
        "areia_britagem": 1.60,
        "areia_industrial": 1.58,
        "brita_0": 1.30,
        "brita_1": 1.35,
        "brita_2": 1.40,
        "brita_3": 1.45,
        "seixo_rolado": 1.50,
        "seixo_misto": 1.45
    }

    @staticmethod
    def obter_desvio_padrao(controle: str) -> float:
        controles = {
            "Classe A (Central / Usinado - Medição em Massa)": 4.0,
            "Classe B (Canteiro Medido em Massa)": 5.5,
            "Classe C (Canteiro Manual / Volumétrico)": 7.0
        }
        return controles.get(controle, 5.5)

    @classmethod
    def validar_incompatividades(
        cls, fck: float, controle: str, tipo_cimento: str, aditivo: str, slump: str, tipo_brita: str
    ) -> List[str]:
        alertas = []

        if fck >= 35.0 and "Classe C" in controle:
            alertas.append("🚨 **IMPEDIMENTO NORMATIVO (NBR 12655):** fck ≥ 35 MPa exige obrigatoriamente Controle Classe A ou B (medição em massa). O preparo manual/volumétrico (Classe C) é PROIBIDO para esta resistência.")

        if fck >= 40.0 and tipo_cimento in ["CP I", "CP II-F"] and "Superplastificante" not in aditivo:
            alertas.append("⚠️ **INCOMPATIBILIDADE TÉCNICA:** Para fck ≥ 40 MPa com cimentos convencionais, é indispensável o uso de aditivo Superplastificante para reduzir a relação água/cimento sem comprometer a trabalhabilidade.")

        if "180-220" in slump and "Nenhum" in aditivo:
            alertas.append("🚨 **RISCO DE SEGREGAÇÃO:** Abatimento elevado (180-220 mm) obtido apenas com adição de água gera exsudação, perda de resistência e fissuração. Utilize aditivo Plastificante ou Superplastificante.")

        if fck >= 45.0 and "seixo" in tipo_brita:
            alertas.append("⚠️ **ALERTA DE ADERÊNCIA:** Para fck ≥ 45 MPa, o uso de seixo rolado (superfície lisa) reduz a aderência pasta-agregado. Recomenda-se Brita 1 ou 2 de rocha britada (granito/basalto).")

        if fck >= 50.0:
            alertas.append("🏗️ **CONCRETO DE ALTA RESISTÊNCIA (CAD):** Exige usinagem com controle rigoroso de umidade dos agregados, análise do calor de hidratação e cura úmida contínua imediata.")

        return alertas

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
        volume_m3: float = 1.0,
        dados_obra: Dict[str, str] = None
    ) -> Dict[str, Any]:

        sd = cls.obter_desvio_padrao(controle)
        fcm28 = fck + (1.65 * sd)
        
        params = cls.PARAMETROS_ABRAMS.get(tipo_cimento, cls.PARAMETROS_ABRAMS["CP II-E"])
        ac_teorico = math.log(params["A"] / fcm28) / math.log(params["B"])

        if "Plastificante" in aditivo:
            ac_teorico *= 0.90
        elif "Superplastificante" in aditivo:
            ac_teorico *= 0.80

        ac_final = max(0.30, min(0.65, round(ac_teorico, 3)))

        agua_base = 200.0
        if "60-80" in slump: agua_base = 185.0
        elif "140-160" in slump: agua_base = 210.0
        elif "180-220" in slump: agua_base = 225.0

        if "Plastificante" in aditivo: agua_base *= 0.90
        elif "Superplastificante" in aditivo: agua_base *= 0.80

        cimento_kg = agua_base / ac_final
        massa_agregados = 2350.0 - cimento_kg - agua_base
        m_proporcao = massa_agregados / cimento_kg

        alpha = 0.48
        if "60-80" in slump: alpha = 0.45
        elif "140-160" in slump: alpha = 0.52
        elif "180-220" in slump: alpha = 0.55

        a_areia = round(m_proporcao * alpha, 2)
        b_brita = round(m_proporcao * (1.0 - alpha), 2)

        areia_seca_kg = cimento_kg * a_areia
        brita_kg = cimento_kg * b_brita

        agua_areia = areia_seca_kg * (umidade_areia_pct / 100.0)
        areia_umida_kg = areia_seca_kg + agua_areia
        agua_efetiva = agua_base - agua_areia

        dens_areia = cls.DENSIDADES.get(tipo_areia, 1.50)
        dens_brita = cls.DENSIDADES.get(tipo_brita, 1.35)

        vol_padiola_m3 = 0.0362 # Padiola NR-17 (36.2 Litros)

        areia_saco_seca = 50.0 * a_areia
        brita_saco = 50.0 * b_brita
        agua_saco = (50.0 * ac_final) - (areia_saco_seca * (umidade_areia_pct / 100.0))

        vol_areia_saco = (areia_saco_seca / dens_areia) * (1.0 + (inchamento_areia_pct / 100.0))
        vol_brita_saco = (brita_saco / dens_brita)

        padiolas_areia = round(vol_areia_saco / (vol_padiola_m3 * 1000.0), 1)
        padiolas_brita = round(vol_brita_saco / (vol_padiola_m3 * 1000.0), 1)

        alertas = cls.validar_incompatividades(fck, controle, tipo_cimento, aditivo, slump, tipo_brita)

        return {
            "fck": fck,
            "sd": sd,
            "fcm28": round(fcm28, 2),
            "relacao_ac": ac_final,
            "traco_seco": f"1 : {a_areia} : {b_brita}",
            "consumo_m3": {
                "cimento_kg": round(cimento_kg * volume_m3, 1),
                "sacos_cimento_50kg": round((cimento_kg * volume_m3) / 50.0, 1),
                "areia_seca_kg": round(areia_seca_kg * volume_m3, 1),
                "areia_umida_kg": round(areia_umida_kg * volume_m3, 1),
                "brita_kg": round(brita_kg * volume_m3, 1),
                "agua_litros": round(agua_efetiva * volume_m3, 1),
                "areia_m3": round((areia_umida_kg * volume_m3) / (dens_areia * 1000.0), 2),
                "brita_m3": round((brita_kg * volume_m3) / (dens_brita * 1000.0), 2)
            },
            "dosagem_saco_50kg": {
                "padiolas_areia": padiolas_areia,
                "padiolas_brita": padiolas_brita,
                "agua_litros": round(agua_saco, 1)
            },
            "alertas": alertas,
            "dados_obra": dados_obra or {}
        }
