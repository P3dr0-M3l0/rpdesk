"""
tela_sistema.py
---------------
Tela de Opções de Sistema e Salvamento (Fase 4.2).

Oferece botões para:
  - Voltar ao Menu Principal (com confirmação)
  - Voltar à guilda (fechar menu)
  - Salvar jogo
  - Salvar e Sair (com confirmação)
  - Sair sem salvar (com confirmação)
"""

import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao
from ui.componentes.painel_hud import PainelHud


class TelaSistema(TelaBase):
    """Menu do sistema / opções de salvamento."""

    def __init__(self, gerenciador, game_state, controller):
        super().__init__(gerenciador, game_state)
        self.__controller = controller
        self.__hud = PainelHud(gerenciador.largura)

        # Botões centralizados
        cx = gerenciador.largura // 2
        largura_b = 360
        altura_b  = 48
        espaco_b  = 12
        y_base    = 175

        # 1. Voltar ao Menu Principal
        self.__btn_menu = Botao(
            pygame.Rect(cx - largura_b // 2, y_base, largura_b, altura_b),
            "Voltar ao Menu Principal",
            callback=self.__confirmar_menu_principal,
            tamanho_fonte=20
        )
        # 2. Voltar à Guilda
        self.__btn_voltar = Botao(
            pygame.Rect(cx - largura_b // 2, y_base + (altura_b + espaco_b), largura_b, altura_b),
            "Voltar à Guilda",
            callback=self.__voltar,
            tamanho_fonte=20
        )
        # 3. Salvar Guilda
        self.__btn_salvar = Botao(
            pygame.Rect(cx - largura_b // 2, y_base + 2 * (altura_b + espaco_b), largura_b, altura_b),
            "Salvar Jogo",
            callback=self.__salvar,
            tamanho_fonte=20
        )
        # 4. Salvar e Sair
        self.__btn_salvar_sair = Botao(
            pygame.Rect(cx - largura_b // 2, y_base + 3 * (altura_b + espaco_b), largura_b, altura_b),
            "Salvar e Sair",
            callback=self.__confirmar_salvar_sair,
            tamanho_fonte=20
        )
        # 5. Sair sem Salvar
        self.__btn_sair_sem_salvar = Botao(
            pygame.Rect(cx - largura_b // 2, y_base + 4 * (altura_b + espaco_b), largura_b, altura_b),
            "Sair sem Salvar",
            callback=self.__confirmar_sair_sem_salvar,
            tamanho_fonte=20
        )

        # Vincula gerenciador
        self.__btn_menu.vincular_gerenciador(gerenciador)
        self.__btn_voltar.vincular_gerenciador(gerenciador)
        self.__btn_salvar.vincular_gerenciador(gerenciador)
        self.__btn_salvar_sair.vincular_gerenciador(gerenciador)
        self.__btn_sair_sem_salvar.vincular_gerenciador(gerenciador)

        self.__botoes_sistema = [
            self.__btn_menu,
            self.__btn_voltar,
            self.__btn_salvar,
            self.__btn_salvar_sair,
            self.__btn_sair_sem_salvar
        ]

        # Modal de confirmação
        self.__modal_ativo = False
        self.__modal_tipo = ""  # "menu" | "salvar_sair" | "sair_sem_salvar"
        self.__btn_confirmar_modal = Botao(
            pygame.Rect(cx - 160, 420, 140, 40),
            "Confirmar",
            callback=self.__executar_acao_modal,
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

        # Mensagens
        self.__status_mensagem = ""
        self.__status_timer = 0.0

    def ao_entrar(self):
        self.__fechar_modal()
        self.__status_mensagem = ""

    def __voltar(self):
        self._gerenciador.pop()

    def __salvar(self):
        if self.__controller and hasattr(self.__controller, "salvar_jogo"):
            self.__controller.salvar_jogo()
            self.__mostrar_mensagem("Jogo salvo com sucesso!", "verde")

    def __confirmar_menu_principal(self):
        self.__modal_tipo = "menu"
        self.__modal_ativo = True

    def __confirmar_salvar_sair(self):
        self.__modal_tipo = "salvar_sair"
        self.__modal_ativo = True

    def __confirmar_sair_sem_salvar(self):
        self.__modal_tipo = "sair_sem_salvar"
        self.__modal_ativo = True

    def __fechar_modal(self):
        self.__modal_ativo = False
        self.__modal_tipo = ""

    def __executar_acao_modal(self):
        if self.__modal_tipo == "menu":
            if self.__controller and hasattr(self.__controller, "voltar_ao_menu_principal"):
                self.__controller.voltar_ao_menu_principal()
        elif self.__modal_tipo == "salvar_sair":
            if self.__controller and hasattr(self.__controller, "salvar_jogo"):
                self.__controller.salvar_jogo()
            self._gerenciador.encerrar()
        elif self.__modal_tipo == "sair_sem_salvar":
            self._gerenciador.encerrar()
        self.__fechar_modal()

    def __mostrar_mensagem(self, texto, cor_tipo="ouro"):
        self.__status_mensagem = texto
        self.__status_timer = 3.0

    # ------------------------------------------------------------------
    # Loop
    # ------------------------------------------------------------------
    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            if self.__modal_ativo:
                self.__btn_confirmar_modal.lidar_evento(ev)
                self.__btn_cancelar_modal.lidar_evento(ev)
            else:
                for btn in self.__botoes_sistema:
                    btn.lidar_evento(ev)

    def atualizar(self, dt: float) -> None:
        if self.__status_timer > 0:
            self.__status_timer -= dt
            if self.__status_timer <= 0:
                self.__status_mensagem = ""

    def desenhar(self, surface: pygame.Surface) -> None:
        cores = self._assets.CORES
        w = self._gerenciador.largura_real
        h = self._gerenciador.altura_real

        # Fontes
        fonte_tit   = self.obter_fonte(16, "pressstart")
        fonte_peq   = self.obter_fonte(20, "vt323")

        # HUD
        self.__hud.desenhar(surface, self._game_state)

        # Título
        self._renderizar_texto_com_sombra(
            surface, "OPÇÕES DE SISTEMA",
            fonte_tit, cores["texto_ouro"],
            (self.obter_x(50), self.obter_y(85))
        )

        # Painel central decorativo
        panel_rect = self.obter_rect(380, 140, 520, 480)
        self._desenhar_moldura(surface, panel_rect, espessura=2)
        pygame.draw.rect(surface, cores["fundo_painel"], panel_rect.inflate(-4, -4))

        # Desenha botões
        for btn in self.__botoes_sistema:
            btn.desenhar(surface)

        # Mensagem temporária
        if self.__status_mensagem:
            self._renderizar_texto_com_sombra(
                surface, self.__status_mensagem,
                fonte_peq, cores["texto_verde"],
                (self.obter_x(480), self.obter_y(165))
            )

        # Modal
        if self.__modal_ativo:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            m_rect = self.obter_rect(390, 210, 500, 300)
            self._desenhar_moldura(surface, m_rect, espessura=3)
            pygame.draw.rect(surface, cores["fundo_painel"], m_rect.inflate(-6, -6))

            self._renderizar_texto_com_sombra(
                surface, "CONFIRMAÇÃO",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(430), self.obter_y(240))
            )

            if self.__modal_tipo == "menu":
                msg = "Sair e voltar ao Menu Principal?"
                submsg = "Qualquer progresso não salvo será perdido!"
            elif self.__modal_tipo == "salvar_sair":
                msg = "Salvar o progresso e fechar o jogo?"
                submsg = "O jogo será salvo no slot antes de sair."
            else:
                msg = "Sair sem salvar o progresso?"
                submsg = "ATENÇÃO: Todo o progresso recente será perdido!"

            self._renderizar_texto_com_sombra(
                surface, msg,
                fonte_peq, cores["texto_creme"],
                (self.obter_x(430), self.obter_y(300))
            )

            self._renderizar_texto_com_sombra(
                surface, submsg,
                fonte_peq, cores["texto_acinzentado"],
                (self.obter_x(430), self.obter_y(340))
            )

            self.__btn_confirmar_modal.desenhar(surface)
            self.__btn_cancelar_modal.desenhar(surface)
