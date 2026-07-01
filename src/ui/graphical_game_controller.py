"""
graphical_game_controller.py
----------------------------
Subclasse gráfica de GameController.

Substitui o loop de terminal pelo loop de eventos do Pygame.
Implementa a renderização em Tela Virtual com Letterbox para responsividade
total: a janela pode ser redimensionada livremente e os botões continuam
funcionando porque as coordenadas do mouse são traduzidas pelo GerenciadorTelas.

POO aplicado:
  - Herança / LSP  : Estende GameController, preservando o construtor original.
  - Abstração      : Gerencia a inicialização do Pygame de forma transparente.
  - Encapsulamento : Estado do canvas e letterbox é privado ao controlador.
"""

import os
import pygame
from core.game_controller import GameController
from ui.asset_manager import AssetManager
from ui.gerenciador_telas import GerenciadorTelas
from ui.tela_inicial import TelaInicial
from ui.tela_guilda import TelaGuilda
from ui.tela_gameover import TelaGameOver
from core.time_manager import GerenciadorDeTempo


class GraphicalGameController(GameController):
    """
    Controlador gráfico principal do jogo.

    Adapta a inicialização e o loop do terminal para o Pygame.
    """

    # Resolução do canvas virtual (imutável – todo o jogo é desenhado aqui)
    LARGURA_LOGICA = 1280
    ALTURA_LOGICA  = 720

    def __init__(self, event_mngr, save_mngr, fbrc_itens, fbrc_herois,
                 fbrc_inimigos, campanha, rodando):
        super().__init__(
            event_mngr=event_mngr,
            save_mngr=save_mngr,
            fbrc_itens=fbrc_itens,
            fbrc_herois=fbrc_herois,
            fbrc_inimigos=fbrc_inimigos,
            campanha=campanha,
            rodando=rodando
        )
        self.__gerenciador = None
        self.__janela      = None
        self.__canvas      = None
        self.__clock       = None
        self.forcar_fade_fim_dia = False
        self.fade_motivo = ""

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------
    def inicializar(self):
        """Inicializa o Pygame, o canvas virtual e a Tela de Entrada."""
        pygame.init()
        pygame.display.set_caption("RpDesk - Gerenciador de Guilda")

        # Janela real: começa no tamanho lógico, pode ser redimensionada
        self.__janela = pygame.display.set_mode(
            (self.LARGURA_LOGICA, self.ALTURA_LOGICA),
            pygame.RESIZABLE
        )
        # Canvas virtual fixo: sempre 800x480
        self.__canvas = pygame.Surface((self.LARGURA_LOGICA, self.ALTURA_LOGICA))
        self.__clock  = pygame.time.Clock()

        # Inicializa o AssetManager com o caminho raiz do projeto
        raiz = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        AssetManager().inicializar(raiz)

        # Cria o gerenciador de telas (passa a resolução lógica)
        self.__gerenciador = GerenciadorTelas(
            self.LARGURA_LOGICA, self.ALTURA_LOGICA
        )

        # Verifica se existe save no disco
        save_mngr  = self._GameController__save_manager
        dict_save  = save_mngr.carregar_save()
        tem_save   = dict_save is not None

        # Tela de entrada visual (substitui o prompt de terminal)
        tela_inicial = TelaInicial(
            gerenciador=self.__gerenciador,
            tem_save=tem_save,
            cb_carregar=lambda: self.__carregar_e_ir_hub(dict_save),
            cb_novo=lambda: self.__novo_jogo_e_ir_hub(),
        )
        self.__gerenciador.trocar(tela_inicial)

    # ------------------------------------------------------------------
    # Callbacks da tela inicial → transição para o Hub
    # ------------------------------------------------------------------
    def __carregar_e_ir_hub(self, dict_save):
        """Carrega o save e vai para a TelaGuilda."""
        self._GameController__carregar_save(dict_save)
        self.__ir_hub()

    def __novo_jogo_e_ir_hub(self):
        """Gera um mundo do zero e vai para a TelaGuilda."""
        self._GameController__gerar_mundo_zero()
        self.__ir_hub()

    def __ir_hub(self):
        """Troca para a tela principal da guilda."""
        game_state = self._GameController__game_state
        tela_hub   = TelaGuilda(self.__gerenciador, game_state, self)
        self.__gerenciador.trocar(tela_hub)

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    def executar_loop(self):
        """
        Loop principal com renderização direta nativa de alta definição.
        """
        self.__gerenciador.executar(
            janela   = self.__janela,
            clock    = self.__clock,
            fps_alvo = 60,
        )
        pygame.quit()

    # ------------------------------------------------------------------
    # Operações de Lógica de Jogo expostas para as Telas
    # ------------------------------------------------------------------
    def executar_fim_dia(self, cobrar_taxa: bool = True):
        """Executa a cobrança de manutenção da guilda e avança o dia."""
        game_state = self._GameController__game_state
        guilda     = game_state.guilda

        if cobrar_taxa:
            if guilda.ouro >= 10:
                guilda.ouro -= 10
            else:
                guilda.ouro = 0

        time_manager = self._GameController__time_manager
        time_manager.avancar_dia()

        # Cura todos os heróis em 20% do seu HP Máximo
        for heroi in guilda.roster_herois:
            if heroi._vivo:
                cura_val = int(heroi.atributos.valor_hp_max * 0.2)
                heroi.curar(cura_val)

        # Checa game over após a passagem do dia
        self.verificar_game_over()

    def salvar_jogo(self):
        """Salva o estado atual do jogo."""
        save_mngr  = self._GameController__save_manager
        game_state = self._GameController__game_state
        save_mngr.salvar_estado(game_state)

    def voltar_ao_menu_principal(self):
        """Limpa o gerenciador e volta à tela inicial do jogo."""
        save_mngr  = self._GameController__save_manager
        dict_save  = save_mngr.carregar_save()
        tem_save   = dict_save is not None

        tela_inicial = TelaInicial(
            gerenciador=self.__gerenciador,
            tem_save=tem_save,
            cb_carregar=lambda: self.__carregar_e_ir_hub(dict_save),
            cb_novo=lambda: self.__novo_jogo_e_ir_hub(),
        )
        self.__gerenciador.trocar(tela_inicial)

    def aplicar_consequencias_missao(self, resultado_expedicao, missao, equipe):
        """
        Aplica as recompensas, XP, mortes e avanço de campanha pós-expedição.
        """
        guilda = self._GameController__game_state.guilda
        resultado = resultado_expedicao['resultado']
        herois_mortos = resultado_expedicao.get('herois_mortos', [])

        if resultado == 'derrota':
            # Remove a equipe inteira
            if equipe in guilda.equipes_ativas:
                guilda.equipes_ativas.remove(equipe)
        else:
            # Vitória: aplica recompensas
            ouro_total  = resultado_expedicao.get('ouro_total', 0)
            xp_total    = resultado_expedicao.get('xp_total', 0)
            reputacao   = resultado_expedicao.get('reputacao_ganha', 0)

            guilda.ouro      += ouro_total
            guilda.reputacao += reputacao

            # Transfere itens saqueados e recuperados para o baú
            for item in resultado_expedicao.get('itens_saqueados', []):
                guilda.inventario_guilda.adicionar_item(item)
            for item in resultado_expedicao.get('itens_recuperados', []):
                guilda.inventario_guilda.adicionar_item(item)

            # Distribui XP aos sobreviventes
            sobreviventes = resultado_expedicao.get('herois_sobreviventes', [])
            for heroi in sobreviventes:
                heroi.ganhar_xp(xp_total)

            # Remove heróis mortos de suas equipes
            for heroi_morto in herois_mortos:
                for eq in guilda.equipes_ativas:
                    if heroi_morto in eq.membros:
                        eq.membros.remove(heroi_morto)
                        break

            # Marca a missão como concluída
            self._GameController__game_state.registrar_missao_concluida(missao.nome)

            # Avança o dia automaticamente e sem descontar ouro de manutenção
            self.executar_fim_dia(cobrar_taxa=False)
            self.forcar_fade_fim_dia = True
            self.fade_motivo = "expedicao"

        # Checa game over após aplicar as consequências da batalha
        self.verificar_game_over()

    def verificar_game_over(self) -> bool:
        """Verifica se as condições de falência da guilda foram atingidas."""
        game_state = self._GameController__game_state
        guilda     = game_state.guilda
        total_herois = len(guilda.roster_herois) + sum(len(eq.membros) for eq in guilda.equipes_ativas)

        if total_herois == 0 and guilda.ouro < 50:
            tela_gameover = TelaGameOver(self.__gerenciador, game_state, self)
            self.__gerenciador.trocar(tela_gameover)
            return True
        return False

