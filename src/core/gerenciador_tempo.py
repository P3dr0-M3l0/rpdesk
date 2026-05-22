class GerenciadorDeTempo():
    
    def __init__(self, game_state, event_manager):
        self.__game_state = game_state
        self.__event_manager = event_manager
        
        
    def avancar_dia(self):
        
        self.__game_state.dia_atual += 1
        
        self.__event_manager.emitir_evento("avancar_dia")
