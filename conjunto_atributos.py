class ConjuntoDeAtributos():

    def __init__(self, forca, destreza, inteligencia, velocidade, hp_max):
        self.__forca = forca
        self.__destreza = destreza
        self.__inteligencia = inteligencia
        self.__velocidade = velocidade
        self.__hp_max = hp_max

    @property
    def get_forca(self):
        return self.__forca

    @forca.setter
    def forca(self, valor):
        try:
            valor = int(valor)
        except ValueError:
            return "ERRO: Atribuição Inválida"
        
        if valor >= 0 and valor <= 1000:
            self.forca == valor
        else:
            return "ERRO: Valor fora da faixa"
