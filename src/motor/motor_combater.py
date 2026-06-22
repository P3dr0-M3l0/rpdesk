import random


class MotorDeCombate:

    def __init__(self, event_manager):
        self.__event_manager = event_manager

    # =====================================================
    # Método Principal ------------------------------------
    # =====================================================
    def rodar_combate(self, herois: list, inimigos: list) -> dict:
        herois_vivos   = [h for h in herois]
        inimigos_vivos = [i for i in inimigos]
        herois_mortos  = []

        self.__event_manager.emitir_evento("combate_iniciado", {
            'herois'  : [h.nome for h in herois_vivos],
            'inimigos': [i.nome for i in inimigos_vivos]
        })

        numero_rodada = 0
        while herois_vivos and inimigos_vivos:
            numero_rodada += 1
            self.__event_manager.emitir_evento("rodada_iniciada", {
                'numero_rodada': numero_rodada
            })

            fila_iniciativa = self.__montar_fila_iniciativa(herois_vivos, inimigos_vivos)

            for entidade in fila_iniciativa:
                if not entidade._vivo:
                    continue

                lado = 'heroi' if entidade in herois_vivos else 'inimigo'
                self.__event_manager.emitir_evento("turno_iniciado", {
                    'nome_entidade': entidade.nome,
                    'lado'         : lado
                })

                contexto = {
                    'herois'  : list(herois_vivos),
                    'inimigos': list(inimigos_vivos)
                }

                acao = entidade.decidir_acao(contexto)
                if acao is None:
                    continue

                self.__executar_acao(acao, entidade)

                mortos_nessa_acao = [h for h in herois_vivos  if not h._vivo]
                mortos_inimigos   = [i for i in inimigos_vivos if not i._vivo]

                for h in mortos_nessa_acao:
                    herois_vivos.remove(h)
                    herois_mortos.append(h)

                for i in mortos_inimigos:
                    inimigos_vivos.remove(i)

                if not herois_vivos or not inimigos_vivos:
                    break

        resultado = "vitoria" if inimigos_vivos == [] and herois_vivos else "derrota"

        xp_acumulado    = self.__calcular_xp(inimigos)
        ouro_saqueado   = self.__calcular_ouro(inimigos)
        itens_saqueados = self.__coletar_itens_inimigos(inimigos)

        itens_recuperados, itens_perdidos = self.__processar_loot_aliados(
            herois_mortos, resultado
        )

        self.__event_manager.emitir_evento("combate_finalizado", {
            'resultado'    : resultado,
            'xp_acumulado' : xp_acumulado,
            'ouro_saqueado': ouro_saqueado
        })

        return {
            'resultado'        : resultado,
            'herois_sobreviventes': herois_vivos,
            'itens_saqueados'  : itens_saqueados,
            'itens_recuperados': itens_recuperados,
            'itens_perdidos'   : itens_perdidos,
            'xp_acumulado'     : xp_acumulado,
            'ouro_saqueado'    : ouro_saqueado
        }

    # =====================================================
    # Métodos Privados de Suporte -------------------------
    # =====================================================
    def __montar_fila_iniciativa(self, herois: list, inimigos: list) -> list:
        """Ordena todas as entidades vivas por velocidade (decrescente)."""
        todas = herois + inimigos
        return sorted(todas, key=lambda e: e.atributos.valor_velocidade, reverse=True)

    def __executar_acao(self, acao: dict, atacante) -> None:
        """Interpreta e executa a intenção de ação retornada pela entidade."""
        tipo_acao = acao.get('acao')
        alvo      = acao.get('alvo')

        if tipo_acao == 'atacar' and alvo is not None and alvo._vivo:
            dano_bruto = atacante.atributos.valor_forca
            alvo.receber_dano(dano_bruto, fonte=atacante.nome)

            self.__event_manager.emitir_evento("acao_executada", {
                'origem'  : atacante.nome,
                'acao'    : 'atacar',
                'alvo'    : alvo.nome,
                'detalhes': {'dano_causado': dano_bruto}
            })

        elif tipo_acao == 'curar' and alvo is not None:
            consumivel = self.__encontrar_consumivel(atacante)
            if consumivel is not None:
                consumivel.usar(alvo)
                atacante.remover_item(consumivel)
                self.__event_manager.emitir_evento("acao_executada", {
                    'origem'  : atacante.nome,
                    'acao'    : 'curar',
                    'alvo'    : alvo.nome,
                    'detalhes': {'item_usado': consumivel.nome}
                })

    def __encontrar_consumivel(self, entidade):
        """Retorna o primeiro consumível encontrado no inventário da entidade, ou None."""
        from itens.consumivel import Consumivel
        for item in entidade.inventario.lista_itens:
            if isinstance(item, Consumivel):
                return item
        return None

    def __calcular_xp(self, inimigos: list) -> int:
        """Soma o XP de recompensa de todos os inimigos que participaram do combate."""
        return sum(i.xp_recompensa for i in inimigos if not i._vivo)

    def __calcular_ouro(self, inimigos: list) -> int:
        """
        Calcula o ouro saqueado dos inimigos mortos.
        Por enquanto usa uma fórmula baseada no XP de recompensa como proxy
        até que um atributo de ouro dedicado seja implementado em Inimigo.
        """
        return sum(max(1, i.xp_recompensa // 5) for i in inimigos if not i._vivo)

    def __coletar_itens_inimigos(self, inimigos: list) -> list:
        """Coleta todos os itens (mochila + slots equipados) dos inimigos mortos."""
        itens = []
        for inimigo in inimigos:
            if not inimigo._vivo:
                itens.extend(inimigo.inventario.lista_itens)
                itens.extend(inimigo.slots_equipados.values())
        return itens

    def __processar_loot_aliados(self, herois_mortos: list, resultado: str):
        """
        Determina quais itens de heróis caídos são recuperados ou perdidos.
        - Derrota: 100% de perda.
        - Vitória: 50% de chance de recuperação por item.
        """
        itens_recuperados = []
        itens_perdidos    = []

        for heroi in herois_mortos:
            todos_itens = list(heroi.inventario.lista_itens)
            todos_itens.extend(heroi.slots_equipados.values())

            for item in todos_itens:
                if resultado == "derrota":
                    itens_perdidos.append(item)
                else:
                    if random.random() < 0.5:
                        itens_recuperados.append(item)
                    else:
                        itens_perdidos.append(item)

        return itens_recuperados, itens_perdidos
