from item import Item


class Consumivel(Item):
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

    def usar(self, alvo):
        if "Cura Menor" in self._nome:
            cura = 15
        elif "Cura Média" in self._nome:
            cura = 35
        elif "Cura Maior" in self._nome:
            cura = 75
        else:
            cura = 10

        alvo.curar(cura)
    
    def serializar(self):
        dicionario_item = {
            'CON_id'   : self._id,
            'CON_nome' : self._nome,
            'CON_valor': self._valor
        }
        return dicionario_item