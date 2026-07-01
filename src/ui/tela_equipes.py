"""
tela_equipes.py
---------------
Tela de Gerenciamento de Equipes (Fase 3.3).

Permite:
  - Visualizar heróis desocupados no Roster da guilda.
  - Visualizar as equipes ativas e seus membros atuais.
  - Alocar/remover heróis das equipes de forma interativa.
  - Criar novas equipes com limite de 3 equipes de no máximo 4 membros cada.
  - Desfazer equipes.
  - Abrir inventário individual do herói.
"""

import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao
from ui.componentes.painel_hud import PainelHud
from gestao.equipe import Equipe


class TelaEquipes(TelaBase):
    """Tela para gerenciar roster, formar e dissolver equipes da guilda."""

    def __init__(self, gerenciador, game_state, controller):
        super().__init__(gerenciador, game_state)
        self.__controller = controller
        self.__hud = PainelHud(gerenciador.largura)

        # Botão Voltar
        self.__btn_voltar = Botao(
            pygame.Rect(50, 640, 180, 40),
            "Voltar p/ Guilda",
            callback=self.__voltar,
            tamanho_fonte=16
        )
        self.__btn_voltar.vincular_gerenciador(gerenciador)

        # Botão Criar Equipe
        self.__btn_criar_equipe = Botao(
            pygame.Rect(970, 640, 260, 40),
            "Criar Nova Equipe",
            callback=self.__abrir_criacao_equipe,
            tamanho_fonte=16
        )
        self.__btn_criar_equipe.vincular_gerenciador(gerenciador)

        # Estado interno de seleção
        self.__heroi_selecionado_roster = None
        self.__status_mensagem = ""
        self.__status_timer = 0.0
        self.__status_cor_tipo = "ouro"

        # Estado da criação de equipe (input)
        self.__modo_criacao = False
        self.__nome_nova_equipe = ""

        # Drag and Drop de Heróis
        self.__dragging_heroi = None
        self.__drag_pos = (0, 0)
        self.__drag_origem = ""

        # Botões dinâmicos de dissolução de equipe
        self.__botoes_dissolver = []
        self.__inicializar_botoes_dissolver()

        # Botões de modal de criação
        cx = gerenciador.largura // 2
        cy = gerenciador.altura // 2
        self.__btn_confirmar_cria = Botao(
            pygame.Rect(cx - 160, cy + 40, 140, 40),
            "Confirmar",
            callback=self.__criar_equipe,
            tamanho_fonte=16
        )
        self.__btn_cancelar_cria = Botao(
            pygame.Rect(cx + 20, cy + 40, 140, 40),
            "Cancelar",
            callback=self.__fechar_criacao_equipe,
            tamanho_fonte=16
        )
        self.__btn_confirmar_cria.vincular_gerenciador(gerenciador)
        self.__btn_cancelar_cria.vincular_gerenciador(gerenciador)

    def __inicializar_botoes_dissolver(self):
        self.__botoes_dissolver.clear()
        # Temos no máximo 3 equipes ativas dispostas na direita.
        # Ys das equipes: Equipe 1 em y=120, Equipe 2 em y=290, Equipe 3 em y=460.
        for idx in range(3):
            y_base = 120 + idx * 170
            btn = Botao(
                pygame.Rect(1110, y_base + 10, 120, 32),
                "Desfazer",
                callback=lambda i=idx: self.__dissolver_equipe(i),
                tamanho_fonte=14
            )
            btn.vincular_gerenciador(self._gerenciador)
            self.__botoes_dissolver.append(btn)

    def ao_entrar(self):
        self.__heroi_selecionado_roster = None
        self.__modo_criacao = False
        self.__nome_nova_equipe = ""
        self.__atualizar_estado_botoes()

    def __atualizar_estado_botoes(self):
        guilda = self._game_state.guilda
        # Desabilita botão de criar equipe se já tiver 3 ou mais
        self.__btn_criar_equipe.ativo = (len(guilda.equipes_ativas) < 3)

        # Atualiza botões de dissolução
        for i, btn in enumerate(self.__botoes_dissolver):
            btn.ativo = (i < len(guilda.equipes_ativas))

    def __voltar(self):
        self._gerenciador.pop()

    def __abrir_criacao_equipe(self):
        self.__nome_nova_equipe = ""
        self.__modo_criacao = True

    def __fechar_criacao_equipe(self):
        self.__modo_criacao = False
        self.__nome_nova_equipe = ""

    def __criar_equipe(self):
        nome = self.__nome_nova_equipe.strip()
        if not nome:
            self.__mostrar_mensagem("Nome da equipe não pode ser vazio!", "erro")
            return
        if len(nome) > 20:
            self.__mostrar_mensagem("Nome muito grande (máximo 20 caracteres)!", "erro")
            return

        guilda = self._game_state.guilda
        guilda.formar_equipe(nome, [])
        self.__mostrar_mensagem(f"Equipe '{nome}' criada com sucesso!", "verde")
        self.__fechar_criacao_equipe()
        self.__atualizar_estado_botoes()

    def __dissolver_equipe(self, idx: int):
        guilda = self._game_state.guilda
        if idx < len(guilda.equipes_ativas):
            equipe = guilda.equipes_ativas[idx]
            # Devolve os heróis ao roster
            for m in list(equipe.membros):
                equipe.remover_membro(m)
            guilda.equipes_ativas.remove(equipe)
            self.__mostrar_mensagem(f"Equipe '{equipe.nome}' foi desfeita.", "ouro")
            self.__atualizar_estado_botoes()

    def __alocar_no_roster(self, heroi):
        # Remove de qualquer equipe se estiver em alguma
        guilda = self._game_state.guilda
        for eq in guilda.equipes_ativas:
            if heroi in eq.membros:
                eq.remover_membro(heroi)
                self.__mostrar_mensagem(f"{heroi.nome} retornou para a reserva.", "ouro")
                break

    def __alocar_na_equipe(self, heroi, equipe):
        if len(equipe.membros) >= equipe.limite_membros:
            self.__mostrar_mensagem(f"Equipe '{equipe.nome}' está cheia!", "erro")
            return

        # Garante que ele é retirado de outra equipe primeiro
        self.__alocar_no_roster(heroi)
        # Adiciona na equipe escolhida
        equipe.adicionar_membro(heroi)
        self.__mostrar_mensagem(f"{heroi.nome} alocado em '{equipe.nome}'.", "verde")

        # Avança tutorial guiado
        if self._game_state.tutorial_passo == 3:
            self._game_state.tutorial_passo = 5

    def __mostrar_mensagem(self, texto, cor_tipo="ouro"):
        self.__status_mensagem = texto
        self.__status_timer = 3.0
        self.__status_cor_tipo = cor_tipo

    # ------------------------------------------------------------------
    # Tratamento de Eventos
    # ------------------------------------------------------------------
    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            if self.__modo_criacao:
                if ev.type == pygame.TEXTINPUT:
                    if len(self.__nome_nova_equipe) < 20:
                        self.__nome_nova_equipe += ev.text
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_RETURN:
                        self.__criar_equipe()
                    elif ev.key == pygame.K_BACKSPACE:
                        self.__nome_nova_equipe = self.__nome_nova_equipe[:-1]
                    elif ev.key == pygame.K_ESCAPE:
                        self.__fechar_criacao_equipe()
                self.__btn_confirmar_cria.lidar_evento(ev)
                self.__btn_cancelar_cria.lidar_evento(ev)
            else:
                self.__btn_voltar.lidar_evento(ev)
                self.__btn_criar_equipe.lidar_evento(ev)
                for btn in self.__botoes_dissolver:
                    btn.lidar_evento(ev)

                # Eventos de Drag & Drop e Cliques
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    # Clique na coluna da esquerda (Reserva)
                    clicado_reserva = self.__checar_clique_roster(ev.pos)
                    if clicado_reserva:
                        self.__dragging_heroi = clicado_reserva
                        self.__drag_pos = ev.pos
                        self.__drag_origem = "roster"
                    else:
                        # Clique nas equipes da direita (pode retornar herói para drag)
                        clicado_equipe = self.__checar_clique_equipes(ev.pos)
                        if clicado_equipe:
                            self.__dragging_heroi = clicado_equipe
                            self.__drag_pos = ev.pos
                            self.__drag_origem = "equipe"

                elif ev.type == pygame.MOUSEMOTION:
                    if self.__dragging_heroi:
                        self.__drag_pos = ev.pos

                elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                    if self.__dragging_heroi:
                        # Soltou o arrasto
                        if self.__drag_origem == "roster":
                            # Se soltou sobre o painel de alguma equipe, aloca!
                            guilda = self._game_state.guilda
                            for idx_eq, eq in enumerate(guilda.equipes_ativas):
                                y_base = 135 + idx_eq * 155
                                eq_rect = self.obter_rect(600, y_base, 620, 140)
                                if eq_rect.collidepoint(ev.pos):
                                    self.__alocar_na_equipe(self.__dragging_heroi, eq)
                                    self.__heroi_selecionado_roster = None
                                    break
                        elif self.__drag_origem == "equipe":
                            # Se soltou sobre a reserva (esquerda), desaloca!
                            rect_reserva = self.obter_rect(40, 120, 520, 500)
                            if rect_reserva.collidepoint(ev.pos):
                                self.__alocar_no_roster(self.__dragging_heroi)
                                if self.__heroi_selecionado_roster == self.__dragging_heroi:
                                    self.__heroi_selecionado_roster = None
                        self.__dragging_heroi = None

    def __checar_clique_roster(self, mouse_pos):
        guilda = self._game_state.guilda
        herois_ocupados = []
        for eq in guilda.equipes_ativas:
            herois_ocupados.extend(eq.membros)
        roster_disponivel = [h for h in guilda.roster_herois if h not in herois_ocupados]

        for idx, heroi in enumerate(roster_disponivel[:4]):
            y_lin = 160 + idx * 48
            rect_linha = self.obter_rect(60, y_lin, 480, 42)
            if rect_linha.collidepoint(mouse_pos):
                if self.__heroi_selecionado_roster == heroi:
                    self.__heroi_selecionado_roster = None
                else:
                    self.__heroi_selecionado_roster = heroi
                return heroi
        return None

    def __checar_clique_equipes(self, mouse_pos) -> object:
        guilda = self._game_state.guilda
        for idx_eq, eq in enumerate(guilda.equipes_ativas):
            y_base = 135 + idx_eq * 155

            for idx_m in range(eq.limite_membros):
                x_pos = 615 + idx_m * 145
                rect_card = self.obter_rect(x_pos, y_base + 40, 135, 85)

                if rect_card.collidepoint(mouse_pos):
                    if idx_m < len(eq.membros):
                        membro = eq.membros[idx_m]
                        # 1. Checa se clicou no botão [X] de remoção (canto superior direito)
                        rect_x_btn = self.obter_rect(x_pos + 112, y_base + 42, 18, 18)
                        if rect_x_btn.collidepoint(mouse_pos):
                            self.__alocar_no_roster(membro)
                            if self.__heroi_selecionado_roster == membro:
                                self.__heroi_selecionado_roster = None
                            return None
                        
                        # 2. Clique simples fora do [X] seleciona para inspeção e inicia drag
                        self.__heroi_selecionado_roster = membro
                        return membro
                    else:
                        # Clicou na vaga vazia. Aloca o selecionado!
                        if self.__heroi_selecionado_roster:
                            # Garante que não aloca o herói que já está em outra equipe se ele foi clicado para inspecionar
                            # (Apenas aloca se o selecionado for de fato um herói da reserva)
                            herois_ocupados = []
                            for eq_act in guilda.equipes_ativas:
                                herois_ocupados.extend(eq_act.membros)
                            if self.__heroi_selecionado_roster not in herois_ocupados:
                                self.__alocar_na_equipe(self.__heroi_selecionado_roster, eq)
                                self.__heroi_selecionado_roster = None
                        return None
        return None

    def atualizar(self, dt: float) -> None:
        if self.__status_timer > 0:
            self.__status_timer -= dt
            if self.__status_timer <= 0:
                self.__status_mensagem = ""

        # Lógica de controle de botões no tutorial
        if self._game_state and self._game_state.tutorial_passo > 0:
            passo = self._game_state.tutorial_passo
            guilda = self._game_state.guilda
            tem_equipes = len(guilda.equipes_ativas) > 0

            if passo == 3:
                if not tem_equipes:
                    self.__btn_voltar.ativo = False
                    self.__btn_criar_equipe.ativo = True
                else:
                    self.__btn_voltar.ativo = False
                    self.__btn_criar_equipe.ativo = False
            elif passo == 5:
                self.__btn_voltar.ativo = True
                self.__btn_criar_equipe.ativo = False
        else:
            # Sem tutorial: comportamento padrão
            self.__btn_voltar.ativo = True
            self.__btn_criar_equipe.ativo = (len(self._game_state.guilda.equipes_ativas) < 3)

    # ------------------------------------------------------------------
    # Renderização da Tela
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

        # 1. HUD
        self.__hud.desenhar(surface, self._game_state)

        # Título
        self._renderizar_texto_com_sombra(
            surface, "GERENCIAMENTO DE ROSTER E EQUIPES",
            fonte_tit, cores["texto_ouro"],
            (self.obter_x(50), self.obter_y(85))
        )

        # Caixa do tutorial flutuante
        if self._game_state and self._game_state.tutorial_passo > 0:
            passo = self._game_state.tutorial_passo
            guilda = self._game_state.guilda
            tem_equipes = len(guilda.equipes_ativas) > 0
            
            texto_tut = ""
            if passo == 3:
                if not tem_equipes:
                    texto_tut = "Clique em 'Criar Nova Equipe' na base direita para fundar seu primeiro grupo!"
                else:
                    texto_tut = "Arraste o heroi da reserva na esquerda para a equipe ativa ou selecione-o e clique em + Alocar!"
            elif passo == 5:
                texto_tut = "Excelente! Sua equipe esta pronta. Clique em 'Voltar p/ Guilda' para retornar ao salao."

            if texto_tut:
                fonte_tut = self.obter_fonte(22, "vt323")
                rect_tut = self.obter_rect(580, 72, 650, 42)
                self._desenhar_moldura(surface, rect_tut, espessura=2)
                pygame.draw.rect(surface, (235, 215, 185), rect_tut.inflate(-4, -4)) # Papiro amarelo
                
                surf_tut = fonte_tut.render(texto_tut, True, (40, 25, 10))
                tx = rect_tut.x + (rect_tut.width - surf_tut.get_width()) // 2
                ty = rect_tut.y + (rect_tut.height - surf_tut.get_height()) // 2
                surface.blit(surf_tut, (tx, ty))

        # 2. Painel Esquerdo: Roster da Guilda (Reserva)
        roster_panel = self.obter_rect(40, 120, 520, 500)
        self._desenhar_moldura(surface, roster_panel, espessura=2)
        pygame.draw.rect(surface, cores["fundo_painel"], roster_panel.inflate(-4, -4))

        self._renderizar_texto_com_sombra(
            surface, "Guerreiros na Reserva:",
            fonte_corpo, cores["texto_azul"],
            (self.obter_x(60), self.obter_y(130))
        )

        guilda = self._game_state.guilda
        # Filtra os desocupados
        herois_ocupados = []
        for eq in guilda.equipes_ativas:
            herois_ocupados.extend(eq.membros)
        roster_disponivel = [h for h in guilda.roster_herois if h not in herois_ocupados]

        if not roster_disponivel:
            self._renderizar_texto_com_sombra(
                surface, "Nenhum herói ocioso no momento.",
                fonte_peq, cores["texto_acinzentado"],
                (self.obter_x(60), self.obter_y(170))
            )
        else:
            for idx, heroi in enumerate(roster_disponivel[:4]):
                y_lin = 160 + idx * 48
                rect_linha = self.obter_rect(60, y_lin, 480, 42)
                
                # Se selecionado para alocação, destaca em ouro/verde
                if self.__heroi_selecionado_roster == heroi:
                    pygame.draw.rect(surface, (70, 50, 20), rect_linha, border_radius=4)
                    pygame.draw.rect(surface, cores["borda_ouro"], rect_linha, 2, border_radius=4)
                else:
                    pygame.draw.rect(surface, (30, 24, 15), rect_linha, border_radius=4)
                    pygame.draw.rect(surface, cores["borda_escura"], rect_linha, 1, border_radius=4)

                # Nome e Nível do Herói
                txt_h = f"{self.formatar_nome_heroi(heroi.nome)} (Lvl {heroi.nivel})"
                self._renderizar_texto_com_sombra(
                    surface, txt_h,
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(74), self.obter_y(y_lin + 10))
                )

                # Atributo principal e HP
                txt_info = f"HP: {heroi.atributos.valor_hp_max} | For: {heroi.atributos.valor_forca} | Des: {heroi.atributos.valor_destreza}"
                self._renderizar_texto_com_sombra(
                    surface, txt_info,
                    fonte_peq, cores["texto_ouro"],
                    (self.obter_x(320), self.obter_y(y_lin + 10))
                )

        # ── Painel de Detalhes do Herói Selecionado (Reserva) ───────────
        detalhes_rect = self.obter_rect(60, 365, 480, 240)
        self._desenhar_moldura(surface, detalhes_rect, espessura=1)
        pygame.draw.rect(surface, (18, 14, 10), detalhes_rect.inflate(-2, -2))

        if self.__heroi_selecionado_roster:
            h_sel = self.__heroi_selecionado_roster
            attrs_sel = h_sel.atributos

            # Linha 1: Nome e Nível
            self._renderizar_texto_com_sombra(
                surface, f"{self.formatar_nome_heroi(h_sel.nome)} (Lvl {h_sel.nivel})",
                fonte_card, cores["texto_ouro"],
                (self.obter_x(74), self.obter_y(380))
            )

            # Linha 2: Atributos condensados
            txt_attrs = f"FOR: {attrs_sel.valor_forca:<2}  DES: {attrs_sel.valor_destreza:<2}  INT: {attrs_sel.valor_inteligencia:<2}  VEL: {attrs_sel.valor_velocidade:<2}"
            self._renderizar_texto_com_sombra(
                surface, txt_attrs,
                fonte_peq, cores["texto_creme"],
                (self.obter_x(74), self.obter_y(410))
            )

            # Linha 3: HP Barra
            self._renderizar_texto_com_sombra(
                surface, f"HP: {attrs_sel.valor_hp_atual}/{attrs_sel.valor_hp_max}",
                fonte_peq, cores["texto_verde"],
                (self.obter_x(74), self.obter_y(440))
            )
            # Desenha barra gráfica de HP
            hp_ratio = max(0.0, min(1.0, attrs_sel.valor_hp_atual / attrs_sel.valor_hp_max))
            pygame.draw.rect(surface, (50, 10, 10), self.obter_rect(180, 442, 120, 12))
            pygame.draw.rect(surface, (10, 150, 10), self.obter_rect(180, 442, int(120 * hp_ratio), 12))

            # Linha 4: Traços
            traco_txt = f"Traco: {h_sel.lista_tracos[0].nome}" if h_sel.lista_tracos else "Traco: Nenhum"
            self._renderizar_texto_com_sombra(
                surface, traco_txt,
                fonte_peq, cores["texto_azul"],
                (self.obter_x(74), self.obter_y(470))
            )

            # Linha 5: Equipamentos condensados
            itens_sel = [item for item in h_sel.slots_equipados.values() if item]
            if not itens_sel:
                txt_eq_sel = "Equipamentos: Nenhum"
            else:
                txt_eq_sel = "Equipamentos: " + ", ".join([it.nome for it in itens_sel[:3]])
            self._renderizar_texto_com_sombra(
                surface, txt_eq_sel,
                fonte_peq, cores["texto_acinzentado"],
                (self.obter_x(74), self.obter_y(500))
            )

            self._renderizar_texto_com_sombra(
                surface, "(Arraste o heroi ou clique na equipe para alocar)",
                fonte_peq, cores["texto_ouro"],
                (self.obter_x(74), self.obter_y(565))
            )
        else:
            self._renderizar_texto_com_sombra(
                surface, "Selecione um heroi da reserva",
                fonte_peq, cores["texto_acinzentado"],
                (self.obter_x(170), self.obter_y(460))
            )
            self._renderizar_texto_com_sombra(
                surface, "para ver seus detalhes",
                fonte_peq, cores["texto_acinzentado"],
                (self.obter_x(200), self.obter_y(485))
            )

        # 3. Painel Direito: Equipes Ativas
        right_panel = self.obter_rect(580, 120, 660, 500)
        self._desenhar_moldura(surface, right_panel, espessura=2)
        pygame.draw.rect(surface, cores["fundo_painel"], right_panel.inflate(-4, -4))

        if not guilda.equipes_ativas:
            self._renderizar_texto_com_sombra(
                surface, "Nenhuma equipe ativa formada.",
                fonte_corpo, cores["texto_acinzentado"],
                (self.obter_x(600), self.obter_y(150))
            )
            self._renderizar_texto_com_sombra(
                surface, "Clique em 'Criar Nova Equipe' na base direita.",
                fonte_peq, cores["texto_acinzentado"],
                (self.obter_x(600), self.obter_y(180))
            )
        else:
            for idx_eq, eq in enumerate(guilda.equipes_ativas):
                y_base = 135 + idx_eq * 155
                eq_panel_rect = self.obter_rect(600, y_base, 620, 140)
                self._desenhar_moldura(surface, eq_panel_rect, espessura=1)
                pygame.draw.rect(surface, (20, 15, 10), eq_panel_rect.inflate(-2, -2))

                # Nome da Equipe
                self._renderizar_texto_com_sombra(
                    surface, f"EQUIPE: {eq.nome.upper()}",
                    fonte_card, cores["texto_ouro"],
                    (self.obter_x(615), self.obter_y(y_base + 10))
                )

                # Capacidade
                self._renderizar_texto_com_sombra(
                    surface, f"Vagas: {len(eq.membros)}/{eq.limite_membros}",
                    fonte_peq, cores["texto_acinzentado"],
                    (self.obter_x(850), self.obter_y(y_base + 10))
                )

                # Desenha o botão Desfazer desta equipe
                # Ajusta a posição lógica do botão para este frame (o próprio botão aplicará a escala física)
                btn_d = self.__botoes_dissolver[idx_eq]
                btn_d.rect.x = 1080
                btn_d.rect.y = y_base + 5
                btn_d.rect.width = 120
                btn_d.rect.height = 26
                btn_d.desenhar(surface)

                # Lista os heróis na equipe
                for idx_m, membro in enumerate(eq.membros):
                    x_pos = 615 + idx_m * 145
                    m_card = self.obter_rect(x_pos, y_base + 40, 135, 85)
                    pygame.draw.rect(surface, (40, 32, 22), m_card, border_radius=4)
                    pygame.draw.rect(surface, cores["borda_bronze"], m_card, 1, border_radius=4)

                    # Nome do membro
                    nome_m = self.formatar_nome_heroi(membro.nome)
                    self._renderizar_texto_com_sombra(
                        surface, nome_m,
                        fonte_peq, cores["texto_creme"],
                        (self.obter_x(x_pos + 10), self.obter_y(y_base + 48))
                    )

                    # Botão [X] de desalocação rápida
                    rect_x = self.obter_rect(x_pos + 112, y_base + 42, 18, 18)
                    pygame.draw.rect(surface, (180, 40, 40), rect_x, border_radius=3)
                    self._renderizar_texto_com_sombra(
                        surface, "x",
                        fonte_peq, (255, 255, 255),
                        (self.obter_x(x_pos + 117), self.obter_y(y_base + 40))
                    )

                    # Nível e Classe
                    self._renderizar_texto_com_sombra(
                        surface, f"Lvl {membro.nivel}",
                        fonte_peq, cores["texto_ouro"],
                        (self.obter_x(x_pos + 10), self.obter_y(y_base + 70))
                    )

                    # HP
                    self._renderizar_texto_com_sombra(
                        surface, f"HP: {membro.atributos.valor_hp_max}",
                        fonte_peq, cores["texto_verde"],
                        (self.obter_x(x_pos + 10), self.obter_y(y_base + 92))
                    )

                # Vagas sobrando na equipe (Slots vazios com aviso visual)
                for idx_v in range(len(eq.membros), eq.limite_membros):
                    x_pos = 615 + idx_v * 145
                    v_card = self.obter_rect(x_pos, y_base + 40, 135, 85)
                    pygame.draw.rect(surface, (30, 24, 18), v_card, border_radius=4)
                    
                    # Highlight leve ao redor dos slots caso um herói esteja selecionado
                    if self.__heroi_selecionado_roster:
                        pygame.draw.rect(surface, (100, 80, 20), v_card, 1, border_radius=4)
                        self._renderizar_texto_com_sombra(
                            surface, "+ Alocar",
                            fonte_peq, cores["texto_ouro"],
                            (self.obter_x(x_pos + 35), self.obter_y(y_base + 70))
                        )
                    else:
                        pygame.draw.rect(surface, (45, 36, 27), v_card, 1, border_radius=4)
                        self._renderizar_texto_com_sombra(
                            surface, "Vazio",
                            fonte_peq, cores["texto_acinzentado"],
                            (self.obter_x(x_pos + 45), self.obter_y(y_base + 70))
                        )

        # 4. Botões de Ação na base
        self.__btn_voltar.desenhar(surface)
        self.__btn_criar_equipe.desenhar(surface)

        # Mensagem temporária
        if self.__status_mensagem:
            cor = cores["texto_verde"] if self.__status_cor_tipo == "verde" else (cores["texto_vermelho"] if self.__status_cor_tipo == "erro" else cores["texto_ouro"])
            self._renderizar_texto_com_sombra(
                surface, self.__status_mensagem,
                fonte_peq, cor,
                (self.obter_x(260), self.obter_y(650))
            )

        # 5. Modal de Criação de Equipe
        if self.__modo_criacao:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            # Caixa
            m_rect = self.obter_rect(390, 210, 500, 300)
            self._desenhar_moldura(surface, m_rect, espessura=3)
            pygame.draw.rect(surface, cores["fundo_painel"], m_rect.inflate(-6, -6))

            # Conteúdo
            self._renderizar_texto_com_sombra(
                surface, "CRIAR NOVA EQUIPE",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(430), self.obter_y(240))
            )

            self._renderizar_texto_com_sombra(
                surface, "Digite o nome da equipe:",
                fonte_peq, cores["texto_creme"],
                (self.obter_x(430), self.obter_y(290))
            )

            # Input Field visual
            input_box = self.obter_rect(430, 315, 420, 36)
            pygame.draw.rect(surface, (20, 16, 12), input_box)
            pygame.draw.rect(surface, cores["borda_ouro"], input_box, 1)

            # Renderiza o nome digitado
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            txt_input = self.__nome_nova_equipe + cursor
            self._renderizar_texto_com_sombra(
                surface, txt_input,
                fonte_corpo, cores["texto_creme"],
                (self.obter_x(440), self.obter_y(320))
            )

            self.__btn_confirmar_cria.desenhar(surface)
            self.__btn_cancelar_cria.desenhar(surface)

        # ── Desenha herói flutuando ao arrastar ──────────────────────────
        if self.__dragging_heroi:
            drag_box = self.obter_rect(self.__drag_pos[0] - 80, self.__drag_pos[1] - 15, 160, 30)
            pygame.draw.rect(surface, (70, 50, 20), drag_box, border_radius=4)
            pygame.draw.rect(surface, cores["borda_ouro"], drag_box, 1, border_radius=4)
            self._renderizar_texto_com_sombra(
                surface, self.__dragging_heroi.nome.split()[0].upper(),
                fonte_peq, cores["texto_creme"],
                (self.__drag_pos[0] - 60, self.__drag_pos[1] - 8)
            )
