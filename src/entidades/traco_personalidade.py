from abc import ABC, abstractmethod


class TracoPersonalidade(ABC):
    def __init__(self, nome:str, descricao:str, heroi_dono):
        self._nome = nome
        self._descricao = descricao
        self._heroi_dono = heroi_dono


    @abstractmethod
    def inicializar_hooks(self, event_manager):
        pass

    @abstractmethod
    def avaliar_situacao(self, contexto):
        pass

    @abstractmethod
    def serializar(self):
        pass
