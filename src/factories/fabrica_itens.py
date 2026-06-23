from uuid import uuid4
import random
from itens.equipamento import Equipamento
from itens.consumivel import Consumivel


class FabricaItens():
    def __init__(self):
        # Mapeamento de nomes de itens por slot e tier de reputação
        self.__nomes_slots = {
            "cabeca": {
                "baixo": ["Capuz de Tecido Desgastado", "Elmo de Couro Amortecido"],
                "medio": ["Elmo de Bronze Comum", "Elmo de Ferro Polido"],
                "alto": ["Elmo de Placas Lendário", "Coroa de Ouro do Rei Caído"]
            },
            "tronco": {
                "baixo": ["Gibão de Couro Gasto", "Túnica de Linho Simples"],
                "medio": ["Cota de Malha de Ferro", "Peitoral de Aço Escovado"],
                "alto": ["Armadura de Égide Celeste", "Couraça de Escamas de Dragão"]
            },
            "pernas": {
                "baixo": ["Calças de Pano Remendadas", "Perneiras de Couro Macio"],
                "medio": ["Perneiras de Ferro Batido", "Grevas de Bronze Pesadas"],
                "alto": ["Grevas de Aço do Paladino", "Perneiras de Titânio Rúnico"]
            },
            "mao_direita": {
                "baixo": ["Adaga de Cobre Enferrujada", "Espada de Treino de Madeira"],
                "medio": ["Espada Curta de Aço", "Machado de Batalha de Ferro"],
                "alto": ["Lâmina Mítica Excalibur", "Espada Larga Matadora de Dragões"]
            },
            "mao_esquerda": {
                "baixo": ["Broquel de Madeira Rachado", "Grimório do Estudante Rasgado"],
                "medio": ["Escudo de Ferro Reforçado", "Grimório do Mago Aprendiz"],
                "alto": ["Escudo Rúnico da Luz Solar", "Códice Sagrado do Arcanista"]
            },
            "pes": {
                "baixo": ["Sandálias Desgastadas", "Botas de Couro Rústicas"],
                "medio": ["Botas de Ferro Pesadas", "Botas Reforçadas de Caçador"],
                "alto": ["Botas Aladas de Hermes", "Passos Leves do Andarilho do Vento"]
            },
            "dedos": {
                "baixo": ["Anel de Cobre Velho", "Anel de Latão Fosco"],
                "medio": ["Anel de Prata Polida", "Anel de Ouro com Selo"],
                "alto": ["Anel Cósmico do Vazio", "Aliança de Rubi do Dragão Infinito"]
            }
        }

        # Mapeamento do atributo que cada slot modifica
        self.__atributos_slots = {
            "cabeca": "hp_max",
            "tronco": "hp_max",
            "pernas": "velocidade",
            "mao_direita": "forca",
            "mao_esquerda": "inteligencia",
            "pes": "velocidade",
            "dedos": "destreza"
        }

    def gerar_equipamento_para_slot(self, reputacao, slot):
        # Determina o tier do item com base na reputação da guilda
        if reputacao < 100:
            tier = "baixo"
        elif reputacao < 300:
            tier = "medio"
        else:
            tier = "alto"

        # Valida se o slot é válido
        if slot not in self.__nomes_slots:
            slot = "mao_direita"

        # Seleciona um nome aleatório para o slot e tier correspondente
        nome = random.choice(self.__nomes_slots[slot][tier])

        # Sorteia o valor do modificador escalado pela reputação
        multiplicador_rep = 0.03
        val_min = int(1 + reputacao * multiplicador_rep)
        val_max = int(5 + reputacao * multiplicador_rep * 2.5)
        valor_mod = random.randint(val_min, val_max)

        atributo_afetado = self.__atributos_slots.get(slot, "hp_max")
        modificador = (atributo_afetado, valor_mod, "somar")

        # Calcula o valor comercial do item
        preco = int(20 + reputacao * 1.5 + valor_mod * 12)

        return Equipamento(
            id=uuid4(),
            nome=nome,
            valor=preco,
            slot=slot,
            modificador=modificador
        )

    def gerar_consumivel(self, reputacao):
        if reputacao < 10:
            nome = "Poção de Cura Menor"
            preco = 10
        elif reputacao < 30:
            nome = "Poção de Cura Média"
            preco = 25
        else:
            nome = "Poção de Cura Maior"
            preco = 60

        return Consumivel(
            id=uuid4(),
            nome=nome,
            valor=preco
        )