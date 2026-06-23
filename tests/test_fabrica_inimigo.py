import pytest
from entidades.inimigo import Inimigo
from factories.fabrica_inimigo import FabricaDeInimigos
from factories.fabrica_itens import FabricaItens
from core.event_manager import EventManager


def test_gerar_inimigo_retorna_instancia_correta():
    em = EventManager()
    fi = FabricaItens()
    fabrica = FabricaDeInimigos(fabrica_itens=fi, event_manager=em)
    
    inimigo = fabrica.gerar_inimigo(reputacao=10)
    
    assert isinstance(inimigo, Inimigo)
    assert inimigo.nome != ""
    assert inimigo.xp_recompensa > 0


def test_gerar_inimigos_unicidade_id():
    em = EventManager()
    fi = FabricaItens()
    fabrica = FabricaDeInimigos(fabrica_itens=fi, event_manager=em)
    
    ids_gerados = set()
    for _ in range(50):
        inimigo = fabrica.gerar_inimigo(reputacao=10)
        ids_gerados.add(inimigo.id)
        
    assert len(ids_gerados) == 50


def test_injecao_dependencia_event_manager_inimigo():
    em_global = EventManager()
    fi = FabricaItens()
    fabrica = FabricaDeInimigos(fabrica_itens=fi, event_manager=em_global)
    
    inimigo = fabrica.gerar_inimigo(reputacao=15)
    
    assert inimigo._event_manager is em_global
    assert inimigo.atributos._ConjuntoDeAtributos__event_manager is em_global


def test_escalonamento_atributos_e_xp():
    import random
    random.seed(42)
    em = EventManager()
    fi = FabricaItens()
    fabrica = FabricaDeInimigos(fabrica_itens=fi, event_manager=em)
    
    inimigo_fraco = fabrica.gerar_inimigo(reputacao=0)
    inimigo_forte = fabrica.gerar_inimigo(reputacao=50)
    
    # Verifica o escalonamento do XP de recompensa
    assert inimigo_forte.xp_recompensa > inimigo_fraco.xp_recompensa
    
    # A verificação de atributos deve levar em conta o aspecto estocástico (random.randint).
    # Como as faixas de random variam, com reputação 0 os atributos variam de 1 a 6 (base),
    # enquanto com reputação 50 eles variam de 13 a 18 (min_val = 1 + 50*0.25 = 13, max_val = 6 + 12 = 18).
    # Portanto, a força mínima do forte (13) é estritamente maior que a força máxima do fraco (6).
    assert inimigo_forte.atributos.forca.valor_base > inimigo_fraco.atributos.forca.valor_base
    assert inimigo_forte.atributos.hp_max.valor_base > inimigo_fraco.atributos.hp_max.valor_base
