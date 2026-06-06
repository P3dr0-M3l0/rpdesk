from entidades.entidade import Entidade


class Heroi(Entidade):
    
    def __init__(self, id, nome, atributos, inventario, slots_equipados, event_manager, lista_tracos, valor):
        super().__init__(id, nome, atributos, inventario, slots_equipados, event_manager)
        self.__lista_tracos = lista_tracos
        self.__valor = valor
        
    
    # =====================================================
    # Getters e Setters -----------------------------------
    # =====================================================
    @property
    def nome(self):
        return self._nome
    
    @property
    def atributos(self):
        return self._atributos
    
    @property
    def inventario(self):
        return self._inventario
    
    @property
    def lista_tracos(self):
        return self.__lista_tracos
    
    @property
    def valor(self):
        return self.__valor
    
    @valor.setter
    def valor(self, n):
        if n < 0:
            raise ValueError("O heróis não pode ter um valor negativo")
        self.__valor = n
    
    # =====================================================
    # Lógica de combate -----------------------------------
    # =====================================================
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

    # =====================================================
    # Equipamentos ----------------------------------------
    # =====================================================
    def equipar_item(self, slot, item):
        return super().equipar_item(slot, item)
        
    def desequipar_item(self, slot, item):
        return super().desequipar_item(slot, item)
    
    # =====================================================
    # Gerenciamento de inventário -------------------------
    # =====================================================
    def adicionar_item(self, item):
        return super().adicionar_item(item)
    
    def remover_item(self, item):
        return super().remover_item(item)
    
    # =====================================================
    # Para save -------------------------------------------
    # =====================================================
    def serializar(self):
        tracos_serializados = []
        for traco in self.__lista_tracos:
            tracos_serializados.append(traco.serializar())
            
        slot_serializado = {}
        for key in self._slots_equipados:
            item = self._slots_equipados.get(key)
            dict_item = item.serializar()
            slot_serializado[key] = dict_item
        
        dicionario_heroi = {
            'HR_id'             : self._id,
            'HR_nome'           : self._nome,
            'HR_atributos'      : self._atributos.serializar(),
            'HR_inventario'     : self._inventario.serializar(),
            'HR_slots_equipados': slot_serializado,
            'HR_lista_tracos'   : tracos_serializados,
            'HR_valor'          : self.__valor
        }
        return dicionario_heroi