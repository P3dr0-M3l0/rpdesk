class EventManager:

    def __init__(self, inscricoes):
        
        self.inscricoes = inscricoes


    def inscrever(self, evento, callback):

        self.inscricoes[evento] = callback


    def desinscrever(self, evento):

        if not evento in self.inscricoes:
            return "Erro: Evento não existe"

        self.inscricoes.pop(evento)
        

    def emitir_evento(self, evento, dados):

        func = self.inscricoes.get(evento, None)
        if func == None:
            raise TypeError('O evento não está cadastrado')
        return func(**dados)

# ----------------------------------------------------

if __name__ == '__main__':
    event_manager = EventManager({})

    def somar(a, b):
        print(a)
        print(b)
        return a+b

    print('Inscrevendo somar')
    event_manager.inscrever('soma', somar)
    print(event_manager.emitir_evento('soma', {'a': 10, 'b': 20}))
    print('Desinscrever')
    event_manager.desinscrever('soma')
 

