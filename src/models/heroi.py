from entidade import Entidade


class Heroi(Entidade):
    
    def __init__(self, id, nome, atributos, inventario, event_manager, lista_tracos):
        super().__init__(id, nome, atributos, inventario, event_manager)
        self.__lista_tracos = lista_tracos
        
        
        def __decidir_acao(self, contexto): # Ainda é necessário definir a lógica
            
            dict_acao = {
                "alvo": 0,
                "ataque": 0
            }
            
            return dict_acao

        
        # Adicionar verificação
        def adicionar_traco(self, traco_personalidade):
            
            self.__lista_tracos.append(traco_personalidade)


        def equipar_item(self, slot, item):
            ...
        
        
        def receber_dano(self, qntd, fonte):
            
            super().receber_dano(self, qntd, fonte)
            
            
        def curar(self):
            
            super().curar
