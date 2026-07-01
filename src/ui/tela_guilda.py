"""
tela_guilda.py
--------------
Tela do Hub Central da Guilda.

Apresenta:
  - Menu esquerdo com as principais opções do jogo (Taverna, Equipes, Baú, Batalha, Fim do Dia, Sistema).
  - Painel direito com visão geral da Guilda (lista de equipes ativas e a missão corrente).
  - HUD superior mostrando recursos.
"""

import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao
from ui.componentes.painel_hud import PainelHud
from ui.tela_taverna import TelaTaverna
from ui.tela_equipes import TelaEquipes
from ui.tela_bau import TelaBau
from ui.tela_batalha import TelaBatalha
from ui.tela_sistema import TelaSistema


class TelaGuilda(TelaBase):
    """Hub central do RpDesk gráfico."""

    def __init__(self, gerenciador, game_state, controller):
        """
        Args:
            gerenciador : GerenciadorTelas.
            game_state  : GameState.
            controller  : GraphicalGameController (para chamar transições globais e fim do dia).
        """
        super().__init__(gerenciador, game_state)
        self.__controller = controller
        self.__hud = PainelHud(gerenciador.largura)

        # ── Posicionamento e criação do Menu de Ações (Esquerda) ─────────
        # Adaptado para 1280x720: painel de menu de largura 210, botões menores de 170
        x_menu = 40
        y_inicial = 120
        largura_b = 170
        altura_b = 42
        espaco_b = 16

        opcoes = [
            ("Taverna", self.__ir_taverna),
            ("Equipes e Roster", self.__ir_equipes),
            ("Baú da Guilda", self.__ir_bau),
            ("Partir p/ Missão", self.__ir_missao),
            ("Encerrar o Dia", self.__encerrar_dia),
            ("Sistema / Salvar", self.__ir_sistema),
        ]

        self.__botoes = []
        for i, (label, callback) in enumerate(opcoes):
            rect = pygame.Rect(x_menu, y_inicial + i * (altura_b + espaco_b),
                               largura_b, altura_b)
            btn = Botao(rect, label, callback, tamanho_fonte=16)
            btn.vincular_gerenciador(gerenciador)
            self.__botoes.append(btn)

        self.__status_mensagem = ""
        self.__status_timer = 0.0
        self.__status_cor_tipo = "ouro"

        # Variáveis da animação de Passagem de Noite (Fim de Dia)
        self.__fade_ativo = False
        self.__fade_alpha = 0.0
        self.__fade_estado = "normal"  # normal | fadeout | noite | fadein
        self.__fade_timer = 0.0
        self.__fade_motivo = "normal"

        # Modal de Confirmação de Fim de Dia
        self.__modal_ativo = False
        cx = gerenciador.largura // 2
        self.__btn_confirmar_modal = Botao(
            pygame.Rect(cx - 160, 420, 140, 40),
            "Confirmar",
            callback=self.__confirmar_fim_dia,
            tamanho_fonte=16
        )
        self.__btn_cancelar_modal = Botao(
            pygame.Rect(cx + 20, 420, 140, 40),
            "Cancelar",
            callback=self.__fechar_modal,
            tamanho_fonte=16
        )
        self.__btn_confirmar_modal.vincular_gerenciador(gerenciador)
        self.__btn_cancelar_modal.vincular_gerenciador(gerenciador)

    def ao_entrar(self) -> None:
        """Executado quando a tela do Hub da Guilda é retomada."""
        if self.__controller and getattr(self.__controller, "forcar_fade_fim_dia", False):
            self.__fade_ativo = True
            self.__fade_alpha = 0.0
            self.__fade_estado = "fadeout"
            self.__fade_timer = 0.0
            self.__fade_motivo = self.__controller.fade_motivo
            self.__controller.forcar_fade_fim_dia = False
        else:
            self.__fade_ativo = False
            self.__fade_estado = "normal"
            self.__fade_motivo = "normal"
            
        self.__modal_ativo = False
        self.__status_mensagem = ""

    # ------------------------------------------------------------------
    # Ações dos botões (Transições e Comandos)
    # ------------------------------------------------------------------
    def __ir_taverna(self):
        self._gerenciador.push(TelaTaverna(self._gerenciador, self._game_state, self.__controller))

    def __ir_equipes(self):
        self._gerenciador.push(TelaEquipes(self._gerenciador, self._game_state, self.__controller))

    def __ir_bau(self):
        self._gerenciador.push(TelaBau(self._gerenciador, self._game_state, self.__controller))

    def __ir_missao(self):
        self._gerenciador.push(TelaBatalha(self._gerenciador, self._game_state, self.__controller))

    def __encerrar_dia(self):
        # Valida ouro mínimo
        guilda = self._game_state.guilda
        if guilda.ouro < 10:
            self.__mostrar_mensagem("Você precisa de pelo menos 10 de ouro para manutenção!", cor_tipo="erro")
            return

        self.__modal_ativo = True

    def __confirmar_fim_dia(self):
        self.__modal_ativo = False
        if hasattr(self.__controller, "executar_fim_dia"):
            self.__fade_ativo = True
            self.__fade_alpha = 0.0
            self.__fade_estado = "fadeout"
            self.__fade_timer = 0.0

    def __fechar_modal(self):
        self.__modal_ativo = False

    def __ir_sistema(self):
        self._gerenciador.push(TelaSistema(self._gerenciador, self._game_state, self.__controller))

    def __mostrar_mensagem(self, texto, cor_tipo="ouro"):
        self.__status_mensagem = texto
        self.__status_timer = 3.0  # Mensagem some em 3 segundos
        self.__status_cor_tipo = cor_tipo

    # ------------------------------------------------------------------
    # Loop de Eventos, Atualização e Renderização
    # ------------------------------------------------------------------
    def lidar_eventos(self, eventos: list) -> None:
        # Bloqueia cliques durante o fade
        if self.__fade_ativo:
            return

        for ev in eventos:
            if self.__modal_ativo:
                self.__btn_confirmar_modal.lidar_evento(ev)
                self.__btn_cancelar_modal.lidar_evento(ev)
            else:
                for btn in self.__botoes:
                    btn.lidar_evento(ev)

    def atualizar(self, dt: float) -> None:
        # Gerenciamento de botões de navegação no tutorial
        if self._game_state and self._game_state.tutorial_passo > 0:
            passo = self._game_state.tutorial_passo
            for idx, btn in enumerate(self.__botoes):
                if passo == 1:
                    btn.ativo = (idx == 0)  # Apenas Taverna
                elif passo == 3:
                    btn.ativo = (idx == 1)  # Apenas Equipes e Roster
                elif passo == 5:
                    btn.ativo = (idx == 3)  # Apenas Partir p/ Missão
                else:
                    btn.ativo = False
        else:
            for btn in self.__botoes:
                btn.ativo = True

        # Atualização do status message
        if self.__status_timer > 0:
            self.__status_timer -= dt
            if self.__status_timer <= 0:
                self.__status_mensagem = ""

        # Máquina de estados do Fade (Passagem de Noite)
        if self.__fade_ativo:
            if self.__fade_estado == "fadeout":
                self.__fade_alpha += dt * 350.0  # ~0.7 segundos para escurecer
                if self.__fade_alpha >= 255.0:
                    self.__fade_alpha = 255.0
                    self.__fade_estado = "noite"
                    self.__fade_timer = 2.0  # 2 segundos de noite total

                    # Executa a ação do core (avançar o dia e cobrar taxas) apenas se for avanço manual
                    if self.__fade_motivo != "expedicao":
                        self.__controller.executar_fim_dia()

            elif self.__fade_estado == "noite":
                self.__fade_timer -= dt
                if self.__fade_timer <= 0:
                    self.__fade_estado = "fadein"

            elif self.__fade_estado == "fadein":
                self.__fade_alpha -= dt * 350.0  # ~0.7 segundos para clarear
                if self.__fade_alpha <= 0.0:
                    self.__fade_alpha = 0.0
                    self.__fade_ativo = False
                    self.__fade_estado = "normal"
                    
                    if self.__fade_motivo == "expedicao":
                        self.__mostrar_mensagem("Um novo dia amanheceu! Herois descansaram e recuperaram HP.", cor_tipo="verde")
                    else:
                        self.__mostrar_mensagem("Um novo dia amanheceu! Manutencao cobrada (-10g).", cor_tipo="verde")

    def desenhar(self, surface: pygame.Surface) -> None:
        cores = self._assets.CORES
        # Fontes maiores e nítidas escaladas para alta resolução
        fonte_corpo = self.obter_fonte(26, "vt323")
        fonte_peq   = self.obter_fonte(20, "vt323")
        fonte_tit   = self.obter_fonte(16, "pressstart")

        # 1. Desenha o HUD superior
        self.__hud.desenhar(surface, self._game_state)

        # Desenha a caixa flutuante do Tutorial
        if self._game_state and self._game_state.tutorial_passo > 0:
            passo = self._game_state.tutorial_passo
            texto_tutorial = ""
            if passo == 1:
                texto_tutorial = "Mestre, o salao esta vazio. Clique na Taverna para recrutar seu primeiro heroi!"
            elif passo == 3:
                texto_tutorial = "Excelente! Agora va em Equipes e Roster para formar sua primeira equipe."
            elif passo == 5:
                texto_tutorial = "Sua equipe esta pronta! Clique em Partir p/ Missao para desbravar as estradas."
                
            if texto_tutorial:
                fonte_tut = self.obter_fonte(24, "vt323")
                # Caixa de pergaminho amarela na parte inferior do painel direito
                rect_tut = self.obter_rect(280, 470, 930, 80)
                self._desenhar_moldura(surface, rect_tut, espessura=2)
                pygame.draw.rect(surface, (235, 215, 185), rect_tut.inflate(-4, -4)) # Papiro amarelo
                
                surf_tut = fonte_tut.render(texto_tutorial, True, (40, 25, 10))
                tx = rect_tut.x + (rect_tut.width - surf_tut.get_width()) // 2
                ty = rect_tut.y + (rect_tut.height - surf_tut.get_height()) // 2
                surface.blit(surf_tut, (tx, ty))

        # 2. Desenha o menu esquerdo (Painel menor e mais refinado de largura 210)
        menu_bg_rect = self.obter_rect(20, 90, 210, 580)
        self._desenhar_moldura(surface, menu_bg_rect, espessura=2)
        pygame.draw.rect(surface, cores["fundo_painel"], menu_bg_rect.inflate(-4, -4))

        for btn in self.__botoes:
            btn.desenhar(surface)

        # 3. Painel de Visão Geral (Direita) - expandido para 1280x720
        painel_rect = self.obter_rect(250, 90, 1000, 580)
        self._desenhar_moldura(surface, painel_rect, espessura=2)
        pygame.draw.rect(surface, cores["fundo_painel"], painel_rect.inflate(-4, -4))

        # Título do Painel Direito
        self._renderizar_texto_com_sombra(
            surface, "MESA DE GESTAO DA GUILDA",
            fonte_tit, cores["texto_ouro"],
            (self.obter_x(280), self.obter_y(115))
        )

        # ── Exibição das Equipes Ativas ──────────────────────────────────
        self._renderizar_texto_com_sombra(
            surface, "Equipes Ativas:",
            fonte_corpo, cores["texto_azul"],
            (self.obter_x(280), self.obter_y(160))
        )

        equipes = self._game_state.guilda.equipes_ativas
        if not equipes:
            self._renderizar_texto_com_sombra(
                surface, "  Nenhuma equipe ativa formada no momento.",
                fonte_corpo, cores["texto_acinzentado"],
                (self.obter_x(280), self.obter_y(195))
            )
        else:
            for idx, eq in enumerate(equipes):
                y_eq = 195 + idx * 60
                y_eq_real = self.obter_y(y_eq)
                
                # Linha de resumo da equipe
                total_membros = len(eq.membros)
                texto_eq = f"- {eq.nome:<20} | Membros: {total_membros}/{eq.limite_membros}"
                self._renderizar_texto_com_sombra(
                    surface, texto_eq,
                    fonte_corpo, cores["texto_creme"],
                    (self.obter_x(280), y_eq_real)
                )
                # Membros em fonte menor abaixo
                nomes_membros = ", ".join([m.nome.split()[0] for m in eq.membros]) if eq.membros else "Vazia"
                self._renderizar_texto_com_sombra(
                    surface, f"  ({nomes_membros})",
                    fonte_peq, cores["texto_acinzentado"],
                    (self.obter_x(295), y_eq_real + self.obter_y(24))
                )

        # ── Exibição da Missão Ativa ────────────────────────────────────
        pygame.draw.line(surface, cores["hud_separador"], 
                         (self.obter_x(280), self.obter_y(440)), 
                         (self.obter_x(1210), self.obter_y(440)), 1)

        self._renderizar_texto_com_sombra(
            surface, "Mesa de Gestao de Expedicoes:",
            fonte_corpo, cores["texto_azul"],
            (self.obter_x(280), self.obter_y(460))
        )

        campanha = self._game_state.campanha
        if not campanha:
            self._renderizar_texto_com_sombra(
                surface, "Nao ha expedicoes disponiveis hoje.",
                fonte_corpo, cores["texto_vermelho"],
                (self.obter_x(280), self.obter_y(495))
            )
        else:
            self._renderizar_texto_com_sombra(
                surface, f"Existem {len(campanha)} expedicoes ativas aguardando ordens.",
                fonte_corpo, cores["texto_ouro"],
                (self.obter_x(280), self.obter_y(495))
            )
            self._renderizar_texto_com_sombra(
                surface, "Parta para a missao para selecionar a equipe e a expedicao ideal.",
                fonte_peq, cores["texto_creme"],
                (self.obter_x(280), self.obter_y(535))
            )

        # ── Desenha a barra de status de mensagem temporária ────────────
        if self.__status_mensagem:
            cor_msg = cores["texto_verde"] if self.__status_cor_tipo == "verde" else (cores["texto_vermelho"] if self.__status_cor_tipo == "erro" else cores["texto_ouro"])
            # Exibe na parte inferior esquerda dentro do menu de forma limpa
            self._renderizar_texto_com_sombra(
                surface, self.__status_mensagem,
                fonte_peq, cor_msg,
                (self.obter_x(30), self.obter_y(680))
            )

        # ── Desenha a animação do Fade (Passagem de Noite) ──────────────
        if self.__fade_ativo:
            w = self._gerenciador.largura_real
            h = self._gerenciador.altura_real

            # Cria superfície do fade
            fade_surface = pygame.Surface((w, h))
            fade_surface.fill((10, 8, 6))  # Marrom bem escuro medieval
            fade_surface.set_alpha(int(self.__fade_alpha))
            surface.blit(fade_surface, (0, 0))

            # Desenha mensagens durante o midnight (noite total)
            if self.__fade_estado == "noite":
                fonte_tit_f   = self.obter_fonte(20, "pressstart")
                fonte_corpo_f = self.obter_fonte(28, "vt323")

                # Mensagem central dinâmica baseada no motivo do avanço
                if self.__fade_motivo == "expedicao":
                    self._renderizar_texto_com_sombra(
                        surface, "RETORNANDO DA EXPEDICAO...",
                        fonte_tit_f, cores["texto_ouro"],
                        (self.obter_x(400), self.obter_y(280))
                    )
                    self._renderizar_texto_com_sombra(
                        surface, "Guerreiros descansando e recuperando forças!",
                        fonte_corpo_f, cores["texto_creme"],
                        (self.obter_x(380), self.obter_y(350))
                    )
                    self._renderizar_texto_com_sombra(
                        surface, "Todos os herois curaram +20% HP maximo!",
                        fonte_corpo_f, cores["texto_verde"],
                        (self.obter_x(400), self.obter_y(390))
                    )
                else:
                    self._renderizar_texto_com_sombra(
                        surface, "PASSANDO A NOITE...",
                        fonte_tit_f, cores["texto_ouro"],
                        (self.obter_x(460), self.obter_y(280))
                    )
                    self._renderizar_texto_com_sombra(
                        surface, "Manutencao da guilda cobrada (-10 ouro)",
                        fonte_corpo_f, cores["texto_creme"],
                        (self.obter_x(420), self.obter_y(350))
                    )
                    self._renderizar_texto_com_sombra(
                        surface, "Novos recrutas chegando na Taverna!",
                        fonte_corpo_f, cores["texto_azul"],
                        (self.obter_x(430), self.obter_y(390))
                    )

        # ── Desenha o Modal de Confirmação do Fim de Dia ─────────────────
        if self.__modal_ativo:
            w = self._gerenciador.largura_real
            h = self._gerenciador.altura_real

            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            m_rect = self.obter_rect(390, 210, 500, 300)
            self._desenhar_moldura(surface, m_rect, espessura=3)
            pygame.draw.rect(surface, cores["fundo_painel"], m_rect.inflate(-6, -6))

            self._renderizar_texto_com_sombra(
                surface, "ENCERRAR O DIA",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(430), self.obter_y(240))
            )

            self._renderizar_texto_com_sombra(
                surface, "Deseja encerrar o dia de gestao?",
                fonte_peq, cores["texto_creme"],
                (self.obter_x(430), self.obter_y(300))
            )

            self._renderizar_texto_com_sombra(
                surface, "A taxa de manutencao (-10 ouro) sera cobrada.",
                fonte_peq, cores["texto_acinzentado"],
                (self.obter_x(430), self.obter_y(335))
            )

            self.__btn_confirmar_modal.desenhar(surface)
            self.__btn_cancelar_modal.desenhar(surface)

    # ------------------------------------------------------------------
    # Auxiliar de formatação de texto
    # ------------------------------------------------------------------
    def __quebrar_texto(self, texto: str, max_chars: int) -> list:
        palavras = texto.split()
        linhas = []
        linha_atual = []
        tamanho_atual = 0

        for palavra in palavras:
            if tamanho_atual + len(palavra) + len(linha_atual) > max_chars:
                linhas.append(" ".join(linha_atual))
                linha_atual = [palavra]
                tamanho_atual = len(palavra)
            else:
                linha_atual.append(palavra)
                tamanho_atual += len(palavra)

        if linha_atual:
            linhas.append(" ".join(linha_atual))

        return list(linhas)
