"""
tela_inicial.py
---------------
Tela de Menu Inicial do RpDesk (Pygame).
Refatorado para parecer um menu medieval imersivo com partículas pulsantes e moldura de pergaminho.
"""

import math
import random
import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao


class TelaInicial(TelaBase):
    """
    Tela de Menu Inicial com opções de carregar save, novo jogo e sair do reino.
    """

    def __init__(self, gerenciador, tem_save: bool, cb_carregar, cb_novo):
        super().__init__(gerenciador, game_state=None)

        self.__tem_save    = tem_save
        self.__cb_carregar = cb_carregar
        self.__cb_novo     = cb_novo

        # Animação do título (alpha pulsante)
        self.__titulo_alpha  = 255
        self.__alpha_timer   = 0.0

        # Animação de entrada (fade-in da tela)
        self.__fade_alpha    = 255

        # Partículas dinâmicas (fagulhas de lareira)
        self.__particulas = []

        # Botões centralizados dentro do pergaminho do Menu Principal
        cx = gerenciador.largura // 2
        largura_b = 320
        altura_b  = 48
        espaco_b  = 18
        y_base    = 300  # Posicionado dentro do pergaminho central

        self.__botao_carregar = Botao(
            pygame.Rect(cx - largura_b // 2, y_base, largura_b, altura_b),
            "Continuar Jornada",
            callback=self.__on_carregar,
            tamanho_fonte=20,
        )
        self.__botao_novo = Botao(
            pygame.Rect(cx - largura_b // 2, y_base + altura_b + espaco_b,
                        largura_b, altura_b),
            "Nova Campanha" if not tem_save else "Nova Campanha (Sobrescreve)",
            callback=self.__on_novo,
            tamanho_fonte=18 if tem_save else 20,
        )
        self.__botao_sair = Botao(
            pygame.Rect(cx - largura_b // 2,
                        y_base + 2 * (altura_b + espaco_b),
                        largura_b, altura_b),
            "Sair do Reino",
            callback=self.__on_sair,
            tamanho_fonte=20,
        )

        self.__botao_carregar.vincular_gerenciador(gerenciador)
        self.__botao_novo.vincular_gerenciador(gerenciador)
        self.__botao_sair.vincular_gerenciador(gerenciador)

        self.__botao_carregar.ativo = tem_save

    def __on_carregar(self):
        if self.__cb_carregar:
            self.__cb_carregar()

    def __on_novo(self):
        if self.__cb_novo:
            self.__cb_novo()

    def __on_sair(self):
        self._gerenciador.encerrar()

    def ao_entrar(self):
        self.__fade_alpha = 255
        self.__particulas.clear()

    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            self.__botao_carregar.lidar_evento(ev)
            self.__botao_novo.lidar_evento(ev)
            self.__botao_sair.lidar_evento(ev)

    def atualizar(self, dt: float) -> None:
        # Fade-in
        if self.__fade_alpha > 0:
            self.__fade_alpha = max(0, self.__fade_alpha - int(300 * dt))

        # Pulsação suave do subtítulo
        self.__alpha_timer += dt
        if self.__alpha_timer >= 2.0:
            self.__alpha_timer = 0.0
        t = self.__alpha_timer / 2.0
        self.__titulo_alpha = int(180 + 75 * math.sin(t * math.pi))

        # Atualização das partículas de fagulha
        for p in self.__particulas[:]:
            p["y"] -= p["vy"] * dt * 60
            p["x"] += p["vx"] * dt * 60
            p["alpha"] -= dt * 90
            if p["y"] < 0 or p["alpha"] <= 0:
                self.__particulas.remove(p)

        # Geração de partículas
        if len(self.__particulas) < 40 and random.random() < 0.25:
            self.__particulas.append({
                "x": random.randint(0, self._gerenciador.largura),
                "y": self._gerenciador.altura + 10,
                "vx": random.uniform(-0.6, 0.6),
                "vy": random.uniform(1.2, 3.0),
                "raio": random.randint(2, 6),
                "alpha": random.uniform(130, 245),
                "cor": random.choice([(255, 175, 45), (255, 115, 25), (240, 205, 75)])
            })

    def desenhar(self, surface: pygame.Surface) -> None:
        cores  = self._assets.CORES
        w      = self._gerenciador.largura_real
        h      = self._gerenciador.altura_real

        # ── 1. Fundo Escuro com Gradiente Radial Medieval ──────────────────────
        surface.fill((20, 15, 12))  # Tons escuros de madeira/carvão

        centro_x, centro_y = w // 2, h // 2
        for raio_logico, alpha in [(550, 10), (420, 14), (300, 18), (200, 22)]:
            raio = self.obter_y(raio_logico)
            circulo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(circulo, (140, 100, 60, alpha), (0, 0, raio * 2, raio * 2))
            surface.blit(circulo, (centro_x - raio, centro_y - raio))

        # ── 2. Renderiza Partículas (Fagulhas) ──────────────────────────
        for p in self.__particulas:
            px = self.obter_x(p["x"])
            py = self.obter_y(p["y"])
            raio_p = max(1, self.obter_y(p["raio"]))
            
            p_surf = pygame.Surface((raio_p * 2, raio_p * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (p["cor"][0], p["cor"][1], p["cor"][2], int(p["alpha"])), (raio_p, raio_p), raio_p)
            surface.blit(p_surf, (px - raio_p, py - raio_p))

        # ── 3. Título Artístico ──────────────────────────────────────────
        fonte_titulo = self.obter_fonte(36, "pressstart")
        fonte_sub    = self.obter_fonte(16, "pressstart")
        fonte_corpo  = self.obter_fonte(26, "vt323")
        fonte_peq    = self.obter_fonte(20, "vt323")

        # RPDESK com Sombra
        txt_titulo = "RPDESK"
        surf_titulo = fonte_titulo.render(txt_titulo, True, cores["texto_ouro"])
        surf_sombra = fonte_titulo.render(txt_titulo, True, (30, 20, 10))
        tx = (w - surf_titulo.get_width()) // 2
        ty = self.obter_y(40)
        surface.blit(surf_sombra, (tx + 4, ty + 4))
        surface.blit(surf_titulo, (tx, ty))

        # Subtítulo pulsante
        txt_sub = "Gerenciador de Guilda"
        surf_sub = fonte_sub.render(txt_sub, True, cores["texto_creme"])
        surf_sub.set_alpha(self.__titulo_alpha)
        sx = (w - surf_sub.get_width()) // 2
        sy = self.obter_y(98)
        surface.blit(surf_sub, (sx, sy))

        # ── 4. Painel/Pergaminho de Menu Centralizado ──────────────────────
        perg_rect = self.obter_rect(420, 180, 440, 390)
        self._desenhar_moldura(surface, perg_rect, espessura=3)
        pygame.draw.rect(surface, (235, 215, 185), perg_rect.inflate(-6, -6))  # Pergaminho creme

        self._renderizar_texto_com_sombra(
            surface, "MENU PRINCIPAL",
            fonte_sub, (60, 40, 20),
            (self.obter_x(545), self.obter_y(205)),
            sombra_offset=0
        )

        # Mensagem do Save no topo do pergaminho
        if self.__tem_save:
            msg = "Save ativo encontrado!"
            cor_msg = (40, 120, 40)
        else:
            msg = "Nenhum save encontrado"
            cor_msg = (120, 60, 60)

        surf_msg = fonte_corpo.render(msg, True, cor_msg)
        mx = (w - surf_msg.get_width()) // 2
        my = self.obter_y(245)
        surface.blit(surf_msg, (mx, my))

        # Linha divisória interna do pergaminho
        pygame.draw.line(surface, (180, 150, 110), 
                         (self.obter_x(460), self.obter_y(278)), 
                         (self.obter_x(820), self.obter_y(278)), 2)

        # ── 5. Botões de Menu ────────────────────────────────────────────
        self.__botao_carregar.desenhar(surface)
        self.__botao_novo.desenhar(surface)
        self.__botao_sair.desenhar(surface)

        # ── 6. Rodapé Decorativo ──────────────────────────────────────────
        txt_footer = "Pedro Oliveira Melo"
        surf_footer = fonte_peq.render(txt_footer, True, cores["texto_acinzentado"])
        fx = (w - surf_footer.get_width()) // 2
        fy = h - self.obter_y(40)
        surface.blit(surf_footer, (fx, fy))

        # ── 7. Fade-in de Entrada ────────────────────────────────────────
        if self.__fade_alpha > 0:
            fade_surf = pygame.Surface((w, h))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.__fade_alpha)
            surface.blit(fade_surf, (0, 0))
