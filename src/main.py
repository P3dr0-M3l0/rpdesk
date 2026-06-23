import sys
import os
import time

# Adiciona o diretório src ao path do Python para evitar problemas de importação
diretorio_src = os.path.dirname(os.path.abspath(__file__))
if diretorio_src not in sys.path:
    sys.path.append(diretorio_src)

from core.event_manager import EventManager
from core.save_manager import SaveManager
from core.time_manager import GerenciadorDeTempo
from core.game_state import GameState
from core.game_controller import GameController
from gestao.guilda import Guilda
from gestao.taverna import Taverna
from gestao.missao import Missao
from gestao.encontro_texto import EncontroTexto
from gestao.encontro_combate import EncontroCombate
from entidades.inventario import Inventario
from factories.fabrica_itens import FabricaItens
from factories.fabrica_heroi import FabricaDeHerois
from factories.fabrica_inimigo import FabricaDeInimigos


def criar_campanha(fabrica_inimigos, reputacao_inicial):
    # Gerando inimigos para as batalhas
    inimigo_goblin1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial)
    inimigo_goblin2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial)
    
    inimigo_boss = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 2)
    # Garante um nome legal para o Boss
    inimigo_boss._nome = "Orc Enfurecido (Chefe)"

    # Missão 1: Floresta dos Goblins
    encontro1_m1 = EncontroTexto(
        narrativa="Sua equipe entra na densa floresta seguindo rastros. Um barulho de galhos quebrando assusta os heróis, mas é apenas um coelho.",
        efeitos={'ouro': 10}  # Encontram algumas moedas perdidas no chão
    )
    encontro2_m1 = EncontroCombate(
        inimigos=[inimigo_goblin1, inimigo_goblin2]
    )
    
    missao1 = Missao(
        nome="Emboscada na Floresta",
        descricao="Limpe a floresta dos goblins saqueadores que ameaçam as caravanas de suprimentos.",
        dificuldade=1,
        encontros=[encontro1_m1, encontro2_m1],
        recompensa_ouro=50,
        recompensa_xp=40,
        recompensa_reputacao=10
    )

    # Missão 2: Caverna da Serpente
    encontro1_m2 = EncontroTexto(
        narrativa="O ar na caverna é frio e úmido. Gotas de água caem do teto. De repente, um gás tóxico vaza de uma fenda!",
        efeitos={'dano_hp': 5}  # Equipe sofre um pequeno dano de veneno
    )
    encontro2_m2 = EncontroTexto(
        narrativa="Após a névoa passar, a equipe encontra uma fonte de água límpida e sagrada.",
        efeitos={'cura_hp': 10, 'ouro': 20}
    )
    encontro3_m2 = EncontroCombate(
        inimigos=[inimigo_boss]
    )

    missao2 = Missao(
        nome="O Covil do Orc",
        descricao="Adentre as profundezas da caverna úmida e derrote o chefe dos saqueadores.",
        dificuldade=2,
        encontros=[encontro1_m2, encontro2_m2, encontro3_m2],
        recompensa_ouro=120,
        recompensa_xp=80,
        recompensa_reputacao=25
    )

    return [missao1, missao2]


def main():
    print("Inicializando Mestre de Guilda RPG...")
    
    # 1. Eventos e Fábricas
    event_manager = EventManager()
    fabrica_itens = FabricaItens()
    fabrica_herois = FabricaDeHerois(fabrica_itens, event_manager)
    fabrica_inimigos = FabricaDeInimigos(fabrica_itens, event_manager)

    # 2. Gestão Central
    inventario_guilda = Inventario(capacidade_max=15, lista_itens=[], event_manager=event_manager)
    guilda = Guilda(
        nome="Guilda dos Destemidos",
        ouro=100,
        reputacao=0,
        roster_herois=[],
        equipes_ativas=[],
        inventario_guilda=inventario_guilda
    )
    
    taverna = Taverna(
        herois_disponiveis=[],
        fabrica_herois=fabrica_herois,
        event_manager=event_manager
    )
    taverna.inicializar_hooks()

    # 3. Estado de Jogo e Campanha
    campanha = criar_campanha(fabrica_inimigos, guilda.reputacao)
    game_state = GameState(
        guilda=guilda,
        taverna=taverna,
        dia_atual=1,
        marco_historia=0,
        list_missoes_concluidas=[],
        campanha=campanha
    )

    # 4. Gerenciadores e Controle
    # Define o caminho do save file (embora não salve de fato por ser stub/mock no MVP)
    os.makedirs(os.path.join(os.path.dirname(diretorio_src), "saves"), exist_ok=True)
    caminho_save = os.path.join(os.path.dirname(diretorio_src), "saves", "save.json")
    
    save_manager = SaveManager(caminho_save, event_manager)
    time_manager = GerenciadorDeTempo(game_state, event_manager)
    
    controller = GameController(
        event_manager=event_manager,
        save_manager=save_manager,
        time_manager=time_manager,
        game_state=game_state,
        rodando=True
    )
    
    # 5. Início do Loop de Jogo
    controller.inicializar()
    controller.executar_loop()
    
    print("\nObrigado por jogar!")


if __name__ == "__main__":
    main()
