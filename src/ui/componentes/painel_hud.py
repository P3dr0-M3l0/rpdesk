"""
painel_hud.py
-------------
HUD persistente exibido no topo de todas as telas do jogo.

Exibe:
  - Nome da Guilda (esquerda)
  - Indicadores: Ouro | Reputação | Dia Atual (direita)
  - Separador decorativo dourado

POO aplicado:
  - Encapsulamento : lê dados do GameState; não os modifica.
  - Composição     : cada TelaBase pode instanciar e usar um PainelHud.
"""

import pygame
from ui.asset_manager import AssetManager


class PainelHud:
    """
    Barra de status global renderizada no topo de qualquer tela.

    Altura padrão: 52 pixels.
    """

    ALTURA = 64

    def __init__(self, largura_janela: int):
        """
        Args:
            largura_janela : largura total da superfície de destino.
        """
        self.__largura = largura_janela
        self._assets   = AssetManager()

    # ------------------------------------------------------------------
    # Renderização
    # ------------------------------------------------------------------
    def desenhar(self, surface: pygame.Surface, game_state) -> None:
        """
        Renderiza o HUD no topo da surface.

        Args:
            surface    : superfície de destino (janela principal).
            game_state : instância de GameState com dados ao vivo.
        """
        cores = self._assets.CORES

        hud_rect = pygame.Rect(0, 0, self.__largura, self.ALTURA)

        # ── Fundo do HUD ────────────────────────────────────────────────
        pygame.draw.rect(surface, cores["hud_fundo"], hud_rect)

        # ── Separador dourado na base ────────────────────────────────────
        sep_y = self.ALTURA - 3
        pygame.draw.line(surface, cores["borda_escura"],
                         (0, sep_y - 1), (self.__largura, sep_y - 1), 1)
        pygame.draw.line(surface, cores["borda_ouro"],
                         (0, sep_y), (self.__largura, sep_y), 2)

        # ── Leitura de dados do GameState ────────────────────────────────
        nome_guilda = game_state.guilda.nome
        ouro        = game_state.guilda.ouro
        reputacao   = game_state.guilda.reputacao
        dia         = game_state.dia_atual

        # ── Fontes (maiores para alta resolução) ───────────────────────
        fonte_titulo = self._assets.fonte(14, "pressstart")
        fonte_corpo  = self._assets.fonte(26, "vt323")

        margem_v = (self.ALTURA - fonte_titulo.get_height()) // 2

        # ── Nome da Guilda (esquerda) ────────────────────────────────────
        self.__blit_sombra(surface, fonte_titulo,
                           nome_guilda.upper(),
                           cores["texto_ouro"],
                           (14, margem_v))

        # ── Indicadores (direita) ────────────────────────────────────────
        indicadores = [
            (f"Ouro: {ouro}",       cores["texto_ouro"]),
            (f"Rep: {reputacao}",   cores["texto_verde"]),
            (f"Dia {dia}",          cores["texto_azul"]),
        ]

        x_direita = self.__largura - 14
        for rotulo, cor in reversed(indicadores):
            surf = fonte_corpo.render(rotulo, True, cor)
            sombra = fonte_corpo.render(rotulo, True, (20, 12, 5))
            y_pos = (self.ALTURA - surf.get_height()) // 2
            x_pos = x_direita - surf.get_width()

            surface.blit(sombra, (x_pos + 1, y_pos + 1))
            surface.blit(surf, (x_pos, y_pos))

            x_direita -= surf.get_width() + 24

            # Divisor vertical entre indicadores
            if rotulo != indicadores[0][0]:
                div_x = x_direita + 12
                pygame.draw.line(surface, cores["hud_separador"],
                                 (div_x, 10), (div_x, self.ALTURA - 10), 1)

    # ------------------------------------------------------------------
    # Auxiliar privado
    # ------------------------------------------------------------------
    def __blit_sombra(self, surface, fonte, texto, cor, pos):
        sombra = fonte.render(texto, True, (20, 12, 5))
        principal = fonte.render(texto, True, cor)
        surface.blit(sombra, (pos[0] + 1, pos[1] + 1))
        surface.blit(principal, pos)
