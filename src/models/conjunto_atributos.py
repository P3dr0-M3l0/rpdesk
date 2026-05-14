from core.event_manager import EventManager


class ConjuntoDeAtributos():

    def __init__(self, forca, destreza, inteligencia, velocidade, hp_max):
        self.__forca = forca
        self.__destreza = destreza
        self.__inteligencia = inteligencia
        self.__velocidade = velocidade
        self.__hp_max = hp_max
        self.__hp_atual = hp_max
        
        
        

    @staticmethod
    def __verificar_valor(valor, min, max):
        try:
            valor = int(valor)
        except ValueError:
            raise ValueError("ERRO: Entrada não é um número")
        
        if valor >= min and valor <= max:
            return valor
        else:
            raise ValueError("ERRO: Valor fora da faixa")

    # FORCA
    @property
    def forca(self):
        return self.__forca
   
    # DESTREZA
    @property
    def destreza(self):
        return self.__destreza

    # INTELIGENCIA
    @property
    def inteligencia(self):
        return self.__inteligencia
        
    # VELOCIDADE
    @property
    def velocidade(self):
        return self.__velocidade
        
    # HP MAX
    @property
    def hp_max(self):
        return self.__hp_max
        
    # HP ATUAL
    @property
    def hp_atual(self):
        return self.__hp_atual
        
        
    def receber_dano(self, valor):
        self.__hp_atual -= valor
        if self.__hp_atual < 0:
            self.__hp_atual = 0