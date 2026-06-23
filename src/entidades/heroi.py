import random
from entidades.entidade import Entidade
# from itens.pocao_cura import PocaoDeCura

class Heroi(Entidade):
    
    def __init__(self, id, nome, atributos, inventario, slots_equipados, event_manager, lista_tracos, valor,
                 xp: int = 0, nivel: int = 1):
        super().__init__(id, nome, atributos, inventario, slots_equipados, event_manager)
        self.__lista_tracos = lista_tracos
        self.__valor = valor
        self.__xp    = xp
        self.__nivel = nivel
        
    
    # =====================================================
    # Getters e Setters -----------------------------------
    # =====================================================
    @property
    def id(self):
        return self._id
    
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
    def slots_equipados(self):
        return self._slots_equipados
    
    @property
    def lista_tracos(self):
        return self.__lista_tracos
    
    @property
    def valor(self):
        return self.__valor

    @valor.setter
    def valor(self, n):
        if n < 0:
            raise ValueError("O herói não pode ter um valor negativo")
        self.__valor = n

    @property
    def xp(self):
        return self.__xp

    @property
    def nivel(self):
        return self.__nivel
    
    # =====================================================
    # Progressão ------------------------------------------
    # =====================================================
    def ganhar_xp(self, valor: int) -> int:
        """
        Acumula XP e sobe de nível a cada 100 pontos.
        A cada nível:
          - +1 em Força, Destreza, Inteligência e Velocidade
          - +5 em HP Máximo (e restaura 5 de HP Atual)

        Returns:
            Número de níveis ganhos nessa chamada.
        """
        self.__xp += valor
        niveis_ganhos = 0
        while self.__xp >= 100:
            self.__xp   -= 100
            self.__nivel += 1
            niveis_ganhos += 1
            self._atributos.forca.valor_base        += 1
            self._atributos.destreza.valor_base     += 1
            self._atributos.inteligencia.valor_base += 1
            self._atributos.velocidade.valor_base   += 1
            self._atributos.hp_max.valor_base       += 5
            self._atributos.curar(5)
        return niveis_ganhos

    # =====================================================
    # Tracos ----------------------------------------------
    # =====================================================
    # Adicionar verificação
    def adicionar_traco(self, traco_personalidade):
        self.__lista_tracos.append(traco_personalidade)
    
    # =====================================================
    # Lógica de combate -----------------------------------
    # =====================================================
    def receber_dano(self, qntd, fonte):
        super().receber_dano(qntd, fonte)
        
    def curar(self, valor):
        super().curar(valor)
    
    def morrer(self):
        super().morrer()

    def decidir_acao(self, contexto): # Ainda é necessário definir a lógica
        acao = None
        if self.__arvore0_cura() != None:
            acao = self.__arvore0_cura()
        elif self.__arvore1_finalizar(contexto) != None:
            acao = self.__arvore1_finalizar(contexto)
        elif self.__arvore_fallback(contexto) != None:
            acao = self.__arvore_fallback(contexto)

        for traco in self.__lista_tracos:
            acao = traco.avaliar_situacao(contexto, acao)

        return acao
    
    # Cláusulas de Guarda ---------------------------------
    def __arvore0_cura(self):
        # if self._atributos.valor_hp_atual <= self._atributos.valor_hp_max * 0.3:
        #     for item in self._inventario.lista_itens:
        #         if isinstance(item, PocaoDeCura):
        #             return {'acao': 'curar', 'alvo': self}
        return None
    
    def __arvore1_finalizar(self, contexto: dict):
        inimigos = contexto['inimigos']
        if not inimigos:
            return None
        
        temp = 0
        temp_alvo = None
        for inimigo in inimigos:
            vida_inimigo = inimigo.atributos.valor_hp_atual
            if vida_inimigo <= self.atributos.valor_forca and vida_inimigo > temp:
                temp = vida_inimigo
                temp_alvo = inimigo
        
        if temp_alvo != None:
            return {'acao': 'atacar', 'alvo': temp_alvo}
        return None
    
    def __arvore_fallback(self, contexto):
        inimigos = contexto['inimigos']
        if not inimigos:
            return None
        
        if random.random() >= 0.45:
            dict_inimigos = {}
            for inimigo in inimigos:
                dict_inimigos[inimigo] = inimigo.atributos.valor_hp_atual
            alvo = min(dict_inimigos, key=dict_inimigos.get)
            return {'acao': 'atacar', 'alvo': alvo}
        else:
            alvo = random.choice(inimigos)
            return {'acao': 'atacar', 'alvo': alvo}
    
    # =====================================================
    # Equipamentos ----------------------------------------
    # =====================================================
    def equipar_item(self, slot, item):
        return super().equipar_item(slot, item)
        
    def desequipar_item(self, slot):
        return super().desequipar_item(slot)
    
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
            'HR_valor'          : self.__valor,
            'HR_xp'             : self.__xp,
            'HR_nivel'          : self.__nivel,
        }
        return dicionario_heroi