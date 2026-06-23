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
        
        # Aplicar modificadores para todos os equipamentos equipados no início
        for slot, item in self._slots_equipados.items():
            if item:
                self._aplicar_modificador_item(item)
        
        # Garantir que o HP atual acompanhe o HP máximo modificado na criação do herói
        if hasattr(self._atributos, 'hp_max') and hasattr(self._atributos, 'hp_atual'):
            self._atributos.hp_atual.valor_base = self._atributos.hp_max.valor_total

    def _aplicar_modificador_item(self, item):
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

    def verificar_defesa_itens(self, qtnd):
        defesa = 0
        for slot, item in self._slots_equipados.items():
            if item and len(item.modificador) > 0 and item.modificador[0] == "defesa":
                defesa += item.modificador[1]
        return defesa

    # =====================================================
    # Equipamento -----------------------------------------
    # =====================================================
    def equipar_item(self, item):
        slot = item.slot
        self._inventario.remover_item(item)
        
        if slot in self._slots_equipados and self._slots_equipados[slot] is not None:
            self._inventario.adicionar_item(item)
            return False
        
        self._slots_equipados[slot] = item
        self._aplicar_modificador_item(item)
        return True
        
    def desequipar_item(self, slot: str):
        if slot not in self._slots_equipados:
            return False
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
        
    def curar(self, valor):
        hp_atual = self._atributos.curar(valor)
        self._event_manager.emitir_evento(
            "entidade_curada",
            {
                'cura': valor,
                'entidade_nome': self._nome
            }
        )
        return hp_atual
        
    def morrer(self):
        
        self._vivo = False
        self._event_manager.emitir_evento("morrer", {"id_morto": self._id})
    