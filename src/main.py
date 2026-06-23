import sys
import os
import time

# Resolve caminhos absolutos para evitar problemas com PYTHONPATH
diretorio_src = os.path.dirname(os.path.abspath(__file__))
diretorio_raiz = os.path.dirname(diretorio_src)

caminhos_adicionais = [
    diretorio_raiz,
    diretorio_src,
    os.path.join(diretorio_src, "entidades"),
    os.path.join(diretorio_src, "core"),
    os.path.join(diretorio_src, "itens"),
    os.path.join(diretorio_src, "gestao"),
    os.path.join(diretorio_src, "factories"),
    os.path.join(diretorio_src, "motor")
]

for caminho in caminhos_adicionais:
    if caminho not in sys.path:
        sys.path.append(caminho)

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
    # Missão 1: Emboscada na Estrada
    inimigo_m1_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial)
    inimigo_m1_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial)
    encontro1_m1 = EncontroTexto(
        narrativa="Sua equipe caminha pela estrada quando vê uma caravana destruída por saqueadores. Moedas estão espalhadas na grama.",
        efeitos={'ouro': 15}
    )
    encontro2_m1 = EncontroCombate(inimigos=[inimigo_m1_1, inimigo_m1_2])
    missao1 = Missao(
        nome="Emboscada na Estrada",
        descricao="Elimine os goblins batedores que atacam os mercadores na entrada da província.",
        dificuldade=1,
        encontros=[encontro1_m1, encontro2_m1],
        recompensa_ouro=60,
        recompensa_xp=50,
        recompensa_reputacao=10
    )

    # Missão 2: O Acampamento Goblin
    inimigo_m2_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 2)
    inimigo_m2_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 2)
    inimigo_m2_3 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 2)
    encontro1_m2 = EncontroTexto(
        narrativa="Ao se aproximar do acampamento goblin, sua equipe encontra um baú abandonado com uma armadilha rudimentar de espinhos.",
        efeitos={'dano_hp': 3, 'ouro': 25}
    )
    encontro2_m2 = EncontroCombate(inimigos=[inimigo_m2_1, inimigo_m2_2, inimigo_m2_3])
    missao2 = Missao(
        nome="O Acampamento Goblin",
        descricao="Ataque a base temporária dos goblins na floresta para reduzir sua presença local.",
        dificuldade=2,
        encontros=[encontro1_m2, encontro2_m2],
        recompensa_ouro=90,
        recompensa_xp=75,
        recompensa_reputacao=15
    )

    # Missão 3: Investigação nas Ruínas
    inimigo_m3_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 5)
    inimigo_m3_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 5)
    encontro1_m3 = EncontroTexto(
        narrativa="Ruínas frias e tomadas pela vegetação. Um gás estranho vaza de uma estátua antiga rachada.",
        efeitos={'dano_hp': 6}
    )
    encontro2_m3 = EncontroTexto(
        narrativa="Ao passar pelo corredor das ruínas, a equipe descobre um altar com água purificadora.",
        efeitos={'cura_hp': 12, 'ouro': 30}
    )
    encontro3_m3 = EncontroCombate(inimigos=[inimigo_m3_1, inimigo_m3_2])
    missao3 = Missao(
        nome="Investigação nas Ruínas",
        descricao="Explore as ruínas de mármore e neutralize os orcs que se instalaram lá.",
        dificuldade=3,
        encontros=[encontro1_m3, encontro2_m3, encontro3_m3],
        recompensa_ouro=130,
        recompensa_xp=100,
        recompensa_reputacao=20
    )

    # Missão 4: Os Esgotos de Prata
    inimigo_m4_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 8)
    inimigo_m4_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 8)
    inimigo_m4_3 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 10)
    encontro1_m4 = EncontroTexto(
        narrativa="O odor fétido nos esgotos é terrível. Mas a equipe avista moedas antigas brilhando sob detritos.",
        efeitos={'ouro': 45}
    )
    encontro2_m4 = EncontroCombate(inimigos=[inimigo_m4_1, inimigo_m4_2, inimigo_m4_3])
    missao4 = Missao(
        nome="Os Esgotos de Prata",
        descricao="Adentre os esgotos da cidade e elimine o ninho de monstros que ameaça os bueiros.",
        dificuldade=4,
        encontros=[encontro1_m4, encontro2_m4],
        recompensa_ouro=180,
        recompensa_xp=130,
        recompensa_reputacao=25
    )

    # Missão 5: A Cripta Esquecida
    inimigo_m5_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 12)
    inimigo_m5_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 12)
    inimigo_m5_3 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 12)
    encontro1_m5 = EncontroTexto(
        narrativa="Lápides quebradas e portas de ferro enferrujadas. Uma presença fria arrepia a espinha de todos.",
        efeitos={'dano_hp': 8}
    )
    encontro2_m5 = EncontroCombate(inimigos=[inimigo_m5_1, inimigo_m5_2, inimigo_m5_3])
    missao5 = Missao(
        nome="A Cripta Esquecida",
        descricao="Purifique a cripta antiga e derrote as criaturas sombrias que a ocuparam.",
        dificuldade=5,
        encontros=[encontro1_m5, encontro2_m5],
        recompensa_ouro=240,
        recompensa_xp=170,
        recompensa_reputacao=30
    )

    # Missão 6: A Floresta dos Murmúrios
    inimigo_m6_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 16)
    inimigo_m6_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 16)
    encontro1_m6 = EncontroTexto(
        narrativa="As árvores parecem sussurrar segredos antigos. A equipe encontra frutos vermelhos brilhantes e deliciosos.",
        efeitos={'cura_hp': 15, 'ouro': 50}
    )
    encontro2_m6 = EncontroCombate(inimigos=[inimigo_m6_1, inimigo_m6_2])
    missao6 = Missao(
        nome="A Floresta dos Murmúrios",
        descricao="Cace os monstros na floresta amaldiçoada para restabelecer a paz regional.",
        dificuldade=6,
        encontros=[encontro1_m6, encontro2_m6],
        recompensa_ouro=310,
        recompensa_xp=220,
        recompensa_reputacao=35
    )

    # Missão 7: A Mina Assombrada
    inimigo_m7_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 20)
    inimigo_m7_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 20)
    inimigo_m7_3 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 22)
    encontro1_m7 = EncontroTexto(
        narrativa="Uma antiga mina abandonada. Um desmoronamento parcial atinge de raspão a retaguarda do grupo.",
        efeitos={'dano_hp': 10}
    )
    encontro2_m7 = EncontroCombate(inimigos=[inimigo_m7_1, inimigo_m7_2, inimigo_m7_3])
    missao7 = Missao(
        nome="A Mina Assombrada",
        descricao="Retome o controle da mina de ferro desocupando-a de invasores letais.",
        dificuldade=7,
        encontros=[encontro1_m7, encontro2_m7],
        recompensa_ouro=400,
        recompensa_xp=280,
        recompensa_reputacao=40
    )

    # Missão 8: O Templo do Fogo
    inimigo_m8_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 25)
    inimigo_m8_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 25)
    inimigo_m8_3 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 25)
    encontro1_m8 = EncontroTexto(
        narrativa="O calor é sufocante e rios de lava cortam o templo. Uma nascente termal mágica cura ferimentos.",
        efeitos={'cura_hp': 20, 'ouro': 80}
    )
    encontro2_m8 = EncontroCombate(inimigos=[inimigo_m8_1, inimigo_m8_2, inimigo_m8_3])
    missao8 = Missao(
        nome="O Templo do Fogo",
        descricao="Expulse os fanáticos orcs que realizam rituais perigosos na cratera do vulcão.",
        dificuldade=8,
        encontros=[encontro1_m8, encontro2_m8],
        recompensa_ouro=500,
        recompensa_xp=350,
        recompensa_reputacao=50
    )

    # Missão 9: A Passagem da Montanha
    inimigo_m9_1 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 30)
    inimigo_m9_2 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 30)
    inimigo_m9_3 = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 35)
    encontro1_m9 = EncontroTexto(
        narrativa="O vento congelante corta a pele. Um desfiladeiro perigoso faz a equipe perder alguns mantimentos.",
        efeitos={'dano_hp': 12}
    )
    encontro2_m9 = EncontroCombate(inimigos=[inimigo_m9_1, inimigo_m9_2, inimigo_m9_3])
    missao9 = Missao(
        nome="A Passagem da Montanha",
        descricao="Abra caminho através da cordilheira gelada e elimine os orcs de elite.",
        dificuldade=9,
        encontros=[encontro1_m9, encontro2_m9],
        recompensa_ouro=650,
        recompensa_xp=450,
        recompensa_reputacao=60
    )

    # Missão 10: A Fortaleza do Dragão Negro
    inimigo_boss = fabrica_inimigos.gerar_inimigo(reputacao_inicial + 45)
    inimigo_boss._nome = "General Orc (Chefe Supremo)"
    encontro1_m10 = EncontroTexto(
        narrativa="Vocês chegam à câmara final da fortaleza. O cheiro de enxofre e cinzas é fortíssimo. Um baú relicário dourado é encontrado.",
        efeitos={'ouro': 150}
    )
    encontro2_m10 = EncontroCombate(inimigos=[inimigo_boss])
    missao10 = Missao(
        nome="A Fortaleza do Dragão Negro",
        descricao="Adentre o covil supremo da fortaleza e derrote o General Orc que comanda a invasão.",
        dificuldade=10,
        encontros=[encontro1_m10, encontro2_m10],
        recompensa_ouro=1000,
        recompensa_xp=600,
        recompensa_reputacao=100
    )

    return [missao1, missao2, missao3, missao4, missao5, missao6, missao7, missao8, missao9, missao10]


