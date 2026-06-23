class EventManager:

    def __init__(self):
        
        self.__inscricoes = {
        }


    def inscrever(self, evento, callback):

        if not evento in self.__inscricoes:
            self.__inscricoes[evento] = []

        self.__inscricoes[evento].append(callback)


    def desinscrever(self, evento, callback):

        if not evento in self.__inscricoes:
            raise Exception("ERRO: Evento não existe e não pode ser descadastrado")

        if callback in self.__inscricoes[evento]:
            self.__inscricoes[evento].remove(callback)
        else:
            raise Exception("ERRO: O 'callback' não está presente na lista desse 'evento'")
        

    def emitir_evento(self, evento, dados = None):

        lista_callbacks = self.__inscricoes.get(evento)
        
        if lista_callbacks == None:
            return
        
        for func in lista_callbacks:
            if dados == None:
                func()
            else:
                func(**dados)
