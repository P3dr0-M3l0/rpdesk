from abc import ABC, abstractmethod


class Item(ABC):
    def __init__(self, id, nome, valor):
        self._id = id
        self._nome = nome
        self._valor = valor
        
    
    @abstractmethod 
    def usar():
        pass
    
    @abstractmethod
    def serializar():
        pass
