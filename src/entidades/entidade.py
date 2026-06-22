from abc import ABC, abstractmethod
from modificador import Modificador


class Entidade(ABC):
    
    def __init__(self, id, nome, atributos, inventario, slots_equipados, event_manager):
        self._id = id
        self._nome = nome
        self._atributos = atributos
        self._inventario = inventario
        self._slots_equipados = slots_equipados
        self._event_manager = event_manager
        self._vivo = True

    
    # =====================================================
    # Equipamento -----------------------------------------
    # =====================================================
    def equipar_item(self, slot: str, item):
        self._inventario.remover_item(item)
        
        if slot in self._slots_equipados:
            self._inventario.adicionar_item(item)
            return False
        
        self._slots_equipados[slot] = item
        
        atributo_modificar = item.modificador[0]
        valor_modificar = item.modificador[1]
        tipo_modificar =  item.modificador[2]
        
        modificador = Modificador(item.id, valor_modificar, tipo_modificar)
        
        if atributo_modificar == "forca":
            self._atributos.forca.adicionar_modificador(modificador)
        elif atributo_modificar == "destreza":
            self._atributos.destreza.adicionar_modificador(modificador)
        elif atributo_modificar == "inteligencia":
            self._atributos.inteligencia.adicionar_modificador(modificador)
        elif atributo_modificar == "velocidade":
            self._atributos.velocidade.adicionar_modificador(modificador)
        elif atributo_modificar == "hp_max":
            self._atributos.hp_max.adicionar_modificador(modificador)
        return True
        
    def desequipar_item(self, slot: str):
        item = self._slots_equipados.pop(slot)
        
        if not self._inventario.adicionar_item(item):
            self._slots_equipados[slot] = item
            return False
        
        atributo_modificado = item.modificador[0]
        
        if atributo_modificado == "forca":
            self._atributos.forca.remover_modificadores_por_origem(item.id)
        elif atributo_modificado == "destreza":
            self._atributos.destreza.remover_modificadores_por_origem(item.id)
        elif atributo_modificado == "inteligencia":
            self._atributos.inteligencia.remover_modificadores_por_origem(item.id)
        elif atributo_modificado == "velocidade":
            self._atributos.velocidade.remover_modificadores_por_origem(item.id)
        elif atributo_modificado == "hp_max":
            self._atributos.hp_max.remover_modificadores_por_origem(item.id)
        return True
    
    # =====================================================
    # Gerenciamento de Inventário -------------------------
    # =====================================================
    def adicionar_item(self, item):
        if not self._inventario.adicionar_item(item):
            print("\n--= Inventário cheio! =--\n")
            return False
        return True
 
    def remover_item(self, item):
        n_item = self._inventario.remover_item(item)
        return n_item
    
    # =====================================================
    # Lógica de Combate -----------------------------------
    # =====================================================
    @abstractmethod
    def decidir_acao(self, contexto):
        pass
    
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
    