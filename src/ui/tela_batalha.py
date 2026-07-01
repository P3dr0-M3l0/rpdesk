"""
tela_batalha.py
---------------
Tela de Expedição / Batalha (Fase 4.1).

Permite:
  - Selecionar uma equipe ativa da guilda.
  - Exibir o resumo da missão corrente da campanha.
  - Rodar e simular o combate em segundo plano.
  - Exibir os turnos de combate de forma animada/compassada na Arena e painel de Logs.
  - Visualizar cartões com HP dinâmico de aliados e inimigos.
  - Modal final com o Resumo da Expedição e aplicação de recompensas/consequências.
"""

import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao
from ui.componentes.painel_hud import PainelHud
from motor.motor_combater import MotorDeCombate


class TelaBatalha(TelaBase):
    """Tela que executa e ilustra a batalha da campanha."""

    def __init__(self, gerenciador, game_state, controller):
        super().__init__(gerenciador, game_state)
        self.__controller = controller
        self.__hud = PainelHud(gerenciador.largura)

        # Botão Voltar (inicialmente visível para cancelar)
        self.__btn_voltar = Botao(
            pygame.Rect(50, 640, 180, 40),
            "Cancelar",
            callback=self.__voltar,
            tamanho_fonte=16
        )
        self.__btn_voltar.vincular_gerenciador(gerenciador)

        # Botão Partir
        self.__btn_partir = Botao(
            pygame.Rect(970, 640, 260, 40),
            "Iniciar Expedição",
            callback=self.__confirmar_partida,
            tamanho_fonte=16
        )
        self.__btn_partir.vincular_gerenciador(gerenciador)

        # Botão Avançar Turno (durante simulação)
        self.__btn_avancar = Botao(
            pygame.Rect(970, 640, 260, 40),
            "Avançar (Pular)",
            callback=self.__pular_logs,
            tamanho_fonte=16
        )
        self.__btn_avancar.vincular_gerenciador(gerenciador)

        # Botão Fechar Resumo Final
        self.__btn_fechar_resumo = Botao(
            pygame.Rect(540, 470, 200, 40),
            "Fechar Resumo",
            callback=self.__finalizar_e_sair,
            tamanho_fonte=16
        )
        self.__btn_fechar_resumo.vincular_gerenciador(gerenciador)

        # Estado de fluxo
        self.__fase_tela = "selecao"  # selecao | animacao | resumo
        self.__idx_equipe_selecionada = 0
        self.__resultado_expedicao = None

        # Dados da animação e log
        self.__fila_logs = []
        self.__logs_visiveis = []
        self.__idx_log_atual = 0
        self.__tempo_proximo_log = 0.0
        self.__duracao_log = 1.0  # 1.0 segundos por linha de combate

        # Estado da arena (para barras de vida)
        self.__aliados_arena = []   # lista de dicts { nome, hp_atual, hp_max, tremer, time_tremer }
        self.__inimigos_arena = []  # lista de dicts { nome, hp_atual, hp_max, tremer, time_tremer }

        # Erros
        self.__status_mensagem = ""
        self.__status_timer = 0.0

    def ao_entrar(self):
        self.__fase_tela = "selecao"
        self.__idx_equipe_selecionada = 0
        self.__resultado_expedicao = None
        self.__fila_logs.clear()
        self.__logs_visiveis.clear()
        self.__idx_log_atual = 0
        self.__aliados_arena.clear()
        self.__inimigos_arena.clear()
        self.__atualizar_estado_botoes()

    def __atualizar_estado_botoes(self):
        guilda = self._game_state.guilda
        tem_equipes = len(guilda.equipes_ativas) > 0
        missao = self._game_state.obter_missao_ativa()

        equipe_valida = False
        if tem_equipes and self.__idx_equipe_selecionada < len(guilda.equipes_ativas):
            equipe = guilda.equipes_ativas[self.__idx_equipe_selecionada]
            if len(equipe.membros) > 0:
                equipe_valida = True

        self.__btn_partir.ativo = (tem_equipes and missao is not None and equipe_valida)

    def __voltar(self):
        self._gerenciador.pop()

    def __confirmar_partida(self):
        guilda = self._game_state.guilda
        equipes = guilda.equipes_ativas

        if not equipes:
            self.__mostrar_mensagem("Nenhuma equipe ativa para expedição!", "erro")
            return

        equipe = equipes[self.__idx_equipe_selecionada]
        membros_vivos = [m for m in equipe.membros if m._vivo]
        if not membros_vivos:
            self.__mostrar_mensagem("Equipe não tem nenhum guerreiro vivo!", "erro")
            return

        missao = self._game_state.obter_missao_ativa()
        if not missao:
            self.__mostrar_mensagem("Nenhuma expedição disponível na campanha!", "erro")
            return

        # ── Inicia a simulação e coleta os logs estruturados ──
        self.__simular_combate(missao, equipe)
        self.__fase_tela = "animacao"
        self.__tempo_proximo_log = 0.5
        self.__idx_log_atual = 0

    def __pular_logs(self):
        # Exibe todos os logs e aplica todos os efeitos visuais restantes instantaneamente
        fonte_log = self.obter_fonte(26, "vt323")
        largura_max = self.obter_x(1100)
        while self.__idx_log_atual < len(self.__fila_logs):
            log_item = self.__fila_logs[self.__idx_log_atual]
            texto_quebrado = self.__quebrar_linha_log(log_item["texto"], largura_max, fonte_log)
            for l in texto_quebrado:
                self.__logs_visiveis.append(l)
            if log_item["efeito"]:
                self.__aplicar_efeito_combate(log_item["efeito"])
            self.__idx_log_atual += 1
        self.__fase_tela = "resumo"

    def __finalizar_e_sair(self):
        # Aplica consequências no core
        guilda = self._game_state.guilda
        equipe = guilda.equipes_ativas[self.__idx_equipe_selecionada]
        missao = self._game_state.obter_missao_ativa()

        if self.__controller and hasattr(self.__controller, "aplicar_consequencias_missao"):
            self.__controller.aplicar_consequencias_missao(self.__resultado_expedicao, missao, equipe)

        self._gerenciador.pop()

    def __mostrar_mensagem(self, texto, cor_tipo="ouro"):
        self.__status_mensagem = texto
        self.__status_timer = 3.0

    # ------------------------------------------------------------------
    # Simulação e Callbacks de Evento
    # ------------------------------------------------------------------
    def __simular_combate(self, missao, equipe):
        self.__fila_logs.clear()
        self.__aliados_arena.clear()
        self.__inimigos_arena.clear()
        self.__inimigos_hp_max_real = {}

        # Adiciona aliados iniciais com HP real inicial
        for m in equipe.membros:
            if m._vivo:
                self.__aliados_arena.append({
                    "nome": self.formatar_nome_heroi(m.nome),
                    "hp_atual": m.atributos.valor_hp_atual,
                    "hp_max": m.atributos.valor_hp_max,
                    "tremer": False,
                    "time_tremer": 0.0
                })

        em = self._game_state._GameState__event_manager if hasattr(self._game_state, "_GameState__event_manager") else self.__controller._GameController__event_manager

        # Callbacks para capturar o log e efeitos estruturados
        def _cb_encontro_iniciado(tipo, **dados):
            if tipo == 'combate':
                inimigos_str = ', '.join(dados.get('inimigos', []))
                self.__fila_logs.append({
                    "texto": f"Combate iniciado! Inimigos: {inimigos_str}",
                    "efeito": None
                })
            elif tipo == 'texto':
                self.__fila_logs.append({
                    "texto": f"Evento: {dados.get('narrativa', '')}",
                    "efeito": None
                })

        def _cb_evento_texto_processado(efeitos, **_):
            dano = efeitos.get('dano_hp', 0)
            if dano > 0:
                self.__fila_logs.append({
                    "texto": f"A equipe sofreu {dano} de dano por armadilha/evento!",
                    "efeito": ("dano_equipe", None, dano)
                })

        def _cb_acao_executada(origem, acao, alvo, detalhes, **_):
            if acao == 'atacar':
                dano = detalhes.get('dano_causado', 0)
                self.__fila_logs.append({
                    "texto": f"{origem} atacou {alvo} causando {dano} de dano!",
                    "efeito": ("dano", alvo, dano)
                })
            elif acao == 'curar':
                item = detalhes.get('item_usado', 'Poção')
                self.__fila_logs.append({
                    "texto": f"{origem} usou {item} em {alvo}!",
                    "efeito": ("curar", alvo, 20)
                })

        def _cb_morrer(nome_morto, **_):
            self.__fila_logs.append({
                "texto": f"💀 {nome_morto} morreu em combate!",
                "efeito": ("morrer", nome_morto, None)
            })

        def _cb_combate_iniciado(herois, inimigos, **_):
            # Limpa inimigos antigos e preenche com estimativa inicial
            self.__inimigos_arena.clear()
            for ini in inimigos:
                nome_ini = ini if isinstance(ini, str) else getattr(ini, "nome", "Monstro")
                self.__inimigos_arena.append({
                    "nome": nome_ini,
                    "hp_atual": 50,
                    "hp_max": 50,
                    "tremer": False,
                    "time_tremer": 0.0
                })

        def _cb_rodada_finalizada(herois, inimigos, **_):
            # Prepara a sincronização de rodada
            herois_sync = []
            for h in herois:
                nome_h = h if isinstance(h, str) else (h.get("nome", "") if isinstance(h, dict) else getattr(h, "nome", ""))
                hp_a = h.get("hp_atual", 0) if isinstance(h, dict) else getattr(h, "hp_atual", 0)
                hp_m = h.get("hp_max", 1) if isinstance(h, dict) else getattr(h, "hp_max", 1)
                herois_sync.append({"nome": nome_h, "hp_atual": hp_a, "hp_max": hp_m})
                
            inimigos_sync = []
            for i in inimigos:
                nome_i = i if isinstance(i, str) else (i.get("nome", "") if isinstance(i, dict) else getattr(i, "nome", ""))
                hp_a = i.get("hp_atual", 0) if isinstance(i, dict) else getattr(i, "hp_atual", 0)
                hp_m = i.get("hp_max", 1) if isinstance(i, dict) else getattr(i, "hp_max", 1)
                inimigos_sync.append({"nome": nome_i, "hp_atual": hp_a, "hp_max": hp_m})
                self.__inimigos_hp_max_real[nome_i] = hp_m

            self.__fila_logs.append({
                "texto": "--- Fim da Rodada ---",
                "efeito": ("sync", herois_sync, inimigos_sync)
            })

        def _cb_combate_finalizado(resultado, xp_acumulado, **_):
            status = "Vitória" if resultado == "vitoria" else "Derrota"
            self.__fila_logs.append({
                "texto": f"Fim de Combate: {status}! (+{xp_acumulado} XP)",
                "efeito": None
            })

        # Inscreve os listeners
        em.inscrever('encontro_iniciado',         _cb_encontro_iniciado)
        em.inscrever('evento_texto_processado',   _cb_evento_texto_processado)
        em.inscrever('combate_iniciado',          _cb_combate_iniciado)
        em.inscrever('acao_executada',            _cb_acao_executada)
        em.inscrever('morrer',                    _cb_morrer)
        em.inscrever('rodada_finalizada',         _cb_rodada_finalizada)
        em.inscrever('combate_finalizado',        _cb_combate_finalizado)

        # Roda o combate instantaneamente
        motor_combate = MotorDeCombate(em)
        self.__resultado_expedicao = missao.executar(equipe, motor_combate, em)

        # Ajusta os inimigos na arena com os HPs reais detectados pós-simulação
        for ini in self.__inimigos_arena:
            hp_m = self.__inimigos_hp_max_real.get(ini["nome"], 50)
            ini["hp_max"] = hp_m
            ini["hp_atual"] = hp_m

        # Desinscreve
        em.desinscrever('encontro_iniciado',        _cb_encontro_iniciado)
        em.desinscrever('evento_texto_processado',  _cb_evento_texto_processado)
        em.desinscrever('combate_iniciado',         _cb_combate_iniciado)
        em.desinscrever('acao_executada',           _cb_acao_executada)
        em.desinscrever('morrer',                   _cb_morrer)
        em.desinscrever('rodada_finalizada',        _cb_rodada_finalizada)
        em.desinscrever('combate_finalizado',       _cb_combate_finalizado)

    def __aplicar_efeito_combate(self, efeito):
        tipo, alvo, valor = efeito
        if tipo == "dano":
            self.__aplicar_dano_arena(alvo, valor)
        elif tipo == "curar":
            self.__aplicar_cura_arena(alvo, valor)
        elif tipo == "morrer":
            self.__matar_entidade_arena(alvo)
        elif tipo == "dano_equipe":
            if self.__aliados_arena:
                dano_por_membro = valor // len(self.__aliados_arena)
                for al in self.__aliados_arena:
                    self.__aplicar_dano_arena(al["nome"], dano_por_membro)
        elif tipo == "sync":
            # Sincroniza HP real ao final da rodada
            for h in alvo:
                for al in self.__aliados_arena:
                    if al["nome"] in h["nome"].upper() or h["nome"].upper() in al["nome"]:
                        al["hp_atual"] = h["hp_atual"]
                        al["hp_max"] = h["hp_max"]
            for i in valor:
                for ini in self.__inimigos_arena:
                    if ini["nome"].upper() in i["nome"].upper() or i["nome"].upper() in ini["nome"].upper():
                        ini["hp_atual"] = i["hp_atual"]
                        ini["hp_max"] = i["hp_max"]

    def __aplicar_dano_arena(self, nome, dano):
        for ini in self.__inimigos_arena:
            if ini["nome"].upper() in nome.upper() or nome.upper() in ini["nome"].upper():
                ini["hp_atual"] = max(0, ini["hp_atual"] - dano)
                ini["tremer"] = True
                ini["time_tremer"] = 0.3
                return
        for al in self.__aliados_arena:
            if al["nome"].upper() in nome.upper() or nome.upper() in al["nome"].upper():
                al["hp_atual"] = max(0, al["hp_atual"] - dano)
                al["tremer"] = True
                al["time_tremer"] = 0.3
                return

    def __aplicar_cura_arena(self, nome, cura):
        for al in self.__aliados_arena:
            if al["nome"].upper() in nome.upper() or nome.upper() in al["nome"].upper():
                al["hp_atual"] = min(al["hp_max"], al["hp_atual"] + cura)
                return
        for ini in self.__inimigos_arena:
            if ini["nome"].upper() in nome.upper() or nome.upper() in ini["nome"].upper():
                ini["hp_atual"] = min(ini["hp_max"], ini["hp_atual"] + cura)
                return

    def __matar_entidade_arena(self, nome):
        for ini in self.__inimigos_arena:
            if ini["nome"].upper() in nome.upper() or nome.upper() in ini["nome"].upper():
                ini["hp_atual"] = 0
        for al in self.__aliados_arena:
            if al["nome"].upper() in nome.upper() or nome.upper() in al["nome"].upper():
                al["hp_atual"] = 0

    def __quebrar_linha_log(self, texto: str, max_largura_px: int, fonte: pygame.font.Font) -> list:
        palavras = texto.split()
        linhas = []
        linha_atual = []
        for pal in palavras:
            teste_linha = " ".join(linha_atual + [pal])
            largura, _ = fonte.size(teste_linha)
            if largura > max_largura_px:
                if linha_atual:
                    linhas.append(" ".join(linha_atual))
                    linha_atual = [pal]
                else:
                    linhas.append(pal)
                    linha_atual = []
            else:
                linha_atual.append(pal)
        if linha_atual:
            linhas.append(" ".join(linha_atual))
        return list(linhas)

    # ------------------------------------------------------------------
    # Loop de Eventos e Atualização do Tempo de Log
    # ------------------------------------------------------------------
    def atualizar(self, dt: float) -> None:
        if self.__status_timer > 0:
            self.__status_timer -= dt

        # Controle da trepidação dos cartões de combate
        for al in self.__aliados_arena:
            if al["tremer"]:
                al["time_tremer"] -= dt
                if al["time_tremer"] <= 0:
                    al["tremer"] = False
        for ini in self.__inimigos_arena:
            if ini["tremer"]:
                ini["time_tremer"] -= dt
                if ini["time_tremer"] <= 0:
                    ini["tremer"] = False

        # Exibição progressiva de logs de batalha
        if self.__fase_tela == "animacao":
            self.__tempo_proximo_log -= dt
            if self.__tempo_proximo_log <= 0:
                if self.__idx_log_atual < len(self.__fila_logs):
                    log_item = self.__fila_logs[self.__idx_log_atual]
                    
                    # Quebra linha dinamicamente usando Word Wrap antes de exibir!
                    fonte_log = self.obter_fonte(26, "vt323")
                    largura_max = self.obter_x(1100)
                    texto_quebrado = self.__quebrar_linha_log(log_item["texto"], largura_max, fonte_log)
                    for l in texto_quebrado:
                        self.__logs_visiveis.append(l)
                        
                    if log_item["efeito"]:
                        self.__aplicar_efeito_combate(log_item["efeito"])
                    self.__idx_log_atual += 1
                    self.__tempo_proximo_log = self.__duracao_log
                else:
                    self.__fase_tela = "resumo"

    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            if self.__fase_tela == "selecao":
                self.__btn_voltar.lidar_evento(ev)
                self.__btn_partir.lidar_evento(ev)

                # Troca de equipe
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self.__checar_selecao_equipe(ev.pos)
            elif self.__fase_tela == "animacao":
                self.__btn_avancar.lidar_evento(ev)
            elif self.__fase_tela == "resumo":
                self.__btn_fechar_resumo.lidar_evento(ev)

    def __checar_selecao_equipe(self, mouse_pos):
        guilda = self._game_state.guilda
        for idx, eq in enumerate(guilda.equipes_ativas):
            y_pos = 160 + idx * 90
            rect_lin = self.obter_rect(60, y_pos, 480, 78)
            if rect_lin.collidepoint(mouse_pos):
                self.__idx_equipe_selecionada = idx
                self.__atualizar_estado_botoes()
                break

    # ------------------------------------------------------------------
    # Desenho
    # ------------------------------------------------------------------
    def desenhar(self, surface: pygame.Surface) -> None:
        cores = self._assets.CORES
        w = self._gerenciador.largura_real
        h = self._gerenciador.altura_real

        # Fontes
        fonte_tit   = self.obter_fonte(16, "pressstart")
        fonte_card  = self.obter_fonte(12, "pressstart")
        fonte_corpo = self.obter_fonte(24, "vt323")
        fonte_peq   = self.obter_fonte(18, "vt323")

        # HUD
        self.__hud.desenhar(surface, self._game_state)

        # ── 1. Modo Seleção de Equipes ──
        if self.__fase_tela == "selecao":
            self._renderizar_texto_com_sombra(
                surface, "SELECIONE A EQUIPE PARA EXPEDIÇÃO",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(50), self.obter_y(85))
            )

            # Lista de equipes
            left_panel = self.obter_rect(40, 120, 520, 500)
            self._desenhar_moldura(surface, left_panel, espessura=2)
            pygame.draw.rect(surface, cores["fundo_painel"], left_panel.inflate(-4, -4))

            self._renderizar_texto_com_sombra(
                surface, "Suas Equipes Ativas:",
                fonte_corpo, cores["texto_azul"],
                (self.obter_x(60), self.obter_y(135))
            )

            guilda = self._game_state.guilda
            if not guilda.equipes_ativas:
                self._renderizar_texto_com_sombra(
                    surface, "Nenhuma equipe formada!",
                    fonte_peq, cores["texto_vermelho"],
                    (self.obter_x(60), self.obter_y(180))
                )
            else:
                for idx, eq in enumerate(guilda.equipes_ativas):
                    y_pos = 160 + idx * 90
                    rect_lin = self.obter_rect(60, y_pos, 480, 78)

                    if self.__idx_equipe_selecionada == idx:
                        pygame.draw.rect(surface, (70, 50, 20), rect_lin, border_radius=4)
                        pygame.draw.rect(surface, cores["borda_ouro"], rect_lin, 2, border_radius=4)
                    else:
                        pygame.draw.rect(surface, (25, 20, 15), rect_lin, border_radius=4)
                        pygame.draw.rect(surface, cores["borda_escura"], rect_lin, 1, border_radius=4)

                    # Linha 1: Nome da Equipe
                    self._renderizar_texto_com_sombra(
                        surface, eq.nome.upper(),
                        fonte_card, cores["texto_ouro"],
                        (self.obter_x(74), self.obter_y(y_pos + 12))
                    )

                    # Nível médio e HP total
                    avg_lvl = sum(m.nivel for m in eq.membros) / len(eq.membros) if eq.membros else 0.0
                    hp_total = sum(m.atributos.valor_hp_max for m in eq.membros if m._vivo) if eq.membros else 0
                    info_txt = f"Lvl: {avg_lvl:.1f} | HP: {hp_total}"
                    self._renderizar_texto_com_sombra(
                        surface, info_txt,
                        fonte_peq, cores["texto_creme"],
                        (self.obter_x(340), self.obter_y(y_pos + 12))
                    )

                    # Linha 2: Membros
                    nomes = ", ".join([m.nome.split()[0] for m in eq.membros]) if eq.membros else "[Vazia]"
                    if len(nomes) > 40:
                        nomes = nomes[:38] + ".."
                    self._renderizar_texto_com_sombra(
                        surface, nomes,
                        fonte_peq, cores["texto_acinzentado"],
                        (self.obter_x(74), self.obter_y(y_pos + 42))
                    )

            # Detalhes da Missão Corrente
            right_panel = self.obter_rect(580, 120, 660, 500)
            self._desenhar_moldura(surface, right_panel, espessura=2)
            pygame.draw.rect(surface, cores["fundo_painel"], right_panel.inflate(-4, -4))

            self._renderizar_texto_com_sombra(
                surface, "Detalhes da Missão da Campanha:",
                fonte_corpo, cores["texto_azul"],
                (self.obter_x(600), self.obter_y(140))
            )

            missao = self._game_state.obter_missao_ativa()
            if not missao:
                self._renderizar_texto_com_sombra(
                    surface, "Toda a campanha concluída com sucesso! Huzzah!",
                    fonte_corpo, cores["texto_verde"],
                    (self.obter_x(600), self.obter_y(180))
                )
            else:
                self._renderizar_texto_com_sombra(
                    surface, f"Nome: {missao.nome}",
                    fonte_corpo, cores["texto_ouro"],
                    (self.obter_x(600), self.obter_y(180))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"Dificuldade: {missao.dificuldade}",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(600), self.obter_y(220))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"Recompensas:",
                    fonte_peq, cores["texto_azul"],
                    (self.obter_x(600), self.obter_y(250))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"- Ouro:      +{missao.recompensa_ouro}g",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(620), self.obter_y(275))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"- XP:        +{missao.recompensa_xp} xp",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(620), self.obter_y(300))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"- Reputação: +{missao.recompensa_reputacao} rep",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(620), self.obter_y(325))
                )

                # Descrição quebrada
                desc_palavras = missao.descricao.split()
                self._renderizar_texto_com_sombra(
                    surface, "Descrição:",
                    fonte_peq, cores["texto_azul"],
                    (self.obter_x(600), self.obter_y(365))
                )
                
                # Helper simples para quebrar descrição da missão
                linhas_desc = []
                linha_corrente = []
                for p in desc_palavras:
                    if len(" ".join(linha_corrente + [p])) > 55:
                        linhas_desc.append(" ".join(linha_corrente))
                        linha_corrente = [p]
                    else:
                        linha_corrente.append(p)
                if linha_corrente:
                    linhas_desc.append(" ".join(linha_corrente))

                for idx_d, l in enumerate(linhas_desc[:5]):
                    self._renderizar_texto_com_sombra(
                        surface, l,
                        fonte_peq, cores["texto_creme"],
                        (self.obter_x(600), self.obter_y(395 + idx_d * 22))
                    )

            self.__btn_voltar.desenhar(surface)
            self.__btn_partir.desenhar(surface)

        # ── 2. Modo Animação de Combate & Metade Arena / Metade Logs ──
        elif self.__fase_tela == "animacao":
            self._renderizar_texto_com_sombra(
                surface, "BATALHA EM ANDAMENTO...",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(50), self.obter_y(85))
            )

            # Arena Superior (HP de aliados e inimigos - Reduzida para 200px)
            arena_panel = self.obter_rect(40, 120, 1200, 200)
            self._desenhar_moldura(surface, arena_panel, espessura=2)
            pygame.draw.rect(surface, (15, 12, 10), arena_panel.inflate(-4, -4))

            # Aliados (Esquerda)
            self._renderizar_texto_com_sombra(
                surface, "SUA EQUIPE",
                fonte_card, cores["texto_azul"],
                (self.obter_x(60), self.obter_y(132))
            )
            
            N_aliados = len(self.__aliados_arena)
            h_card_aliado = min(36, 150 // max(1, N_aliados))
            espaco_aliado = h_card_aliado + 5
            
            for idx_a, al in enumerate(self.__aliados_arena):
                shake_x = 0
                if al["tremer"]:
                    import random
                    shake_x = random.randint(-4, 4)

                y_p = 155 + idx_a * espaco_aliado
                rect_h = self.obter_rect(60 + shake_x, y_p, 280, h_card_aliado)
                pygame.draw.rect(surface, (35, 25, 20), rect_h, border_radius=4)
                pygame.draw.rect(surface, cores["borda_escura"], rect_h, 1, border_radius=4)

                # Nome formatado (Apenas primeiro nome)
                nome_f = self.formatar_nome_heroi(al["nome"])
                self._renderizar_texto_com_sombra(
                    surface, nome_f,
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(70 + shake_x), self.obter_y(y_p + (h_card_aliado - 18) // 2))
                )

                # Barra HP
                hp_ratio = max(0.0, min(1.0, al["hp_atual"] / al["hp_max"]))
                rect_hp_back = self.obter_rect(170 + shake_x, y_p + (h_card_aliado - 18) // 2 + 2, 100, 14)
                rect_hp_fill = self.obter_rect(170 + shake_x, y_p + (h_card_aliado - 18) // 2 + 2, int(100 * hp_ratio), 14)
                pygame.draw.rect(surface, (60, 20, 20), rect_hp_back, border_radius=3)
                pygame.draw.rect(surface, (20, 140, 40), rect_hp_fill, border_radius=3)

                # HP Text
                if h_card_aliado >= 30:
                    self._renderizar_texto_com_sombra(
                        surface, f"{int(al['hp_atual'])}/{int(al['hp_max'])}",
                        fonte_peq, (255, 255, 255),
                        (self.obter_x(280 + shake_x), self.obter_y(y_p + (h_card_aliado - 18) // 2 - 2))
                    )

            # Inimigos (Direita)
            self._renderizar_texto_com_sombra(
                surface, "INIMIGOS",
                fonte_card, cores["texto_vermelho"],
                (self.obter_x(880), self.obter_y(132))
            )
            
            N_inimigos = len(self.__inimigos_arena)
            h_card_inimigo = min(36, 150 // max(1, N_inimigos))
            espaco_inimigo = h_card_inimigo + 5
            
            for idx_i, ini in enumerate(self.__inimigos_arena):
                shake_x = 0
                if ini["tremer"]:
                    import random
                    shake_x = random.randint(-4, 4)

                y_p = 155 + idx_i * espaco_inimigo
                rect_e = self.obter_rect(880 + shake_x, y_p, 280, h_card_inimigo)
                pygame.draw.rect(surface, (35, 20, 20), rect_e, border_radius=4)
                pygame.draw.rect(surface, cores["borda_escura"], rect_e, 1, border_radius=4)

                # Nome Inimigo (Até 2 palavras)
                nome_i_parts = ini["nome"].split()
                nome_i_exib = " ".join(nome_i_parts[:2]).upper()
                self._renderizar_texto_com_sombra(
                    surface, nome_i_exib,
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(890 + shake_x), self.obter_y(y_p + (h_card_inimigo - 18) // 2))
                )

                # Barra HP Inimigo
                hp_ratio = max(0.0, min(1.0, ini["hp_atual"] / ini["hp_max"]))
                rect_hp_back = self.obter_rect(990 + shake_x, y_p + (h_card_inimigo - 18) // 2 + 2, 100, 14)
                rect_hp_fill = self.obter_rect(990 + shake_x, y_p + (h_card_inimigo - 18) // 2 + 2, int(100 * hp_ratio), 14)
                pygame.draw.rect(surface, (60, 20, 20), rect_hp_back, border_radius=3)
                pygame.draw.rect(surface, (180, 30, 30), rect_hp_fill, border_radius=3)

                if h_card_inimigo >= 30:
                    self._renderizar_texto_com_sombra(
                        surface, f"{int(ini['hp_atual'])}/{int(ini['hp_max'])}",
                        fonte_peq, (255, 255, 255),
                        (self.obter_x(1100 + shake_x), self.obter_y(y_p + (h_card_inimigo - 18) // 2 - 2))
                    )

            # Painel Inferior de Logs de Batalha (Papiro com fonte grande, ampliado para 280px)
            logs_panel = self.obter_rect(40, 340, 1200, 280)
            self._desenhar_moldura(surface, logs_panel, espessura=2)
            pygame.draw.rect(surface, (25, 20, 15), logs_panel.inflate(-4, -4))

            # Exibe logs com fonte grande vt323 e colorização medieval (últimas 8 linhas)
            fonte_log = self.obter_fonte(26, "vt323")
            linhas_log = self.__logs_visiveis[-8:]
            for idx_l, linha in enumerate(linhas_log):
                cor_linha = cores["texto_creme"]
                if "💀" in linha:
                    cor_linha = (255, 75, 75)
                elif "Fim de Combate" in linha or "Vitória" in linha:
                    cor_linha = (100, 255, 100)
                elif "Derrota" in linha or "fracassou" in linha:
                    cor_linha = (255, 100, 100)
                elif "atacou" in linha:
                    atacante = linha.split(" atacou ")[0].strip()
                    eh_aliado = False
                    for al in self.__aliados_arena:
                        if al["nome"].upper() in atacante.upper() or atacante.upper() in al["nome"].upper():
                            eh_aliado = True
                            break
                    if eh_aliado:
                        cor_linha = (130, 200, 255)
                    else:
                        cor_linha = (255, 160, 100)
                elif "usou" in linha or "curou" in linha:
                    cor_linha = (160, 230, 160)
                elif "--- Fim da" in linha:
                    cor_linha = cores["texto_acinzentado"]
                
                self._renderizar_texto_com_sombra(
                    surface, linha,
                    fonte_log, cor_linha,
                    (self.obter_x(60), self.obter_y(358 + idx_l * 32))
                )

            self.__btn_avancar.desenhar(surface)

        # ── 3. Modo Resumo da Expedição (Modal final) ──
        elif self.__fase_tela == "resumo":
            # Arena de Fundo congelada
            arena_panel = self.obter_rect(40, 120, 1200, 500)
            self._desenhar_moldura(surface, arena_panel, espessura=2)
            pygame.draw.rect(surface, (15, 12, 10), arena_panel.inflate(-4, -4))

            # Overlay Escuro
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            # Caixa de Diálogo
            modal_rect = self.obter_rect(340, 160, 600, 380)
            self._desenhar_moldura(surface, modal_rect, espessura=3)
            pygame.draw.rect(surface, cores["fundo_painel"], modal_rect.inflate(-6, -6))

            # Título Resumo
            self._renderizar_texto_com_sombra(
                surface, "RESUMO DA EXPEDIÇÃO",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(480), self.obter_y(190))
            )

            res = self.__resultado_expedicao
            resultado = res["resultado"]

            if resultado == "derrota":
                self._renderizar_texto_com_sombra(
                    surface, "RESULTADO: FRACASSO / DERROTA",
                    fonte_corpo, cores["texto_vermelho"],
                    (self.obter_x(380), self.obter_y(250))
                )
                self._renderizar_texto_com_sombra(
                    surface, "A equipe foi totalmente derrotada em combate.",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(380), self.obter_y(300))
                )
                self._renderizar_texto_com_sombra(
                    surface, "Todos os guerreiros alocados morreram.",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(380), self.obter_y(330))
                )
                self._renderizar_texto_com_sombra(
                    surface, "Seus pertences e mochilas foram perdidos.",
                    fonte_peq, cores["texto_acinzentado"],
                    (self.obter_x(380), self.obter_y(360))
                )
            else:
                self._renderizar_texto_com_sombra(
                    surface, "RESULTADO: EXPEDIÇÃO CONCLUÍDA!",
                    fonte_corpo, cores["texto_verde"],
                    (self.obter_x(380), self.obter_y(250))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"Ouro Saqueado: +{res.get('ouro_total', 0)}g",
                    fonte_peq, cores["texto_ouro"],
                    (self.obter_x(380), self.obter_y(295))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"Experiência:   +{res.get('xp_total', 0)} XP por sobrevivente",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(380), self.obter_y(320))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"Reputação:     +{res.get('reputacao_ganha', 0)} rep",
                    fonte_peq, cores["texto_azul"],
                    (self.obter_x(380), self.obter_y(345))
                )

                # Exibição dos Itens Conquistados no Resumo
                itens_ganhos = res.get('itens_saqueados', []) + res.get('itens_recuperados', [])
                if itens_ganhos:
                    nomes_itens = ", ".join([it.nome for it in itens_ganhos])
                    if len(nomes_itens) > 35:
                        nomes_itens = nomes_itens[:32] + "..."
                    txt_itens = f"Itens: {nomes_itens}"
                    cor_itens = cores["texto_verde"]
                else:
                    txt_itens = "Itens: Nenhum item saqueado"
                    cor_itens = cores["texto_acinzentado"]

                self._renderizar_texto_com_sombra(
                    surface, txt_itens,
                    fonte_peq, cor_itens,
                    (self.obter_x(380), self.obter_y(370))
                )

                # Mortos se houver
                mortos = res.get('herois_mortos', [])
                if mortos:
                    mortos_nomes = ", ".join([h.nome for h in mortos])
                    self._renderizar_texto_com_sombra(
                        surface, f"Baixas: 💀 {mortos_nomes}",
                        fonte_peq, cores["texto_vermelho"],
                        (self.obter_x(380), self.obter_y(405))
                    )

            self.__btn_fechar_resumo.desenhar(surface)
