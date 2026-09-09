"""
Carta Traço de Concreto - Módulo Principal
Cálculo de dosagem de concreto baseado no método ABCP/IPT.
"""

def calcular_fcm(fck: float, sd: float) -> float:
    """
    Calcula a resistência média de dosagem aos 28 dias (fcm28).
    Fórmula: fcm = fck + 1.65 * sd
    """
    return fck + (1.65 * sd)


def obter_desvio_padrao(nivel_controle: str) -> float:
    """
    Retorna o desvio padrão (sd) em MPa com base no nível de controle tecnológico.
    - Rigoroso: 4.0 MPa
    - Razoável: 5.5 MPa
    - Regular:  7.0 MPa
    """
    controles = {
        "rigoroso": 4.0,
        "razoavel": 5.5,
        "regular": 7.0
    }
    return controles.get(nivel_controle.lower(), 5.5)


if __name__ == "__main__":
    # Parâmetros de teste (dados extraídos da planilha)
    fck_projeto = 20.0  # MPa
    controle_tecnologico = "rigoroso"

    sd = obter_desvio_padrao(controle_tecnologico)
    fcm = calcular_fcm(fck_projeto, sd)

    print("=== DOSAGEM DE CONCRETO - CARTA TRAÇO ===")
    print(f"fck especificado: {fck_projeto:.1f} MPa")
    print(f"Controle tecnológico: {controle_tecnologico.capitalize()} (sd = {sd:.1f} MPa)")
    print(f"Resistência de dosagem (fcm28): {fcm:.2f} MPa")
