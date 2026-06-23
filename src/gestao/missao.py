# =====================================================
# Missão ----------------------------------------------
# =====================================================
class Missao:
    """
    Representa uma expedição completa da campanha, composta
    por uma sequência linear de Encontros.

    Orquestra o loop de encontros e devolve ao GameController
    um relatório consolidado para aplicação no GameState.
    """

    def __init__(self, nome: str, descricao: str, dificuldade: int,
                 encontros: list, recompensa_ouro: int,
                 recompensa_xp: int, recompensa_reputacao: int):
        """
        Args:
            nome              : Nome da missão exibido ao jogador.
            descricao         : Texto de introdução/contexto da expedição.
            dificuldade       : Nível de dificuldade sugerido (int).
            encontros         : Lista ordenada de instâncias de Encontro.
            recompensa_ouro   : Ouro adicional concedido na vitória total.
            recompensa_xp     : XP adicional concedido aos sobreviventes na vitória.
            recompensa_reputacao : Reputação ganha na Guilda ao concluir a missão.
        """
        self.__nome                = nome
        self.__descricao           = descricao
        self.__dificuldade         = dificuldade
        self.__encontros           = encontros
        self.__recompensa_ouro     = recompensa_ouro
        self.__recompensa_xp       = recompensa_xp
        self.__recompensa_reputacao = recompensa_reputacao

    # =====================================================
    # Getters ---------------------------------------------
    # =====================================================
    @property
    def nome(self):
        return self.__nome

    @property
    def descricao(self):
        return self.__descricao

    @property
    def dificuldade(self):
        return self.__dificuldade

    @property
    def encontros(self):
        return list(self.__encontros)

    @property
    def recompensa_ouro(self):
        return self.__recompensa_ouro

    @property
    def recompensa_xp(self):
        return self.__recompensa_xp

    @property
    def recompensa_reputacao(self):
        return self.__recompensa_reputacao

    # =====================================================
    # Execução Principal ----------------------------------
    # =====================================================
    def executar(self, equipe, motor_combate, event_manager) -> dict:
        """
        Roda todos os encontros da missão em sequência.
        Interrompe imediatamente se a equipe for derrotada.

        Args:
            equipe        : Instância de Equipe com a lista de membros.
            motor_combate : Instância de MotorDeCombate (injetada).
            event_manager : Instância de EventManager (injetada).

        Returns:
            Dicionário consolidado com o resultado final da expedição:
            {
                'resultado'           : str,   # 'vitoria' | 'derrota'
                'herois_sobreviventes': list,
                'herois_mortos'       : list,
                'itens_saqueados'     : list,
                'itens_recuperados'   : list,
                'itens_perdidos'      : list,
                'xp_total'            : int,
                'ouro_total'          : int,
                'reputacao_ganha'     : int,
            }
        """
        event_manager.emitir_evento("missao_iniciada", {
            'nome'      : self.__nome,
            'descricao' : self.__descricao,
            'dificuldade': self.__dificuldade,
        })

        # Acumuladores consolidados ao longo de toda a expedição
        membros_atuais     = list(equipe.membros)
        todos_mortos        = []
        todos_saqueados     = []
        todos_recuperados   = []
        todos_perdidos      = []
        xp_total            = 0
        ouro_total          = 0

        for i, encontro in enumerate(self.__encontros):
            resultado_enc = encontro.executar(membros_atuais, motor_combate, event_manager)

            # Atualiza os acumuladores com o resultado deste encontro
            mortos_enc = resultado_enc.get('herois_mortos', [])
            todos_mortos.extend(mortos_enc)
            todos_saqueados.extend(resultado_enc.get('itens_saqueados', []))
            todos_recuperados.extend(resultado_enc.get('itens_recuperados', []))
            todos_perdidos.extend(resultado_enc.get('itens_perdidos', []))
            xp_total   += resultado_enc.get('xp_ganho', 0)
            ouro_total += resultado_enc.get('ouro_ganho', 0)

            # Atualiza a lista de combatentes para o próximo encontro
            membros_atuais = resultado_enc.get('herois_vivos', [])

            # Se o encontro falhou (equipe dizimada), encerra a expedição
            if not resultado_enc['sucesso']:
                event_manager.emitir_evento("missao_finalizada", {
                    'resultado' : 'derrota',
                    'nome'      : self.__nome,
                    'encontro'  : i + 1,
                })
                return {
                    'resultado'           : 'derrota',
                    'herois_sobreviventes': [],
                    'herois_mortos'       : todos_mortos,
                    'itens_saqueados'     : todos_saqueados,
                    'itens_recuperados'   : todos_recuperados,
                    'itens_perdidos'      : todos_perdidos,
                    'xp_total'            : xp_total,
                    'ouro_total'          : ouro_total,
                    'reputacao_ganha'     : 0,
                }

        # Todos os encontros superados → VITÓRIA
        ouro_total   += self.__recompensa_ouro
        xp_total     += self.__recompensa_xp
        reputacao     = self.__recompensa_reputacao

        event_manager.emitir_evento("missao_finalizada", {
            'resultado'         : 'vitoria',
            'nome'              : self.__nome,
            'recompensa_ouro'   : self.__recompensa_ouro,
            'recompensa_xp'     : self.__recompensa_xp,
            'recompensa_reputacao': reputacao,
        })

        return {
            'resultado'           : 'vitoria',
            'herois_sobreviventes': membros_atuais,
            'herois_mortos'       : todos_mortos,
            'itens_saqueados'     : todos_saqueados,
            'itens_recuperados'   : todos_recuperados,
            'itens_perdidos'      : todos_perdidos,
            'xp_total'            : xp_total,
            'ouro_total'          : ouro_total,
            'reputacao_ganha'     : reputacao,
        }
