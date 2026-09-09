"""
Módulo de Utilitários e Conversões para Canteiro de Obras
Converte traço em massa para dosagem volumétrica (latas de 18L por saco de cimento).
"""

def converter_para_canteiro(consumo_m3: dict, massa_esp_areia: float = 1.5, massa_esp_brita: float = 1.35) -> dict:
    """
    Calcula as quantidades operacionais por saco de cimento de 50 kg.
    - massa_esp_areia: densidade aparente da areia seca (kg/L)
    - massa_esp_brita: densidade aparente da brita (kg/L)
    """
    cimento_kg = consumo_m3["cimento_kg"]
    
    # Proporções em kg por saco de cimento (50 kg)
    areia_kg_saco = (consumo_m3["areia_kg"] / cimento_kg) * 50.0
    brita_kg_saco = (consumo_m3["brita_kg"] / cimento_kg) * 50.0
    agua_l_saco = (consumo_m3["agua_litros"] / cimento_kg) * 50.0

    # Conversão para latas de 18 Litros
    latas_areia = (areia_kg_saco / massa_esp_areia) / 18.0
    latas_brita = (brita_kg_saco / massa_esp_brita) / 18.0
    latas_agua = agua_l_saco / 18.0

    return {
        "sacos_cimento": 1.0,
        "areia_latas_18l": round(latas_areia, 1),
        "brita_latas_18l": round(latas_brita, 1),
        "agua_latas_18l": round(latas_agua, 1),
        "agua_litros_saco": round(agua_l_saco, 1)
    }
