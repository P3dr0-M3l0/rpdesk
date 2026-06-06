class Modificador:
    def __init__(self, origem_id: str, valor: int, tipo: str):
        self.origem_id = origem_id
        self.valor = valor
        self.tipo = tipo # ("somar" | "multiplicar")
