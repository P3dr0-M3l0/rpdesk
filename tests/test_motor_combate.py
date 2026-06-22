import pytest
from unittest.mock import MagicMock
from motor.motor_combater import MotorDeCombate
from core.event_manager import EventManager


# =============================================================
# Helpers e Mocks de Entidade para os Testes
# =============================================================
def _make_entidade(nome, velocidade, forca, hp, xp=0, lado='heroi'):
    """Cria uma entidade mock completa para os testes do motor de combate."""
    em = EventManager()
    
    atributos = MagicMock()
    atributos.valor_velocidade = velocidade
    atributos.valor_forca      = forca
    atributos.valor_hp_atual   = hp

    def receber_dano_side_effect(valor):
        atributos.valor_hp_atual = max(0, atributos.valor_hp_atual - valor)
        return atributos.valor_hp_atual

    atributos.receber_dano = MagicMock(side_effect=receber_dano_side_effect)
    atributos.verificar_defesa_attr = MagicMock(return_value=0)

    inventario = MagicMock()
    inventario.lista_itens = []

    entidade = MagicMock()
    entidade.nome            = nome
    entidade.atributos       = atributos
    entidade.inventario      = inventario
    entidade.slots_equipados = {}
    entidade._event_manager  = em
    entidade._vivo           = True
    entidade.xp_recompensa   = xp

    def receber_dano_entidade(qtnd, fonte):
        hp_resultante = receber_dano_side_effect(qtnd)
        em.emitir_evento("dano_recebido", {'dano': qtnd, 'fonte': fonte})
        if hp_resultante == 0:
            entidade._vivo = False
            em.emitir_evento("morrer", {"id_morto": entidade.nome})

    entidade.receber_dano = receber_dano_entidade

    if lado == 'heroi':
        def decidir_acao_heroi(contexto):
            inimigos_vivos = [i for i in contexto['inimigos'] if i._vivo]
            if not inimigos_vivos:
                return None
            return {'acao': 'atacar', 'alvo': inimigos_vivos[0]}
        entidade.decidir_acao = decidir_acao_heroi
    else:
        def decidir_acao_inimigo(contexto):
            herois_vivos = [h for h in contexto['herois'] if h._vivo]
            if not herois_vivos:
                return None
            return {'acao': 'atacar', 'alvo': herois_vivos[0]}
        entidade.decidir_acao = decidir_acao_inimigo

    return entidade


# =============================================================
# Testes de Resultado
# =============================================================
def test_combate_vitoria_da_guilda():
    em = EventManager()
    motor = MotorDeCombate(em)

    heroi   = _make_entidade("Arthur",  velocidade=10, forca=50, hp=100, lado='heroi')
    inimigo = _make_entidade("Goblin",  velocidade=5,  forca=5,  hp=10, xp=50, lado='inimigo')

    resultado = motor.rodar_combate([heroi], [inimigo])

    assert resultado['resultado'] == "vitoria"
    assert heroi in resultado['herois_sobreviventes']


def test_combate_derrota_da_guilda():
    em = EventManager()
    motor = MotorDeCombate(em)

    heroi   = _make_entidade("Arthur",  velocidade=5,  forca=1,  hp=10, lado='heroi')
    inimigo = _make_entidade("Dragão",  velocidade=10, forca=50, hp=500, xp=200, lado='inimigo')

    resultado = motor.rodar_combate([heroi], [inimigo])

    assert resultado['resultado'] == "derrota"
    assert resultado['herois_sobreviventes'] == []


# =============================================================
# Testes de Iniciativa
# =============================================================
def test_iniciativa_respeita_velocidade():
    """A entidade mais rápida deve agir primeiro e deve derrotar a outra antes de levar dano."""
    em = EventManager()
    motor = MotorDeCombate(em)

    # Herói lento e fraco; inimigo rápido e poderoso
    heroi   = _make_entidade("Lerdo",   velocidade=1,  forca=1,  hp=20, lado='heroi')
    inimigo = _make_entidade("Relâmpago", velocidade=20, forca=25, hp=5, xp=10, lado='inimigo')

    resultado = motor.rodar_combate([heroi], [inimigo])

    # O inimigo age primeiro (vel 20 > vel 1) e mata o herói de HP 20 com forca 25
    assert resultado['resultado'] == "derrota"


# =============================================================
# Testes de Limpeza de Mortos
# =============================================================
def test_remocao_entidades_mortas_da_fila():
    """
    Um inimigo abatido numa ação não deve conseguir atacar mais tarde na mesma rodada.
    O herói tem forca suficiente para matar em 1 hit. O inimigo não age.
    """
    em = EventManager()
    motor = MotorDeCombate(em)

    # Herói age primeiro (vel 20), mata o inimigo (vel 5, hp 1)
    heroi   = _make_entidade("Arthur",  velocidade=20, forca=100, hp=100, lado='heroi')
    inimigo = _make_entidade("Zumbi",   velocidade=5,  forca=100, hp=1,  xp=30, lado='inimigo')

    resultado = motor.rodar_combate([heroi], [inimigo])

    assert resultado['resultado'] == "vitoria"
    # O herói sobreviveu intacto pois o inimigo foi removido antes de agir
    assert heroi._vivo is True
    assert heroi.atributos.valor_hp_atual == 100


