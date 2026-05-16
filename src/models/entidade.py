from abc import ABC, abstractmethod


class Entidade(ABC):
    
    def __init__(self, id, nome, atributos, inventario, event_manager):
        self._id = id
        self._nome = nome
        self._atributos = atributos
        self._inventario = inventario
        self._event_manager = event_manager
        self._vivo = True


    @abstractmethod
    def decidir_acao(self, contexto):
        pass
    
    
    def verificar_defesa_itens(self):
        
        # Verificar os itens de defesa no inventário
        
        # Retorna o número da defesa total
        ...
    
    
    def receber_dano(self, qtnd, fonte):
        
        defesa = self.verificar_defesa_itens(qtnd)
        qntd_temp = qtnd - defesa if qtnd - defesa > 0 else 0
        
        defesa += self._atributos.verificar_defesa_attr(qntd_temp)
        
        dano_recebido = qtnd - defesa if qtnd - defesa > 0 else 0
        
        # Essa variável hp_atual é local desse método e não interfere na variável 
        # privada do ConjuntoDeAtributos
        hp_atual = self._atributos.receber_dano(dano_recebido)
        
        self._event_manager.emitir_evento(
            f"dano_recebido",
            {
                'dano': dano_recebido,
                'fonte': fonte
            }
            )
        
        if hp_atual == 0:
            self.morrer()
        
        
    def curar(self):
        
        # Implementar com Item PocaoDeCura
        
        ...
        
        
    def morrer(self):
        
        self._vivo = False
        self._event_manager.emitir_evento("morrer", {"id_morto": self._id})
    