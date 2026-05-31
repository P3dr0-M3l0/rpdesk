class Inventario():
    def __init__(self, capacidade_max, lista_itens, event_manager):
        self.__capacidade_max = capacidade_max
        self.__lista_itens = lista_itens
        
    
    @property    
    def lista_itens(self):
        return self.__lista_itens
    
    def definir_capacidade(self, valor):
        if valor <= 0 or valor > 20:
            raise Exception('''Erro: Não é possível criar um inventário com capacidade
fora do intervalo  0 < x <= 20''')    
        self.__capacidade_max = valor
        
    def adicionar_item(self, item):
        if self.__capacidade_max == None:
            raise ValueError("Erro: Não foi definida capacidade para esse inventário")
        if len(self.__lista_itens) < self.__capacidade_max:
            self.__lista_itens.append(item)
            return True
        return False
    
    def remover_item(self, item):
        if item not in self.__lista_itens:
            raise Exception("Erro: Item para ser removido não foi encontrado")
        self.__lista_itens.remove(item)
        return item
    
    def serializar(self):
        itens_serializados = []
        for item in self.__lista_itens:
            itens_serializados.append(item.serializar())
        
        dicionario_inventario = {
            'IN_capacidade_max': self.__capacidade_max,
            'IN_lista_itens'   : itens_serializados
        }
        return dicionario_inventario
