from abc import ABC, abstractmethod
from item import Item


class Consumivel(Item, ABC):
    def __init__(self, id, nome, valor):
        super().__init__(id, nome, valor)


    @property
    def id(self):
        return super().id
    
    @property
    def nome(self):
        return super().nome
    
    @property
    def valor(self):
        return super().valor

    @abstractmethod
    def usar(self):
        pass
    
    def serializar(self):
        dicionario_item = {
            'CON_id'   : self._id,
            'CON_nome' : self._nome,
            'CON_valor': self._valor
        }
        return dicionario_item