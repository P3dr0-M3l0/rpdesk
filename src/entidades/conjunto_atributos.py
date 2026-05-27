from core.event_manager import EventManager


class ConjuntoDeAtributos():

    def __init__(self, forca, destreza, inteligencia, velocidade, hp_max, event_manager):
        self.__forca = forca
        self.__destreza = destreza
        self.__inteligencia = inteligencia
        self.__velocidade = velocidade
        self.__hp_max = hp_max
        self.__hp_atual = hp_max
        self.__event_manager = event_manager

    # GETTERS -----------------------------------------------------------
    
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

    # --------------------------------------------------------------------------

    def calcular_defesa_attr(self):
        
        # Verificar a defesa a partir dos atributos, como destreza
        
        ...
    
    
    def receber_dano(self, valor):
        
        self.__hp_atual -= valor
        if self.__hp_atual < 0:
            self.__hp_atual = 0
            
        return self.hp_atual
    
    def aplicar_buff_temporario(self, str_atributo, valor):
        ...
            
    def calcular_modificador(self, str_atributo):
        ...

    def serializar(self):
        dicionario_conjunto_attr = {
            'AT_forca'        : self.__forca,
            'AT_destreza'     : self.__destreza,
            'AT_inteligencia' : self.__inteligencia,
            'AT_velocidade'   : self.__velocidade,
            'AT_hp_max'       : self.__hp_max,
            'AT_hp_atual'     : self.__hp_atual
        }
        return dicionario_conjunto_attr
