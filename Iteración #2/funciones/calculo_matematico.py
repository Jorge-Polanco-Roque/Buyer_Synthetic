def calculo_matematico(state):
    a = state["row_data"]["valor1"]
    b = state["row_data"]["valor2"]
    return {"resultado_math": a**2 + b**2}
