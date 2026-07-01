"""
tela_batalha.py
---------------
Tela de Expedição / Batalha (Fase 4.1).

Permite:
  - Selecionar uma equipe ativa da guilda.
  - Exibir e selecionar entre as 3 missões procedurais do dia.
  - Rodar e simular o combate encontro por encontro de forma interativa.
  - Exibir os encontros narrativos de escolha e esperar o input do jogador.
  - Exibir o resultado das escolhas em uma fase de resultado dedicada antes do combate.
  - Turnos de combate animados na Arena e logs estruturados no papiro.
  - Resumo final da expedição e aplicação de recompensas/consequências.
"""

import time
import pygame
import random
from ui.tela_base import TelaBase
from ui.componentes.botao import Botao
from ui.componentes.painel_hud import PainelHud
from motor.motor_combater import MotorDeCombate
from gestao.encontro_combate import EncontroCombate
from gestao.encontro_texto import EncontroTexto


class TelaBatalha(TelaBase):
    """Tela que executa e ilustra a batalha e expedição procedural."""

    def __init__(self, gerenciador, game_state, controller):
        super().__init__(gerenciador, game_state)
        self.__controller = controller
        self.__hud = PainelHud(gerenciador.largura)

        # Botão Voltar (inicialmente visível para cancelar)
        self.__btn_voltar = Botao(
            pygame.Rect(50, 640, 180, 40),
            "Cancelar",
            callback=self.__voltar,
            tamanho_fonte=16
        )
        self.__btn_voltar.vincular_gerenciador(gerenciador)

        # Botão Partir
        self.__btn_partir = Botao(
            pygame.Rect(970, 640, 260, 40),
            "Iniciar Expedição",
            callback=self.__confirmar_partida,
            tamanho_fonte=16
        )
        self.__btn_partir.vincular_gerenciador(gerenciador)

        # Botão Pular Animação
        self.__btn_avancar = Botao(
            pygame.Rect(970, 640, 260, 40),
            "Avançar (Pular)",
            callback=self.__pular_logs,
            tamanho_fonte=16
        )
        self.__btn_avancar.vincular_gerenciador(gerenciador)

        # Botão Fechar Resumo Final
        self.__btn_fechar_resumo = Botao(
            pygame.Rect(540, 545, 200, 40),
            "Fechar Resumo",
            callback=self.__finalizar_e_sair,
            tamanho_fonte=16
        )
        self.__btn_fechar_resumo.vincular_gerenciador(gerenciador)

        # Estado de fluxo
        self.__fase_tela = "selecao"  # selecao | animacao | escolha | resultado_texto | resumo
        self.__idx_equipe_selecionada = 0
        self.__idx_missao_selecionada = 0
        self.__resultado_expedicao = None

        # Dados de fluxo encontro por encontro (Roguelike)
        self.__encontro_atual_idx = 0
        self.__membros_atuais = []
        self.__todos_mortos = []
        self.__todos_saqueados = []
        self.__todos_recuperados = []
        self.__todos_perdidos = []
        self.__xp_total_acumulado = 0
        self.__ouro_total_acumulado = 0
        self.__rep_total_acumulada = 0
        self.__missao_corrente = None
        self.__equipe_corrente = None
        
        self.__encontro_em_escolha = None  # EncontroTexto ativo
        self.__botoes_escolha = []

        # Novo: Variáveis de resultado do encontro texto
        self.__narrativa_resultado = ""
        self.__consequencias_texto = []
        self.__btn_avancar_evento = None

        # Dados da animação e log de combate
        self.__fila_logs = []
        self.__logs_visiveis = []
        self.__idx_log_atual = 0
        self.__tempo_proximo_log = 0.0
        self.__duracao_log = 1.3  # Tempo de exibição de cada linha

        # Estado da arena (para barras de vida)
        self.__aliados_arena = []   # { nome, hp_atual, hp_max, tremer, time_tremer }
        self.__inimigos_arena = []  # { nome, hp_atual, hp_max, tremer, time_tremer }
        self.__inimigos_hp_max_real = {}

        # Erros
        self.__status_mensagem = ""
        self.__status_timer = 0.0

    def ao_entrar(self):
        self.__fase_tela = "selecao"
        self.__idx_equipe_selecionada = 0
        self.__idx_missao_selecionada = 0
        self.__resultado_expedicao = None
        self.__fila_logs.clear()
        self.__logs_visiveis.clear()
        self.__idx_log_atual = 0
        self.__aliados_arena.clear()
        self.__inimigos_arena.clear()
        self.__encontro_em_escolha = None
        self.__botoes_escolha.clear()
        self.__btn_avancar_evento = None
        self.__atualizar_estado_botoes()

    def __atualizar_estado_botoes(self):
        guilda = self._game_state.guilda
        tem_equipes = len(guilda.equipes_ativas) > 0
        campanha = self._game_state.campanha
        tem_missao = len(campanha) > 0

        equipe_valida = False
        if tem_equipes and self.__idx_equipe_selecionada < len(guilda.equipes_ativas):
            equipe = guilda.equipes_ativas[self.__idx_equipe_selecionada]
            if len([m for m in equipe.membros if m._vivo]) > 0:
                equipe_valida = True

        self.__btn_partir.ativo = (tem_equipes and tem_missao and equipe_valida)

    def __voltar(self):
        self._gerenciador.pop()

    def __confirmar_partida(self):
        guilda = self._game_state.guilda
        equipes = guilda.equipes_ativas
        campanha = self._game_state.campanha

        if not equipes:
            self.__mostrar_mensagem("Nenhuma equipe ativa para expedição!", "erro")
            return

        if not campanha:
            self.__mostrar_mensagem("Nenhuma missão disponível!", "erro")
            return

        # Inicializa o estado Roguelike encontro por encontro
        self.__equipe_corrente = equipes[self.__idx_equipe_selecionada]
        self.__missao_corrente = campanha[self.__idx_missao_selecionada]

        # Vincula a missão ativa no core
        self._game_state.missao_ativa = self.__missao_corrente

        # Conclui tutorial guiado
        if self._game_state.tutorial_passo == 5:
            self._game_state.tutorial_passo = 0

        self.__encontro_atual_idx = 0
        self.__membros_atuais = list(self.__equipe_corrente.membros)
        self.__todos_mortos.clear()
        self.__todos_saqueados.clear()
        self.__todos_recuperados.clear()
        self.__todos_perdidos.clear()
        self.__xp_total_acumulado = 0
        self.__ouro_total_acumulado = 0
        self.__rep_total_acumulada = 0

        self.__aliados_arena.clear()
        self.__inimigos_arena.clear()
        self.__logs_visiveis.clear()
        self.__fila_logs.clear()

        # Adiciona aliados iniciais com HP real inicial
        for m in self.__membros_atuais:
            if m._vivo:
                self.__aliados_arena.append({
                    "nome": self.formatar_nome_heroi(m.nome),
                    "hp_atual": m.atributos.valor_hp_atual,
                    "hp_max": m.atributos.valor_hp_max,
                    "tremer": False,
                    "time_tremer": 0.0
                })

        # Inicia a execução do primeiro encontro
        self.__iniciar_encontro_atual()

    def __iniciar_encontro_atual(self):
        self.__fila_logs.clear()
        self.__idx_log_atual = 0
        self.__tempo_proximo_log = 0.5
        self.__encontro_em_escolha = None

        encontro = self.__missao_corrente.encontros[self.__encontro_atual_idx]

        if isinstance(encontro, EncontroCombate):
            self.__fase_tela = "animacao"

            em = self._game_state._GameState__event_manager if hasattr(self._game_state, "_GameState__event_manager") else self.__controller._GameController__event_manager
            self.__inimigos_hp_max_real.clear()

            # Listeners locais para logs estruturados deste combate
            def _cb_encontro_iniciado(tipo, **dados):
                if tipo == 'combate':
                    inimigos_str = ', '.join(dados.get('inimigos', []))
                    self.__fila_logs.append({
                        "texto": f"Combate iniciado! Inimigos na arena: {inimigos_str}",
                        "efeito": None,
                        "cor": (140, 95, 30)  # Dourado/Marrom
                    })

            def _cb_combate_iniciado(herois, inimigos, **_):
                self.__inimigos_arena.clear()
                for ini in inimigos:
                    nome_ini = ini if isinstance(ini, str) else getattr(ini, "nome", "Monstro")
                    self.__inimigos_arena.append({
                        "nome": nome_ini,
                        "hp_atual": 50,
                        "hp_max": 50,
                        "tremer": False,
                        "time_tremer": 0.0
                    })

            def _cb_acao_executada(origem, acao, alvo, detalhes, **_):
                eh_aliado = False
                for m in self.__membros_atuais:
                    if origem.upper() in m.nome.upper() or m.nome.upper() in origem.upper():
                        eh_aliado = True
                        break
                
                # Aliado = Verde Escuro, Inimigo = Vermelho
                cor_entidade = (40, 130, 40) if eh_aliado else (190, 45, 45)

                if acao == 'atacar':
                    dano = detalhes.get('dano_causado', 0)
                    self.__fila_logs.append({
                        "texto": f"{origem} atacou {alvo} causando {dano} de dano!",
                        "efeito": ("dano", alvo, dano),
                        "cor": cor_entidade
                    })
                elif acao == 'curar':
                    item = detalhes.get('item_usado', 'Poção')
                    self.__fila_logs.append({
                        "texto": f"{origem} usou {item} em {alvo}!",
                        "efeito": ("curar", alvo, 20),
                        "cor": (40, 130, 40)  # Verde
                    })

            def _cb_morrer(nome_morto, **_):
                self.__fila_logs.append({
                    "texto": f"💀 {nome_morto} morreu em combate!",
                    "efeito": ("morrer", nome_morto, None),
                    "cor": (140, 30, 30)  # Vermelho Escuro / Morte
                })

            def _cb_rodada_finalizada(herois, inimigos, **_):
                herois_sync = []
                for h in herois:
                    nome_h = h if isinstance(h, str) else (h.get("nome", "") if isinstance(h, dict) else getattr(h, "nome", ""))
                    hp_a = h.get("hp_atual", 0) if isinstance(h, dict) else getattr(h, "hp_atual", 0)
                    hp_m = h.get("hp_max", 1) if isinstance(h, dict) else getattr(h, "hp_max", 1)
                    herois_sync.append({"nome": nome_h, "hp_atual": hp_a, "hp_max": hp_m})

                inimigos_sync = []
                for i in inimigos:
                    nome_i = i if isinstance(i, str) else (i.get("nome", "") if isinstance(i, dict) else getattr(i, "nome", ""))
                    hp_a = i.get("hp_atual", 0) if isinstance(i, dict) else getattr(i, "hp_atual", 0)
                    hp_m = i.get("hp_max", 1) if isinstance(i, dict) else getattr(i, "hp_max", 1)
                    inimigos_sync.append({"nome": nome_i, "hp_atual": hp_a, "hp_max": hp_m})
                    self.__inimigos_hp_max_real[nome_i] = hp_m

                self.__fila_logs.append({
                    "texto": "--- Fim da Rodada ---",
                    "efeito": ("sync", herois_sync, inimigos_sync),
                    "cor": (100, 95, 90)  # Cinza neutro
                })

            def _cb_combate_finalizado(resultado, xp_acumulado, **_):
                status = "Vitória" if resultado == "vitoria" else "Derrota"
                cor = (40, 130, 40) if resultado == "vitoria" else (190, 45, 45)
                self.__fila_logs.append({
                    "texto": f"Fim de Combate: {status}! (+{xp_acumulado} XP)",
                    "efeito": None,
                    "cor": cor
                })

            # Inscreve listeners
            em.inscrever('encontro_iniciado',         _cb_encontro_iniciado)
            em.inscrever('combate_iniciado',          _cb_combate_iniciado)
            em.inscrever('acao_executada',            _cb_acao_executada)
            em.inscrever('morrer',                    _cb_morrer)
            em.inscrever('rodada_finalizada',         _cb_rodada_finalizada)
            em.inscrever('combate_finalizado',        _cb_combate_finalizado)

            # Executa
            motor_combate = MotorDeCombate(em)
            resultado_combate = encontro.executar(self.__membros_atuais, motor_combate, em)

            # Acumuladores
            self.__membros_atuais = resultado_combate['herois_vivos']
            self.__todos_mortos.extend(resultado_combate['herois_mortos'])
            self.__todos_saqueados.extend(resultado_combate['itens_saqueados'])
            self.__todos_recuperados.extend(resultado_combate['itens_recuperados'])
            self.__todos_perdidos.extend(resultado_combate['itens_perdidos'])
            self.__xp_total_acumulado += resultado_combate['xp_ganho']
            self.__ouro_total_acumulado += resultado_combate['ouro_ganho']

            # Corrige HP inimigos com dados pós-combate
            for ini in self.__inimigos_arena:
                hp_m = self.__inimigos_hp_max_real.get(ini["nome"], 50)
                ini["hp_max"] = hp_m
                ini["hp_atual"] = hp_m

            # Desinscreve
            em.desinscrever('encontro_iniciado',        _cb_encontro_iniciado)
            em.desinscrever('combate_iniciado',         _cb_combate_iniciado)
            em.desinscrever('acao_executada',           _cb_acao_executada)
            em.desinscrever('morrer',                   _cb_morrer)
            em.desinscrever('rodada_finalizada',        _cb_rodada_finalizada)
            em.desinscrever('combate_finalizado',       _cb_combate_finalizado)

        elif isinstance(encontro, EncontroTexto):
            opcoes = encontro.efeitos.get("opcoes", [])
            if opcoes:
                # Encontro de escolha (Fase Interativa)
                self.__encontro_em_escolha = encontro
                self.__fase_tela = "escolha"

                # Cria botões das opções centralizados no pergaminho (cx = 830)
                self.__botoes_escolha.clear()
                cx = 830
                largura_b = 740
                altura_b = 42

                for idx_op, opcao in enumerate(opcoes):
                    y_pos = 350 + idx_op * 52
                    rect_op = pygame.Rect(cx - largura_b // 2, y_pos, largura_b, altura_b)
                    
                    btn = Botao(
                        rect_op,
                        opcao["texto"],
                        callback=lambda op=opcao: self.__selecionar_opcao_encontro(op),
                        tamanho_fonte=16
                    )
                    btn.vincular_gerenciador(self._gerenciador)
                    self.__botoes_escolha.append(btn)
            else:
                # Encontro clássico automático (sem escolhas)
                self.__fase_tela = "animacao"

                em = self._game_state._GameState__event_manager if hasattr(self._game_state, "_GameState__event_manager") else self.__controller._GameController__event_manager
                resultado_texto = encontro.executar(self.__membros_atuais, None, em)

                self.__membros_atuais = resultado_texto['herois_vivos']
                self.__todos_mortos.extend(resultado_texto['herois_mortos'])
                self.__ouro_total_acumulado += resultado_texto['ouro_ganho']

                # Cria log automático simples
                self.__fila_logs.append({
                    "texto": f"Evento: {encontro.narrativa}",
                    "efeito": None,
                    "cor": (50, 100, 150)  # Azul
                })
                dano_hp = encontro.efeitos.get("dano_hp", 0)
                if dano_hp > 0:
                    self.__fila_logs.append({
                        "texto": f"A equipe sofreu {dano_hp} de dano por armadilha!",
                        "efeito": ("dano_equipe", None, dano_hp),
                        "cor": (190, 45, 45)
                    })
                cura_hp = encontro.efeitos.get("cura_hp", 0)
                if cura_hp > 0:
                    self.__fila_logs.append({
                        "texto": f"A equipe recuperou {cura_hp} HP com suprimentos!",
                        "efeito": ("cura_equipe", None, cura_hp),
                        "cor": (40, 130, 40)
                    })

    def __selecionar_opcao_encontro(self, opcao):
        # Transiciona para o resultado exibido na mesma tela
        self.__narrativa_resultado = opcao["narrativa_resultado"]
        
        # Processamento de efeitos
        efeitos = opcao.get("efeitos", {})
        ouro_ganho = efeitos.get("ouro", 0)
        ouro_custo = efeitos.get("ouro_custo", 0)
        dano_hp = efeitos.get("dano_hp", 0)
        cura_hp = efeitos.get("cura_hp", 0)

        self.__ouro_total_acumulado += (ouro_ganho + ouro_custo)
        
        self.__consequencias_texto = []
        if (ouro_ganho + ouro_custo) != 0:
            sinal = "+" if (ouro_ganho + ouro_custo) > 0 else ""
            self.__consequencias_texto.append(f"Ouro da Guilda: {sinal}{ouro_ganho + ouro_custo}g")

        # Aplica dano a todos os membros vivos
        if dano_hp > 0:
            self.__consequencias_texto.append(f"Todos os herois sofreram {dano_hp} de dano!")
            for h in self.__membros_atuais:
                if h._vivo:
                    h.receber_dano(dano_hp, fonte="evento")

        # Aplica cura a todos os membros vivos
        if cura_hp > 0:
            self.__consequencias_texto.append(f"Todos os herois curaram {cura_hp} HP!")
            for h in self.__membros_atuais:
                if h._vivo:
                    h.curar(cura_hp)

        # Sincroniza HP na arena de aliados
        for al in self.__aliados_arena:
            for h in self.__membros_atuais:
                if al["nome"].upper() in h.nome.upper():
                    al["hp_atual"] = h.atributos.valor_hp_atual
                    al["hp_max"] = h.atributos.valor_hp_max

        # Processa mortes por consequência do evento
        mortos_evento = []
        for h in self.__membros_atuais:
            if not h._vivo:
                mortos_evento.append(h)
                self.__consequencias_texto.append(f"💀 {self.formatar_nome_heroi(h.nome)} sucumbiu aos ferimentos do evento!")

        self.__membros_atuais = [h for h in self.__membros_atuais if h._vivo]
        self.__todos_mortos.extend(mortos_evento)

        # Atualiza a fase da tela para resultado narrativo
        self.__fase_tela = "resultado_texto"

        # Criar botão para "Avançar"
        cx = 830
        largura_b = 300
        altura_b = 42
        self.__btn_avancar_evento = Botao(
            pygame.Rect(cx - largura_b // 2, 480, largura_b, altura_b),
            "Avançar Expedição",
            callback=self.__concluir_resultado_texto,
            tamanho_fonte=16
        )
        self.__btn_avancar_evento.vincular_gerenciador(self._gerenciador)

    def __concluir_resultado_texto(self):
        # Avança de encontro ou finaliza
        self.__checar_avanco_encontro()

    def __finalizar_expedicao_completa(self, resultado):
        self.__fase_tela = "resumo"

        if resultado == "vitoria":
            self.__ouro_total_acumulado += self.__missao_corrente.recompensa_ouro
            self.__xp_total_acumulado += self.__missao_corrente.recompensa_xp
            self.__rep_total_acumulada = self.__missao_corrente.recompensa_reputacao
        else:
            # Em caso de derrota, a guilda não obtém nenhuma recompensa (ouro e rep zerados)
            self.__ouro_total_acumulado = 0
            self.__rep_total_acumulada = 0

        self.__resultado_expedicao = {
            'resultado': resultado,
            'herois_sobreviventes': self.__membros_atuais,
            'herois_mortos': self.__todos_mortos,
            'itens_saqueados': self.__todos_saqueados,
            'itens_recuperados': self.__todos_recuperados,
            'itens_perdidos': self.__todos_perdidos,
            'xp_total': self.__xp_total_acumulado,
            'ouro_total': self.__ouro_total_acumulado,
            'reputacao_ganha': self.__rep_total_acumulada,
        }

    def __pular_logs(self):
        # Conclui papiro e aplica todos os efeitos visuais instantaneamente
        fonte_log = self.obter_fonte(26, "vt323")
        largura_max = self.obter_x(1100)
        while self.__idx_log_atual < len(self.__fila_logs):
            log_item = self.__fila_logs[self.__idx_log_atual]
            cor = log_item.get("cor", (30, 25, 20))
            texto_quebrado = self.__quebrar_linha_log(log_item["texto"], largura_max, fonte_log)
            for l in texto_quebrado:
                self.__logs_visiveis.append((l, cor))
            if log_item["efeito"]:
                self.__aplicar_efeito_combate(log_item["efeito"])
            self.__idx_log_atual += 1
        
        # Avança de encontro ou finaliza
        self.__checar_avanco_encontro()

    def __checar_avanco_encontro(self):
        if not self.__membros_atuais:
            self.__finalizar_expedicao_completa(resultado="derrota")
        elif self.__encontro_atual_idx < len(self.__missao_corrente.encontros) - 1:
            self.__encontro_atual_idx += 1
            self.__iniciar_encontro_atual()
        else:
            self.__finalizar_expedicao_completa(resultado="vitoria")

    def __finalizar_e_sair(self):
        guilda = self._game_state.guilda
        equipe = guilda.equipes_ativas[self.__idx_equipe_selecionada]
        missao = self.__missao_corrente

        if self.__controller and hasattr(self.__controller, "aplicar_consequencias_missao"):
            self.__controller.aplicar_consequencias_missao(self.__resultado_expedicao, missao, equipe)

        self._gerenciador.pop()

    def __mostrar_mensagem(self, texto, cor_tipo="ouro"):
        self.__status_mensagem = texto
        self.__status_timer = 3.0

    def __checar_selecao_missao(self, mouse_pos):
        campanha = self._game_state.campanha
        for i in range(min(3, len(campanha))):
            x_aba = 600 + i * 210
            rect_aba = self.obter_rect(x_aba, 120, 200, 40)
            if rect_aba.collidepoint(mouse_pos):
                self.__idx_missao_selecionada = i
                self.__atualizar_estado_botoes()
                break

    def __checar_selecao_equipe(self, mouse_pos):
        guilda = self._game_state.guilda
        for idx, eq in enumerate(guilda.equipes_ativas):
            y_pos = 160 + idx * 90
            rect_lin = self.obter_rect(60, y_pos, 480, 78)
            if rect_lin.collidepoint(mouse_pos):
                self.__idx_equipe_selecionada = idx
                self.__atualizar_estado_botoes()
                break

    def formatar_nome_heroi(self, nome: str) -> str:
        return nome.split()[0] if nome else "Guerreiro"

    def __aplicar_efeito_combate(self, e):
        tipo, alvo, valor = e
        if tipo == "dano":
            self.__aplicar_dano_arena(alvo, valor)
        elif tipo == "curar":
            self.__aplicar_cura_arena(alvo, valor)
        elif tipo == "morrer":
            self.__matar_entidade_arena(alvo)
        elif tipo == "dano_equipe":
            if self.__aliados_arena:
                d_membro = valor // len(self.__aliados_arena)
                for al in self.__aliados_arena:
                    self.__aplicar_dano_arena(al["nome"], d_membro)
        elif tipo == "cura_equipe":
            for al in self.__aliados_arena:
                al["hp_atual"] = min(al["hp_max"], al["hp_atual"] + valor)
        elif tipo == "sync":
            for h in alvo:
                for al in self.__aliados_arena:
                    if al["nome"].upper() in h["nome"].upper() or h["nome"].upper() in al["nome"].upper():
                        al["hp_atual"] = h["hp_atual"]
                        al["hp_max"] = h["hp_max"]
            for i in valor:
                for ini in self.__inimigos_arena:
                    if ini["nome"].upper() in i["nome"].upper() or i["nome"].upper() in ini["nome"].upper():
                        ini["hp_atual"] = i["hp_atual"]
                        ini["hp_max"] = i["hp_max"]

    def __aplicar_dano_arena(self, nome, dano):
        for ini in self.__inimigos_arena:
            if ini["nome"].upper() in nome.upper() or nome.upper() in ini["nome"].upper():
                ini["hp_atual"] = max(0, ini["hp_atual"] - dano)
                ini["tremer"] = True
                ini["time_tremer"] = 0.3
                return
        for al in self.__aliados_arena:
            if al["nome"].upper() in nome.upper() or nome.upper() in al["nome"].upper():
                al["hp_atual"] = max(0, al["hp_atual"] - dano)
                al["tremer"] = True
                al["time_tremer"] = 0.3
                return

    def __aplicar_cura_arena(self, nome, cura):
        for al in self.__aliados_arena:
            if al["nome"].upper() in nome.upper() or nome.upper() in al["nome"].upper():
                al["hp_atual"] = min(al["hp_max"], al["hp_atual"] + cura)
                return
        for ini in self.__inimigos_arena:
            if ini["nome"].upper() in nome.upper() or nome.upper() in ini["nome"].upper():
                ini["hp_atual"] = min(ini["hp_max"], ini["hp_atual"] + cura)
                return

    def __matar_entidade_arena(self, nome):
        for ini in self.__inimigos_arena:
            if ini["nome"].upper() in nome.upper() or nome.upper() in ini["nome"].upper():
                ini["hp_atual"] = 0
        for al in self.__aliados_arena:
            if al["nome"].upper() in nome.upper() or nome.upper() in al["nome"].upper():
                al["hp_atual"] = 0

    def __quebrar_linha_log(self, text: str, max_largura_px: int, fonte: pygame.font.Font) -> list:
        palavras = text.split()
        linhas = []
        linha_atual = []
        for pal in palavras:
            teste_linha = " ".join(linha_atual + [pal])
            largura, _ = fonte.size(teste_linha)
            if largura > max_largura_px:
                if linha_atual:
                    linhas.append(" ".join(linha_atual))
                    linha_atual = [pal]
                else:
                    linhas.append(pal)
                    linha_atual = []
            else:
                linha_atual.append(pal)
        if linha_atual:
            linhas.append(" ".join(linha_atual))
        return linhas

    def atualizar(self, dt: float) -> None:
        if self.__status_timer > 0:
            self.__status_timer -= dt

        # Trepidação dos cartões
        for al in self.__aliados_arena:
            if al["tremer"]:
                al["time_tremer"] -= dt
                if al["time_tremer"] <= 0:
                    al["tremer"] = False
        for ini in self.__inimigos_arena:
            if ini["tremer"]:
                ini["time_tremer"] -= dt
                if ini["time_tremer"] <= 0:
                    ini["tremer"] = False

        if self.__fase_tela == "animacao":
            self.__tempo_proximo_log -= dt
            if self.__tempo_proximo_log <= 0:
                if self.__idx_log_atual < len(self.__fila_logs):
                    log_item = self.__fila_logs[self.__idx_log_atual]
                    cor = log_item.get("cor", (30, 25, 20))
                    
                    fonte_log = self.obter_fonte(26, "vt323")
                    largura_max = self.obter_x(1100)
                    texto_quebrado = self.__quebrar_linha_log(log_item["texto"], largura_max, fonte_log)
                    for l in texto_quebrado:
                        self.__logs_visiveis.append((l, cor))

                    if log_item["efeito"]:
                        self.__aplicar_efeito_combate(log_item["efeito"])
                    self.__idx_log_atual += 1
                    self.__tempo_proximo_log = self.__duracao_log
                else:
                    # Encontro atual concluído de forma animada! Checa o avanço
                    self.__checar_avanco_encontro()

    def lidar_eventos(self, eventos: list) -> None:
        for ev in eventos:
            if self.__fase_tela == "selecao":
                self.__btn_voltar.lidar_evento(ev)
                self.__btn_partir.lidar_evento(ev)

                # Clique nas abas e tabelas
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self.__checar_selecao_equipe(ev.pos)
                    self.__checar_selecao_missao(ev.pos)
            elif self.__fase_tela == "animacao":
                self.__btn_avancar.lidar_evento(ev)
            elif self.__fase_tela == "escolha":
                for btn in self.__botoes_escolha:
                    btn.lidar_evento(ev)
            elif self.__fase_tela == "resultado_texto":
                if self.__btn_avancar_evento:
                    self.__btn_avancar_evento.lidar_evento(ev)
            elif self.__fase_tela == "resumo":
                self.__btn_fechar_resumo.lidar_evento(ev)

    def desenhar(self, surface: pygame.Surface) -> None:
        cores = self._assets.CORES
        w = self._gerenciador.largura_real
        h = self._gerenciador.altura_real

        fonte_tit   = self.obter_fonte(16, "pressstart")
        fonte_card  = self.obter_fonte(12, "pressstart")
        fonte_corpo = self.obter_fonte(24, "vt323")
        fonte_peq   = self.obter_fonte(18, "vt323")

        # HUD superior
        self.__hud.desenhar(surface, self._game_state)

        # ── 1. Fase Seleção ────────────────────────────────────────────────
        if self.__fase_tela == "selecao":
            self._renderizar_texto_com_sombra(
                surface, "SELECIONE A EQUIPE E A EXPEDICAO",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(50), self.obter_y(85))
            )

            # Caixa do tutorial flutuante
            if self._game_state and self._game_state.tutorial_passo == 5:
                fonte_tut = self.obter_fonte(22, "vt323")
                rect_tut = self.obter_rect(650, 72, 580, 42)
                self._desenhar_moldura(surface, rect_tut, espessura=2)
                pygame.draw.rect(surface, (235, 215, 185), rect_tut.inflate(-4, -4)) # Papiro amarelo
                
                surf_tut = fonte_tut.render("Selecione a equipe e inicie a expedicao!", True, (40, 25, 10))
                tx = rect_tut.x + (rect_tut.width - surf_tut.get_width()) // 2
                ty = rect_tut.y + (rect_tut.height - surf_tut.get_height()) // 2
                surface.blit(surf_tut, (tx, ty))

            # Lista de Equipes (Esquerda)
            left_panel = self.obter_rect(40, 120, 520, 500)
            self._desenhar_moldura(surface, left_panel, espessura=2)
            pygame.draw.rect(surface, cores["fundo_painel"], left_panel.inflate(-4, -4))

            self._renderizar_texto_com_sombra(
                surface, "Equipes Ativas:",
                fonte_corpo, cores["texto_azul"],
                (self.obter_x(60), self.obter_y(135))
            )

            guilda = self._game_state.guilda
            if not guilda.equipes_ativas:
                self._renderizar_texto_com_sombra(
                    surface, "Nenhuma equipe ativa!",
                    fonte_peq, cores["texto_vermelho"],
                    (self.obter_x(60), self.obter_y(180))
                )
            else:
                for idx, eq in enumerate(guilda.equipes_ativas):
                    y_pos = 160 + idx * 90
                    rect_lin = self.obter_rect(60, y_pos, 480, 78)

                    if self.__idx_equipe_selecionada == idx:
                        pygame.draw.rect(surface, (70, 50, 20), rect_lin, border_radius=4)
                        pygame.draw.rect(surface, cores["borda_ouro"], rect_lin, 2, border_radius=4)
                    else:
                        pygame.draw.rect(surface, (25, 20, 15), rect_lin, border_radius=4)
                        pygame.draw.rect(surface, cores["borda_escura"], rect_lin, 1, border_radius=4)

                    self._renderizar_texto_com_sombra(
                        surface, eq.nome.upper(),
                        fonte_card, cores["texto_ouro"],
                        (self.obter_x(74), self.obter_y(y_pos + 12))
                    )

                    avg_lvl = sum(m.nivel for m in eq.membros) / len(eq.membros) if eq.membros else 0.0
                    hp_total = sum(m.atributos.valor_hp_max for m in eq.membros if m._vivo) if eq.membros else 0
                    info_txt = f"Lvl: {avg_lvl:.1f} | HP: {hp_total}"
                    self._renderizar_texto_com_sombra(
                        surface, info_txt,
                        fonte_peq, cores["texto_creme"],
                        (self.obter_x(340), self.obter_y(y_pos + 12))
                    )

                    nomes = ", ".join([self.formatar_nome_heroi(m.nome) for m in eq.membros]) if eq.membros else "Vazia"
                    if len(nomes) > 40:
                        nomes = nomes[:38] + ".."
                    self._renderizar_texto_com_sombra(
                        surface, nomes,
                        fonte_peq, cores["texto_acinzentado"],
                        (self.obter_x(74), self.obter_y(y_pos + 42))
                    )

            # Abas de Missões (Direita - Meta 1)
            campanha = self._game_state.campanha
            for idx_m in range(min(3, len(campanha))):
                missao_op = campanha[idx_m]
                x_aba = 580 + idx_m * 216
                rect_aba = self.obter_rect(x_aba, 120, 210, 42)

                if self.__idx_missao_selecionada == idx_m:
                    pygame.draw.rect(surface, cores["fundo_painel"], rect_aba, border_radius=4)
                    self._desenhar_moldura(surface, rect_aba, espessura=2)
                    cor_txt_aba = cores["texto_ouro"]
                else:
                    pygame.draw.rect(surface, cores["fundo_principal"], rect_aba, border_radius=4)
                    self._desenhar_moldura(surface, rect_aba, espessura=1)
                    cor_txt_aba = cores["texto_acinzentado"]

                txt_aba = f"Missao {idx_m + 1} (Dif. {missao_op.dificuldade})"
                surf_aba = fonte_peq.render(txt_aba, True, cor_txt_aba)
                tx_aba = rect_aba.x + (rect_aba.width - surf_aba.get_width()) // 2
                ty_aba = rect_aba.y + (rect_aba.height - surf_aba.get_height()) // 2
                surface.blit(surf_aba, (tx_aba, ty_aba))

            # Detalhes da Missão Selecionada
            right_panel = self.obter_rect(580, 172, 660, 448)
            self._desenhar_moldura(surface, right_panel, espessura=2)
            pygame.draw.rect(surface, cores["fundo_painel"], right_panel.inflate(-4, -4))

            if self.__idx_missao_selecionada < len(campanha):
                missao_sel = campanha[self.__idx_missao_selecionada]
                
                self._renderizar_texto_com_sombra(
                    surface, f"EXPEDICAO: {missao_sel.nome}",
                    fonte_corpo, cores["texto_ouro"],
                    (self.obter_x(600), self.obter_y(195))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"Dificuldade: {missao_sel.dificuldade}",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(600), self.obter_y(235))
                )

                self._renderizar_texto_com_sombra(
                    surface, "Recompensas:",
                    fonte_peq, cores["texto_azul"],
                    (self.obter_x(600), self.obter_y(270))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"- Ouro:      +{missao_sel.recompensa_ouro}g",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(620), self.obter_y(295))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"- XP:        +{missao_sel.recompensa_xp} xp",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(620), self.obter_y(320))
                )
                self._renderizar_texto_com_sombra(
                    surface, f"- Reputacao: +{missao_sel.recompensa_reputacao} rep",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(620), self.obter_y(345))
                )

                self._renderizar_texto_com_sombra(
                    surface, "Descricao:",
                    fonte_peq, cores["texto_azul"],
                    (self.obter_x(600), self.obter_y(385))
                )
                desc_palavras = missao_sel.descricao.split()
                linhas_desc = []
                linha_corrente = []
                for p in desc_palavras:
                    if len(" ".join(linha_corrente + [p])) > 55:
                        linhas_desc.append(" ".join(linha_corrente))
                        linha_corrente = [p]
                    else:
                        linha_corrente.append(p)
                if linha_corrente:
                    linhas_desc.append(" ".join(linha_corrente))

                for idx_d, l in enumerate(linhas_desc[:5]):
                    self._renderizar_texto_com_sombra(
                        surface, l,
                        fonte_peq, cores["texto_creme"],
                        (self.obter_x(600), self.obter_y(415 + idx_d * 22))
                    )

            self.__btn_voltar.desenhar(surface)
            self.__btn_partir.desenhar(surface)

        # ── 2. Fase Animação (Papiro e Combate Arena) ────────────────────────
        elif self.__fase_tela == "animacao":
            self._renderizar_texto_com_sombra(
                surface, "SIMULACAO DE EXPEDICAO...",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(50), self.obter_y(85))
            )

            # Arena (HP de Aliados e Inimigos) compactada verticalmente
            arena_panel = self.obter_rect(40, 95, 1200, 150)
            self._desenhar_moldura(surface, arena_panel, espessura=2)
            pygame.draw.rect(surface, (15, 12, 10), arena_panel.inflate(-4, -4))

            # Aliados
            self._renderizar_texto_com_sombra(
                surface, "ALIADOS",
                fonte_card, cores["texto_azul"],
                (self.obter_x(60), self.obter_y(105))
            )
            for idx_a, al in enumerate(self.__aliados_arena):
                shake_x = random.randint(-3, 3) if al["tremer"] else 0
                y_p = 130 + idx_a * 26
                rect_h = self.obter_rect(60 + shake_x, y_p, 330, 22)
                pygame.draw.rect(surface, (35, 25, 20), rect_h, border_radius=4)
                pygame.draw.rect(surface, cores["borda_escura"], rect_h, 1, border_radius=4)

                self._renderizar_texto_com_sombra(
                    surface, al["nome"],
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(70 + shake_x), self.obter_y(y_p + 1))
                )

                hp_ratio = max(0.0, min(1.0, al["hp_atual"] / al["hp_max"]))
                rect_hp_back = self.obter_rect(205 + shake_x, y_p + 4, 100, 12)
                pygame.draw.rect(surface, (50, 15, 15), rect_hp_back, border_radius=2)
                if hp_ratio > 0:
                    rect_hp_front = self.obter_rect(205 + shake_x, y_p + 4, int(100 * hp_ratio), 12)
                    pygame.draw.rect(surface, cores["texto_verde"], rect_hp_front, border_radius=2)

                self._renderizar_texto_com_sombra(
                    surface, f"{int(al['hp_atual'])}/{int(al['hp_max'])}",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(315 + shake_x), self.obter_y(y_p + 1))
                )

            # Inimigos (deslocados para a esquerda para caber com largura ampliada)
            self._renderizar_texto_com_sombra(
                surface, "INIMIGOS DETECTADOS",
                fonte_card, cores["texto_vermelho"],
                (self.obter_x(810), self.obter_y(105))
            )
            for idx_i, ini in enumerate(self.__inimigos_arena):
                shake_x = random.randint(-3, 3) if ini["tremer"] else 0
                y_p = 130 + idx_i * 26
                rect_i = self.obter_rect(810 + shake_x, y_p, 330, 22)
                pygame.draw.rect(surface, (35, 25, 20), rect_i, border_radius=4)
                pygame.draw.rect(surface, cores["borda_escura"], rect_i, 1, border_radius=4)

                self._renderizar_texto_com_sombra(
                    surface, ini["nome"],
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(820 + shake_x), self.obter_y(y_p + 1))
                )

                hp_ratio = max(0.0, min(1.0, ini["hp_atual"] / ini["hp_max"]))
                rect_hp_back = self.obter_rect(955 + shake_x, y_p + 4, 100, 12)
                pygame.draw.rect(surface, (50, 15, 15), rect_hp_back, border_radius=2)
                if hp_ratio > 0:
                    rect_hp_front = self.obter_rect(955 + shake_x, y_p + 4, int(100 * hp_ratio), 12)
                    pygame.draw.rect(surface, cores["texto_vermelho"], rect_hp_front, border_radius=2)

                self._renderizar_texto_com_sombra(
                    surface, f"{int(ini['hp_atual'])}/{int(ini['hp_max'])}",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(1065 + shake_x), self.obter_y(y_p + 1))
                )

            # Pergaminho de Logs Expandido (Altura ampliada)
            papiro_rect = self.obter_rect(40, 255, 1200, 365)
            self._desenhar_moldura(surface, papiro_rect, espessura=3)
            pygame.draw.rect(surface, (235, 215, 185), papiro_rect.inflate(-6, -6))  # Creme papel pergaminho

            # Título do Papiro
            self._renderizar_texto_com_sombra(
                surface, "PAGINAS DO DIARIO DE BATALHA",
                fonte_card, (60, 40, 20),
                (self.obter_x(70), self.obter_y(270)),
                sombra_offset=0
            )

            # Logs Visíveis Coloridos com rolagem dinâmica (últimas 9 linhas)
            linhas_exibir = self.__logs_visiveis[-9:]
            for idx_log, (linha, cor_log) in enumerate(linhas_exibir):
                self._renderizar_texto_com_sombra(
                    surface, f"  {linha}",
                    fonte_corpo, cor_log,
                    (self.obter_x(70), self.obter_y(300 + idx_log * 30)),
                    sombra_offset=0
                )

            self.__btn_avancar.desenhar(surface)

        # ── 3. Fase Escolha Narrativa (Meta 1 - Roguelike) ────────────────
        elif self.__fase_tela == "escolha":
            self._renderizar_texto_com_sombra(
                surface, "EVENTO NARRATIVO",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(50), self.obter_y(85))
            )

            # Arena Esquerda (Aliados)
            aliados_panel = self.obter_rect(40, 120, 360, 200)
            self._desenhar_moldura(surface, aliados_panel, espessura=2)
            pygame.draw.rect(surface, (15, 12, 10), aliados_panel.inflate(-4, -4))
            
            self._renderizar_texto_com_sombra(
                surface, "SUA EQUIPE",
                fonte_card, cores["texto_azul"],
                (self.obter_x(60), self.obter_y(132))
            )
            for idx_a, al in enumerate(self.__aliados_arena):
                y_p = 155 + idx_a * 42
                rect_h = self.obter_rect(60, y_p, 320, 36)
                pygame.draw.rect(surface, (35, 25, 20), rect_h, border_radius=4)
                pygame.draw.rect(surface, cores["borda_escura"], rect_h, 1, border_radius=4)

                self._renderizar_texto_com_sombra(
                    surface, al["nome"],
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(70), self.obter_y(y_p + 8))
                )

                hp_ratio = max(0.0, min(1.0, al["hp_atual"] / al["hp_max"]))
                rect_hp_back = self.obter_rect(170, y_p + 10, 100, 14)
                pygame.draw.rect(surface, (50, 15, 15), rect_hp_back, border_radius=2)
                if hp_ratio > 0:
                    rect_hp_front = self.obter_rect(170, y_p + 10, int(100 * hp_ratio), 14)
                    pygame.draw.rect(surface, cores["texto_verde"], rect_hp_front, border_radius=2)

                self._renderizar_texto_com_sombra(
                    surface, f"{int(al['hp_atual'])}/{int(al['hp_max'])}",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(280), self.obter_y(y_p + 8))
                )

            # Painel do Encontro de Escolha (Direita - Centralizado horizontalmente em cx = 830)
            pergam_rect = self.obter_rect(420, 120, 820, 500)
            self._desenhar_moldura(surface, pergam_rect, espessura=3)
            pygame.draw.rect(surface, (235, 215, 185), pergam_rect.inflate(-6, -6))  # Pergaminho creme

            self._renderizar_texto_com_sombra(
                surface, "UM EVENTO EM SEU CAMINHO...",
                fonte_card, (60, 40, 20),
                (self.obter_x(450), self.obter_y(140)),
                sombra_offset=0
            )

            # Narrativa quebrada
            desc_linhas = self.__quebrar_texto(self.__encontro_em_escolha.narrativa, 60)
            for idx_l, pointer in enumerate(desc_linhas):
                self._renderizar_texto_com_sombra(
                    surface, pointer,
                    fonte_corpo, (30, 25, 20),
                    (self.obter_x(450), self.obter_y(180 + idx_l * 28)),
                    sombra_offset=0
                )

            # Botões de escolha
            for btn in self.__botoes_escolha:
                btn.desenhar(surface)

        # ── 4. Fase Resultado do Evento Narrativo ──────────────────────────
        elif self.__fase_tela == "resultado_texto":
            self._renderizar_texto_com_sombra(
                surface, "CONSEQUENCIA DO EVENTO",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(50), self.obter_y(85))
            )

            # Arena Esquerda (Aliados)
            aliados_panel = self.obter_rect(40, 120, 360, 200)
            self._desenhar_moldura(surface, aliados_panel, espessura=2)
            pygame.draw.rect(surface, (15, 12, 10), aliados_panel.inflate(-4, -4))
            
            self._renderizar_texto_com_sombra(
                surface, "SUA EQUIPE",
                fonte_card, cores["texto_azul"],
                (self.obter_x(60), self.obter_y(132))
            )
            for idx_a, al in enumerate(self.__aliados_arena):
                y_p = 155 + idx_a * 42
                rect_h = self.obter_rect(60, y_p, 320, 36)
                pygame.draw.rect(surface, (35, 25, 20), rect_h, border_radius=4)
                pygame.draw.rect(surface, cores["borda_escura"], rect_h, 1, border_radius=4)

                self._renderizar_texto_com_sombra(
                    surface, al["nome"],
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(70), self.obter_y(y_p + 8))
                )

                hp_ratio = max(0.0, min(1.0, al["hp_atual"] / al["hp_max"]))
                rect_hp_back = self.obter_rect(170, y_p + 10, 100, 14)
                pygame.draw.rect(surface, (50, 15, 15), rect_hp_back, border_radius=2)
                if hp_ratio > 0:
                    rect_hp_front = self.obter_rect(170, y_p + 10, int(100 * hp_ratio), 14)
                    pygame.draw.rect(surface, cores["texto_verde"], rect_hp_front, border_radius=2)

                self._renderizar_texto_com_sombra(
                    surface, f"{int(al['hp_atual'])}/{int(al['hp_max'])}",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(280), self.obter_y(y_p + 8))
                )

            # Painel do Pergaminho do Resultado (Direita - Sem inimigos na arena superior)
            pergam_rect = self.obter_rect(420, 120, 820, 500)
            self._desenhar_moldura(surface, pergam_rect, espessura=3)
            pygame.draw.rect(surface, (235, 215, 185), pergam_rect.inflate(-6, -6))  # Pergaminho creme

            self._renderizar_texto_com_sombra(
                surface, "DIARIO DE EVENTOS - RESULTADO",
                fonte_card, (60, 40, 20),
                (self.obter_x(450), self.obter_y(140)),
                sombra_offset=0
            )

            # Narrativa de Resultado quebrada
            desc_linhas = self.__quebrar_texto(self.__narrativa_resultado, 60)
            for idx_l, pointer in enumerate(desc_linhas):
                self._renderizar_texto_com_sombra(
                    surface, pointer,
                    fonte_corpo, (30, 25, 20),
                    (self.obter_x(450), self.obter_y(180 + idx_l * 28)),
                    sombra_offset=0
                )

            # Conseqüências detalhadas na tela
            pygame.draw.line(surface, (180, 150, 110), (self.obter_x(450), self.obter_y(320)), (self.obter_x(1200), self.obter_y(320)), 1)
            
            self._renderizar_texto_com_sombra(
                surface, "CONSEQUENCIAS IMEDIATAS:",
                fonte_card, (80, 50, 20),
                (self.obter_x(450), self.obter_y(340)),
                sombra_offset=0
            )
            
            for idx_c, cons in enumerate(self.__consequencias_texto):
                cor_c = cores["texto_vermelho"] if "dano" in cons or "sucumbiu" in cons or "💀" in cons else (40, 120, 40)
                self._renderizar_texto_com_sombra(
                    surface, f"- {cons}",
                    fonte_corpo, cor_c,
                    (self.obter_x(450), self.obter_y(370 + idx_c * 28)),
                    sombra_offset=0
                )

            # Botão de Avançar Evento
            if self.__btn_avancar_evento:
                self.__btn_avancar_evento.desenhar(surface)

        # ── 5. Fase Resumo Expedição ──────────────────────────────────────
        elif self.__fase_tela == "resumo":
            w_real, h_real = self._gerenciador.largura_real, self._gerenciador.altura_real
            overlay = pygame.Surface((w_real, h_real), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            res_rect = self.obter_rect(340, 100, 600, 500)
            self._desenhar_moldura(surface, res_rect, espessura=3)
            pygame.draw.rect(surface, cores["fundo_painel"], res_rect.inflate(-6, -6))

            status_res = self.__resultado_expedicao["resultado"].upper()
            cor_status = cores["texto_verde"] if status_res == "VITORIA" else cores["texto_vermelho"]

            self._renderizar_texto_com_sombra(
                surface, "RESUMO DA EXPEDICAO",
                fonte_tit, cores["texto_ouro"],
                (self.obter_x(480), self.obter_y(130))
            )
            self._renderizar_texto_com_sombra(
                surface, f"RESULTADO: {status_res}",
                fonte_corpo, cor_status,
                (self.obter_x(380), self.obter_y(190))
            )

            # Recompensas ganhas
            self._renderizar_texto_com_sombra(
                surface, "Recompensas obtidas:",
                fonte_corpo, cores["texto_azul"],
                (self.obter_x(380), self.obter_y(235))
            )
            self._renderizar_texto_com_sombra(
                surface, f"- Ouro obtido: +{self.__resultado_expedicao['ouro_total']}g",
                fonte_peq, cores["texto_creme"],
                (self.obter_x(400), self.obter_y(270))
            )
            self._renderizar_texto_com_sombra(
                surface, f"- XP obtido:   +{self.__resultado_expedicao['xp_total']} XP",
                fonte_peq, cores["texto_creme"],
                (self.obter_x(400), self.obter_y(300))
            )
            self._renderizar_texto_com_sombra(
                surface, f"- Reputacao:   +{self.__resultado_expedicao['reputacao_ganha']} rep",
                fonte_peq, cores["texto_creme"],
                (self.obter_x(400), self.obter_y(330))
            )

            # Baixas da equipe
            self._renderizar_texto_com_sombra(
                surface, "Baixas na equipe:",
                fonte_corpo, cores["texto_vermelho"],
                (self.obter_x(380), self.obter_y(375))
            )
            mortos = self.__resultado_expedicao.get("herois_mortos", [])
            if not mortos:
                self._renderizar_texto_com_sombra(
                    surface, "Nenhum heroi faleceu! Todos retornaram a salvo.",
                    fonte_peq, cores["texto_verde"],
                    (self.obter_x(400), self.obter_y(410))
                )
            else:
                nomes_mortos = ", ".join([self.formatar_nome_heroi(h.nome) for h in mortos])
                self._renderizar_texto_com_sombra(
                    surface, f"Mortes: {nomes_mortos}",
                    fonte_peq, cores["texto_creme"],
                    (self.obter_x(400), self.obter_y(410))
                )

            # Itens Saqueados (Loot)
            self._renderizar_texto_com_sombra(
                surface, "Itens Saqueados:",
                fonte_corpo, cores["texto_azul"],
                (self.obter_x(380), self.obter_y(445))
            )
            itens = self.__resultado_expedicao.get("itens_saqueados", [])
            if not itens:
                self._renderizar_texto_com_sombra(
                    surface, "Nenhum item coletado nesta expedicao.",
                    fonte_peq, cores["texto_acinzentado"],
                    (self.obter_x(400), self.obter_y(475))
                )
            else:
                nomes_itens = ", ".join([getattr(item, "nome", "Item") for item in itens])
                if len(nomes_itens) > 50:
                    nomes_itens = nomes_itens[:48] + ".."
                self._renderizar_texto_com_sombra(
                    surface, nomes_itens,
                    fonte_peq, cores["texto_verde"],
                    (self.obter_x(400), self.obter_y(475))
                )

            self.__btn_fechar_resumo.desenhar(surface)

    def __quebrar_texto(self, text: str, max_chars: int) -> list:
        palavras = text.split()
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
