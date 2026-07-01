import sys
import os

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
from ui.graphical_game_controller import GraphicalGameController
from factories.fabrica_itens import FabricaItens
from factories.fabrica_heroi import FabricaDeHerois
from factories.fabrica_inimigo import FabricaDeInimigos


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
    print(CYAN + "\nInicializando interface gráfica..." + RESET)
    
    # 1. Eventos e Fábricas
    event_manager = EventManager()
    fabrica_itens = FabricaItens()
    fabrica_herois = FabricaDeHerois(fabrica_itens, event_manager)
    fabrica_inimigos = FabricaDeInimigos(fabrica_itens, event_manager)

    # 2. Gerenciadores e Controle
    os.makedirs(os.path.join(os.path.dirname(diretorio_src), "saves"), exist_ok=True)
    caminho_save = os.path.join(os.path.dirname(diretorio_src), "saves", "save.json")
    
    save_manager = SaveManager(caminho_save)
    
    controller = GraphicalGameController(
        event_mngr=event_manager,
        save_mngr=save_manager,
        fbrc_inimigos=fabrica_inimigos,
        fbrc_herois=fabrica_herois,
        fbrc_itens=fabrica_itens,
        campanha=[],
        rodando=True
    )
    
    controller.inicializar()
    controller.executar_loop()
    
    print("\nObrigado por jogar!")


if __name__ == "__main__":
    main()
