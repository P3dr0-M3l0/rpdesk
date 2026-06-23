import pytest
from unittest.mock import MagicMock
from entidades.heroi import Heroi
from factories.fabrica_heroi import FabricaDeHerois
from factories.fabrica_itens import FabricaItens
from core.event_manager import EventManager


# =============================================================
# Helpers
# =============================================================
def _make_heroi():
    """Cria um Herói real via fábrica para testar progressão."""
    em = EventManager()
    fi = FabricaItens()
    fabrica = FabricaDeHerois(fabrica_itens=fi, event_manager=em)
    return fabrica.gerar_heroi(reputacao=0)


# =============================================================
# Testes de XP e Nível
# =============================================================
def test_heroi_inicia_com_xp_zero_e_nivel_um():
    heroi = _make_heroi()
    assert heroi.xp    == 0
    assert heroi.nivel == 1


def test_ganhar_xp_sem_subir_de_nivel():
    heroi = _make_heroi()
    niveis = heroi.ganhar_xp(50)
    assert niveis    == 0
    assert heroi.xp  == 50
    assert heroi.nivel == 1


def test_ganhar_xp_sobe_um_nivel():
    heroi = _make_heroi()
    niveis = heroi.ganhar_xp(100)
    assert niveis      == 1
    assert heroi.nivel == 2
    assert heroi.xp    == 0


def test_ganhar_xp_sobe_multiplos_niveis():
    heroi = _make_heroi()
    niveis = heroi.ganhar_xp(250)
    assert niveis      == 2
    assert heroi.nivel == 3
    assert heroi.xp    == 50   # sobra 50 após descontar 200 (2 níveis)


def test_subir_nivel_incrementa_atributos():
    heroi = _make_heroi()
    forca_antes     = heroi.atributos.forca.valor_base
    destreza_antes  = heroi.atributos.destreza.valor_base
    intel_antes     = heroi.atributos.inteligencia.valor_base
    veloc_antes     = heroi.atributos.velocidade.valor_base
    hp_max_antes    = heroi.atributos.hp_max.valor_base

    heroi.ganhar_xp(100)  # 1 nível

    assert heroi.atributos.forca.valor_base        == forca_antes     + 1
    assert heroi.atributos.destreza.valor_base     == destreza_antes  + 1
    assert heroi.atributos.inteligencia.valor_base == intel_antes     + 1
    assert heroi.atributos.velocidade.valor_base   == veloc_antes     + 1
    assert heroi.atributos.hp_max.valor_base       == hp_max_antes    + 5


def test_subir_nivel_cura_hp_parcialmente():
    heroi = _make_heroi()
    # Causa dano ao herói para testar a cura de +5 ao subir de nível
    heroi.atributos.receber_dano(10)
    hp_antes = heroi.atributos.valor_hp_atual

    heroi.ganhar_xp(100)

    # HP atual deve ter aumentado em 5 (sem exceder o novo hp_max)
    hp_esperado = min(hp_antes + 5, heroi.atributos.valor_hp_max)
    assert heroi.atributos.valor_hp_atual == hp_esperado


def test_xp_e_nivel_incluidos_em_serializar():
    heroi = _make_heroi()
    heroi.ganhar_xp(150)  # nível 2, 50 xp restantes
    dados = heroi.serializar()
    assert 'HR_xp'    in dados
    assert 'HR_nivel' in dados
    assert dados['HR_xp']    == 50
    assert dados['HR_nivel'] == 2
