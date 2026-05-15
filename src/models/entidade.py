# from conjunto_atributos import ConjuntoDeAtributos
from abc import ABC, abstractmethod


class Entidade(ABC):
    
    def __init__(self, id, nome, atributos, inventario, event_manager):
        self._id = id
        self._nome = nome
        self._atributos = atributos
        self._inventario = inventario
        self._event_manager = event_manager
        self._vivo = True

        # Inscrição no evento de "morte"
        self._event_manager.inscrever(f"morrer_{self._id}", self.__del__)
        
        # Inscrição no evento "receber dano"
        self._event_manager.inscrever(f"printar_dano_recebido_{self._id}")


    @abstractmethod
    def decidir_acao(self, contexto):
        pass
    
    
    def receber_dano(self, qtnd, fonte):
        
        dano_recebido = self._atributos.calcular_defesa(qtnd)
        
        hp_atual = self._atributos.receber_dano(dano_recebido)
        
        self._event_manager.emitir_evento(
            f"printar_dano_recebido_{self._id}"
            # ,
            # {
            #     'dano': dano_recebido,
            #     'fonte': fonte
            # }
            )
        
        if hp_atual == 0:
            self.__del__()
        
        
    def curar(self):
        ...
        
        
    def __del__(self):
        
        self._event_manager.emitir_evento(f"morrer_{self._id}")
        self._event_manager.desinscrever(f"morrer_{self._id}")