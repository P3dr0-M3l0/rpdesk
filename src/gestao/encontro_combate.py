from gestao.encontro import Encontro


# =====================================================
# Encontro de Combate ---------------------------------
# =====================================================
class EncontroCombate(Encontro):
    """
    Encontro que aciona o MotorDeCombate com uma lista
    de inimigos pré-definida.
    """

    def __init__(self, inimigos: list):
        """
        Args:
            inimigos: Lista de instâncias de Inimigo para esse encontro.
        """
        self.__inimigos = inimigos

    def executar(self, membros_equipe: list, motor_combate, event_manager) -> dict:
        event_manager.emitir_evento("encontro_iniciado", {
            'tipo'    : 'combate',
            'inimigos': [i.nome for i in self.__inimigos]
        })

        resultado_combate = motor_combate.rodar_combate(membros_equipe, self.__inimigos)

        sucesso = resultado_combate['resultado'] == 'vitoria'

        herois_vivos  = resultado_combate['herois_sobreviventes']
        herois_mortos = [h for h in membros_equipe if h not in herois_vivos]

        return {
            'tipo'             : 'combate',
            'sucesso'          : sucesso,
            'herois_vivos'     : herois_vivos,
            'herois_mortos'    : herois_mortos,
            'itens_saqueados'  : resultado_combate['itens_saqueados'],
            'itens_recuperados': resultado_combate['itens_recuperados'],
            'itens_perdidos'   : resultado_combate['itens_perdidos'],
            'xp_ganho'         : resultado_combate['xp_acumulado'],
            'ouro_ganho'       : resultado_combate['ouro_saqueado'],
        }

    def serializar(self) -> dict:
        return {
            'tipo': 'combate',
            'inimigos': [
                {
                    'nome': i.nome,
                    'forca': i.atributos.forca.valor_base,
                    'destreza': i.atributos.destreza.valor_base,
                    'inteligencia': i.atributos.inteligencia.valor_base,
                    'velocidade': i.atributos.velocidade.valor_base,
                    'hp_max': i.atributos.hp_max.valor_base,
                    'hp_atual': i.atributos.hp_atual.valor_base,
                    'xp_recompensa': i.xp_recompensa
                } for i in self.__inimigos
            ]
        }
