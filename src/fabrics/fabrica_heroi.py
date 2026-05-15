from models.conjunto_atributos import ConjuntoDeAtributos
from models.heroi import Heroi
from uuid import uuid4
import random


class FabricaDeHerois():
    
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.__nomes = ["Pedro", "Isabella"]
        self.__sobrenomes = ["Oliveira Moreira", "Moreira Melo", "Melo Oliveira Moreira"]
        
    
    # *Adicionar Nível de Reputação Posteriormente
    def gerar_heroi(self):
        
        id_heroi = uuid4()
        nome_heroi = f"{random.choice(self.__nomes)} {random.choice(self.__sobrenomes)}"
        atributos_heroi = self.__gerar_atributos()
        inventario_heroi = self.__gerar_inventario()
        tracos_heroi = self.__gerar_tracos()
        event_manager_heroi = self.event_manager
        
        heroi = Heroi(
            id_heroi,
            nome_heroi,
            atributos_heroi,
            inventario_heroi,
            event_manager_heroi,
            tracos_heroi
            )
        
        return heroi

        
    def __gerar_atributos(self):
        
        # FORCA
        max = 30
        attr_forca = random.randint(0, max)
        
        # DESTREZA
        max = 30
        attr_destreza = random.randint(0, max)
        
        # INTELIGENCIA
        max = 0
        attr_inteligencia = random.randint(0, max)
        
        # VELOCIDADE
        max = 0
        attr_velocidade = random.randint(0, max)
        
        # HP_MAX
        max = 50
        attr_hp_max = random.randint(0, max)
        
        atributos = ConjuntoDeAtributos(
            attr_forca,
            attr_destreza,
            attr_inteligencia,
            attr_velocidade,
            attr_hp_max,
            self.event_manager
            )
        
        return atributos
        
        
    def __gerar_inventario(self):
        ...
        
    
    def __gerar_tracos(self):
        ...
