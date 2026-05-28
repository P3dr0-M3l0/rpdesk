from entidades.entidade import Entidade


class Heroi(Entidade):
    
    def __init__(self, id, nome, atributos, inventario, slots_equipados, event_manager, lista_tracos):
        super().__init__(id, nome, atributos, inventario, slots_equipados, event_manager)
        self.__lista_tracos = lista_tracos
        
        
    def decidir_acao(self, contexto): # Ainda é necessário definir a lógica
        
        dict_acao = {
            "alvo": 0,
            "ataque": 0
        }
        return dict_acao
    
    def receber_dano(self, qntd, fonte):
        super().receber_dano(qntd, fonte)
        
    def curar(self):     
        super().curar()
    
    def morrer(self):
        super().morrer()
        
    # Adicionar verificação
    def adicionar_traco(self, traco_personalidade):
        self.__lista_tracos.append(traco_personalidade)

    def equipar_item(self, slot, item):
        return super().equipar_item(slot, item)
        
    def desequipar_item(self, slot, item):
        return super().desequipar_item(slot, item)

    def serializar(self):
        tracos_serializados = []
        for traco in self.__lista_tracos:
            tracos_serializados.append(traco.serializar())
        
        dicionario_heroi = {
            'HR_id'          : self._id,
            'HR_nome'        : self._nome,
            'HR_atributos'   : self._atributos.serializar(),
            'HR_inventario'  : self._inventario.serializar(),
            'HR_lista_tracos': tracos_serializados
        }
        return dicionario_heroi