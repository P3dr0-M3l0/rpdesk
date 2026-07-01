"""
tela_gameover.py
----------------
Tela de Game Over (Fase 4.2).

Exibida solenemente quando a guilda falir (0 heróis e < 50 de ouro).
Permite voltar ao menu inicial para começar uma nova jornada.
"""

import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao


class TelaGameOver(TelaBase):
    """Tela de Game Over quando o jogador falha em manter a guilda viva."""

    def __init__(self, gerenciador, game_state, controller):
        super().__init__(gerenciador, game_state)
        self.__controller = controller

        # Botão para recomeçar (voltar ao menu)
        cx = gerenciador.largura // 2
        self.__btn_menu = Botao(
            pygame.Rect(cx - 150, 480, 300, 52),
            "Menu Principal",
            callback=self.__voltar_ao_menu,
            tamanho_fonte=22
        )
        self.__btn_menu.vincular_gerenciador(gerenciador)

    def ao_entrar(self):
        # Garante que o cursor está ativado
        pygame.mouse.set_visible(True)

    def __voltar_ao_menu(self):
        if self.__controller and hasattr(self.__controller, "inicializar"):
            self.__controller.inicializar()

    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            self.__btn_menu.lidar_evento(ev)

    def atualizar(self, dt: float) -> None:
        pass

    def desenhar(self, surface: pygame.Surface) -> None:
        cores = self._assets.CORES
        surface.fill((10, 5, 5))  # Fundo escuro avermelhado solene

        # Fontes
        fonte_tit   = self.obter_fonte(24, "pressstart")
        fonte_corpo = self.obter_fonte(26, "vt323")
        fonte_peq   = self.obter_fonte(20, "vt323")

        # Título "GAME OVER" pulsante com o tempo
        tempo = pygame.time.get_ticks() / 1000.0
        pulsar = int(180 + 75 * abs(pygame.math.sin(tempo * 3)))
        cor_vermelho_pulsante = (pulsar, 20, 20)

        self._renderizar_texto_com_sombra(
            surface, "GAME OVER",
            fonte_tit, cor_vermelho_pulsante,
            (self.obter_x(460), self.obter_y(150))
        )

        # Moldura solene de fracasso
        box_rect = self.obter_rect(320, 240, 640, 200)
        self._desenhar_moldura(surface, box_rect, espessura=2)
        pygame.draw.rect(surface, (20, 10, 10), box_rect.inflate(-4, -4))

        # Texto explicativo
        self._renderizar_texto_com_sombra(
            surface, "A SUA GUILDA FALIU!",
            fonte_corpo, cores["texto_ouro"],
            (self.obter_x(360), self.obter_y(265))
        )

        self._renderizar_texto_com_sombra(
            surface, "Voce ficou sem herois vivos e com menos de 50 moedas",
            fonte_peq, cores["texto_creme"],
            (self.obter_x(360), self.obter_y(315))
        )
        self._renderizar_texto_com_sombra(
            surface, "de ouro para contratar novos aventureiros na taverna.",
            fonte_peq, cores["texto_creme"],
            (self.obter_x(360), self.obter_y(340))
        )

        self._renderizar_texto_com_sombra(
            surface, "O seu legado como gerente de guilda termina aqui...",
            fonte_peq, cores["texto_acinzentado"],
            (self.obter_x(360), self.obter_y(385))
        )

        # Botão
        self.__btn_menu.desenhar(surface)
