from abc import ABC, abstractmethod
from item import Item


class Equipamento(Item, ABC):
    def __init__(self, id, nome, valor, slot, modificador):
        super().__init__(id, nome, valor)
        self._slot = slot
        self._modificador = modificador # Lista de atributo a ser modificado, valor da modificação, tipo mod

    
    @property
    def id(self):
        return super().id
    
    @property
    def nome(self):
        return super().nome
    
    @property
    def valor(self):
        return super().valor
    
    @property
    def slot(self):
        return self._slot
    
    @property
    def modificador(self):
        return self._modificador

    @abstractmethod
    def usar(self):
        pass
    
    def serializar(self):
        dicionario_equipamento = {
            'EQPM_id'          : self._id,
            'EQPM_nome'        : self._nome,
            'EQPM_valor'       : self._valor,
            'EQPM_slot'        : self._slot,
            'EQPM_modificador' : self._modificador
        }
        return dicionario_equipamento
    