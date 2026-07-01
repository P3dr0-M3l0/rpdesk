"""
tela_introducao.py
------------------
Tela de Introdução Narrativa e Rebatismo da Guilda.

Apresenta a história inicial em formato de páginas de livro com fundos medievais procedurais
e partículas por código. Ao final, permite rebatizar a guilda com validações de erro cruzadas.
"""

import time
import math
import random
import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao


class TelaIntroducao(TelaBase):
    """
    Tela de lore do jogo com fundos procedurais animados
    e input de texto dinâmico para renomear a guilda.
    """

    def __init__(self, gerenciador, game_state, controller, cb_finalizar):
        super().__init__(gerenciador, game_state)
        self.__controller = controller
        self.__cb_finalizar = cb_finalizar

        self.__indice_pagina = 0
        self.__fase = "livro"  # "livro" ou "rebatismo"
        self.__nome_guilda_temp = ""
        self.__max_caracteres = 20  # Limitado a 20 caracteres pelo setter da guilda

        # Lore medieval dividida em páginas
        self.__paginas = [
            {
                "texto": (
                    "Há mil anos, os reinos de Valen-Ur e "
                    "as profundezas abissais de Nifl-Karr viviam isolados por uma barreira "
                    "intransponível erguida pelo sacrifício dos primeiros arcanos. Contudo, "
                    "a ganância dos reis da superfície e o desgaste dos selos mágicos provocaram "
                    "a Grande Confluência. Um portal colossal e instável abriu-se no Vale dos "
                    "Sussurros, e com ele vieram as hordas corrompidas e os orcs selvagens, "
                    "sedentos pelo ouro e pela essência vital dos vivos."
                )
            },
            {
                "texto": (
                    "Em poucos invernos, a devastação espalhou-se como fogo em palha seca. "
                    "Cidades fortificadas viraram cinzas e poeira, e os monstros dominaram as "
                    "estradas comerciais, isolando os vilarejos e trazendo a fome e a morte. "
                    "O ouro tornou-se raro, a segurança transformou-se em lenda, e os reis se "
                    "trancaram em seus castelos de pedra, abandonando o povo comum à própria sorte."
                )
            },
            {
                "texto": (
                    "A única esperança residia na reconstrução das antigas Guildas de Expedicionários. "
                    "O lendário e antigo Mestre de nossa guilda reuniu os últimos guerreiros destemidos "
                    "e partiu em uma jornada suicida rumo ao Vale dos Sussurros para selar o portal. "
                    "Ele e sua equipe jamais retornaram, deixando para trás apenas silêncio, luto e ruínas."
                )
            },
            {
                "texto": (
                    "O salão da guilda, outrora barulhento e cheio de vida, caiu no esquecimento. "
                    "Teias de aranha cobrem os tronos de carvalho, poeira repousa sobre as mesas "
                    "de banquete e as moedas no cofre secaram. Mas os pergaminhos da profecia "
                    "dizem que um novo Mestre se ergueria das cinzas para reescrever a história "
                    "e reerguer a guilda de sua ruína..."
                )
            }
        ]

        # Partículas de poeira dourada para a página da guilda e rebatismo
        self.__particulas_poeira = []

        # Botões de navegação da fase de Livro
        self.__btn_avancar = Botao(
            pygame.Rect(940, 570, 160, 42),
            "Avançar",
            callback=self.__avancar_pagina,
            tamanho_fonte=18
        )
        self.__btn_pular = Botao(
            pygame.Rect(180, 570, 140, 42),
            "Pular",
            callback=self.__pular_introducao,
            tamanho_fonte=18
        )

        self.__btn_avancar.vincular_gerenciador(gerenciador)
        self.__btn_pular.vincular_gerenciador(gerenciador)

        # Botões da fase de Rebatismo
        self.__btn_confirmar = Botao(
            pygame.Rect(460, 520, 360, 48),
            "Confirmar Nome e Iniciar",
            callback=self.__confirmar_rebatismo,
            tamanho_fonte=20
        )
        self.__btn_confirmar.vincular_gerenciador(gerenciador)
        self.__btn_confirmar.ativo = False

        self.__erro_mensagem = ""
        self.__erro_timer = 0.0

    def ao_entrar(self) -> None:
        self.__indice_pagina = 0
        self.__fase = "livro"
        self.__nome_guilda_temp = ""
        self.__erro_mensagem = ""
        self.__particulas_poeira.clear()

    def __avancar_pagina(self):
        if self.__indice_pagina < len(self.__paginas) - 1:
            self.__indice_pagina += 1
        else:
            self.__fase = "rebatismo"

    def __pular_introducao(self):
        self.__fase = "rebatismo"

    def __confirmar_rebatismo(self):
        nome_limpo = self.__nome_guilda_temp.strip()
        if not nome_limpo:
            self.__erro_mensagem = "O nome da guilda nao pode ser vazio!"
            self.__erro_timer = 3.5
            return
        
        if len(nome_limpo) > 20:
            self.__erro_mensagem = "O nome da guilda deve ter entre 1 e 20 caracteres!"
            self.__erro_timer = 3.5
            return
        
        # Altera o nome da guilda no game state
        if self._game_state and self._game_state.guilda:
            self._game_state.guilda.nome = nome_limpo
            # Checagem de dupla segurança com o setter do core
            if self._game_state.guilda.nome != nome_limpo:
                self.__erro_mensagem = "Nome invalido! Deve ter entre 1 e 20 caracteres."
                self.__erro_timer = 3.5
                return

        if self.__cb_finalizar:
            self.__cb_finalizar()

    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            if self.__fase == "livro":
                self.__btn_avancar.lidar_evento(ev)
                self.__btn_pular.lidar_evento(ev)
            elif self.__fase == "rebatismo":
                self.__btn_confirmar.lidar_evento(ev)

                # Input do teclado
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_BACKSPACE:
                        self.__nome_guilda_temp = self.__nome_guilda_temp[:-1]
                    elif ev.key == pygame.K_RETURN:
                        if len(self.__nome_guilda_temp.strip()) > 0:
                            self.__confirmar_rebatismo()
                    else:
                        char = ev.unicode
                        if char.isalnum() or char in " -_":
                            if len(self.__nome_guilda_temp) < self.__max_caracteres:
                                self.__nome_guilda_temp += char

    def atualizar(self, dt: float) -> None:
        if self.__fase == "rebatismo":
            self.__btn_confirmar.ativo = len(self.__nome_guilda_temp.strip()) > 0

        if self.__erro_timer > 0:
            self.__erro_timer -= dt
            if self.__erro_timer <= 0:
                self.__erro_mensagem = ""

        # Atualiza partículas de poeira dourada (páginas de guilda e rebatismo)
        if self.__fase == "rebatismo" or (self.__fase == "livro" and self.__indice_pagina == 3):
            for p in self.__particulas_poeira[:]:
                p["y"] -= p["vy"] * dt * 30
                p["x"] += p["vx"] * dt * 30
                p["alpha"] -= dt * 60
                if p["y"] < 0 or p["alpha"] <= 0:
                    self.__particulas_poeira.remove(p)

            if len(self.__particulas_poeira) < 25 and random.random() < 0.15:
                self.__particulas_poeira.append({
                    "x": random.randint(0, self._gerenciador.largura),
                    "y": self._gerenciador.altura + 5,
                    "vx": random.uniform(-0.4, 0.4),
                    "vy": random.uniform(0.6, 1.8),
                    "raio": random.randint(2, 5),
                    "alpha": random.uniform(90, 180),
                    "cor": (210, 180, 100)  # Poeira dourada
                })

    def desenhar(self, surface: pygame.Surface) -> None:
        cores = self._assets.CORES
        w = self._gerenciador.largura_real
        h = self._gerenciador.altura_real

        # ── 1. Desenha Fundos Procedurais Dinâmicos de Acordo com a Página ──
        # Substitui completamente os blits de imagens PNG externas.
        if self.__fase == "rebatismo":
            # Fundo marrom-conhaque (guilda abandonada)
            surface.fill((25, 18, 14))
        else:
            if self.__indice_pagina == 0:
                # O Portal: Azul e Roxo Arcanos
                surface.fill((15, 10, 20))
                for raio_logico, alpha in [(480, 25), (320, 35), (180, 45)]:
                    raio = self.obter_y(raio_logico)
                    circ = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(circ, (90, 45, 150, alpha), (0, 0, raio * 2, raio * 2))
                    surface.blit(circ, (w // 2 - raio, h // 2 - raio))
            elif self.__indice_pagina == 1:
                # A Horda: Vermelho chamas e laranja pulsante
                surface.fill((20, 8, 8))
                frequencia = time.time() * 2.5
                pulsar = int(25 * abs(math.sin(frequencia)))
                for raio_logico, alpha in [(500, 20), (350, 30), (200, 40)]:
                    raio = self.obter_y(raio_logico)
                    circ = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(circ, (120 + pulsar, 35, 10, alpha), (0, 0, raio * 2, raio * 2))
                    surface.blit(circ, (w // 2 - raio, h // 2 - raio))
            elif self.__indice_pagina == 2:
                # O Caverna Escura
                surface.fill((10, 10, 11))
                for raio_logico, alpha in [(450, 15), (300, 20)]:
                    raio = self.obter_y(raio_logico)
                    circ = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(circ, (40, 40, 45, alpha), (0, 0, raio * 2, raio * 2))
                    surface.blit(circ, (w // 2 - raio, h // 2 - raio))
            elif self.__indice_pagina == 3:
                # A Guilda em Ruínas
                surface.fill((25, 18, 14))

        # Desenha poeira dourada
        if self.__fase == "rebatismo" or (self.__fase == "livro" and self.__indice_pagina == 3):
            for p in self.__particulas_poeira:
                px = self.obter_x(p["x"])
                py = self.obter_y(p["y"])
                r = max(1, self.obter_y(p["raio"]))
                p_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(p_surf, (p["cor"][0], p["cor"][1], p["cor"][2], int(p["alpha"])), (r, r), r)
                surface.blit(p_surf, (px - r, py - r))

        # Overlay para maior profundidade
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        surface.blit(overlay, (0, 0))

        # Fontes
        fonte_tit = self.obter_fonte(20, "pressstart")
        fonte_corpo = self.obter_fonte(26, "vt323")
        fonte_peq = self.obter_fonte(20, "vt323")

        # ── 2. Painel Principal do Livro ──────────────────────────────────
        livro_rect = self.obter_rect(140, 80, 1000, 560)
        painel_surf = pygame.Surface((livro_rect.width, livro_rect.height), pygame.SRCALPHA)
        painel_surf.fill((22, 16, 12, 230))
        surface.blit(painel_surf, (livro_rect.x, livro_rect.y))
        self._desenhar_moldura(surface, livro_rect, espessura=3)

        if self.__fase == "livro":
            # Título do Pergaminho (Horizontalmente Centralizado)
            surf_tit = fonte_tit.render("O PERGAMINHO DE ALVORADA", True, cores["texto_ouro"])
            tx = (w - surf_tit.get_width()) // 2
            ty = self.obter_y(120)
            
            # Sombra
            surf_tit_s = fonte_tit.render("O PERGAMINHO DE ALVORADA", True, (30, 20, 10))
            surface.blit(surf_tit_s, (tx + 2, ty + 2))
            surface.blit(surf_tit, (tx, ty))

            # Conteúdo da Lore (Horizontalmente Centralizado)
            texto_lore = self.__paginas[self.__indice_pagina]["texto"]
            linhas = self.__quebrar_texto(texto_lore, 72)
            for idx, linha in enumerate(linhas):
                surf_l = fonte_corpo.render(linha, True, cores["texto_creme"])
                lx = (w - surf_l.get_width()) // 2
                ly = self.obter_y(200 + idx * 32)
                
                # Sombra
                surf_l_s = fonte_corpo.render(linha, True, (20, 15, 10))
                surface.blit(surf_l_s, (lx + 2, ly + 2))
                surface.blit(surf_l, (lx, ly))

            # Indicador de Página (Centralizado)
            pag_info = f"Cronica {self.__indice_pagina + 1} de {len(self.__paginas)}"
            surf_pag = fonte_peq.render(pag_info, True, cores["texto_acinzentado"])
            px = (w - surf_pag.get_width()) // 2
            py = self.obter_y(525)
            surface.blit(surf_pag, (px, py))

            # Botões
            self.__btn_avancar.desenhar(surface)
            self.__btn_pular.desenhar(surface)

        elif self.__fase == "rebatismo":
            # Título da tela de Rebatismo
            surf_tit = fonte_tit.render("FUNDACAO DA GUILDA", True, cores["texto_ouro"])
            tx = (w - surf_tit.get_width()) // 2
            ty = self.obter_y(120)
            
            surf_tit_s = fonte_tit.render("FUNDACAO DA GUILDA", True, (30, 20, 10))
            surface.blit(surf_tit_s, (tx + 2, ty + 2))
            surface.blit(surf_tit, (tx, ty))

            # Mensagem
            mensagem_falar = (
                "Mestre, os saloes estao vazios e o silencio eh o nosso unico companheiro. "
                "Mas a lenda de um novo alvorecer começa a se espalhar. Diga-nos: "
                "por qual nome epico os bardos cantarao a historia de nossa guilda?"
            )
            linhas = self.__quebrar_texto(mensagem_falar, 72)
            for idx, linha in enumerate(linhas):
                surf_l = fonte_corpo.render(linha, True, cores["texto_creme"])
                lx = (w - surf_l.get_width()) // 2
                ly = self.obter_y(180 + idx * 32)
                
                surf_l_s = fonte_corpo.render(linha, True, (20, 15, 10))
                surface.blit(surf_l_s, (lx + 2, ly + 2))
                surface.blit(surf_l, (lx, ly))

            # Caixa de digitação do nome (Centralizado)
            input_box = self.obter_rect(240, 360, 800, 56)
            pygame.draw.rect(surface, cores["fundo_principal"], input_box)
            self._desenhar_moldura(surface, input_box, espessura=2)

            # Texto digitado + cursor piscante
            cursor = "|" if int(time.time() * 2) % 2 == 0 else ""
            txt_exibir = self.__nome_guilda_temp + cursor
            if not self.__nome_guilda_temp:
                txt_exibir = "Digite o nome da guilda aqui..." + cursor
                cor_txt = cores["texto_acinzentado"]
            else:
                cor_txt = cores["texto_ouro"]

            surf_in = fonte_corpo.render(txt_exibir, True, cor_txt)
            ix = (w - surf_in.get_width()) // 2
            iy = self.obter_y(375)
            surface.blit(surf_in, (ix, iy))

            # Mensagem de erro vermelha se houver (Centralizado)
            if self.__erro_mensagem:
                surf_err = fonte_peq.render(self.__erro_mensagem, True, cores["texto_vermelho"])
                ex = (w - surf_err.get_width()) // 2
                ey = self.obter_y(440)
                surface.blit(surf_err, (ex, ey))

            # Botão Confirmar
            self.__btn_confirmar.desenhar(surface)

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

        return linhas
