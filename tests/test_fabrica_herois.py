import pytest
from entidades.heroi import Heroi
from factories.fabrica_heroi import FabricaDeHerois
from core.event_manager import EventManager

def test_gerar_heroi_retorna_instancia():
    em = EventManager()
    fabrica = FabricaDeHerois(event_manager=em)
    
    heroi = fabrica.gerar_heroi()
    
    assert isinstance(heroi, Heroi)
    assert heroi._nome != ""

def test_gerar_herois_unicidade_id():
    em = EventManager()
    fabrica = FabricaDeHerois(event_manager=em)
    
    ids_gerados = set()
    for _ in range(50):
        heroi = fabrica.gerar_heroi()
        ids_gerados.add(heroi._id)
        
    # Se o tamanho do set for 50, significa que não houve IDs duplicados
    assert len(ids_gerados) == 50

def test_injecao_dependencia_event_manager():
    em_global = EventManager()
    fabrica = FabricaDeHerois(event_manager=em_global)
    
    heroi = fabrica.gerar_heroi()
    
    # Verifica se a instância na Fábrica, no Herói e nos Atributos é exatamente o mesmo objeto na memória
    assert heroi._event_manager is em_global
    assert heroi._atributos._ConjuntoDeAtributos__event_manager is em_global