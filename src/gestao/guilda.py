from equipe import Equipe


class Guilda:
    def __init__(self, nome, ouro, reputacao, roster_herois, equipes_ativas, inventario_guilda):
        self.__nome = nome
        self.__ouro = ouro
        self.__reputacao = reputacao
        self.__roster_herois = roster_herois # lista de HEROIS disponiveis para EQUIPES
        self.__equipes_ativas = equipes_ativas # lista de EQUIPES
        self.__inventario_guilda = inventario_guilda # objeto do tipo Inventario


    # =====================================================
    # Getter e Setters ------------------------------------
    # =====================================================        
    @property
    def nome(self):
        return self.__nome
    
    @nome.setter
    def nome(self, valor):
        if valor == "" or len(valor) > 20:
            return False
        self.__nome = valor
        return True
    
    @property
    def ouro(self):
        return self.__ouro
    
    @ouro.setter
    def ouro(self, valor):
        if valor < 0:
            raise ValueError("Não é possível ter uma quantidade negativa de ouro... ainda")
        self.__ouro = valor
        
    @property
    def reputacao(self):
        return self.__reputacao
    
    @reputacao.setter
    def reputacao(self, valor):
        self.__reputacao = valor
        
    @property
    def roster_herois(self):
        return self.__roster_herois
    
    @property
    def equipes_ativas(self):
        return self.__equipes_ativas
    
    @property
    def inventario_guilda(self):
        return self.__inventario_guilda

    # ===============================================
    # Gestão ----------------------------------------
    # ===============================================
    def remover_heroi_roster(self, heroi):
        if heroi not in self.__roster_herois:
            raise Exception("Erro: O herói a ser removido não está no roster")
        self.__roster_herois.remove(heroi)
        return heroi

    def adicionar_heroi_roster(self, heroi):
        if heroi in self.__roster_herois:
            return
        self.__roster_herois.append(heroi)

    def contratar_heroi(self, heroi, custo):
        if custo <= self.__ouro:
            self.__ouro -= custo
            self.__roster_herois.append(heroi)
            return True
        return False
    
    def formar_equipe(self, nome, list_herois):
        equipe = Equipe(
            nome = nome,
            membros = list_herois,
            limite_membros = 4 # travei como 4 para todas
        )
        for heroi in list_herois:
            self.__roster_herois.remove(heroi)
        self.__equipes_ativas.append(equipe)
        return equipe

    # ===============================================
    # Gestão do baú ---------------------------------
    # ===============================================   
    def adicionar_item_bau(self, item, heroi):
        n_item = heroi.remover_item(item)
        if not self.__inventario_guilda.adicionar_item(n_item):
            heroi.adicionar_item(n_item)
            return False
        return True

    def apagar_item(self, item):
        self.__inventario_guilda.remover_item(item)

    def transferir_item_heroi(self, item, heroi):
        n_item = self.__inventario_guilda.remover_item(item)
        if not heroi.adicionar_item(n_item):
            self.__inventario_guilda.adicionar_item(n_item)

    # ===============================================
    # Para save -------------------------------------
    # ===============================================
    def serializar(self):
        # Serializando o roster
        roster_serializado = []
        for heroi in self.__roster_herois:
            roster_serializado.append(heroi.serializar())

        # Serializando as equipes
        equipes_serializadas = []
        for equipe in self.__equipes_ativas:
            equipes_serializadas.append(equipe.serializar())

        dicionario_guilda = {
            'GU_nome'             : self.__nome,
            'GU_ouro'             : self.__ouro,
            'GU_reputacao'        : self.__reputacao,
            'GU_roster_herois'    : roster_serializado,
            'GU_equipes_ativas'   : equipes_serializadas,
            'GU_inventario_guilda': self.__inventario_guilda.serializar()
        }
        return dicionario_guilda
