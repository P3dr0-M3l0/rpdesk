"""
tela_bau.py
-----------
Tela do Baú da Guilda e Mochilas (Fase 3.4).

Consolida em uma única tela de Pygame:
  - Visualização do Baú central da guilda.
  - Seleção de herói ativo para gerenciamento de equipamentos.
  - Slots de equipamentos equipados do herói (Cabeça, Tronco, Mão Esquerda, Mão Direita, etc.).
  - Mochila do herói ativo.
  - Transferência de itens (Mochila <-> Baú, Mochila <-> Corpo).
"""

import pygame
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao
from ui.componentes.painel_hud import PainelHud
from itens.equipamento import Equipamento
from itens.consumivel import Consumivel


class TelaBau(TelaBase):
    """Tela consolidada para gerenciar o Baú da Guilda e Equipamentos dos Heróis."""

    def __init__(self, gerenciador, game_state, controller):
        super().__init__(gerenciador, game_state)
        self.__controller = controller
        self.__hud = PainelHud(gerenciador.largura)

        # Botão Voltar
        self.__btn_voltar = Botao(
            pygame.Rect(50, 640, 180, 40),
            "Voltar p/ Guilda",
            callback=self.__voltar,
            tamanho_fonte=16
        )
        self.__btn_voltar.vincular_gerenciador(gerenciador)

        # Estado interno de seleção
        self.__idx_heroi_selecionado = 0
        self.__item_selecionado_bau = None
        self.__item_selecionado_mochila = None

        # Drag and Drop de Itens
        self.__dragging_item = None
        self.__drag_pos = (0, 0)
        self.__drag_origem = ""

        # Detecção de Clique Duplo
        self.__ultimo_clique_tempo = 0
        self.__ultimo_clique_item = None

        # Botões de Ação
        self.__btn_dar_ao_heroi = Botao(
            pygame.Rect(50, 580, 240, 36),
            "Enviar item p/ Mochila",
            callback=self.__transferir_bau_para_mochila,
            tamanho_fonte=14
        )
        self.__btn_enviar_ao_bau = Botao(
            pygame.Rect(690, 580, 240, 36),
            "Mover item p/ Baú",
            callback=self.__transferir_mochila_para_bau,
            tamanho_fonte=14
        )
        self.__btn_dar_ao_heroi.vincular_gerenciador(gerenciador)
        self.__btn_enviar_ao_bau.vincular_gerenciador(gerenciador)

        # Botões para navegar entre heróis
        self.__btn_ant_heroi = Botao(
            pygame.Rect(720, 130, 40, 32),
            "<",
            callback=self.__anterior_heroi,
            tamanho_fonte=16
        )
        self.__btn_prox_heroi = Botao(
            pygame.Rect(1140, 130, 40, 32),
            ">",
            callback=self.__proximo_heroi,
            tamanho_fonte=16
        )
        self.__btn_ant_heroi.vincular_gerenciador(gerenciador)
        self.__btn_prox_heroi.vincular_gerenciador(gerenciador)

        # Slots padrão de equipamento do herói
        self.__slots_padrao = [
            ("cabeca", "Cabeça"),
            ("tronco", "Tronco"),
            ("pernas", "Pernas"),
            ("mao_esquerda", "Mão Esq."),
            ("mao_direita", "Mão Dir."),
            ("pes", "Pés"),
            ("dedos", "Dedos")
        ]

        # Mensagens
        self.__status_mensagem = ""
        self.__status_timer = 0.0
        self.__status_cor_tipo = "ouro"

    def ao_entrar(self):
        self.__idx_heroi_selecionado = 0
        self.__item_selecionado_bau = None
        self.__item_selecionado_mochila = None
        self.__atualizar_estado_botoes()

    def __atualizar_estado_botoes(self):
        guilda = self._game_state.guilda
        has_heroes = len(guilda.roster_herois) > 0

        self.__btn_ant_heroi.ativo = has_heroes
        self.__btn_prox_heroi.ativo = has_heroes
        self.__btn_dar_ao_heroi.ativo = (self.__item_selecionado_bau is not None and has_heroes)
        self.__btn_enviar_ao_bau.ativo = (self.__item_selecionado_mochila is not None and has_heroes)

    def __voltar(self):
        self._gerenciador.pop()

    def __anterior_heroi(self):
        guilda = self._game_state.guilda
        if guilda.roster_herois:
            self.__idx_heroi_selecionado = (self.__idx_heroi_selecionado - 1) % len(guilda.roster_herois)
            self.__item_selecionado_mochila = None
            self.__atualizar_estado_botoes()

    def __proximo_heroi(self):
        guilda = self._game_state.guilda
        if guilda.roster_herois:
            self.__idx_heroi_selecionado = (self.__idx_heroi_selecionado + 1) % len(guilda.roster_herois)
            self.__item_selecionado_mochila = None
            self.__atualizar_estado_botoes()

    def __obter_heroi_ativo(self):
        guilda = self._game_state.guilda
        if guilda.roster_herois and self.__idx_heroi_selecionado < len(guilda.roster_herois):
            return guilda.roster_herois[self.__idx_heroi_selecionado]
        return None

    # ------------------------------------------------------------------
    # Transferências de Itens
    # ------------------------------------------------------------------
    def __transferir_bau_para_mochila(self):
        heroi = self.__obter_heroi_ativo()
        if not heroi or not self.__item_selecionado_bau:
            return

        item = self.__item_selecionado_bau
        guilda = self._game_state.guilda
        mochila = heroi.inventario

        if len(mochila.lista_itens) >= mochila.capacidade_max:
            self.__mostrar_mensagem(f"Mochila de {heroi.nome} está cheia!", "erro")
            return

        # Executa a transferência
        guilda.inventario_guilda.lista_itens.remove(item)
        mochila.adicionar_item(item)
        self.__mostrar_mensagem(f"{item.nome} movido para a mochila de {heroi.nome}.", "verde")

        self.__item_selecionado_bau = None
        self.__atualizar_estado_botoes()

    def __transferir_mochila_para_bau(self):
        heroi = self.__obter_heroi_ativo()
        if not heroi or not self.__item_selecionado_mochila:
            return

        item = self.__item_selecionado_mochila
        guilda = self._game_state.guilda
        mochila = heroi.inventario

        if len(guilda.inventario_guilda.lista_itens) >= guilda.inventario_guilda.capacidade_max:
            self.__mostrar_mensagem("O Baú da Guilda está cheio!", "erro")
            return

        # Executa a transferência usando o método do core
        if guilda.adicionar_item_bau(item, heroi):
            self.__mostrar_mensagem(f"{item.nome} enviado ao Baú central.", "verde")
        else:
            self.__mostrar_mensagem("Erro ao transferir item.", "erro")

        self.__item_selecionado_mochila = None
        self.__atualizar_estado_botoes()

    def __equipar_item_mochila(self, item):
        heroi = self.__obter_heroi_ativo()
        if not heroi:
            return

        if not isinstance(item, Equipamento):
            self.__mostrar_mensagem("Você não pode equipar um consumível!", "erro")
            return

        if heroi.equipar_item(item):
            self.__mostrar_mensagem(f"{item.nome} equipado com sucesso!", "verde")
            if self.__item_selecionado_mochila == item:
                self.__item_selecionado_mochila = None
        else:
            self.__mostrar_mensagem("Já existe outro equipamento nesse slot!", "erro")
        self.__atualizar_estado_botoes()

    def __desequipar_item_corpo(self, slot: str):
        heroi = self.__obter_heroi_ativo()
        if not heroi:
            return

        item_equipado = heroi.slots_equipados.get(slot)
        if not item_equipado:
            return

        if heroi.desequipar_item(slot):
            self.__mostrar_mensagem(f"Item desequipado com sucesso!", "verde")
        else:
            self.__mostrar_mensagem(f"Mochila de {heroi.nome} cheia para desequipar!", "erro")
        self.__atualizar_estado_botoes()

    def __mostrar_mensagem(self, texto, cor_tipo="ouro"):
        self.__status_mensagem = texto
        self.__status_timer = 3.0
        self.__status_cor_tipo = cor_tipo

    # ------------------------------------------------------------------
    # Cliques nos Painéis e Eventos
    # ------------------------------------------------------------------
    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            self.__btn_voltar.lidar_evento(ev)
            self.__btn_ant_heroi.lidar_evento(ev)
            self.__btn_prox_heroi.lidar_evento(ev)
            self.__btn_dar_ao_heroi.lidar_evento(ev)
            self.__btn_enviar_ao_bau.lidar_evento(ev)

            # Eventos de Drag & Drop e Cliques de Itens
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # 1. Clique nos itens do Baú (Esquerda)
                item_bau = self.__checar_clique_bau(ev.pos)
                if item_bau:
                    self.__dragging_item = item_bau
                    self.__drag_pos = ev.pos
                    self.__drag_origem = "bau"
                
                # 2. Clique nos slots de Equipamentos ou Mochila do herói ativo (Direita)
                item_mochila = self.__checar_clique_heroi(ev.pos)
                if item_mochila:
                    self.__dragging_item = item_mochila
                    self.__drag_pos = ev.pos
                    self.__drag_origem = "mochila"

            elif ev.type == pygame.MOUSEMOTION:
                if self.__dragging_item:
                    self.__drag_pos = ev.pos

            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if self.__dragging_item:
                    # Soltou o arrasto
                    if self.__drag_origem == "bau":
                        # Soltou no painel do herói (mochila ou slots)?
                        panel_heroi = self.obter_rect(580, 120, 660, 440)
                        if panel_heroi.collidepoint(ev.pos):
                            self.__item_selecionado_bau = self.__dragging_item
                            self.__transferir_bau_para_mochila()
                    elif self.__drag_origem == "mochila":
                        # Soltou no painel do Baú (esquerda)?
                        panel_bau = self.obter_rect(40, 120, 520, 440)
                        if panel_bau.collidepoint(ev.pos):
                            self.__item_selecionado_mochila = self.__dragging_item
                            self.__transferir_mochila_para_bau()
                        
                        # Soltou na área dos slots equipados?
                        panel_slots = self.obter_rect(590, 150, 240, 380)
                        if panel_slots.collidepoint(ev.pos):
                            self.__equipar_item_mochila(self.__dragging_item)
                    
                    self.__dragging_item = None

    def __checar_clique_bau(self, mouse_pos) -> object:
        guilda = self._game_state.guilda
        bau = guilda.inventario_guilda

        # Cada item do baú ocupa uma linha na listagem à esquerda de y=170 em diante
        for idx, item in enumerate(bau.lista_itens):
            y_lin = 170 + idx * 45
            rect_lin = self.obter_rect(60, y_lin, 480, 38)
            if rect_lin.collidepoint(mouse_pos):
                if self.__item_selecionado_bau == item:
                    self.__item_selecionado_bau = None
                else:
                    self.__item_selecionado_bau = item
                self.__atualizar_estado_botoes()
                return item
        return None

    def __checar_clique_heroi(self, mouse_pos) -> object:
        heroi = self.__obter_heroi_ativo()
        if not heroi:
            return None

        # ── 1. Clique nos Slots Equipados (Esquerda do painel do herói)
        for idx_s, (slot_key, slot_name) in enumerate(self.__slots_padrao):
            y_slot = 185 + idx_s * 55
            # Caixa do slot
            rect_slot = self.obter_rect(600, y_slot, 42, 42)
            if rect_slot.collidepoint(mouse_pos):
                # Desequipa item clicado
                if heroi.slots_equipados.get(slot_key):
                    self.__desequipar_item_corpo(slot_key)
                return None

        # ── 2. Clique na Mochila do Herói (Limitado à capacidade real)
        mochila = heroi.inventario
        cap_max = mochila.capacidade_max
        for idx_m in range(cap_max):
            col = idx_m % 4
            row = idx_m // 4
            x_slot = 850 + col * 90
            y_slot = 185 + row * 90
            rect_slot = self.obter_rect(x_slot, y_slot, 56, 56)

            if rect_slot.collidepoint(mouse_pos):
                if idx_m < len(mochila.lista_itens):
                    item = mochila.lista_itens[idx_m]
                    tempo_atual = pygame.time.get_ticks()
                    
                    # Detecção de Clique Duplo rápido (< 250ms)
                    if tempo_atual - self.__ultimo_clique_tempo < 250 and self.__ultimo_clique_item == item:
                        self.__equipar_item_mochila(item)
                        self.__item_selecionado_mochila = None
                        self.__ultimo_clique_item = None
                        self.__ultimo_clique_tempo = 0
                        self.__atualizar_estado_botoes()
                        return None
                    else:
                        self.__item_selecionado_mochila = item
                        self.__ultimo_clique_item = item
                        self.__ultimo_clique_tempo = tempo_atual
                        self.__atualizar_estado_botoes()
                        return item
        return None

    def atualizar(self, dt: float) -> None:
        if self.__status_timer > 0:
            self.__status_timer -= dt
            if self.__status_timer <= 0:
                self.__status_mensagem = ""

    # ------------------------------------------------------------------
    # Renderização da Tela
    # ------------------------------------------------------------------
    def desenhar(self, surface: pygame.Surface) -> None:
        cores = self._assets.CORES

        # Fontes
        fonte_tit   = self.obter_fonte(16, "pressstart")
        fonte_card  = self.obter_fonte(12, "pressstart")
        fonte_corpo = self.obter_fonte(24, "vt323")
        fonte_peq   = self.obter_fonte(18, "vt323")

        # 1. HUD
        self.__hud.desenhar(surface, self._game_state)

        # Título
        self._renderizar_texto_com_sombra(
            surface, "BAU DA GUILDA & GERENCIAMENTO DE INVENTARIO",
            fonte_tit, cores["texto_ouro"],
            (self.obter_x(50), self.obter_y(85))
        )

        # 2. Painel Esquerdo: Baú Central
        left_panel = self.obter_rect(40, 120, 520, 440)
        self._desenhar_moldura(surface, left_panel, espessura=2)
        pygame.draw.rect(surface, cores["fundo_painel"], left_panel.inflate(-4, -4))

        guilda = self._game_state.guilda
        bau = guilda.inventario_guilda
        self._renderizar_texto_com_sombra(
            surface, f"Baú Central: {len(bau.lista_itens)}/{bau.capacidade_max} itens",
            fonte_corpo, cores["texto_azul"],
            (self.obter_x(60), self.obter_y(130))
        )

        # Listagem do baú
        if not bau.lista_itens:
            self._renderizar_texto_com_sombra(
                surface, "Baú da guilda está vazio.",
                fonte_peq, cores["texto_acinzentado"],
                (self.obter_x(60), self.obter_y(170))
            )
        else:
            for idx, item in enumerate(bau.lista_itens):
                y_lin = 170 + idx * 45
                rect_lin = self.obter_rect(60, y_lin, 480, 38)

                # Destaque de seleção
                if self.__item_selecionado_bau == item:
                    pygame.draw.rect(surface, (70, 50, 20), rect_lin, border_radius=4)
                    pygame.draw.rect(surface, cores["borda_ouro"], rect_lin, 1, border_radius=4)
                else:
                    pygame.draw.rect(surface, (25, 20, 15), rect_lin, border_radius=4)

                # Desenha o ícone do item (32x32) dentro da listagem
                img = self._assets.imagem_item(item.nome, (24, 24))
                surface.blit(img, (self.obter_x(66), self.obter_y(y_lin + 7)))

                # Nome do Item
                self._renderizar_texto_com_sombra(
                    surface, item.nome,
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(100), self.obter_y(y_lin + 8))
                )

                # Detalhes do efeito se for equipamento
                if isinstance(item, Equipamento):
                    attr_lbl = item.modificador[0].split('_')[-1][:3].upper()
                    sign = "+" if item.modificador[1] >= 0 else ""
                    lbl = f"{attr_lbl} {sign}{item.modificador[1]}"
                    self._renderizar_texto_com_sombra(
                        surface, lbl,
                        fonte_peq, cores["texto_ouro"],
                        (self.obter_x(460), self.obter_y(y_lin + 8))
                    )
                else:
                    self._renderizar_texto_com_sombra(
                        surface, "Consum.",
                        fonte_peq, cores["texto_verde"],
                        (self.obter_x(445), self.obter_y(y_lin + 8))
                    )

        # 3. Painel Direito: Herói Selecionado & Equipamento
        right_panel = self.obter_rect(580, 120, 660, 440)
        self._desenhar_moldura(surface, right_panel, espessura=2)
        pygame.draw.rect(surface, cores["fundo_painel"], right_panel.inflate(-4, -4))

        heroi = self.__obter_heroi_ativo()
        if not heroi:
            self._renderizar_texto_com_sombra(
                surface, "Contrate heróis na Taverna primeiro.",
                fonte_corpo, cores["texto_acinzentado"],
                (self.obter_x(620), self.obter_y(150))
            )
        else:
            # Seleção de Herói
            self.__btn_ant_heroi.desenhar(surface)
            self.__btn_prox_heroi.desenhar(surface)

            # Centraliza o Nome do Herói na caixa de seleção (Apenas primeiro nome)
            nome_limpo = self.formatar_nome_heroi(heroi.nome)
            txt_heroi = f"Herói: {nome_limpo} (Lvl {heroi.nivel})"
            self._renderizar_texto_com_sombra(
                surface, txt_heroi,
                fonte_card, cores["texto_ouro"],
                (self.obter_x(770), self.obter_y(138))
            )

            # ── 3.1. Desenhar Equipamentos Equipados
            self._renderizar_texto_com_sombra(
                surface, "Slots Equipados:",
                fonte_peq, cores["texto_azul"],
                (self.obter_x(600), self.obter_y(155))
            )

            for idx_s, (slot_key, slot_name) in enumerate(self.__slots_padrao):
                y_slot = 185 + idx_s * 55
                # Caixa do slot
                rect_slot = self.obter_rect(600, y_slot, 42, 42)
                pygame.draw.rect(surface, cores["slot_vazio"], rect_slot, border_radius=4)
                pygame.draw.rect(surface, cores["slot_borda"], rect_slot, 1, border_radius=4)

                item_equipado = heroi.slots_equipados.get(slot_key)
                if item_equipado:
                    # Imagem do item centralizada no slot (32x32)
                    img = self._assets.imagem_item(item_equipado.nome, (32, 32))
                    surface.blit(img, (self.obter_x(605), self.obter_y(y_slot + 5)))

                    # Nome e efeito do item
                    self._renderizar_texto_com_sombra(
                        surface, item_equipado.nome,
                        fonte_peq, cores["texto_creme"],
                        (self.obter_x(655), self.obter_y(y_slot + 2))
                    )
                    attr_name = item_equipado.modificador[0].replace('_', ' ').capitalize()
                    val = item_equipado.modificador[1]
                    sign = "+" if val >= 0 else ""
                    self._renderizar_texto_com_sombra(
                        surface, f"{attr_name} {sign}{val}",
                        fonte_peq, cores["texto_ouro"],
                        (self.obter_x(655), self.obter_y(y_slot + 22))
                    )
                else:
                    self._renderizar_texto_com_sombra(
                        surface, f"{slot_name}: [Vazio]",
                        fonte_peq, cores["texto_acinzentado"],
                        (self.obter_x(655), self.obter_y(y_slot + 12))
                    )

            # ── 3.2. Desenhar Mochila do Herói (Limitado à capacidade real)
            cap_mochila = len(heroi.inventario.lista_itens)
            cap_max = heroi.inventario.capacity_max if hasattr(heroi.inventario, 'capacity_max') else heroi.inventario.capacidade_max
            self._renderizar_texto_com_sombra(
                surface, f"Mochila: {cap_mochila}/{cap_max}",
                fonte_peq, cores["texto_azul"],
                (self.obter_x(850), self.obter_y(155))
            )

            # Desenha slots da mochila (grade baseada em cap_max)
            for idx_slot in range(cap_max):
                col = idx_slot % 4
                row = idx_slot // 4
                x_slot = 850 + col * 90
                y_slot = 185 + row * 90
                
                rect_slot = self.obter_rect(x_slot, y_slot, 56, 56)
                pygame.draw.rect(surface, cores["slot_vazio"], rect_slot, border_radius=4)
                pygame.draw.rect(surface, cores["slot_borda"], rect_slot, 1, border_radius=4)

                # Se tiver item alocado nesse slot da mochila
                if idx_slot < len(heroi.inventario.lista_itens):
                    item = heroi.inventario.lista_itens[idx_slot]

                    # Desenha imagem do item
                    img = self._assets.imagem_item(item.nome, (32, 32))
                    surface.blit(img, (self.obter_x(x_slot + 12), self.obter_y(y_slot + 12)))

                    # Se selecionado, desenha borda amarela
                    if self.__item_selecionado_mochila == item:
                        pygame.draw.rect(surface, cores["borda_ouro"], rect_slot, 2, border_radius=4)

                    # Pequena dica de texto ao redor do slot se selecionado (Sem truncamento!)
                    if self.__item_selecionado_mochila == item:
                        self._renderizar_texto_com_sombra(
                            surface, item.nome,
                            fonte_peq, cores["texto_ouro"],
                            (self.obter_x(850), self.obter_y(545))
                        )

        # 4. Botões de ação da parte inferior
        self.__btn_voltar.desenhar(surface)
        self.__btn_dar_ao_heroi.desenhar(surface)
        self.__btn_enviar_ao_bau.desenhar(surface)

        # Mensagens temporárias
        if self.__status_mensagem:
            cor = cores["texto_verde"] if self.__status_cor_tipo == "verde" else (cores["texto_vermelho"] if self.__status_cor_tipo == "erro" else cores["texto_ouro"])
            self._renderizar_texto_com_sombra(
                surface, self.__status_mensagem,
                fonte_peq, cor,
                (self.obter_x(260), self.obter_y(650))
            )

        # ── Desenha item flutuando ao arrastar ───────────────────────────
        if self.__dragging_item:
            img = self._assets.imagem_item(self.__dragging_item.nome, (32, 32))
            surface.blit(img, (self.__drag_pos[0] - 16, self.__drag_pos[1] - 16))
