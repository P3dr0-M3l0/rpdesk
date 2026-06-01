class GameState():
    
    def __init__(self, guilda, taverna, dia_atual, marco_historia, list_missoes_concluidas):
        self.__dia_atual = dia_atual
        self.__guilda = guilda
        self.__taverna = taverna
        self.__marco_historia = marco_historia
        self.__list_missoes_concluidas = list_missoes_concluidas
    

    # =====================================================
    # Getter e Setters ------------------------------------
    # =====================================================        
    @property
    def dia_atual(self):
        return self.__dia_atual
    
    @dia_atual.setter
    def dia_atual(self, valor):
        if valor <= 0:
            raise ValueError("Erro: Dia inteiro não positivo não é permitido")
        self.__dia_atual = valor
    
    @property
    def guilda(self):
        return self.__guilda
    
    @property
    def taverna(self):
        return self.__taverna
    
    @property 
    def marco_historia(self):
        return self.__marco_historia
    
    @property
    def list_missoes_concluidas(self):
        return self.__list_missoes_concluidas
    
    # =====================================================
    # Gerenciamento do Dia---------------------------------
    # =====================================================        
    def incrementar_dia(self):
        self.__dia_atual += 1
    
    # =====================================================
    # Serialização e Desserialização-----------------------
    # =====================================================        
    def get_estado_para_save(self):
        
        guilda_serializada = self.__guilda.serializar()
        
        taverna_serializada = self.__taverna.serializar()
        
        dicionario_obj = {
            'GS_guilda': guilda_serializada,
            'GS_taverna': taverna_serializada,
            'GS_dia_atual': self.__dia_atual,
            'GS_marco_historia': self.__marco_historia,
            'GS_list_missoes_concluidas': self.list_missoes_concluidas
        }
        
        return dicionario_obj
    
        
    def carregar_estado(): # entra um dict de dados (o json)
        ...