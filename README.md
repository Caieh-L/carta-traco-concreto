# Carta Traço de Concreto 🏗️

Ferramenta de automação em Python para cálculo de dosagem de concreto (Método ABCP/IPT) e conversão de traço em massa para medidas operacionais de canteiro de obras.

## 📋 Funcionalidades

- **Cálculo da Resistência de Dosagem ($f_{cm28}$):** Aplicação de margens de segurança normativas baseadas no desvio padrão ($s_d$).
- **Determinação do Traço Seco em Massa:** Proporção $1 : a : b$ e relação água/cimento ($a/c$).
- **Consumo de Materiais por $\text{m}^3$:** Cálculo automático de cimento, areia, brita e água.
- **Conversão para Canteiro:** Proporção prática em latas de 18L por saco de cimento ($50\text{ kg}$).

## 📁 Estrutura do Projeto

```text
carta-traco-concreto/
│
├── main.py              # Script principal de execução
├── requirements.txt     # Dependências do projeto
├── README.md            # Documentação
└── src/                 # Módulos de lógica de engenharia
    ├── dosagem.py       # Algoritmos de dosagem ABCP/IPT
    └── utils.py         # Conversões para canteiro de obras
