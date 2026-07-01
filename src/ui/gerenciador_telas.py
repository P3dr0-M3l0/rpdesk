"""
gerenciador_telas.py
--------------------
Controla a navegação entre telas usando uma pilha (State Pattern).

POO aplicado:
  - Encapsulamento : a pilha de telas é privada; mudanças só via push/pop/troca.
  - Composição     : o gerenciador contém telas (TelaBase); não as herda.
  - Polimorfismo   : chama lidar_eventos/atualizar/desenhar sem saber a tela
                     concreta, graças ao contrato de TelaBase.

Responsividade (Renderização Vetorial Direta / Dynamic Resolution):
  Em vez de desenhar em uma tela pequena e esticar (o que gera embaçamento das fontes
  e linhas), as telas desenham diretamente na resolução real da janela.
  Todas as posições e tamanhos de fonte são calculados sob demanda baseados
  na escala proporcional da janela atual em relação à resolução de projeto (1280x720).
  Isso garante fontes e linhas 100% nítidas (sem borrões/aliasing) em qualquer resolução.
"""

import pygame
from ui.asset_manager import AssetManager


class GerenciadorTelas:
    """
    Pilha de telas do jogo com suporte a redimensionamento em alta qualidade (Dynamic resolution).
    """

    def __init__(self, largura_logica: int, altura_logica: int):
        """
        Args:
            largura_logica : largura projetada do jogo (ex: 1280).
            altura_logica  : altura projetada do jogo (ex: 720).
        """
        self.__pilha: list = []
        self.__largura_logica = largura_logica
        self.__altura_logica  = altura_logica
        self.__rodando = True

        # Resolução real da janela física do sistema
        self.__largura_real = largura_logica
        self.__altura_real  = altura_logica

    # ------------------------------------------------------------------
    # Propriedades de Resolução
    # ------------------------------------------------------------------
    @property
    def rodando(self) -> bool:
        return self.__rodando

    @property
    def largura(self) -> int:
        """Largura LÓGICA projetada (1280)."""
        return self.__largura_logica

    @property
    def altura(self) -> int:
        """Altura LÓGICA projetada (720)."""
        return self.__altura_logica

    @property
    def largura_real(self) -> int:
        """Largura física real atual da janela do sistema."""
        return self.__largura_real

    @property
    def altura_real(self) -> int:
        """Altura física real atual da janela do sistema."""
        return self.__altura_real

    @property
    def tela_ativa(self):
        """Retorna a tela no topo da pilha ou None se vazia."""
        return self.__pilha[-1] if self.__pilha else None

    # ------------------------------------------------------------------
    # Navegação
    # ------------------------------------------------------------------
    def push(self, tela) -> None:
        """
        Empilha uma nova tela sem descartar a atual.
        Útil para submenus e painéis modais.
        """
        if self.__pilha:
            self.__pilha[-1].ao_sair()
        self.__pilha.append(tela)
        tela.ao_entrar()

    def pop(self) -> None:
        """
        Remove a tela do topo, revelando a anterior.
        Não faz nada se a pilha estiver vazia ou tiver só uma tela.
        """
        if len(self.__pilha) <= 1:
            return
        self.__pilha[-1].ao_sair()
        self.__pilha.pop()
        self.__pilha[-1].ao_entrar()

    def trocar(self, tela) -> None:
        """
        Substitui a tela atual sem empilhar (transição sem retorno direto).
        Ideal para: Menu Principal → Hub da Guilda.
        """
        if self.__pilha:
            self.__pilha[-1].ao_sair()
            self.__pilha.pop()
        self.__pilha.append(tela)
        tela.ao_entrar()

    def encerrar(self) -> None:
        """Sinaliza que o loop principal deve terminar."""
        self.__rodando = False

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def executar(self, janela: pygame.Surface, clock: pygame.time.Clock,
                 fps_alvo: int = 60) -> None:
        """
        Inicia e mantém o loop de eventos/renderização do Pygame.
        Desenha as telas diretamente na janela física do sistema.

        Args:
            janela   : superfície da janela real do sistema (tamanho variável).
            clock    : pygame.time.Clock para controle de FPS.
            fps_alvo : quadros por segundo desejados.
        """
        assets   = AssetManager()
        cor_fundo = assets.CORES["fundo_principal"]

        # Define as dimensões reais iniciais baseado na janela recebida
        self.__largura_real, self.__altura_real = janela.get_size()

        while self.__rodando and self.__pilha:
            dt = clock.tick(fps_alvo) / 1000.0  # segundos

            # ── Coleta e filtragem de eventos ────────────────────────────
            eventos_raw = pygame.event.get()
            for evento in eventos_raw:
                if evento.type == pygame.QUIT:
                    self.__rodando = False
                elif evento.type == pygame.VIDEORESIZE:
                    # Atualiza o tamanho físico real da janela
                    self.__largura_real = evento.w
                    self.__altura_real  = evento.h
                    janela = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)

            if not self.__rodando:
                break

            # ── Delegação para a tela ativa desenhar diretamente ─────────
            tela = self.tela_ativa
            if tela:
                # Com renderização direta, as coordenadas de eventos vêm corretas do SO
                tela.lidar_eventos(eventos_raw)
                tela.atualizar(dt)

                # Limpa a janela diretamente
                janela.fill(cor_fundo)
                # Renderiza diretamente na superfície de alta definição da janela do SO
                tela.desenhar(janela)

            pygame.display.flip()
