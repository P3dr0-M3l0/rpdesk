import pytest # type: ignore
from src.entidades.conjunto_atributos import ConjuntoDeAtributos

# Mock simples do EventManager para injeção
class MockEventManager:
    pass

def test_inicializacao_atributos():
    mock_em = MockEventManager()
    atributos = ConjuntoDeAtributos(forca=10, destreza=15, inteligencia=5, velocidade=12, hp_max=50, event_manager=mock_em)
    
    assert atributos.forca == 10
    assert atributos.hp_max == 50
    assert atributos.hp_atual == 50

def test_receber_dano_normal_e_limite_zero():
    mock_em = MockEventManager()
    atributos = ConjuntoDeAtributos(10, 10, 10, 10, 50, mock_em)
    
    # Dano normal
    hp_restante = atributos.receber_dano(20)
    assert hp_restante == 30
    assert atributos.hp_atual == 30
    
    # Dano letal (excedente)
    hp_restante = atributos.receber_dano(50)
    assert hp_restante == 0
    assert atributos.hp_atual == 0 # Garante que não ficou negativo