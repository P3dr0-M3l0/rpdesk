from abc import ABC, abstractmethod
from item import Item


class Consumivel(Item, ABC):
    def __init__(self, id, nome, valor):
        super().__init__(id, nome, valor)
        
        
    def usar(self):
        pass
    
    def serializar(self):
        dicionario_item = {
            'IT_id'   : self._id,
            'IT_nome' : self._nome,
            'IT_valor': self._valor
        }
        return dicionario_item