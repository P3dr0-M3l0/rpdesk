"""
asset_manager.py
----------------
Gerenciador centralizado de assets (Singleton + Cache / Lazy Loading).

Responsabilidades (POO aplicado):
  - Abstração    : esconde do restante do sistema como, quando e de onde os
                   recursos são carregados.
  - Encapsulamento: estado interno (cache, caminhos) totalmente privado.
  - Singleton    : garante que exista apenas UMA instância ativa na memória,
                   evitando recarregamentos desnecessários em diferentes telas.
"""

import os
import pygame


class AssetManager:
    """Singleton para carregamento e cache de fontes e imagens."""

    _instancia = None  # Referência única da classe

    # ------------------------------------------------------------------
    # Paleta de cores global do RpDesk (medieval dark fantasy)
    # ------------------------------------------------------------------
    CORES = {
        # Fundos
        "fundo_principal":    (18, 14, 10),
        "fundo_painel":       (28, 22, 16),
        "fundo_painel2":      (38, 30, 22),
        # Bordas e molduras
        "borda_ouro":         (180, 140, 60),
        "borda_ouro_claro":   (220, 185, 90),
        "borda_bronze":       (120, 90, 45),
        "borda_escura":       (60, 40, 20),
        # Texto
        "texto_creme":        (230, 215, 190),
        "texto_ouro":         (255, 210, 80),
        "texto_verde":        (90, 200, 100),
        "texto_vermelho":     (210, 70, 60),
        "texto_azul":         (100, 160, 220),
        "texto_acinzentado":  (130, 115, 100),
        "texto_branco":       (255, 255, 255),
        # Botões
        "botao_fundo":        (90, 65, 30),
        "botao_hover":        (120, 90, 45),
        "botao_clicado":      (60, 44, 20),
        "botao_borda":        (180, 140, 60),
        "botao_borda_escura": (50, 35, 15),
        # HUD
        "hud_fundo":          (20, 15, 10),
        "hud_separador":      (100, 75, 35),
        # Slots de itens
        "slot_vazio":         (35, 27, 18),
        "slot_borda":         (90, 70, 35),
    }

    # ------------------------------------------------------------------
    # Mapeamento de nomes de itens → arquivos de sprite
    # ------------------------------------------------------------------
    _MAPA_ITENS = {
        # ── Cabeça ──────────────────────────────────────────────────────
        "Capuz de Tecido Desgastado":           ("oi",  "Item__55.png"),
        "Elmo de Couro Amortecido":             ("oi",  "Item__44.png"),
        "Elmo de Bronze Comum":                 ("oi",  "Item__45.png"),
        "Elmo de Ferro Polido":                 ("oi",  "Item__46.png"),
        "Elmo de Placas Lendário":              ("oi",  "Item__47.png"),
        "Coroa de Ouro do Rei Caído":           ("oi2", "Item_47.png"),
        # ── Tronco ──────────────────────────────────────────────────────
        "Gibão de Couro Gasto":                 ("oi",  "Item__56.png"),
        "Túnica de Linho Simples":              ("oi",  "Item__56.png"),
        "Cota de Malha de Ferro":               ("oi",  "Item__57.png"),
        "Peitoral de Aço Escovado":             ("oi",  "Item__58.png"),
        "Armadura de Égide Celeste":            ("oi",  "Item__59.png"),
        "Couraça de Escamas de Dragão":         ("oi",  "Item__59.png"),
        # ── Pernas ──────────────────────────────────────────────────────
        "Calças de Pano Remendadas":            ("oi",  "Item__48.png"),
        "Perneiras de Couro Macio":             ("oi",  "Item__48.png"),
        "Perneiras de Ferro Batido":            ("oi",  "Item__49.png"),
        "Grevas de Bronze Pesadas":             ("oi",  "Item__51.png"),
        "Grevas de Aço do Paladino":            ("oi",  "Item__50.png"),
        "Perneiras de Titânio Rúnico":          ("oi",  "Item__50.png"),
        # ── Pés ─────────────────────────────────────────────────────────
        "Sandálias Desgastadas":                ("oi",  "Item__48.png"),
        "Botas de Couro Rústicas":              ("oi",  "Item__48.png"),
        "Botas de Ferro Pesadas":               ("oi",  "Item__49.png"),
        "Botas Reforçadas de Caçador":          ("oi",  "Item__51.png"),
        "Botas Aladas de Hermes":               ("oi",  "Item__50.png"),
        "Passos Leves do Andarilho do Vento":   ("oi",  "Item__50.png"),
        # ── Mão Direita (armas) ──────────────────────────────────────────
        "Adaga de Cobre Enferrujada":           ("oi",  "Item__02.png"),
        "Espada de Treino de Madeira":          ("oi2", "Item_04.png"),
        "Espada Curta de Aço":                  ("oi",  "Item__00.png"),
        "Machado de Batalha de Ferro":          ("oi",  "Item__13.png"),
        "Lâmina Mítica Excalibur":              ("oi",  "Item__07.png"),
        "Espada Larga Matadora de Dragões":     ("oi",  "Item__05.png"),
        # ── Mão Esquerda (escudos/grimórios) ────────────────────────────
        "Broquel de Madeira Rachado":           ("oi",  "Item__24.png"),
        "Grimório do Estudante Rasgado":        ("oi",  "Item__36.png"),
        "Escudo de Ferro Reforçado":            ("oi",  "Item__25.png"),
        "Grimório do Mago Aprendiz":            ("oi",  "Item__37.png"),
        "Escudo Rúnico da Luz Solar":           ("oi",  "Item__27.png"),
        "Códice Sagrado do Arcanista":          ("oi",  "Item__39.png"),
        # ── Dedos (anéis) ───────────────────────────────────────────────
        "Anel de Cobre Velho":                  ("oi",  "Item__40.png"),
        "Anel de Latão Fosco":                  ("oi",  "Item__40.png"),
        "Anel de Prata Polida":                 ("oi",  "Item__41.png"),
        "Anel de Ouro com Selo":                ("oi",  "Item__43.png"),
        "Anel Cósmico do Vazio":                ("oi",  "Item__41.png"),
        "Aliança de Rubi do Dragão Infinito":   ("oi",  "Item__42.png"),
        # ── Consumíveis ─────────────────────────────────────────────────
        "Poção de Cura Menor":                  ("oi",  "Item__28.png"),
        "Poção de Cura Média":                  ("oi",  "Item__28.png"),
        "Poção de Cura Maior":                  ("oi",  "Item__29.png"),
    }

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------
    def inicializar(self, raiz_projeto: str):
        """
        Deve ser chamado UMA VEZ após pygame.init().

        Args:
            raiz_projeto: caminho absoluto para a raiz do projeto RpDesk.
        """
        if self._inicializado:
            return

        self._raiz = raiz_projeto
        self._cache_fontes: dict = {}
        self._cache_imagens: dict = {}

        # Superfície fallback 48x48 para imagens ausentes
        self._img_fallback = pygame.Surface((48, 48), pygame.SRCALPHA)
        self._img_fallback.fill((80, 60, 40, 200))
        pygame.draw.rect(self._img_fallback, (160, 120, 60), (0, 0, 48, 48), 2)

        self._inicializado = True

    # ------------------------------------------------------------------
    # Fontes
    # ------------------------------------------------------------------
    def fonte(self, tamanho: int, estilo: str = "pressstart") -> pygame.font.Font:
        """
        Retorna a fonte pixel art em cache ou a carrega.

        Args:
            tamanho : Tamanho em pontos.
            estilo  : 'pressstart' (títulos) | 'vt323' (corpo de texto)
        """
        chave = (estilo, tamanho)
        if chave in self._cache_fontes:
            return self._cache_fontes[chave]

        nomes_arquivo = {
            "pressstart": "PressStart2P.ttf",
            "vt323":      "VT323.ttf",
        }
        arquivo = nomes_arquivo.get(estilo, "VT323.ttf")
        caminho = os.path.join(self._raiz, "assets", "fontes", arquivo)

        try:
            font = pygame.font.Font(caminho, tamanho)
        except Exception:
            font = pygame.font.SysFont("monospace", tamanho)

        self._cache_fontes[chave] = font
        return font

    # ------------------------------------------------------------------
    # Imagens de itens
    # ------------------------------------------------------------------
    def imagem_item(self, nome_item: str, tamanho: tuple = (48, 48)) -> pygame.Surface:
        """
        Retorna a superfície do item em cache.

        Args:
            nome_item : Nome exato do item (igual ao da FabricaItens).
            tamanho   : (largura, altura) em pixels.

        Returns:
            pygame.Surface pronta para blit ou fallback dourado.
        """
        chave = (nome_item, tamanho)
        if chave in self._cache_imagens:
            return self._cache_imagens[chave]

        pasta_arquivo = self._MAPA_ITENS.get(nome_item)
        surf = None

        if pasta_arquivo:
            pasta, arquivo = pasta_arquivo
            caminho = os.path.join(
                self._raiz, "assets", "sprites", "itens", pasta, arquivo
            )
            try:
                surf = pygame.image.load(caminho).convert_alpha()
                surf = pygame.transform.scale(surf, tamanho)
            except Exception:
                surf = None

        if surf is None:
            surf = pygame.transform.scale(self._img_fallback, tamanho)

        self._cache_imagens[chave] = surf
        return surf

    # ------------------------------------------------------------------
    # Imagem genérica por caminho relativo
    # ------------------------------------------------------------------
    def imagem(self, caminho_relativo: str, tamanho: tuple = None) -> pygame.Surface:
        """
        Carrega qualquer imagem pelo caminho relativo à raiz do projeto.

        Args:
            caminho_relativo : ex. 'assets/fundos/taverna.png'
            tamanho          : (w, h) opcional para redimensionar.

        Returns:
            pygame.Surface ou fallback em caso de erro.
        """
        chave = (caminho_relativo, tamanho)
        if chave in self._cache_imagens:
            return self._cache_imagens[chave]

        caminho = os.path.join(self._raiz, caminho_relativo)
        try:
            surf = pygame.image.load(caminho).convert_alpha()
            if tamanho:
                surf = pygame.transform.scale(surf, tamanho)
        except Exception:
            surf = pygame.transform.scale(self._img_fallback, tamanho or (64, 64))

        self._cache_imagens[chave] = surf
        return surf
