from entidades.conjunto_atributos import ConjuntoDeAtributos
from entidades.inventario import Inventario
from entidades.heroi import Heroi
from uuid import uuid4
import random


class FabricaDeHerois():
    
    def __init__(self, fabrica_itens, event_manager):
        self.__fabrica_itens = fabrica_itens
        self.__event_manager = event_manager
        
        import json
        import os
        caminho_dir = os.path.dirname(os.path.abspath(__file__))
        caminho_arquivo = os.path.join(caminho_dir, "nomes_herois.json")
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                self.__nomes = dados.get("nomes", ["Pedro", "Isabella"])
                self.__sobrenomes = dados.get("sobrenomes", ["Oliveira Moreira", "Moreira Melo"])
        except Exception:
            self.__nomes = ["Pedro", "Isabella"]
            self.__sobrenomes = ["Oliveira Moreira", "Moreira Melo", "Melo Oliveira Moreira"]
        
    
    # *Adicionar Nível de Reputação Posteriormente
    def gerar_heroi(self, reputacao):

        id_heroi = uuid4()
        nome_heroi = f"{random.choice(self.__nomes)} {random.choice(self.__sobrenomes)}"
        atributos_heroi = self.__gerar_atributos(reputacao)
        inventario_heroi = self.__gerar_inventario(reputacao)
        slots_equipados = self.__gerar_slots(reputacao)
        tracos_heroi = self.__gerar_tracos(reputacao)
        valor_heroi = self.__gerar_valor(reputacao)
        event_manager_heroi = self.__event_manager

        heroi = Heroi(
            id              = id_heroi,
            nome            = nome_heroi,
            atributos       = atributos_heroi,
            inventario      = inventario_heroi,
            slots_equipados = slots_equipados,
            lista_tracos    = tracos_heroi,
            event_manager   = event_manager_heroi,
            valor           = valor_heroi,
            xp              = 0,
            nivel           = 1,
            )
        return heroi


    def __gerar_atributos(self, reputacao):
        multiplicador_rep = 0.25
        # FORCA
        min = int(1 + reputacao*multiplicador_rep)
        max = int(10 + reputacao*multiplicador_rep)
        attr_forca = random.randint(min, max)
        
        # DESTREZA
        min = int(1 + reputacao*multiplicador_rep)
        max = int(10 + reputacao*multiplicador_rep)
        attr_destreza = random.randint(min, max)
        
        # INTELIGENCIA
        min = int(1 + reputacao*multiplicador_rep)
        max = int(10 + reputacao*multiplicador_rep)
        attr_inteligencia = random.randint(min, max)
        
        # VELOCIDADE
        min = int(1 + reputacao*multiplicador_rep)
        max = int(10 + reputacao*multiplicador_rep)
        attr_velocidade = random.randint(min, max)
        
        # HP_MAX
        min = int(10 + reputacao*multiplicador_rep)
        max = int(30 + reputacao*multiplicador_rep)
        attr_hp_max = random.randint(min, max)
        
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
        
    def __gerar_valor(self, reputacao):
        return 50 + int(reputacao * 5)
    
    def __gerar_tracos(self, reputacao):
        return []