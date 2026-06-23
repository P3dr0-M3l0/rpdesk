from entidades.heroi import Heroi


class Equipe():
    def __init__(self, nome: str, membros, limite_membros: int):
        self.__nome = nome
        self.__membros = membros # lista de heróis
        self.__limite_membros = limite_membros


    @property
    def nome(self):
        return self.__nome
    
    @property
    def membros(self):
        return self.__membros
    
    @property
    def limite_membros(self):
        return self.__limite_membros

    @property    
    def obter_membros_vivos(self):
        return self.__membros

    def alterar_limite_membros(self, valor):
        self.__limite_membros = valor
        
    def adicionar_membro(self, membro):
        if isinstance(membro, Heroi):
            if len(self.__membros) < self.__limite_membros:
                self.__membros.append(membro)
            else:
                # PRINT TEMPORÁRIO
                print("\n\nTemporário: A sua equipe já está com o máximo de integrantes\n")    
        else:
            raise TypeError("Erro: Um objeto diferente de 'Herói' está sendo adicionado a uma equipe")
        
    def remover_membro(self, membro):
        if membro not in self.__membros:
            raise Exception("Erro: Não é possível retirar um membro não presente na equipe")
        self.__membros.remove(membro)
        
    def serializar(self):
        membros_serializados = []
        for membro in self.__membros:
            membros_serializados.append(membro.serializar())
            
        dicionario_equipe = {
            'EQ_nome'           : self.__nome,
            'EQ_membros'        : membros_serializados,
            'EQ_limite_membros' : self.__limite_membros
        }
        return dicionario_equipe