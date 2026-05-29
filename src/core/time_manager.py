class GerenciadorDeTempo():
    
    def __init__(self, game_state, event_manager):
        self.__game_state = game_state
        self.__event_manager = event_manager
        
        
    def avancar_dia(self):
        
        temp = self.__game_state.dia_atual
        self.__game_state.incrementar_dia()
        
        if temp == self.__game_state.dia_atual:
            raise ValueError("Erro: Não foi possível avançar o dia")
            return 
        
        self.__event_manager.emitir_evento("novo_dia")
