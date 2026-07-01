"""
tela_taverna.py
---------------
Tela da Taverna da Cidade (Fase 3.2).

Permite:
  - Visualizar os 3 heróis da vitrine atual com seus atributos, traços e equipamentos.
  - Contratar heróis gastando ouro.
  - Modal gráfico de confirmação de contratação.
  - Voltar para o Hub da Guilda.
"""

import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao
from ui.componentes.painel_hud import PainelHud


class TelaTaverna(TelaBase):
    """Tela da Taverna com vitrine de 3 heróis disponíveis para contratação."""

    def __init__(self, gerenciador, game_state, controller):
        super().__init__(gerenciador, game_state)
        self.__controller = controller
        self.__hud = PainelHud(gerenciador.largura)

        # Botão Voltar (inferior esquerdo)
        self.__btn_voltar = Botao(
            pygame.Rect(50, 620, 200, 44),
            "Voltar p/ Guilda",
            callback=self.__voltar,
            tamanho_fonte=18
        )
        self.__btn_voltar.vincular_gerenciador(gerenciador)

        # Estado do Modal de Confirmação
        self.__modal_ativo = False
        self.__heroi_selecionado = None

        # Botões do Modal
        cx = gerenciador.largura // 2
        cy = gerenciador.altura // 2
        self.__btn_confirmar = Botao(
            pygame.Rect(cx - 160, cy + 40, 140, 40),
            "Contratar",
            callback=self.__confirmar_contratacao,
            tamanho_fonte=16
        )
        self.__btn_cancelar = Botao(
            pygame.Rect(cx + 20, cy + 40, 140, 40),
            "Cancelar",
            callback=self.__fechar_modal,
            tamanho_fonte=16
        )
        self.__btn_confirmar.vincular_gerenciador(gerenciador)
        self.__btn_cancelar.vincular_gerenciador(gerenciador)

        # Botões de contratação das 3 colunas
        self.__botoes_vitrine = []
        self.__inicializar_botoes_vitrine()

        # Mensagem de status temporária
        self.__status_mensagem = ""
        self.__status_timer = 0.0
        self.__status_cor_tipo = "ouro"

    def __inicializar_botoes_vitrine(self):
        self.__botoes_vitrine.clear()
        # 3 colunas posicionadas em x = 60, 460, 860. Largura do card = 360
        pos_x = [60, 460, 860]
        for idx, x in enumerate(pos_x):
            rect_btn = pygame.Rect(x + 60, 520, 240, 44)
            # Cria o callback passando o índice atual
            btn = Botao(
                rect_btn,
                "Contratar Herói",
                callback=lambda i=idx: self.__abrir_modal(i),
                tamanho_fonte=18
            )
            btn.vincular_gerenciador(self._gerenciador)
            self.__botoes_vitrine.append(btn)

    def ao_entrar(self):
        self.__fechar_modal()
        self.__atualizar_disponibilidade_botoes()

    def __atualizar_disponibilidade_botoes(self):
        # Atualiza a ativação dos botões de contratação
        lista_herois = self._game_state.taverna.obter_vitrine()
        ouro_guilda = self._game_state.guilda.ouro

        for i, btn in enumerate(self.__botoes_vitrine):
            if i < len(lista_herois):
                heroi = lista_herois[i]
                btn.ativo = (ouro_guilda >= heroi.valor)
            else:
                btn.ativo = False

    # ------------------------------------------------------------------
    # Lógica do Modal e Ações
    # ------------------------------------------------------------------
    def __abrir_modal(self, idx: int):
        lista_herois = self._game_state.taverna.obter_vitrine()
        if idx < len(lista_herois):
            self.__heroi_selecionado = lista_herois[idx]
            self.__modal_ativo = True

    def __fechar_modal(self):
        self.__modal_ativo = False
        self.__heroi_selecionado = None

    def __confirmar_contratacao(self):
        if self.__heroi_selecionado:
            heroi = self.__heroi_selecionado
            guilda = self._game_state.guilda
            taverna = self._game_state.taverna

            if guilda.contratar_heroi(heroi, heroi.valor):
                taverna.remover_heroi_comprado(heroi)
                self.__mostrar_mensagem(f"{heroi.nome} foi contratado!", cor_tipo="verde")
            else:
                self.__mostrar_mensagem("Ouro insuficiente!", cor_tipo="erro")

            self.__fechar_modal()
            self.__atualizar_disponibilidade_botoes()

    def __voltar(self):
        self._gerenciador.pop()

    def __mostrar_mensagem(self, texto, cor_tipo="ouro"):
        self.__status_mensagem = texto
        self.__status_timer = 3.0
        self.__status_cor_tipo = cor_tipo

    # ------------------------------------------------------------------
    # Loop de Eventos, Atualização e Desenho
    # ------------------------------------------------------------------
    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            if self.__modal_ativo:
                self.__btn_confirmar.lidar_evento(ev)
                self.__btn_cancelar.lidar_evento(ev)
            else:
                self.__btn_voltar.lidar_evento(ev)
                for btn in self.__botoes_vitrine:
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
        fonte_card  = self.obter_fonte(12, "pressstart")
        fonte_corpo = self.obter_fonte(24, "vt323")
        fonte_peq   = self.obter_fonte(18, "vt323")

        # 1. Desenha o HUD Superior
        self.__hud.desenhar(surface, self._game_state)

        # Título da taverna
        self._renderizar_texto_com_sombra(
            surface, "TAVERNA DA CIDADE - RECRUTAMENTO",
            fonte_tit, cores["texto_ouro"],
            (self.obter_x(50), self.obter_y(85))
        )

        # 2. Desenha a vitrine de 3 heróis
        lista_herois = self._game_state.taverna.obter_vitrine()
        pos_x = [60, 460, 860]

        for i in range(3):
            card_rect = self.obter_rect(pos_x[i], 120, 360, 460)
            self._desenhar_moldura(surface, card_rect, espessura=2)
            pygame.draw.rect(surface, cores["fundo_painel"], card_rect.inflate(-4, -4))

            if i < len(lista_herois):
                heroi = lista_herois[i]
                attrs = heroi.atributos

                # Nome do Herói (Apenas primeiro nome)
                nome_exibido = self.formatar_nome_heroi(heroi.nome)
                self._renderizar_texto_com_sombra(
                    surface, nome_exibido,
                    fonte_card, cores["texto_creme"],
                    (self.obter_x(pos_x[i] + 20), self.obter_y(140))
                )

                # Detalhes do Custo
                self._renderizar_texto_com_sombra(
                    surface, f"Custo: {heroi.valor} Ouro",
                    fonte_corpo, cores["texto_ouro"],
                    (self.obter_x(pos_x[i] + 20), self.obter_y(175))
                )

                pygame.draw.line(surface, cores["hud_separador"],
                                 (self.obter_x(pos_x[i] + 20), self.obter_y(205)),
                                 (self.obter_x(pos_x[i] + 340), self.obter_y(205)), 1)

                # Atributos (Tabela Dinâmica de 3 colunas ou Única)
                # Verifica se há modificadores
                lista_attrs = [
                    ("Força", attrs.forca),
                    ("Destreza", attrs.destreza),
                    ("Inteligência", attrs.inteligencia),
                    ("Velocidade", attrs.velocidade),
                    ("HP Máximo", attrs.hp_max)
                ]

                tem_mod = False
                for label, atr in lista_attrs:
                    if (atr.valor_total - atr.valor_base) != 0:
                        tem_mod = True
                        break

                for idx_a, (label, atr) in enumerate(lista_attrs):
                    y_atr = 220 + idx_a * 25
                    base_val = atr.valor_base
                    tot_val  = atr.valor_total
                    mod_val  = tot_val - base_val

                    # Label e base
                    label_formatada = f"{label:<12}"
                    self._renderizar_texto_com_sombra(
                        surface, f"{label_formatada} {base_val}",
                        fonte_corpo, cores["texto_creme"],
                        (self.obter_x(pos_x[i] + 20), self.obter_y(y_atr))
                    )

                    if tem_mod:
                        # Coluna do Modificador (se houver variação)
                        if mod_val != 0:
                            sinal = "+" if mod_val > 0 else ""
                            cor_mod = cores["texto_ouro"] if mod_val > 0 else cores["texto_vermelho"]
                            self._renderizar_texto_com_sombra(
                                surface, f"{sinal}{mod_val}",
                                fonte_corpo, cor_mod,
                                (self.obter_x(pos_x[i] + 200), self.obter_y(y_atr))
                            )
                        # Coluna de Valor Total
                        self._renderizar_texto_com_sombra(
                            surface, f"= {tot_val}",
                            fonte_corpo, cores["texto_creme"],
                            (self.obter_x(pos_x[i] + 280), self.obter_y(y_atr))
                        )

                pygame.draw.line(surface, cores["hud_separador"],
                                 (self.obter_x(pos_x[i] + 20), self.obter_y(355)),
                                 (self.obter_x(pos_x[i] + 340), self.obter_y(355)), 1)

                # Traço de Personalidade
                self._renderizar_texto_com_sombra(
                    surface, "Traço de Destaque:",
                    fonte_peq, cores["texto_azul"],
                    (self.obter_x(pos_x[i] + 20), self.obter_y(365))
                )
                if heroi.lista_tracos:
                    traco = heroi.lista_tracos[0]
                    self._renderizar_texto_com_sombra(
                        surface, f"{traco.nome}",
                        fonte_corpo, cores["texto_ouro"],
                        (self.obter_x(pos_x[i] + 20), self.obter_y(390))
                    )
                    # Descrição curta do traço
                    desc_palavras = traco.descricao.split()
                    desc_curta = " ".join(desc_palavras[:7]) + ("..." if len(desc_palavras) > 7 else "")
                    self._renderizar_texto_com_sombra(
                        surface, desc_curta,
                        fonte_peq, cores["texto_acinzentado"],
                        (self.obter_x(pos_x[i] + 20), self.obter_y(415))
                    )
                else:
                    self._renderizar_texto_com_sombra(
                        surface, "Nenhum",
                        fonte_corpo, cores["texto_acinzentado"],
                        (self.obter_x(pos_x[i] + 20), self.obter_y(390))
                    )

                # Equipamentos Detalhados no Card
                itens_eq = [item for item in heroi.slots_equipados.values() if item]
                if not itens_eq:
                    self._renderizar_texto_com_sombra(
                        surface, "Equipamentos: Nenhum",
                        fonte_peq, cores["texto_acinzentado"],
                        (self.obter_x(pos_x[i] + 20), self.obter_y(455))
                    )
                else:
                    for idx_e, item in enumerate(itens_eq[:2]):
                        slot_nome = item.slot.replace('mao_esquerda', 'M.Esq').replace('mao_direita', 'M.Dir').replace('cabeca', 'Cab').replace('tronco', 'Tro').replace('pernas', 'Per').capitalize()
                        attr_lbl = item.modificador[0].split('_')[-1][:3].upper()
                        sinal = "+" if item.modificador[1] >= 0 else ""
                        txt_eq = f"{slot_nome}: {item.nome} ({attr_lbl} {sinal}{item.modificador[1]})"
                        self._renderizar_texto_com_sombra(
                            surface, txt_eq,
                            fonte_peq, cores["texto_creme"],
                            (self.obter_x(pos_x[i] + 20), self.obter_y(445 + idx_e * 22))
                        )

                # Desenha o botão de contratação
                self.__botoes_vitrine[i].desenhar(surface)
            else:
                # Slot de herói já contratado (Vazio)
                self._renderizar_texto_com_sombra(
                    surface, "CONTRATADO",
                    fonte_card, cores["texto_acinzentado"],
                    (self.obter_x(pos_x[i] + 110), self.obter_y(300))
                )

        # 3. Desenha o botão Voltar
        self.__btn_voltar.desenhar(surface)

        # Mensagem temporária
        if self.__status_mensagem:
            cor = cores["texto_verde"] if self.__status_cor_tipo == "verde" else (cores["texto_vermelho"] if self.__status_cor_tipo == "erro" else cores["texto_ouro"])
            self._renderizar_texto_com_sombra(
                surface, self.__status_mensagem,
                fonte_peq, cor,
                (self.obter_x(280), self.obter_y(632))
            )

        # 4. Desenha o Modal de Confirmação (sobreposto)
        if self.__modal_ativo and self.__heroi_selecionado:
            # Fundo escurecido semi-transparente
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            # Caixa do Modal
            modal_rect = self.obter_rect(390, 210, 500, 300)
            self._desenhar_moldura(surface, modal_rect, espessura=3)
            pygame.draw.rect(surface, cores["fundo_painel"], modal_rect.inflate(-6, -6))

            # Conteúdo do Modal
            self._renderizar_texto_com_sombra(
                surface, "CONTRATAR HERÓI",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(430), self.obter_y(250))
            )

            msg_pergunta = f"Deseja recrutar {self.__heroi_selecionado.nome}?"
            self._renderizar_texto_com_sombra(
                surface, msg_pergunta,
                fonte_corpo, cores["texto_creme"],
                (self.obter_x(430), self.obter_y(310))
            )

            msg_custo = f"Custo: {self.__heroi_selecionado.valor} Moedas de Ouro"
            self._renderizar_texto_com_sombra(
                surface, msg_custo,
                fonte_corpo, cores["texto_ouro"],
                (self.obter_x(430), self.obter_y(350))
            )

            # Botões do modal
            self.__btn_confirmar.desenhar(surface)
            self.__btn_cancelar.desenhar(surface)
