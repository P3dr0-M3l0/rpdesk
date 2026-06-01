from game_state import GameState


class GameController:
    def __init__(self, event_manager, save_manager, time_manager, game_state, rodando):
        self.__event_manager = event_manager
        self.__save_manager = save_manager
        self.__time_manager = time_manager
        self.__game_state = game_state
        self.__rodando = rodando
       
    
    def __gerar_mundo_dados_iniciais(self):
        # QUANTIA DE OURO QUE O JOGADOR COMEÇA O JOGO
        ouro_inicial = 100
        
        # Definindo o dia do jogo para 1
        self.__game_state.dia_atual = 1
        
        # Definindo a quantia inicial de ouro e a reputação
        guilda = self.__game_state.guilda
        guilda.ouro = ouro_inicial
        guilda.reputacao = 0
        
        # Gerando os primeiros heróis na taverna
        taverna = self.__game_state.taverna
        taverna.renovar_herois()
        
    def inicializar(self):
        pass
    
    def executar_loop(self):
        pass
    
    def __parar_motor(self, dados:dict = None):
        pass