from entidades.modificador import Modificador


class Atributo:
    def __init__(self, valor_base: int, modificadores: list[Modificador]):
        self.__valor_base = valor_base
        self.__modificadores = modificadores # Lista de objetos Modificadores
        
    
    @property
    def valor_base(self):
        return self.__valor_base
    
    @valor_base.setter
    def valor_base(self, valor:int):
        if not isinstance(valor, int):
            raise TypeError("Erro: Valor deve ser um inteiro")
        self.__valor_base = valor

    @property
    def valor_total(self):
        somas = 0
        multiplicacoes = 0
        for modificador in self.__modificadores:
            if modificador.tipo == "somar":
                somas += modificador.valor
            elif modificador.tipo == "multiplicar":
                multiplicacoes += modificador.valor
        total = (self.__valor_base + somas) * (1 + multiplicacoes)
        return total
    
    def adicionar_modificador(self, modificador):
        if not isinstance(modificador, Modificador):
            raise TypeError("Erro: Era esperado um objeto do tipo Modificador")
        if modificador is None:
            raise ValueError("Erro: Modificador não possui valores")
        if modificador not in self.__modificadores:
            self.__modificadores.append(modificador)
            
    def remover_modificadores_por_origem(self, origem_id: str):
        indices = []
        for i in range(len(self.__modificadores)):
            if self.__modificadores[i].origem_id == origem_id:
                indices.append(i)
        for i in indices:
            self.__modificadores.pop(i)