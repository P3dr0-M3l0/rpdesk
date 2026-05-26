import pytest
from src.entidades.entidade import Entidade

class MockEventManager:
    def __init__(self):
        self.eventos_emitidos = []
    def emitir_evento(self, evento, dados=None):
        self.eventos_emitidos.append((evento, dados))

class MockAtributos:
    def verificar_defesa_attr(self, valor):
        return 2 # Defesa fixa de 2 para o teste
    def receber_dano(self, valor):
        self.hp_atual = 0 if valor >= 10 else 10 - valor
        return self.hp_atual

class DummyEntidade(Entidade):
    def decidir_acao(self, contexto):
        return {"acao": "atacar"}
    def verificar_defesa_itens(self, qtnd):
        return 3 # Defesa de item fixa de 3

def test_receber_dano_e_morte():
    mock_em = MockEventManager()
    mock_attr = MockAtributos()
    
    # hp fictício de 10. Dano base será 15.
    # Defesa total: 3 (item) + 2 (attr) = 5. Dano real = 10. (Leva o HP a 0).
    entidade = DummyEntidade(id="uuid-123", nome="Dummy", atributos=mock_attr, inventario=None, event_manager=mock_em)
    
    entidade.receber_dano(15, fonte="Inimigo1")
    
    # Verifica se os eventos foram emitidos corretamente
    assert len(mock_em.eventos_emitidos) == 2
    
    # Primeiro evento: dano_recebido
    assert mock_em.eventos_emitidos[0][0] == "dano_recebido"
    assert mock_em.eventos_emitidos[0][1]["dano"] == 10
    
    # Segundo evento: morte
    assert mock_em.eventos_emitidos[1][0] == "morrer"
    assert mock_em.eventos_emitidos[1][1]["id_morto"] == "uuid-123"
    assert entidade._vivo is False