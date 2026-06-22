from entidades.conjunto_atributos import ConjuntoDeAtributos
from entidades.inventario import Inventario
from entidades.inimigo import Inimigo
from uuid import uuid4
import random


class FabricaDeInimigos():
    
    def __init__(self, fabrica_itens, event_manager):
        self.__fabrica_itens = fabrica_itens
        self.__event_manager = event_manager
        
        import json
        import os
        caminho_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(caminho_dir, "nomes_inimigos.json")
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.__nomes = dados.get("nomes", ["Goblin", "Orc"])
                self.__adjetivos = dados.get("adjetivos", ["Corrompido", "Selvagem"])
        except Exception:
            self.__nomes = ["Goblin", "Orc"]
            self.__adjetivos = ["Corrompido", "Selvagem"]

    def gerar_inimigo(self, reputacao):
        id_inimigo = uuid4()
        nome_inimigo = f"{random.choice(self.__nomes)} {random.choice(self.__adjetivos)}"
        atributos_inimigo = self.__gerar_atributos(reputacao)
        inventario_inimigo = self.__gerar_inventario(reputacao)
        slots_equipados = self.__gerar_slots(reputacao)
        xp_recompensa = self.__gerar_xp_recompensa(reputacao)
        event_manager_inimigo = self.__event_manager

        inimigo = Inimigo(
            id              = id_inimigo,
            nome            = nome_inimigo,
            atributos       = atributos_inimigo,
            inventario      = inventario_inimigo,
            slots_equipados = slots_equipados,
            event_manager   = event_manager_inimigo,
            xp_recompensa   = xp_recompensa
        )
        return inimigo

    def __gerar_atributos(self, reputacao):
        multiplicador_rep = 0.25
        
        # FORCA
        min_val = int(1 + reputacao * multiplicador_rep)
        max_val = int(10 + reputacao * multiplicador_rep)
        attr_forca = random.randint(min_val, max_val)
        
        # DESTREZA
        min_val = int(1 + reputacao * multiplicador_rep)
        max_val = int(10 + reputacao * multiplicador_rep)
        attr_destreza = random.randint(min_val, max_val)
        
        # INTELIGENCIA
        min_val = int(1 + reputacao * multiplicador_rep)
        max_val = int(10 + reputacao * multiplicador_rep)
        attr_inteligencia = random.randint(min_val, max_val)
        
        # VELOCIDADE
        min_val = int(1 + reputacao * multiplicador_rep)
        max_val = int(10 + reputacao * multiplicador_rep)
        attr_velocidade = random.randint(min_val, max_val)
        
        # HP_MAX
        min_hp = int(10 + reputacao * multiplicador_rep)
        max_hp = int(30 + reputacao * multiplicador_rep)
        attr_hp_max = random.randint(min_hp, max_hp)
        
        atributos = ConjuntoDeAtributos(
            attr_forca,
            attr_destreza,
            attr_inteligencia,
            attr_velocidade,
            attr_hp_max,
            self.__event_manager
        )
        return atributos

    def __gerar_inventario(self, reputacao):
        capacidade_max = random.randint(3, 5 + int(reputacao * 0.25))
        return Inventario(capacidade_max, lista_itens=[], event_manager=self.__event_manager)

    def __gerar_slots(self, reputacao):
        multiplicador_rep = 0.10
        slots_disponiveis = ["cabeca", "tronco", "pernas", "mao_esquerda", "mao_direita", "pes", "dedos"]
        
        slots_equipados = {}
        max_slots = min(len(slots_disponiveis), 1 + int(reputacao * multiplicador_rep))
        qtnd_slots_equipados = random.randint(0, max_slots)
        
        for _ in range(qtnd_slots_equipados):
            slot = random.choice(slots_disponiveis)
            slots_disponiveis.remove(slot)
            item = self.__fabrica_itens.gerar_equipamento_para_slot(reputacao, slot)
            slots_equipados[slot] = item
        return slots_equipados

    def __gerar_xp_recompensa(self, reputacao):
        return 10 + int(reputacao * 5)
