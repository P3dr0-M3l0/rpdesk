"""
tela_splash.py
--------------
Tela de Splash Screen de inicialização rápida (fundo estético e barra de carregamento).
Refatorado para usar fundos procedurais medievais e poeira mágica dinâmica via Pygame.
"""

import random
import math
import pygame
from ui.tela_base import TelaBase
from ui.tela_inicial import TelaInicial


class TelaSplash(TelaBase):
    """
    Exibe a Splash Screen de carregamento do RpDesk antes de revelar o menu principal.
    """

    def __init__(self, gerenciador, controller, tem_save, cb_carregar, cb_novo):
        super().__init__(gerenciador, game_state=None)
        self.__controller = controller
        self.__tem_save = tem_save
        self.__cb_carregar = cb_carregar
        self.__cb_novo = cb_novo

        self.__progresso = 0.0  # 0.0 a 1.0
        self.__tempo_carregamento = 1.8  # Segundos de carregamento
        self.__timer = 0.0

        # Partículas de poeira arcana (dourada e azul mística)
        self.__particulas = []

    def lidar_eventos(self, eventos: list) -> None:
        # Ignora interações do usuário durante o splash screen
        pass

    def atualizar(self, dt: float) -> None:
        self.__timer += dt
        self.__progresso = min(1.0, self.__timer / self.__tempo_carregamento)

        # Atualização das partículas de poeira arcana
        for p in self.__particulas[:]:
            p["y"] -= p["vy"] * dt * 50
            p["x"] += p["vx"] * dt * 50
            p["alpha"] -= dt * 75
            if p["y"] < 0 or p["alpha"] <= 0:
                self.__particulas.remove(p)

        # Geração de poeira arcana
        if len(self.__particulas) < 35 and random.random() < 0.3:
            self.__particulas.append({
                "x": random.randint(0, self._gerenciador.largura),
                "y": self._gerenciador.altura + 10,
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(0.8, 2.2),
                "raio": random.randint(3, 7),
                "alpha": random.uniform(100, 220),
                "cor": random.choice([(140, 190, 255), (255, 200, 80), (220, 160, 255)]) # Tons arcanos
            })

        # Transiciona para a Tela Inicial quando o carregamento for concluído
        if self.__progresso >= 1.0:
            tela_inicial = TelaInicial(
                gerenciador=self._gerenciador,
                tem_save=self.__tem_save,
                cb_carregar=self.__cb_carregar,
                cb_novo=self.__cb_novo
            )
            self._gerenciador.trocar(tela_inicial)

    def desenhar(self, surface: pygame.Surface) -> None:
        cores = self._assets.CORES
        w = self._gerenciador.largura_real
        h = self._gerenciador.altura_real

        # 1. Fundo escuro cinza/marrom medieval
        surface.fill((22, 18, 15))

        # Gradiente radial central místico
        centro_x, centro_y = w // 2, h // 2
        for raio_logico, alpha in [(500, 12), (380, 16), (260, 20), (150, 24)]:
            raio = self.obter_y(raio_logico)
            circulo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(circulo, (110, 80, 140, alpha), (0, 0, raio * 2, raio * 2)) # Brilho místico roxo/azul
            surface.blit(circulo, (centro_x - raio, centro_y - raio))

        # 2. Desenha Partículas Arcanas
        for p in self.__particulas:
            px = self.obter_x(p["x"])
            py = self.obter_y(p["y"])
            raio_p = max(1, self.obter_y(p["raio"]))
            
            p_surf = pygame.Surface((raio_p * 2, raio_p * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (p["cor"][0], p["cor"][1], p["cor"][2], int(p["alpha"])), (raio_p, raio_p), raio_p)
            surface.blit(p_surf, (px - raio_p, py - raio_p))

        # Moldura solene da tela inteira
        tela_moldura = self.obter_rect(10, 10, 1260, 700)
        self._desenhar_moldura(surface, tela_moldura, espessura=2)

        # Fontes
        fonte_tit = self.obter_fonte(42, "pressstart")
        fonte_sub = self.obter_fonte(20, "vt323")
        fonte_hint = self.obter_fonte(16, "pressstart")

        # 3. Logotipo RPDESK centralizado
        txt_titulo = "RPDESK"
        surf_titulo = fonte_tit.render(txt_titulo, True, cores["texto_ouro"])
        surf_sombra = fonte_tit.render(txt_titulo, True, (30, 20, 10))
        tx = (w - surf_titulo.get_width()) // 2
        ty = self.obter_y(180)
        surface.blit(surf_sombra, (tx + 5, ty + 5))
        surface.blit(surf_titulo, (tx, ty))

        # Subtítulo
        txt_sub = "Carregando grimorios e pergaminhos arcanos..."
        surf_sub = fonte_sub.render(txt_sub, True, cores["texto_creme"])
        sx = (w - surf_sub.get_width()) // 2
        sy = self.obter_y(320)
        surface.blit(surf_sub, (sx, sy))

        # 4. Desenha a Barra de Carregamento
        bar_bg = self.obter_rect(340, 400, 600, 24)
        pygame.draw.rect(surface, cores["fundo_painel"], bar_bg, border_radius=4)
        self._desenhar_moldura(surface, bar_bg, espessura=2)

        # Barra interna preenchida
        if self.__progresso > 0.05:
            preenchido_w = int(592 * self.__progresso)
            bar_fg = self.obter_rect(344, 404, preenchido_w, 16)
            pygame.draw.rect(surface, cores["borda_ouro_claro"], bar_fg, border_radius=2)

        # Hint no rodapé
        txt_hint = "Google DeepMind pair programming"
        surf_hint = fonte_hint.render(txt_hint, True, cores["texto_acinzentado"])
        hx = (w - surf_hint.get_width()) // 2
        hy = h - self.obter_y(60)
        surface.blit(surf_hint, (hx, hy))
