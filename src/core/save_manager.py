import json
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class SaveManager():
    
    def __init__(self, caminho_arquivo):
        self.__caminho_arquivo = caminho_arquivo

    
    def resumo_slots(self):
        ...
    
    def salvar_estado(self, game_state):
        dir_save = game_state.get_estado_para_save()
        with open(f"{self.__caminho_arquivo}", "w", encoding="utf-8") as arq:
            json.dump(dir_save, arq, indent=4, ensure_ascii=False, cls=UUIDEncoder)
        
    def carregar_save(self):
        with open(f"{self.__caminho_arquivo}", 'r', encoding="utf-8") as arq:
            try:
                dict_save = json.load(arq)
            except json.decoder.JSONDecodeError:
                return None
        return dict_save
