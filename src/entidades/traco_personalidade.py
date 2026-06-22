from abc import ABC, abstractmethod


class TracoPersonalidade(ABC):
    def __init__(self, nome:str, descricao:str, heroi_dono):
        self._nome = nome
        self._descricao = descricao
        self._heroi_dono = heroi_dono


    @property
    def nome(self):
        return self._nome
    
    @property
    def descricao(self):
        return self._descricao

    @abstractmethod
    def inicializar_hooks(self, event_manager):
        pass

    @abstractmethod
    def avaliar_situacao(self, contexto: dict, decisao: dict):
        pass

    @abstractmethod
    def serializar(self):
        pass
