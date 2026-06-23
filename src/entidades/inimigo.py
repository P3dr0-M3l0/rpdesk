import random
# from itens.pocao_cura import PocaoDeCura
from entidade import Entidade


class Inimigo(Entidade):
    def __init__(self, id:int, nome:str, atributos, inventario, slots_equipados, event_manager, xp_recompensa:int):
        super().__init__(id, nome, atributos, inventario, slots_equipados, event_manager)
        self.__xp_recompensa = xp_recompensa        
    
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
    def xp_recompensa(self):
        return self.__xp_recompensa

    # =====================================================
    # Lógica de Combate -----------------------------------
    # =====================================================
    def receber_dano(self, qtdn, fonte):
        super().receber_dano(qtdn, fonte)
    
    def curar(self, valor):
        super().curar(valor)
        
    def morrer(self):
        super().morrer()
        
    def decidir_acao(self, contexto: dict):
        # Estrutura do dicionário "contexto":
        # {'herois': [], 'inimigos': []}
        if self.__arvore0_cura() != None:
            return self.__arvore0_cura()
        
        if self.__arvore1_finalizacao(contexto) != None:
            return self.__arvore1_finalizacao(contexto)
        
        if self.__arvore_fallback(contexto) != None:
            return self.__arvore_fallback(contexto)

    # Cláusulas de Guarda ---------------------------------
    def __arvore0_cura(self):
        # if self._atributos.valor_hp_atual <= self.atributos.valor_hp_max * 0.3:
        #     for item in self.inventario.lista_itens:
        #         if isinstance(item, PocaoDeCura):
        #             return  {'acao': 'curar', 'alvo': self}
        return None
    
    def __arvore1_finalizacao(self, contexto):
        herois = contexto['herois']

        temp = 0
        alvo_temp = None
        for heroi in herois:
            vida_heroi = heroi.atributos.valor_hp_atual
            
            if vida_heroi <= self._atributos.valor_forca and vida_heroi >= temp:
                temp = vida_heroi
                alvo_temp = heroi
                
        if alvo_temp != None:
            return {'acao': 'atacar', 'alvo': alvo_temp}
        return None
    
    def __arvore_fallback(self, contexto: dict):
        herois = contexto['herois']
        if not herois:
            return None

        if random.random() >= 0.8: 
            dict_herois = {}
            for heroi in herois:
                dict_herois[heroi] = heroi.atributos.valor_hp_atual

            alvo = min(dict_herois, key=dict_herois.get)
            return {'acao': 'atacar', 'alvo': alvo}
        else:
            escolha = random.choice(herois)
            return {'acao': 'atacar', 'alvo': escolha}            
    
    # =====================================================
    # Equipamento -----------------------------------------
    # =====================================================
    def equipar_item(self, item):
        super().equipar_item(item)
        
    def desequipar_item(self, slot):
        super().desequipar_item(slot)
    
    # =====================================================
    # Gerenciamento de Inventário -------------------------
    # =====================================================
    def adicionar_item(self, item):
        super().adicionar_item(item)
        
    def remover_item(self, item):
        super().remover_item(item)

    