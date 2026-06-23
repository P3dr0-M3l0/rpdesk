from abc import ABC, abstractmethod


class Item(ABC):
    def __init__(self, id, nome, valor):
        self._id = id
        self._nome = nome
        self._valor = valor


    @property
    def id(self):
        return self._id
    
    @property
    def nome(self):
        return self._nome
    
    @property
    def valor(self):
        return self._valor
    
    @abstractmethod
    def serializar(self):
        pass
