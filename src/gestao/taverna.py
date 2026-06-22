class Taverna:
    def __init__(self, herois_disponiveis, fabrica_herois, event_manager):
        self.__herois_disponiveis = herois_disponiveis
        self.__fabrica_herois = fabrica_herois
        self.__event_manager = event_manager

        
    def obter_vitrine(self):
        return self.__herois_disponiveis
        
    def inicializar_hooks(self):
        self.__event_manager.inscrever('novo_dia', self.renovar_herois)    
    
    def remover_heroi_comprado(self, heroi):
        if heroi not in self.__herois_disponiveis:
            raise Exception("Erro: O herói a ser removido não existe")
        self.__herois_disponiveis.remove(heroi)
        if heroi in self.__herois_disponiveis:
            raise Exception("Erro: O herói não foi corretamente removido da vitrine")
        return heroi
    
    def renovar_herois(self):
        if self.__herois_disponiveis != []:
            self.__herois_disponiveis.clear()

        if self.__herois_disponiveis != []:
            raise Exception("Erro: Os heróis não foram removidos corretamente da vitrinni")        

        # Por enquanto, a vitrine vai sempre ter 3 heróis
        for i in range(3):
            heroi = self.__fabrica_herois.gerar_heroi()
            self.__herois_disponiveis.append(heroi)
            
    def serializar(self):
        herois_serializados = []
        for heroi in self.__herois_disponiveis:
            herois_serializados.append(heroi.serializar())
        
        dicionario_taverna = {
            'TA_herois_disponiveis' : herois_serializados
        }
        return dicionario_taverna
