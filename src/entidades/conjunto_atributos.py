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

    # ===============================================
    # GETTERS ---------------------------------------
    # ===============================================
    
    # Getters do Objeto Atributo
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
    
    # Getters do valor numérico com modificações
    # FORCA
    @property
    def valor_forca(self):
        return self.__forca.valor_total
    # DESTREZA
    @property
    def valor_destreza(self):
        return self.__destreza.valor_total
    # INTELIGENCIA
    @property
    def valor_inteligencia(self):
        return self.__inteligencia.valor_total
    # VELOCIDADE
    @property
    def valor_velocidade(self):
        return self.__velocidade.valor_total
    # HP MAX
    @property
    def valor_hp_max(self):
        return self.__hp_max.valor_total
    # HP ATUAL
    @property
    def valor_hp_atual(self):
        return self.__hp_atual.valor_total

    # ===============================================
    # Matemática ------------------------------------
    # ===============================================
    def calcular_defesa_attr(self):
        # Verificar a defesa a partir dos atributos, como destreza
        ...
    
    def receber_dano(self, valor):
        
        self.__hp_atual -= valor
        if self.__hp_atual < 0:
            self.__hp_atual = 0
            
        return self.hp_atual
    
    def aplicar_buff_temporario(self, str_atributo, modificador):
        ...
        
    def remover_buff_temporario(self, str_atributo, modificador):
        ...
            
    def calcular_modificador(self, str_atributo):
        ...

    # ===============================================
    # Para save -------------------------------------
    # ===============================================
    def serializar(self):
        dicionario_conjunto_attr = {
            'AT_forca'        : self.__forca.valor_base,
            'AT_destreza'     : self.__destreza.valor_base,
            'AT_inteligencia' : self.__inteligencia.valor_base,
            'AT_velocidade'   : self.__velocidade.valor_base,
            'AT_hp_max'       : self.__hp_max.valor_base,
            'AT_hp_atual'     : self.__hp_atual.valor_base
        }
        return dicionario_conjunto_attr