# =============================================================
# Testes de XP e Ouro
# =============================================================
def test_calculo_acumulado_xp():
    em = EventManager()
    motor = MotorDeCombate(em)

    heroi    = _make_entidade("Arthur",  velocidade=20, forca=100, hp=100, lado='heroi')
    inimigo1 = _make_entidade("Goblin",  velocidade=1,  forca=1,  hp=1, xp=50,  lado='inimigo')
    inimigo2 = _make_entidade("Troll",   velocidade=2,  forca=1,  hp=1, xp=150, lado='inimigo')

    resultado = motor.rodar_combate([heroi], [inimigo1, inimigo2])

    assert resultado['xp_acumulado'] == 200


# =============================================================
# Testes de Emissão de Eventos
# =============================================================
def test_emissao_eventos_combate():
    em = EventManager()
    eventos_capturados = []

    def capturar(dados):
        eventos_capturados.append(dados)

    em.inscrever("combate_iniciado",   lambda **d: eventos_capturados.append(("combate_iniciado",   d)))
    em.inscrever("rodada_iniciada",    lambda **d: eventos_capturados.append(("rodada_iniciada",    d)))
    em.inscrever("turno_iniciado",     lambda **d: eventos_capturados.append(("turno_iniciado",     d)))
    em.inscrever("acao_executada",     lambda **d: eventos_capturados.append(("acao_executada",     d)))
    em.inscrever("combate_finalizado", lambda **d: eventos_capturados.append(("combate_finalizado", d)))

    motor = MotorDeCombate(em)
    heroi   = _make_entidade("Arthur",  velocidade=20, forca=100, hp=100, lado='heroi')
    inimigo = _make_entidade("Goblin",  velocidade=1,  forca=1,  hp=1, xp=30, lado='inimigo')

    motor.rodar_combate([heroi], [inimigo])

    tipos_emitidos = [e[0] for e in eventos_capturados]
    assert "combate_iniciado"   in tipos_emitidos
    assert "rodada_iniciada"    in tipos_emitidos
    assert "turno_iniciado"     in tipos_emitidos
    assert "acao_executada"     in tipos_emitidos
    assert "combate_finalizado" in tipos_emitidos


# =============================================================
# Testes do Dicionário de Retorno
# =============================================================
def test_retorno_detalhado_dicionario():
    em = EventManager()
    motor = MotorDeCombate(em)

    heroi   = _make_entidade("Arthur",  velocidade=20, forca=100, hp=100, lado='heroi')
    inimigo = _make_entidade("Goblin",  velocidade=1,  forca=1,  hp=1, xp=50, lado='inimigo')

    resultado = motor.rodar_combate([heroi], [inimigo])

    assert 'resultado'            in resultado
    assert 'herois_sobreviventes' in resultado
    assert 'itens_saqueados'      in resultado
    assert 'itens_recuperados'    in resultado
    assert 'itens_perdidos'       in resultado
    assert 'xp_acumulado'         in resultado
    assert 'ouro_saqueado'        in resultado
    assert isinstance(resultado['itens_saqueados'],   list)
    assert isinstance(resultado['itens_recuperados'], list)
    assert isinstance(resultado['itens_perdidos'],    list)
    assert isinstance(resultado['xp_acumulado'],      int)
    assert isinstance(resultado['ouro_saqueado'],     int)


# =============================================================
# Testes de Loot de Aliados Caídos
# =============================================================
def test_recuperacao_estocastica_itens_aliados_em_vitoria():
    """
    A soma de itens_recuperados + itens_perdidos deve ser exatamente
    igual ao total de itens que o herói caído carregava.
    """
    em = EventManager()
    motor = MotorDeCombate(em)

    # Herói poderoso que sobrevive
    sobrevivente = _make_entidade("Arthur",  velocidade=20, forca=100, hp=100, lado='heroi')

    # Herói fraco que morre rapidamente (vel baixa, o inimigo age antes)
    # Configuramos com 2 itens no inventário e 1 no slot
    item1, item2, item3 = MagicMock(), MagicMock(), MagicMock()
    vitima = _make_entidade("Vítima", velocidade=1, forca=1, hp=1, lado='heroi')
    vitima.inventario.lista_itens = [item1, item2]
    vitima.slots_equipados        = {"tronco": item3}

    inimigo = _make_entidade("Dragão", velocidade=15, forca=100, hp=200, xp=100, lado='inimigo')

    resultado = motor.rodar_combate([sobrevivente, vitima], [inimigo])

    total_originais   = 3  # item1, item2, item3
    total_recuperados = len(resultado['itens_recuperados'])
    total_perdidos    = len(resultado['itens_perdidos'])

    assert total_recuperados + total_perdidos == total_originais


def test_derrota_perde_todos_itens_aliados():
    """Em caso de derrota, 100% dos itens dos heróis mortos devem ser perdidos."""
    em = EventManager()
    motor = MotorDeCombate(em)

    item1, item2 = MagicMock(), MagicMock()
    heroi = _make_entidade("Fraco",  velocidade=1, forca=1, hp=1, lado='heroi')
    heroi.inventario.lista_itens = [item1, item2]

    inimigo = _make_entidade("Dragão", velocidade=20, forca=100, hp=999, xp=200, lado='inimigo')

    resultado = motor.rodar_combate([heroi], [inimigo])

    assert resultado['resultado']            == "derrota"
    assert resultado['itens_recuperados']    == []
    assert len(resultado['itens_perdidos'])  == 2
