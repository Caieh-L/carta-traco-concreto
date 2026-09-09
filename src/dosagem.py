"""
Módulo de Dosagem de Concreto (Método ABCP/IPT)
Cálculos de traço seco, consumo de materiais e proporções volumétricas.
"""

def calcular_traco_seco(m: float, alpha: float, ac: float) -> dict:
    """
    Calcula as proporções do traço seco em massa (1 : a : b).
    - m: proporção agregados/cimento (m = a + b)
    - alpha: teor de argamassa em decimal (ex: 0.47 para 47%)
    - ac: relação água/cimento
    """
    # Proporção de areia (a) e brita (b)
    a = (m + 1) * alpha - 1
    b = m - a

    return {
        "cimento": 1.0,
        "areia": round(a, 2),
        "brita": round(b, 2),
        "agua": round(ac, 2),
        "m_total": m
    }


def consumo_materiais_m3(traco: dict, gamma_c: float = 2350.0) -> dict:
    """
    Calcula o consumo de materiais por metro cúbico (kg/m³) de concreto.
    - gamma_c: massa específica do concreto fresco (padrão ~2350 kg/m³)
    """
    m = traco["m_total"]
    ac = traco["agua"]
    
    # Consumo de cimento (kg/m³)
    c = gamma_c / (1 + m + ac)
    
    areia_kg = c * traco["areia"]
    brita_kg = c * traco["brita"]
    agua_l = c * ac

    return {
        "cimento_kg": round(c, 1),
        "areia_kg": round(areia_kg, 1),
        "brita_kg": round(brita_kg, 1),
        "agua_litros": round(agua_l, 1)
    }
