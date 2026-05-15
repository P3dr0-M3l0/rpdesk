class EventManager:

    def __init__(self):
        
        self.inscricoes = {
        }


    def inscrever(self, evento, lista_callback):

        if type(lista_callback) != "<class 'list'>":
            lista = []
            lista.append(lista_callback)
            lista_callback = lista

        if evento in self.inscricoes:
            self.inscricoes[evento].extend(lista_callback)
        else:
            self.inscricoes[evento] = lista_callback


    def desinscrever(self, evento):

        if not evento in self.inscricoes:
            raise Exception("ERRO: Evento não existe e não pode ser descadastrado")

        self.inscricoes.pop(evento)
        

    def emitir_evento(self, evento, dados=None):

        lista_func = self.inscricoes.get(evento, None)
        if lista_func == None:
            raise Exception('ERRO: Evento não possui callback')
        for func in lista_func:
            if func == None:
                raise Exception('ERRO: Evento não está cadastrado')
            if dados == None:
                func()
            else:
                func(**dados)

# ----------------------------------------------------

if __name__ == '__main__':
    event_manager = EventManager()

    def somar(a, b):
        print(a)
        print(b)
        return a+b

    print('Inscrevendo somar')
    event_manager.inscrever('soma', somar)
    print(event_manager.inscricoes)
    print(event_manager.emitir_evento('soma', {'a': 10, 'b': 20}))
    print('Desinscrever')
    event_manager.desinscrever('soma')
