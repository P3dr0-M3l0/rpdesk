"""
tela_base.py
------------
Classe abstrata (ABC) que define o contrato de todas as telas do RpDesk.

POO aplicado:
  - Abstração    : define a interface mínima que toda tela deve respeitar.
  - Herança      : TelaGuilda, TelaTaverna etc. herdam TelaBase e ganham o
                   comportamento de renderização de moldura e HUD gratuitamente.
  - Polimorfismo : o GerenciadorTelas só conhece TelaBase; chama lidar_eventos,
                   atualizar e desenhar sem saber a tela concreta ativa.
"""

from abc import ABC, abstractmethod
import pygame
from ui.asset_manager import AssetManager


class TelaBase(ABC):
    """
    Contrato que toda tela do jogo deve implementar.

    Subclasses DEVEM implementar:
        lidar_eventos(eventos)
        atualizar(dt)
        desenhar(surface)

    Subclasses podem sobrescrever opcionalmente:
        ao_entrar()   – executado quando a tela entra na pilha
        ao_sair()     – executado quando a tela é desempilhada
    """

    def __init__(self, gerenciador, game_state):
        """
        Args:
            gerenciador : instância de GerenciadorTelas (referência fraca de uso).
            game_state  : instância de GameState com os dados ao vivo do jogo.
        """
        self._gerenciador = gerenciador
        self._game_state  = game_state
        self._assets      = AssetManager()

    # ------------------------------------------------------------------
    # Métodos de Escala Dinâmica (Resolução Dinâmica/Física)
    # ------------------------------------------------------------------
    def obter_x(self, x: float) -> int:
        """Mapeia x lógico (de base 1280) para a largura real da janela."""
        return int((x / 1280.0) * self._gerenciador.largura_real)

    def obter_y(self, y: float) -> int:
        """Mapeia y lógico (de base 720) para a altura real da janela."""
        return int((y / 720.0) * self._gerenciador.altura_real)

    def obter_rect(self, x: float, y: float, w: float, h: float) -> pygame.Rect:
        """Retorna um Rect escalado para o tamanho físico real atual."""
        return pygame.Rect(
            self.obter_x(x),
            self.obter_y(y),
            self.obter_x(w),
            self.obter_y(h)
        )

    def obter_fonte(self, tamanho: int, estilo: str = "pressstart") -> pygame.font.Font:
        """
        Retorna a fonte escalada dinamicamente para o tamanho físico real da tela.
        Isso garante que o Pygame renderize as fontes de forma perfeita,
        evitando aliasing e embaçamentos.
        """
        tamanho_real = int(tamanho * (self._gerenciador.altura_real / 720.0))
        return self._assets.fonte(max(6, tamanho_real), estilo)


    # ------------------------------------------------------------------
    # Interface obrigatória (Abstração / Polimorfismo)
    # ------------------------------------------------------------------
    @abstractmethod
    def lidar_eventos(self, eventos: list) -> None:
        """Processa a lista de eventos pygame.event capturados no loop."""
        ...

    @abstractmethod
    def atualizar(self, dt: float) -> None:
        """
        Atualiza a lógica interna da tela.

        Args:
            dt : delta time em segundos desde o último frame.
        """
        ...

    @abstractmethod
    def desenhar(self, surface: pygame.Surface) -> None:
        """
        Renderiza a tela inteira na superfície recebida.

        Args:
            surface : pygame.Surface onde tudo será desenhado.
        """
        ...

    # ------------------------------------------------------------------
    # Hooks opcionais de ciclo de vida
    # ------------------------------------------------------------------
    def ao_entrar(self) -> None:
        """Chamado pelo GerenciadorTelas quando a tela entra na pilha."""
        pass

    def ao_sair(self) -> None:
        """Chamado pelo GerenciadorTelas quando a tela é desempilhada."""
        pass

    # ------------------------------------------------------------------
    # Utilitários de renderização compartilhados por todas as telas
    # ------------------------------------------------------------------
    def _desenhar_moldura(self, surface: pygame.Surface, rect: pygame.Rect,
                          espessura: int = 2) -> None:
        """
        Desenha a moldura medieval dourada padronizada ao redor de um rect.

        Técnica: duas bordas concêntricas (escura externa + dourada interna)
        criam a ilusão de profundidade sem precisar de imagens.
        """
        cores = self._assets.CORES

        # Sombra externa
        sombra = rect.inflate(4, 4)
        pygame.draw.rect(surface, cores["borda_escura"], sombra, espessura + 1,
                         border_radius=4)
        # Borda dourada principal
        pygame.draw.rect(surface, cores["borda_ouro"], rect, espessura,
                         border_radius=4)
        # Highlight interno superior (sensação de metal polido)
        highlight = pygame.Rect(rect.x + 2, rect.y + 2,
                                rect.width - 4, espessura)
        pygame.draw.rect(surface, cores["borda_ouro_claro"], highlight)

    def _renderizar_texto_com_sombra(self, surface: pygame.Surface, texto: str,
                                     fonte: pygame.font.Font, cor: tuple,
                                     pos: tuple, sombra_offset: int = 1) -> pygame.Rect:
        """
        Renderiza texto com sombra escura deslocada para legibilidade pixel art.

        Args:
            surface       : onde desenhar.
            texto         : string a renderizar.
            fonte         : pygame.font.Font já carregada.
            cor           : cor RGB do texto principal.
            pos           : (x, y) do canto superior esquerdo.
            sombra_offset : deslocamento em pixels da sombra.

        Returns:
            pygame.Rect com a área ocupada pelo texto.
        """
        cor_sombra = (20, 12, 5)
        x, y = pos

        # Sombra (renderizada        # Desenha a sombra
        sombra_surface = fonte.render(texto, True, (15, 12, 10))
        surface.blit(sombra_surface, (pos[0] + sombra_offset, pos[1] + sombra_offset))

        # Desenha o texto principal
        texto_surface = fonte.render(texto, True, cor)
        surface.blit(texto_surface, pos)

        # Retorna a área de colisão para uso dinâmico se necessário
        return texto_surface.get_rect(topleft=pos)

    def formatar_nome_heroi(self, nome: str) -> str:
        """Retorna apenas o primeiro nome em caixa alta para uniformidade visual."""
        if not nome:
            return ""
        return nome.split()[0].upper()
