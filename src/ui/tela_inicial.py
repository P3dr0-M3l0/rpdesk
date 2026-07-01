"""
tela_inicial.py
---------------
Tela de Menu Inicial do RpDesk (Pygame).

Apresenta:
  - Título artístico do jogo em pixel art
  - Opções: Carregar Save, Novo Jogo, Sair
  - Aviso de save existente (ou mensagem de primeira vez)

POO aplicado:
  - Herança    : estende TelaBase, recebe polimorfismo do GerenciadorTelas.
  - Composição : usa Botao e PainelHud (e cria TextoAnimado interno).
  - Abstração  : o GerenciadorTelas não sabe o que é TelaInicial; só chama
                 lidar_eventos / atualizar / desenhar.
"""

import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao


class TelaInicial(TelaBase):
    """
    Tela de boas-vindas com opções de carga ou novo jogo.

    Args:
        gerenciador : GerenciadorTelas
        tem_save    : bool – indica se existe um arquivo de save no disco.
        cb_carregar : callable – chamado ao clicar em "Carregar Jogo"
        cb_novo     : callable – chamado ao clicar em "Novo Jogo"
    """

    def __init__(self, gerenciador, tem_save: bool,
                 cb_carregar, cb_novo):
        # TelaInicial não precisa de GameState (ainda não existe)
        super().__init__(gerenciador, game_state=None)

        self.__tem_save    = tem_save
        self.__cb_carregar = cb_carregar
        self.__cb_novo     = cb_novo

        # Animação do título (alpha pulsante)
        self.__titulo_alpha  = 255
        self.__alpha_dir     = -1       # -1 = escurecendo, +1 = clareando
        self.__alpha_timer   = 0.0

        # Animação de entrada (fade-in da tela)
        self.__fade_alpha    = 255      # começa opaco e vai clareando
        self.__fade_surface  = pygame.Surface(
            (gerenciador.largura, gerenciador.altura)
        )
        self.__fade_surface.fill((0, 0, 0))

        # Botões centralizados - reposicionados para 1280x720
        cx = gerenciador.largura // 2
        largura_b = 320
        altura_b  = 52
        espaco_b  = 20
        y_base    = 340  # Posicionado perfeitamente na zona central/baixa

        self.__botao_carregar = Botao(
            pygame.Rect(cx - largura_b // 2, y_base, largura_b, altura_b),
            "Carregar Jogo",
            callback=self.__on_carregar,
            tamanho_fonte=22,
        )
        self.__botao_novo = Botao(
            pygame.Rect(cx - largura_b // 2, y_base + altura_b + espaco_b,
                        largura_b, altura_b),
            "Novo Jogo" if not tem_save else "Novo Jogo (Sobrescreve)",
            callback=self.__on_novo,
            tamanho_fonte=22,
        )
        self.__botao_sair = Botao(
            pygame.Rect(cx - largura_b // 2,
                        y_base + 2 * (altura_b + espaco_b),
                        largura_b, altura_b),
            "Sair",
            callback=self.__on_sair,
            tamanho_fonte=22,
        )

        # Vincula o gerenciador aos botões para que eles calculem a escala física
        self.__botao_carregar.vincular_gerenciador(gerenciador)
        self.__botao_novo.vincular_gerenciador(gerenciador)
        self.__botao_sair.vincular_gerenciador(gerenciador)

        # Desabilita "Carregar" se não há save
        self.__botao_carregar.ativo = tem_save

    # ------------------------------------------------------------------
    # Callbacks internos
    # ------------------------------------------------------------------
    def __on_carregar(self):
        if self.__cb_carregar:
            self.__cb_carregar()

    def __on_novo(self):
        if self.__cb_novo:
            self.__cb_novo()

    def __on_sair(self):
        self._gerenciador.encerrar()

    # ------------------------------------------------------------------
    # Loop
    # ------------------------------------------------------------------
    def ao_entrar(self):
        self.__fade_alpha = 255  # Reinicia o fade ao entrar

    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            self.__botao_carregar.lidar_evento(ev)
            self.__botao_novo.lidar_evento(ev)
            self.__botao_sair.lidar_evento(ev)

    def atualizar(self, dt: float) -> None:
        # Fade-in de entrada
        if self.__fade_alpha > 0:
            self.__fade_alpha = max(0, self.__fade_alpha - int(300 * dt))

        # Pulsação suave do subtítulo (ciclo de 2 segundos)
        self.__alpha_timer += dt
        if self.__alpha_timer >= 2.0:
            self.__alpha_timer = 0.0
        # Seno para suavidade: de 180 a 255
        import math
        t = self.__alpha_timer / 2.0
        self.__titulo_alpha = int(180 + 75 * math.sin(t * math.pi))

    def desenhar(self, surface: pygame.Surface) -> None:
        cores  = self._assets.CORES
        w      = self._gerenciador.largura_real
        h      = self._gerenciador.altura_real

        # ── 1. Fundo escuro vinheta ──────────────────────────────────────
        surface.fill(cores["fundo_principal"])

        # Gradiente radial simulado via círculos concêntricos semitransparentes
        centro_x, centro_y = w // 2, h // 2
        for raio_logico, alpha in [(550, 8), (420, 10), (300, 12), (200, 15)]:
            raio = self.obter_y(raio_logico)
            circulo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(circulo, (180, 140, 60, alpha), (0, 0, raio * 2, raio * 2))
            surface.blit(circulo, (centro_x - raio, centro_y - raio))

        # ── 2. Separadores horizontais decorativos adaptados ──────────────
        pygame.draw.line(surface, cores["borda_escura"],  (self.obter_x(60), self.obter_y(142)),  (w - self.obter_x(60), self.obter_y(142)), 1)
        pygame.draw.line(surface, cores["borda_ouro"],    (self.obter_x(60), self.obter_y(144)),  (w - self.obter_x(60), self.obter_y(144)), 2)
        pygame.draw.line(surface, cores["borda_escura"],  (self.obter_x(60), self.obter_y(147)),  (w - self.obter_x(60), self.obter_y(147)), 1)

        pygame.draw.line(surface, cores["borda_escura"],  (self.obter_x(60), h - self.obter_y(82)), (w - self.obter_x(60), h - self.obter_y(82)), 1)
        pygame.draw.line(surface, cores["borda_ouro"],    (self.obter_x(60), h - self.obter_y(80)), (w - self.obter_x(60), h - self.obter_y(80)), 2)
        pygame.draw.line(surface, cores["borda_escura"],  (self.obter_x(60), h - self.obter_y(77)), (w - self.obter_x(60), h - self.obter_y(77)), 1)

        # ── 3. Título principal redimensionado para alta resolução ──────────
        fonte_titulo = self.obter_fonte(36, "pressstart")
        fonte_sub    = self.obter_fonte(16, "pressstart")
        fonte_corpo  = self.obter_fonte(28, "vt323")
        fonte_hint   = self.obter_fonte(22, "vt323")

        # Título "RPDESK"
        txt_titulo = "RPDESK"
        surf_titulo = fonte_titulo.render(txt_titulo, True, cores["texto_ouro"])
        surf_sombra = fonte_titulo.render(txt_titulo, True, (40, 28, 10))
        tx = (w - surf_titulo.get_width()) // 2
        ty = self.obter_y(35)
        surface.blit(surf_sombra, (tx + 4, ty + 4))
        surface.blit(surf_titulo, (tx, ty))

        # Subtítulo pulsante
        txt_sub = "Gerenciador de Guilda"
        surf_sub = fonte_sub.render(txt_sub, True, cores["texto_creme"])
        surf_sub.set_alpha(self.__titulo_alpha)
        sx = (w - surf_sub.get_width()) // 2
        sy = self.obter_y(95)
        surface.blit(surf_sub, (sx, sy))

        # ── 4. Mensagem de save ──────────────────────────────────────────
        if self.__tem_save:
            msg = ">> Save encontrado! Deseja continuar sua aventura? <<"
            cor_msg = cores["texto_verde"]
        else:
            msg = ">> Nenhum save encontrado. Inicie uma nova guilda! <<"
            cor_msg = cores["texto_acinzentado"]

        surf_msg = fonte_corpo.render(msg, True, cor_msg)
        mx = (w - surf_msg.get_width()) // 2
        my = self.obter_y(280)
        surface.blit(surf_msg, (mx, my))

        # ── 5. Botões ────────────────────────────────────────────────────
        self.__botao_carregar.desenhar(surface)
        self.__botao_novo.desenhar(surface)
        self.__botao_sair.desenhar(surface)

        # ── 6. Rodapé ────────────────────────────────────────────────────
        txt_footer = "Pedro Oliveira Melo"
        surf_footer = fonte_hint.render(txt_footer, True, cores["texto_acinzentado"])
        fx = (w - surf_footer.get_width()) // 2
        fy = h - self.obter_y(55)
        surface.blit(surf_footer, (fx, fy))

        # ── 7. Fade-in de entrada ────────────────────────────────────────
        if self.__fade_alpha > 0:
            # Recria fade surface para o tamanho real atual
            fade_surf = pygame.Surface((w, h))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.__fade_alpha)
            surface.blit(fade_surf, (0, 0))
