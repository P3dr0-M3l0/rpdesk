"""
botao.py
--------
Componente de botão pixel art medieval, inteiramente desenhado por código.

POO aplicado:
  - Encapsulamento : estado interno (hover, clicado, callback) totalmente privado.
  - Composição     : as telas possuem botões (Botao); não herdam deles.
"""

import pygame
from ui.asset_manager import AssetManager


class Botao:
    """
    Botão clicável com visual pixel art medieval.

    Renderiza:
      - Fundo com gradiente simulado (camadas de retângulos)
      - Borda dupla: sombra escura externa + dourado interno
      - Highlight superior (sensação de metal polido)
      - Texto com sombra no estilo pixel art
      - Estados visuais distintos: normal, hover, clicado, desabilitado
    """

    def __init__(self, rect: pygame.Rect, texto: str,
                 callback=None, tamanho_fonte: int = 16,
                 estilo_fonte: str = "vt323"):
        """
        Args:
            rect         : posição e tamanho LÓGICOS do botão (em base 1280x720).
            texto        : rótulo exibido no centro.
            callback     : função chamada ao clicar.
            tamanho_fonte: tamanho LÓGICO da fonte.
            estilo_fonte : 'pressstart' ou 'vt323'.
        """
        self.__logical_rect  = pygame.Rect(rect)
        self.__texto         = texto
        self.__callback      = callback
        self.__tamanho_fonte = tamanho_fonte
        self.__estilo_fonte  = estilo_fonte

        self.__hover     = False
        self.__clicado   = False
        self.__ativo     = True

        self._assets = AssetManager()
        self.__gerenciador = None  # Vinculado na primeira renderização/evento

    # ------------------------------------------------------------------
    # Propriedades e Cálculo do Retângulo Físico Real
    # ------------------------------------------------------------------
    def vincular_gerenciador(self, gerenciador):
        self.__gerenciador = gerenciador

    def obter_rect_real(self, gerenciador=None) -> pygame.Rect:
        """Calcula o rect na resolução física atual baseando-se no gerenciador."""
        g = gerenciador or self.__gerenciador
        if not g:
            return self.__logical_rect

        # Mapeia coordenadas lógicas 1280x720 para o tamanho real da janela
        w_real, h_real = g.largura_real, g.altura_real
        return pygame.Rect(
            int((self.__logical_rect.x / 1280.0) * w_real),
            int((self.__logical_rect.y / 720.0) * h_real),
            int((self.__logical_rect.width / 1280.0) * w_real),
            int((self.__logical_rect.height / 720.0) * h_real)
        )

    @property
    def rect(self) -> pygame.Rect:
        return self.__logical_rect

    @property
    def ativo(self) -> bool:
        return self.__ativo

    @ativo.setter
    def ativo(self, valor: bool):
        self.__ativo = valor

    @property
    def texto(self) -> str:
        return self.__texto

    @texto.setter
    def texto(self, valor: str):
        self.__texto = valor

    # ------------------------------------------------------------------
    # Atualização de estado
    # ------------------------------------------------------------------
    def lidar_evento(self, evento: pygame.event.Event) -> bool:
        """
        Processa um único evento pygame baseado no rect físico escalado.
        """
        if not self.__ativo or not self.__gerenciador:
            return False

        r_real = self.obter_rect_real()

        if evento.type == pygame.MOUSEMOTION:
            self.__hover = r_real.collidepoint(evento.pos)

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if r_real.collidepoint(evento.pos):
                self.__clicado = True
                return False

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            if self.__clicado and r_real.collidepoint(evento.pos):
                self.__clicado = False
                if self.__callback:
                    self.__callback()
                return True
            self.__clicado = False

        return False

    # ------------------------------------------------------------------
    # Renderização Direta de Alta Definição
    # ------------------------------------------------------------------
    def desenhar(self, surface: pygame.Surface) -> None:
        """Renderiza o botão com nitidez máxima na janela real."""
        cores = self._assets.CORES

        # ── Determina esquema de cor pelo estado ────────────────────────
        if not self.__ativo:
            cor_fundo  = (50, 38, 20)
            cor_borda  = cores["borda_bronze"]
            cor_texto  = cores["texto_acinzentado"]
        elif self.__clicado:
            cor_fundo  = cores["botao_clicado"]
            cor_borda  = cores["borda_bronze"]
            cor_texto  = cores["texto_creme"]
        elif self.__hover:
            cor_fundo  = cores["botao_hover"]
            cor_borda  = cores["borda_ouro_claro"]
            cor_texto  = cores["texto_ouro"]
        else:
            cor_fundo  = cores["botao_fundo"]
            cor_borda  = cores["borda_ouro"]
            cor_texto  = cores["texto_creme"]

        # Calcula o retângulo real para desenhar
        r = self.obter_rect_real()

        # ── Sombra projetada (deslocada 2px para baixo) ─────────────────
        sombra = r.move(2, 2)
        pygame.draw.rect(surface, (15, 10, 5), sombra, border_radius=5)

        # ── Fundo principal ─────────────────────────────────────────────
        pygame.draw.rect(surface, cor_fundo, r, border_radius=5)

        # ── Chanfro 3D interno (Bevel) ──────────────────────────────────
        if self.__ativo:
            # Highlight (topo e esquerda)
            cor_high = cores["borda_ouro_claro"] if self.__hover else (240, 205, 130)
            if self.__clicado:
                # Inverte no clique (sensação de afundar)
                pygame.draw.line(surface, cores["borda_escura"], (r.x + 2, r.bottom - 3), (r.x + 2, r.y + 2), 2)
                pygame.draw.line(surface, cores["borda_escura"], (r.x + 2, r.y + 2), (r.right - 3, r.y + 2), 2)
                pygame.draw.line(surface, cores["borda_bronze"], (r.right - 3, r.y + 2), (r.right - 3, r.bottom - 3), 2)
                pygame.draw.line(surface, cores["borda_bronze"], (r.x + 2, r.bottom - 3), (r.right - 3, r.bottom - 3), 2)
            else:
                pygame.draw.line(surface, cor_high, (r.x + 2, r.bottom - 3), (r.x + 2, r.y + 2), 2)
                pygame.draw.line(surface, cor_high, (r.x + 2, r.y + 2), (r.right - 3, r.y + 2), 2)
                pygame.draw.line(surface, cores["borda_escura"], (r.right - 3, r.y + 2), (r.right - 3, r.bottom - 3), 2)
                pygame.draw.line(surface, cores["borda_escura"], (r.x + 2, r.bottom - 3), (r.right - 3, r.bottom - 3), 2)

        # ── Borda dupla (escura externa + dourada interna) ──────────────
        borda_ext = r.inflate(4, 4)
        pygame.draw.rect(surface, cores["botao_borda_escura"],
                         borda_ext, 2, border_radius=6)
        pygame.draw.rect(surface, cor_borda, r, 2, border_radius=5)

        # ── Texto centralizado com fonte escalada ───────────────────────
        # Escala o tamanho da fonte proporcionalmente à altura física atual
        tamanho_fonte_real = int(self.__tamanho_fonte * (self.__gerenciador.altura_real / 720.0))
        fonte = self._assets.fonte(max(6, tamanho_fonte_real), self.__estilo_fonte)
        
        surf_txt = fonte.render(self.__texto, True, cor_texto)
        surf_sombra = fonte.render(self.__texto, True, (20, 12, 5))
        
        centro = r.center
        txt_rect = surf_txt.get_rect(center=centro)
        surface.blit(surf_sombra, txt_rect.move(1, 1))
        surface.blit(surf_txt, txt_rect)

