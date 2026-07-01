from gestao.encontro import Encontro


# =====================================================
# Encontro de Texto -----------------------------------
# =====================================================
class EncontroTexto(Encontro):
    """
    Encontro narrativo que exibe um texto de sabor e aplica
    um efeito mecânico automático na equipe (sem input do jogador).
    """

    def __init__(self, narrativa: str, efeitos: dict):
        """
        Args:
            narrativa: Texto descritivo do evento para exibição.
            efeitos: Dicionário com os efeitos mecânicos a aplicar.
                Chaves suportadas:
                - 'dano_hp'  : int — dano aplicado a todos os membros
                - 'cura_hp'  : int — cura aplicada a todos os membros
                - 'ouro'     : int — ouro ganho (positivo) ou perdido (negativo)
        """
        self.__narrativa = narrativa
        self.__efeitos   = efeitos

    @property
    def narrativa(self):
        return self.__narrativa

    @property
    def efeitos(self):
        return self.__efeitos

    def executar(self, membros_equipe: list, motor_combate, event_manager) -> dict:
        event_manager.emitir_evento("encontro_iniciado", {
            'tipo'     : 'texto',
            'narrativa': self.__narrativa
        })

        ouro_ganho = self.__efeitos.get('ouro', 0)

        # Aplica dano a todos os membros vivos
        if 'dano_hp' in self.__efeitos:
            dano = self.__efeitos['dano_hp']
            for heroi in membros_equipe:
                if heroi._vivo:
                    heroi.receber_dano(dano, fonte='evento')

        # Aplica cura a todos os membros vivos
        if 'cura_hp' in self.__efeitos:
            cura = self.__efeitos['cura_hp']
            for heroi in membros_equipe:
                if heroi._vivo:
                    heroi.curar(cura)

        event_manager.emitir_evento("evento_texto_processado", {
            'narrativa': self.__narrativa,
            'efeitos'  : self.__efeitos
        })

        herois_vivos  = [h for h in membros_equipe if h._vivo]
        herois_mortos = [h for h in membros_equipe if not h._vivo]
        sucesso       = len(herois_vivos) > 0

        return {
            'tipo'             : 'texto',
            'sucesso'          : sucesso,
            'herois_vivos'     : herois_vivos,
            'herois_mortos'    : herois_mortos,
            'itens_saqueados'  : [],
            'itens_recuperados': [],
            'itens_perdidos'   : [],
            'xp_ganho'         : 0,
            'ouro_ganho'       : ouro_ganho,
        }

    def serializar(self) -> dict:
        return {
            'tipo': 'texto',
            'narrativa': self.__narrativa,
            'efeitos': self.__efeitos
        }
