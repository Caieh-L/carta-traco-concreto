"""
Carta Traço de Concreto - Módulo Principal
Integra os cálculos de dosagem e a conversão de materiais para canteiro.
"""

from src.dosagem import calcular_traco_seco, consumo_materiais_m3
from src.utils import converter_para_canteiro


def obter_desvio_padrao(nivel_controle: str) -> float:
    controles = {
        "rigoroso": 4.0,
        "razoavel": 5.5,
        "regular": 7.0
    }
    return controles.get(nivel_controle.lower(), 5.5)


if __name__ == "__main__":
    # Parâmetros de entrada (extraídos da planilha de referência)
    fck_projeto = 20.0  # MPa
    controle_tecnologico = "rigoroso"
    m_agregados = 4.22  # Proporção total de agregados / cimento
    alpha_argamassa = 0.474  # 47.4% de teor de argamassa seca
    relacao_ac = 0.47

    # 1. Desvio padrão e resistência de dosagem
    sd = obter_desvio_padrao(controle_tecnologico)
    fcm28 = fck_projeto + (1.65 * sd)

    # 2. Traço seco
    traco_seco = calcular_traco_seco(m_agregados, alpha_argamassa, relacao_ac)

    # 3. Consumo de materiais por m³
    consumo = consumo_materiais_m3(traco_seco)

    # 4. Conversão para canteiro de obras
    canteiro = converter_para_canteiro(consumo)

    # Exibição dos resultados no terminal
    print("==================================================")
    print("          DOSAGEM DE CONCRETO - CARTA TRAÇO       ")
    print("==================================================")
    print(f"Resistência fck: {fck_projeto:.1f} MPa")
    print(f"Desvio Padrão (sd): {sd:.1f} MPa | fcm28: {fcm28:.2f} MPa")
    print("--------------------------------------------------")
    print("Traço Seco em Massa (1 : a : b):")
    print(f"1 : {traco_seco['areia']} : {traco_seco['brita']} (a/c = {traco_seco['agua']})")
    print("--------------------------------------------------")
    print("Consumo por m³:")
    print(f"- Cimento: {consumo['cimento_kg']} kg")
    print(f"- Areia:   {consumo['areia_kg']} kg")
    print(f"- Brita:   {consumo['brita_kg']} kg")
    print(f"- Água:    {consumo['agua_litros']} L")
    print("--------------------------------------------------")
    print("Quantidade por Saco de Cimento (50 kg):")
    print(f"- Areia: {canteiro['areia_latas_18l']} latas de 18L")
    print(f"- Brita: {canteiro['brita_latas_18l']} latas de 18L")
    print(f"- Água:  {canteiro['agua_latas_18l']} latas ({canteiro['agua_litros_saco']} L)")
    print("==================================================")
