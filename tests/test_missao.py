import pytest
from unittest.mock import MagicMock
from gestao.missao import Missao, EncontroCombate, EncontroTexto
from core.event_manager import EventManager
from core.game_state import GameState


# =============================================================
# Helpers e Mocks
# =============================================================
def _make_equipe(herois: list):
    """Cria uma equipe mock com a lista de heróis fornecida."""
    equipe = MagicMock()
    equipe.membros = herois
    return equipe


def _make_heroi(nome, hp=100, forca=10, vivo=True):
    """Cria um mock simples de Heroi para os testes de missão."""
    heroi = MagicMock()
    heroi.nome   = nome
    heroi._vivo  = vivo

    heroi.receber_dano = MagicMock(side_effect=lambda valor, fonte: None)
    heroi.curar        = MagicMock(side_effect=lambda valor: None)
    return heroi


def _make_motor_vitoria(herois_vivos):
    """Retorna um MotorDeCombate mock que sempre reporta vitória."""
    motor = MagicMock()
    motor.rodar_combate.return_value = {
        'resultado'           : 'vitoria',
        'herois_sobreviventes': herois_vivos,
        'itens_saqueados'     : [],
        'itens_recuperados'   : [],
        'itens_perdidos'      : [],
        'xp_acumulado'        : 50,
        'ouro_saqueado'       : 10,
    }
    return motor


def _make_motor_derrota():
    """Retorna um MotorDeCombate mock que sempre reporta derrota."""
    motor = MagicMock()
    motor.rodar_combate.return_value = {
        'resultado'           : 'derrota',
        'herois_sobreviventes': [],
        'itens_saqueados'     : [],
        'itens_recuperados'   : [],
        'itens_perdidos'      : [],
        'xp_acumulado'        : 0,
        'ouro_saqueado'       : 0,
    }
    return motor


def _make_missao(encontros=None, recompensa_ouro=100, recompensa_xp=50, recompensa_reputacao=1):
    """Cria uma missão de teste com os encontros fornecidos."""
    return Missao(
        nome="Floresta Proibida",
        descricao="Uma missão de teste",
        dificuldade=1,
        encontros=encontros or [],
        recompensa_ouro=recompensa_ouro,
        recompensa_xp=recompensa_xp,
        recompensa_reputacao=recompensa_reputacao,
    )


# =============================================================
# Testes de Resultado da Missão
# =============================================================
def test_execucao_missao_vitoria_completa():
    """
    Uma expedição em que todos os encontros são vencidos deve retornar
    'vitoria' e consolidar corretamente XP, ouro e reputação.
    """
    em    = EventManager()
    heroi = _make_heroi("Arthur")
    motor = _make_motor_vitoria([heroi])
    equipe = _make_equipe([heroi])

    inimigos_mock = [MagicMock()]
    encontro_combate = EncontroCombate(inimigos_mock)
    encontro_texto   = EncontroTexto("Você encontra um acampamento!", {'ouro': 20})

    missao = _make_missao(
        encontros=[encontro_texto, encontro_combate],
        recompensa_ouro=100,
        recompensa_xp=50,
        recompensa_reputacao=2,
    )

    resultado = missao.executar(equipe, motor, em)

    assert resultado['resultado']    == 'vitoria'
    assert heroi in resultado['herois_sobreviventes']
    # ouro: 20 (evento texto) + 10 (combate) + 100 (recompensa)
    assert resultado['ouro_total']   == 130
    # xp: 0 (texto) + 50 (combate) + 50 (recompensa)
    assert resultado['xp_total']     == 100
    assert resultado['reputacao_ganha'] == 2


def test_execucao_missao_derrota_interrompe_encontros():
    """
    Se a equipe for derrotada em um encontro intermediário, a missão deve
    ser interrompida imediatamente e os encontros seguintes não devem ser executados.
    """
    em    = EventManager()
    motor = _make_motor_derrota()
    equipe = _make_equipe([_make_heroi("Arthur")])

    # Dois encontros de combate; o primeiro resulta em derrota
    inimigos_mock   = [MagicMock()]
    encontro1       = EncontroCombate(inimigos_mock)
    encontro2       = MagicMock()  # Este NÃO deve ser chamado

    missao = _make_missao(encontros=[encontro1, encontro2])
    resultado = missao.executar(equipe, motor, em)

    assert resultado['resultado'] == 'derrota'
    assert resultado['herois_sobreviventes'] == []
    assert resultado['reputacao_ganha']      == 0
    # O segundo encontro nunca deve ter sido executado
    encontro2.executar.assert_not_called()


