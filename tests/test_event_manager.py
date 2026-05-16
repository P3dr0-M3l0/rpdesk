import pytest
from src.core.event_manager import EventManager

def test_inscricao_e_emissao():
    em = EventManager()
    resultado = []
    
    def mock_callback(dano, alvo):
        resultado.append((dano, alvo))

    em.inscrever("dano_recebido", mock_callback)
    em.emitir_evento("dano_recebido", {"dano": 10, "alvo": "Heroi1"})
    
    assert len(resultado) == 1
    assert resultado[0] == (10, "Heroi1")

def test_emissao_sem_inscritos():
    em = EventManager()
    # Não deve quebrar, apenas retornar silenciosamente
    em.emitir_evento("evento_fantasma", {"dado": 1})
    assert True 

def test_desinscrever_erro_evento_inexistente():
    em = EventManager()
    def mock_callback(): pass
    
    with pytest.raises(Exception, match="ERRO: Evento não existe e não pode ser descadastrado"):
        em.desinscrever("evento_falso", mock_callback)

def test_desinscrever_erro_callback_inexistente():
    em = EventManager()
    def mock_callback(): pass
    def mock_callback_nao_inscrito(): pass
    
    em.inscrever("evento_real", mock_callback)
    
    with pytest.raises(Exception, match="ERRO: O 'callback' não está presente na lista desse 'evento'"):
        em.desinscrever("evento_real", mock_callback_nao_inscrito)