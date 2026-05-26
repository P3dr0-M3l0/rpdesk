import json


class SaveManager():
    
    def __init__(self, caminho_arquivo, event_manager):
        self.__caminho_arquivo = caminho_arquivo
        self.__event_manager = event_manager
        
    
    def salvar_estado(self, game_state):
        ...
        
    def carregar_estado_para(self, game_state):
        ...