def test_encontro_texto_aplica_dano_nos_herois():
    """
    Um EncontroTexto com efeito de dano deve chamar receber_dano
    em todos os heróis vivos da equipe.
    """
    em = EventManager()
    heroi1 = _make_heroi("Arthur")
    heroi2 = _make_heroi("Merlin")
    equipe = _make_equipe([heroi1, heroi2])

    encontro = EncontroTexto("Uma armadilha dispara!", {'dano_hp': 15})
    resultado = encontro.executar(equipe.membros, None, em)

    heroi1.receber_dano.assert_called_once_with(15, fonte='evento')
    heroi2.receber_dano.assert_called_once_with(15, fonte='evento')
    assert resultado['sucesso'] is True


def test_encontro_texto_aplica_cura_nos_herois():
    """
    Um EncontroTexto com efeito de cura deve chamar curar
    em todos os heróis vivos da equipe.
    """
    em = EventManager()
    heroi = _make_heroi("Arthur")
    equipe = _make_equipe([heroi])

    encontro = EncontroTexto("Você descansa num acampamento.", {'cura_hp': 20})
    resultado = encontro.executar(equipe.membros, None, em)

    heroi.curar.assert_called_once_with(20)
    assert resultado['sucesso'] is True


def test_encontro_texto_retorna_ouro():
    """Um EncontroTexto com efeito de ouro positivo deve retornar esse valor."""
    em = EventManager()
    heroi = _make_heroi("Arthur")

    encontro = EncontroTexto("Você encontra um baú abandonado!", {'ouro': 50})
    resultado = encontro.executar([heroi], None, em)

    assert resultado['ouro_ganho'] == 50
    assert resultado['tipo']       == 'texto'


# =============================================================
# Testes de Progressão de Campanha (GameState)
# =============================================================
def test_progressao_campanha_avanca_missao_ao_registrar():
    """
    Registrar uma missão concluída deve avançar o índice da missão ativa.
    """
    missao1 = _make_missao()
    missao1_obj = MagicMock()
    missao1_obj.nome = "Floresta Proibida"
    missao2_obj = MagicMock()
    missao2_obj.nome = "Ruínas do Norte"

    gs = GameState(
        guilda=MagicMock(),
        taverna=MagicMock(),
        dia_atual=1,
        marco_historia=0,
        list_missoes_concluidas=[],
        campanha=[missao1_obj, missao2_obj]
    )

    # A missão ativa inicial é a primeira
    assert gs.obter_missao_ativa() is missao1_obj

    # Registra a conclusão da primeira
    gs.registrar_missao_concluida("Floresta Proibida")

    # Agora a missão ativa deve ser a segunda
    assert gs.obter_missao_ativa() is missao2_obj


def test_campanha_concluida_retorna_none():
    """
    Quando todas as missões foram concluídas, obter_missao_ativa deve
    retornar None.
    """
    missao_obj = MagicMock()
    missao_obj.nome = "Floresta Proibida"

    gs = GameState(
        guilda=MagicMock(),
        taverna=MagicMock(),
        dia_atual=1,
        marco_historia=0,
        list_missoes_concluidas=["Floresta Proibida"],
        campanha=[missao_obj]
    )

    assert gs.obter_missao_ativa() is None


# =============================================================
# Testes de Emissão de Eventos da Missão
# =============================================================
def test_emissao_eventos_missao():
    """
    Uma missão executada deve emitir os eventos:
    missao_iniciada, encontro_iniciado e missao_finalizada.
    """
    em = EventManager()
    eventos_capturados = []

    em.inscrever("missao_iniciada",   lambda **d: eventos_capturados.append("missao_iniciada"))
    em.inscrever("encontro_iniciado", lambda **d: eventos_capturados.append("encontro_iniciado"))
    em.inscrever("missao_finalizada", lambda **d: eventos_capturados.append("missao_finalizada"))

    heroi  = _make_heroi("Arthur")
    motor  = _make_motor_vitoria([heroi])
    equipe = _make_equipe([heroi])

    encontro = EncontroCombate([MagicMock()])
    missao   = _make_missao(encontros=[encontro])

    missao.executar(equipe, motor, em)

    assert "missao_iniciada"   in eventos_capturados
    assert "encontro_iniciado" in eventos_capturados
    assert "missao_finalizada" in eventos_capturados