def main():
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    titulo = r"""
____/\\\\\\\\\______________________/\\\\\\\\\\\\_________________________________________________        
 __/\\\///////\\\___________________\/\\\////////\\\__________________________________/\\\_________       
  _\/\\\_____\/\\\______/\\\\\\\\\___\/\\\______\//\\\________________________________\/\\\_________      
   _\/\\\\\\\\\\\/______/\\\/////\\\__\/\\\_______\/\\\______/\\\\\\\\____/\\\\\\\\\\__\/\\\\\\\\____     
    _\/\\\//////\\\_____\/\\\\\\\\\\___\/\\\_______\/\\\____/\\\/////\\\__\/\\\//////___\/\\\////\\\__    
     _\/\\\____\//\\\____\/\\\//////____\/\\\_______\/\\\___/\\\\\\\\\\\___\/\\\\\\\\\\__\/\\\\\\\\/___   
      _\/\\\_____\//\\\___\/\\\__________\/\\\_______/\\\___\//\\///////____\////////\\\__\/\\\///\\\___  
       _\/\\\______\//\\\__\/\\\__________\/\\\\\\\\\\\\/_____\//\\\\\\\\\\___/\\\\\\\\\\__\/\\\_\///\\\_ 
        _\///________\///___\///___________\////////////________\//////////___\//////////___\///____\///__
"""
    print(MAGENTA + titulo + RESET)
    print(CYAN + "\nInicializando RpDesk" + RESET, end="", flush=True)
    for _ in range(12):
        time.sleep(0.66)
        print(CYAN + "." + RESET, end="", flush=True)
    time.sleep(1)
    print("\n")
    
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
