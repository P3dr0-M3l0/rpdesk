import os
import time
from game_state import GameState
from motor.motor_combater import MotorDeCombate
from gestao.missao import Missao
from itens.equipamento import Equipamento
from itens.consumivel import Consumivel

class GameController:
    def __init__(self, event_manager, save_manager, time_manager, game_state, rodando):
        self.__event_manager = event_manager
        self.__save_manager = save_manager
        self.__time_manager = time_manager
        self.__game_state = game_state
        self.__rodando = rodando
       
    
    def __gerar_mundo_dados_iniciais(self):
        # QUANTIA DE OURO QUE O JOGADOR COMEÇA O JOGO
        ouro_inicial = 100
        
        # Definindo o dia do jogo para 1
        self.__game_state.dia_atual = 1
        
        # Definindo a quantia inicial de ouro e a reputação
        guilda = self.__game_state.guilda
        guilda.ouro = ouro_inicial
        guilda.reputacao = 0
        
        # Gerando os primeiros heróis na taverna
        taverna = self.__game_state.taverna
        taverna.renovar_herois()
        
    def inicializar(self):
        self.__gerar_mundo_dados_iniciais()
    
    def __parar_motor(self, dados:dict = None):
        pass
    
    # =====================================================
    # Menus -----------------------------------------------
    # =====================================================
    def hud_global(self, menu_atual: str = "Principal"):
        # Informações HUD
        nome_guilda = self.__game_state.guilda.nome
        ouro = self.__game_state.guilda.ouro
        reputacao = self.__game_state.guilda.reputacao
        dia_atual = self.__game_state.dia_atual
        
        # HUD GLOBAL
        os.system('cls' if os.name == 'nt' else 'clear')   
        
        # ANSI color codes
        GOLD = "\033[93m"
        BORDER = "\033[90m"
        GREEN = "\033[92m"
        CYAN = "\033[96m"
        RESET = "\033[0m"
        
        # Centered title text parts
        part1 = "GUILDA: "
        part2 = nome_guilda.upper()
        part3 = "  |  "
        part4 = menu_atual.upper()
        
        uncolored_title = part1 + part2 + part3 + part4
        padding_title = 78 - len(uncolored_title)
        left_pad = padding_title // 2
        right_pad = padding_title - left_pad
        
        title_line = (
            " " * left_pad
            + RESET + part1
            + CYAN + part2
            + BORDER + part3
            + GOLD + part4
            + " " * right_pad
        )
        
        # Columns layout (uncolored for padding calculations)
        col1 = f"Ouro: {ouro}"
        col2 = f"Reputação: {reputacao}"
        col3 = f"Dia: {dia_atual}"
        
        # We need exact inner width of 78
        total_len = len(col1) + len(col2) + len(col3)
        padding_cols = 78 - total_len
        
        left_margin = 6
        right_margin = 6
        middle_padding = padding_cols - left_margin - right_margin
        pad1 = middle_padding // 2
        pad2 = middle_padding - pad1
        
        # stats_line with colors separate for labels and values
        stats_line = (
            " " * left_margin
            + RESET + "Ouro: " + GOLD + str(ouro)
            + " " * pad1
            + RESET + "Reputação: " + GREEN + str(reputacao)
            + " " * pad2
            + RESET + "Dia: " + CYAN + str(dia_atual)
            + " " * right_margin
        )
        
        print(BORDER + "╔" + "═" * 78 + "╗" + RESET)
        print(BORDER + "║" + title_line + BORDER + "║" + RESET)
        print(BORDER + "╠" + "═" * 78 + "╣" + RESET)
        print(BORDER + "║" + stats_line + BORDER + "║" + RESET)
        print(BORDER + "╚" + "═" * 78 + "╝" + RESET)
        print()

    
    def verificar_game_over(self):
        guilda = self.__game_state.guilda
        total_herois = len(guilda.roster_herois) + sum(len(eq.membros) for eq in guilda.equipes_ativas)
        if total_herois == 0 and guilda.ouro < 50:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n" + "="*58)
            print("┌────────────────────────────────────────────────────────┐")
            print("│                     GAME OVER                          │")
            print("├────────────────────────────────────────────────────────┤")
            print("│ A sua guilda faliu!                                    │")
            print("│ Você ficou sem heróis vivos e sem ouro suficiente      │")
            print("│ para contratar novos aventureiros (mínimo 50 ouro).    │")
            print("│                                                        │")
            print("│ O seu legado como gerente de guilda termina aqui...    │")
            print("└────────────────────────────────────────────────────────┘")
            print("="*58 + "\n")
            input("> Pressione Enter para sair...")
            self.__rodando = False
            return True
        return False

    def executar_loop(self):
        """
        Início do Loop do Jogo (while self.__rodando):
        
        1. Renderiza o HUD Global
           Mostra o Dia Atual, Reputação da Guilda e Ouro disponível (lidos do GameState).
           
        2. Mostra as Opções do Menu da Guilda (Hub)
           Aguardando input numérico do jogador:
           
           Opção 1: Ir para a Taverna
           Opção 2: Gerenciar Equipes e Heróis
           Opção 3: Abrir o Baú da Guilda
           Opção 4: Ir para a Batalha (Expedições)
           Opção 5: Avançar o Tempo (Encerrar o Dia)
           Opção 6: Opções de Sistema
        """
        while self.__rodando:
            if self.verificar_game_over():
                break
            self.hud_global("Menu Principal")
            
            # Menu da GUILDA
            print('\n\n> “Gerente, o que deseja fazer?”\n')
            print("1. Ir para a taverna;\n2. Gerenciar Equipes e Heróis;\n3. Abrir o Baú da Guilda;")
            print("4. Ir para a batalha;\n5. Encerrar o Dia;\n6. Opções do Sistema")
            escolha = input("\n> “Digite o número da opção desejada”\n> ")
            
            # Estrutura de seleção
            if escolha == '1':
                self.menu_taverna()
            elif escolha == '2':
                self.menu_equipes()
            elif escolha == '3':
                self.menu_bau()
            elif escolha == '4':
                self.menu_batalha()
            elif escolha == '5':
                self.menu_fim_dia()
            elif escolha == '6':
                self.menu_sistema()
            else:
                print('> “Opção inválida, tente novamente!”')
                continue
        
    def menu_taverna(self):
        """
        Opção 1: Ir para a Taverna
           - Mostra a vitrine atual de heróis gerados pela Fábrica.
           - Permite visualizar atributos, traços e custo.
           - Permite comprar (reduz ouro, transfere instância para a Guilda, remove da Taverna).
           - Retorna ao Menu da Guilda.
        """
        while True:
            lista_herois = self.__game_state.taverna.obter_vitrine()
            
            # Menu da Taverna
            self.hud_global("Taverna")
            print("\n> “Bem Vindo à Taverna!”")
            print("\n  +====================+\n  |    Heróis do Dia   |\n  +====================+")
            print("\n===------------------------------------------------------------------------------===")
            for i in range(len(lista_herois)):
                heroi = lista_herois[i]
                atributos = heroi.atributos
                print(f"---- Herói ----== {i+1} ==----")
                print(f"Atributos:\n    - Força: {atributos.valor_forca}\n    - Destreza: {atributos.valor_destreza}")
                print(f"    - Inteligência: {atributos.valor_inteligencia}")
                print(f"    - Velocidade: {atributos.valor_velocidade}\n    - HP Máximo: {atributos.valor_hp_max}")
                
                print("Traços:")
                tracos = heroi.lista_tracos
                for j in range(len(tracos)):
                    t_nome = tracos[j].nome
                    t_descricao = tracos[j].descricao
                    print(f"    {j}. {t_nome}\n        {t_descricao}")

                eq_list = []
                for slot, item in heroi.slots_equipados.items():
                    if item:
                        eq_list.append(f"{slot}: {item.nome}")
                eq_str = ", ".join(eq_list) if eq_list else "Nenhum"
                
                inv_list = [item.nome for item in heroi.inventario.lista_itens]
                inv_str = ", ".join(inv_list) if inv_list else "Vazio"
                
                print(f"    - Equipados: [{eq_str}] | Mochila: [{inv_str}]")
                print(f"\nValor: {heroi.valor} Moedas de Ouro\n")
            print("===------------------------------------------------------------------------------===")
            
            print("\n> “Deseja comprar algum desses heróis?”\n> “Se sim, digite o número do herói”")
            print("> “Se não, volte ao Menu da Guilda digitando * 0 *”")
            try:
                escolha = int(input("> "))
            except ValueError:
                print("Entrada Inválida, tente novamente!")
                time.sleep(1.0)
                continue
            
            if escolha in range(1, len(lista_herois)+1):
                heroi_escolhido = lista_herois[escolha-1]
                confirmacao = input(f"> “Deseja realmente contratar {heroi_escolhido.nome} por {heroi_escolhido.valor} moedas de ouro? (S/N)”\n> ").strip().upper()
                if confirmacao == 'S':
                    self.processar_contratacao_taverna(heroi_escolhido)
                else:
                    print("> “Contratação cancelada.”")
                    time.sleep(1.5)
            elif escolha == 0:
                break
            else:
                print("Entrada Inválida, tente novamente!")
                time.sleep(1.0)
                continue
    def menu_equipes(self):
        """
        Opção 2: Gerenciar Equipes e Heróis
           - Lista todos os heróis recrutados no roster da Guilda.
           - Permite acessar o inventário de um herói específico.
           - Permite equipar/desequipar itens nos slots (trânsito corpo <-> mochila).
           - Permite editar equipes existentes ou equipes novas.
           - Retorna ao Menu da Guilda.
        """
        guilda = self.__game_state.guilda
        
        while True:
            self.hud_global("Gerenciamento de Equipes")
            
            # Mostrar equipes ativas e suas informações
            print("\n-== Equipes Ativas ==-")
            equipes = guilda.equipes_ativas
            if not equipes:
                print("  Nenhuma equipe ativa.")
            else:
                for i, eq in enumerate(equipes):
                    if eq.membros:
                        total_xp = sum(m.xp + (m.nivel - 1) * 100 for m in eq.membros)
                        avg_xp = total_xp / len(eq.membros)
                    else:
                        avg_xp = 0.0
                    print(f"  [{i+1}] {eq.nome:<20} | Lotação: {len(eq.membros)}/{eq.limite_membros} | XP Médio: {avg_xp:.1f}")
            print("======================\n")
            
            print("> “Como vamos organizar os heróis hoje, senhor?”")
            print("    1. Listar Heróis disponíveis para alocação")
            print("    2. Editar equipes existentes")
            print("    3. Criar equipe nova")
            print("    0. Voltar ao menu anterior")
            escolha = input("> ")
            print("\n")

            if escolha == '1':
                self.menu_roster_guilda(guilda, True)
            elif escolha == '2':
                equipes = guilda.equipes_ativas
                if not equipes:
                    print("> “Não há nenhuma equipe ativa ainda, senhor!”")
                    time.sleep(1.5)
                    continue
                
                print("┌────────────────────────────────────────────────────────┐")
                print("│             Selecione uma Equipe para Editar           │")
                print("├────────────────────────────────────────────────────────┤")
                for i in range(len(equipes)):
                    eq = equipes[i]
                    if eq.membros:
                        total_xp = sum(m.xp + (m.nivel - 1) * 100 for m in eq.membros)
                        avg_xp = total_xp / len(eq.membros)
                    else:
                        avg_xp = 0.0
                    info_str = f" {i+1}. {eq.nome:<18} | Membros: {len(eq.membros)}/{eq.limite_membros} | XP Médio: {avg_xp:.1f} "
                    print(f"│ {info_str:<54} │")
                print("└────────────────────────────────────────────────────────┘")
                print("> “Qual dessas equipes tu queres gerenciar? (ou 0 para voltar)”")
                try:
                    escolha_input = input("> ").strip()
                    if escolha_input == '0':
                        continue
                    i_equipe = int(escolha_input)
                    if i_equipe in range(1, len(equipes) + 1):
                        self.menu_equipe_individual(equipes[i_equipe - 1], guilda)
                    else:
                        print("> “Essa equipe não existe!”")
                        time.sleep(1.5)
                except ValueError:
                    print("> “Acho que isso não é um número válido”")
                    time.sleep(1.5)
            elif escolha == '3':
                if len(guilda.equipes_ativas) >= 3:
                    print("\n> “Erro: Você já atingiu o limite máximo de 3 equipes ativas!”")
                    time.sleep(1.5)
                    continue
                    
                print("\n> “Uhhh, uma equipe nova é?!”")
                print("> “Sempre fico animado!”")
                print("> “Qual o nome que o senhor vai escolher dessa vez?”")
                nome = None
                while True:
                    nome_input = input("\n> ").strip()
                    if len(nome_input) > 20:
                        print("\n> “Que nome grande, chefe, tente algo com menos de 20 letras”")
                        time.sleep(1.5)
                    elif len(nome_input) == 0:
                        print("\n> “Nome não pode ser vazio, chefe!”")
                        time.sleep(1.5)
                    else:
                        # Confirmação do nome S/N
                        print(f"\n> “Confirmar o nome '{nome_input}' para a nova equipe? (S/N)”")
                        confirmar = input("> ").strip().upper()
                        if confirmar == 'S':
                            nome = nome_input
                            break
                        elif confirmar == 'N':
                            print("> “Criação de equipe cancelada.”")
                            time.sleep(1.5)
                            break
                        else:
                            print("> “Opção inválida. Digite S ou N.”")
                            time.sleep(1.5)
                
                if nome:
                    print("\n> “Hm, achei que seria melhor”")
                    print(f"> “Equipe {nome} criada com sucesso!”")
                    time.sleep(1.5)
                    self.menu_equipe_individual(guilda.formar_equipe(nome, []), guilda)
            elif escolha == '0':
                break
            else:
                print("> “Não quer tentar de novo, senhor?”")
                time.sleep(1.5)
           
    def menu_roster_guilda(self, guilda, flag_inv_herois: bool):
        """
        Opção 2.1: Lista todos os heróis recrutados no roster da Guilda
        """
        roster = guilda.roster_herois
        print("-== Heróis Disponíveis para Alocação:")
        for i in range(len(roster)):
            heroi = roster[i]
            atributos = heroi.atributos
            tracos = heroi.lista_tracos
            
            tracos_names = [t.nome for t in tracos]
            tracos_str = "/".join(tracos_names) if tracos_names else "Nenhum"
            
            # Format equipped items
            eq_list = []
            for slot, item in heroi.slots_equipados.items():
                if item:
                    eq_list.append(f"{slot}: {item.nome} (+{item.modificador[1]} {item.modificador[0].replace('_', ' ').capitalize()})")
            eq_str = ", ".join(eq_list) if eq_list else "Nenhum"
            
            # Format inventory items
            inv_list = []
            for item in heroi.inventario.lista_itens:
                if isinstance(item, Equipamento):
                    inv_list.append(f"{item.nome} (+{item.modificador[1]} {item.modificador[0].replace('_', ' ').capitalize()})")
                else:
                    inv_list.append(item.nome)
            inv_str = ", ".join(inv_list) if inv_list else "Vazio"
            
            print(f"\n-== {i} ==-. {heroi.nome}")
            print(f"    >-- HP Atual: {atributos.valor_hp_atual}/{atributos.valor_hp_max} - Força: {atributos.valor_forca} - Velocidade: {atributos.valor_velocidade} - Destreza: {atributos.valor_destreza} - Inteligencia: {atributos.valor_inteligencia} -->")
            print(f"    >-- Traços: {tracos_str} -->")
            print(f"    >-- Equipados: [{eq_str}] -->")
            print(f"    >-- Mochila: [{inv_str}] -->")
        
        if flag_inv_herois:
            print("\n> “Quer ver o inventário de alguns desses heróis?”")
            print("> “Se sim, coloque o número do herói correspondente. Se não, pressione enter”")
            try:
                i_heroi = int(input("> "))
            except ValueError:
                return
            if i_heroi in range(len(roster)):
                self.menu_inventario_heroi(roster[i_heroi])
        
    def menu_inventario_heroi(self, heroi):
        """
        Opção 2.2: Acessa o inventário de um herói específico
        """
        while True:
            inventario = heroi.inventario
            lista_itens = inventario.lista_itens
            slots_equipados = heroi.slots_equipados
            atributos = heroi.atributos
            
            self.hud_global(f"Inventário: {heroi.nome}")
            print(f"\n-== Inventário de {heroi.nome} ==-")
            print(f"Atributos:")
            print(f"  HP: {atributos.valor_hp_atual}/{atributos.valor_hp_max} | Força: {atributos.valor_forca} | Destreza: {atributos.valor_destreza} | Velocidade: {atributos.valor_velocidade} | Inteligência: {atributos.valor_inteligencia}")
            print(f"Lotação do inventário: {len(lista_itens)}/{inventario.capacidade_max}\n")
            
            for i in range(len(lista_itens)):
                item = lista_itens[i]
                if isinstance(item, Equipamento):
                    slot_str = item.slot.replace('_', ' ').capitalize()
                    attr_name = item.modificador[0].replace('_', ' ').capitalize()
                    val = item.modificador[1]
                    sign = "+" if val >= 0 else ""
                    print(f"  {i+1}. {item.nome:<25} | Slot: {slot_str:<12} | Efeito: {attr_name} {sign}{val:<3} | Valor: {item.valor} Ouro")
                elif isinstance(item, Consumivel):
                    print(f"  {i+1}. {item.nome:<25} | Tipo: Consumível | Valor: {item.valor} Ouro")
            
            print(f"\n-== Itens equipados em {heroi.nome} ==-")
            slots_padrao = ["cabeca", "tronco", "pernas", "mao_esquerda", "mao_direita", "pes", "dedos"]
            for slot in slots_padrao:
                item_equipado = slots_equipados.get(slot)
                if item_equipado:
                    attr_name = item_equipado.modificador[0].replace('_', ' ').capitalize()
                    val = item_equipado.modificador[1]
                    sign = "+" if val >= 0 else ""
                    print(f"  Slot: {slot.capitalize():<12} - {item_equipado.nome:<25} | Efeito: {attr_name} {sign}{val:<3}")
                else:
                    print(f"  Slot: {slot.capitalize():<12} - [Vazio]")
                    
            print("\n> “O que deseja fazer?”")
            print("    1. Equipar item ao Herói")
            print("    2. Desequipar item")
            print("    3. Mover item do herói para o baú da guilda")
            print("    0. Voltar ao menu anterior")
            escolha = input("\n> ")

            if escolha == '1':
                print("> “Qual o número do item a ser equipado?”")
                try:
                    i_item = int(input("> "))-1
                except ValueError:
                    i_item = -1
                if i_item in range(len(lista_itens)):
                    item = lista_itens[i_item]
                    if not isinstance(item, Equipamento):
                        print("> “Você não pode equipar um consumível!”")
                        time.sleep(1.5)
                        continue
                    if heroi.equipar_item(item):
                        print("> “Ah, agora sim! Equipamento novinho em folha”")
                        time.sleep(1.5)
                    else:
                        print("> “Parece que esse herói já tem um item equipado nesse slot”")
                        time.sleep(1.5)
                else:
                    print("> “Não existe um item com essa numeração!”")
                    time.sleep(1.5)
            elif escolha == '2':
                print("> “De qual slot quer tirar o item?”")
                slot = input("> ").strip().lower()
                slot = slot.replace("cabeça", "cabeca").replace("mão esquerda", "mao_esquerda").replace("mão direita", "mao_direita").replace("mao esquerda", "mao_esquerda").replace("mao direita", "mao_direita")
                if slot not in slots_equipados or slots_equipados[slot] is None:
                    print("> “Isso não é um slot válido ou não há nenhum item equipado nele!”")
                    time.sleep(1.5)
                    continue
                if heroi.desequipar_item(slot):
                    print("> “Item desequipado com sucesso!”")
                    time.sleep(1.5)
                else:
                    print("> “Parece que o nosso herói está com o inventário cheio! Vamos tentar desequipar esse item depois”")
                    time.sleep(1.5)
            elif escolha == '3':
                print("> “Qual o número do item a ser movido?”")
                try:
                    i_item = int(input("> "))-1
                except ValueError:
                    i_item = -1
                if i_item in range(len(lista_itens)):
                    if not self.__game_state.guilda.adicionar_item_bau(lista_itens[i_item], heroi):
                        print("> “Parece que o baú da guilda está cheio, chefe!”")
                        time.sleep(1.5)
                    else:
                        print("> “Mais um item para o baú!”")
                        time.sleep(1.5)
                else:
                    print("> “Não existe um item com essa numeração”")
                    time.sleep(1.5)
            elif escolha == '0':
                break
            else:
                print("\n> “Essa é uma opção inválida chefe, tente mais uma vez!”")
                time.sleep(1.5)
    
    def menu_equipe_individual(self, equipe, guilda):
        """
        Opção 2.3: Permite editar equipes existentes ou equipes novas
        """
        membros = equipe.membros
        roster = guilda.roster_herois
        while True:
            self.hud_global(f"Equipe: {equipe.nome}")

            print(f"\n-== Equipe {equipe.nome} ==-")
            print(f"Heróis ativos: {len(membros)}/{equipe.limite_membros}")
            for i in range(len(membros)):
                heroi = membros[i]
                atributos = heroi.atributos
                tracos = heroi.lista_tracos
                
                tracos_names = [t.nome for t in tracos]
                tracos_str = "/".join(tracos_names) if tracos_names else "Nenhum"
                
                eq_list = []
                for slot, item in heroi.slots_equipados.items():
                    if item:
                        eq_list.append(f"{slot.capitalize()}: {item.nome} (+{item.modificador[1]} {item.modificador[0].replace('_', ' ').capitalize()})")
                eq_str = ", ".join(eq_list) if eq_list else "Nenhum"
                
                inv_list = []
                for item in heroi.inventario.lista_itens:
                    if isinstance(item, Equipamento):
                        inv_list.append(f"{item.nome} (+{item.modificador[1]} {item.modificador[0].replace('_', ' ').capitalize()})")
                    else:
                        inv_list.append(item.nome)
                inv_str = ", ".join(inv_list) if inv_list else "Vazio"
                
                print(f"{i}. {heroi.nome}")
                print(f"    >-- HP Atual: {atributos.valor_hp_atual}/{atributos.valor_hp_max} - Força: {atributos.valor_forca} - Velocidade: {atributos.valor_velocidade} - Destreza: {atributos.valor_destreza} - Inteligência: {atributos.valor_inteligencia} -->")
                print(f"    >-- Traços: {tracos_str} -->")
                print(f"    >-- Equipados: [{eq_str}] -->")
                print(f"    >-- Mochila: [{inv_str}] -->")
                print()
            print("=============================-------------------------------------------------------")
            self.menu_roster_guilda(guilda, False)
            print("=============================-------------------------------------------------------")
            print("> “O que deseja fazer nessa equipe?”\n")
            print("    1. Acessar inventário de um Herói")
            print("    2. Adicionar novo Herói")
            print("    3. Remover um Herói")
            print("    4. Desfazer equipe (Apagar)")
            print("    0. Voltar ao menu anterior")
            escolha = input("\n> ")
            
            if escolha == '1':
                while True:
                    print("> “Os da equipe(*1*) ou os disponíveis(*2*)?”")
                    escolha2 = input("> ")
                    if escolha2 == '1':
                        if membros == []:
                            print("> “Essa equipe ainda não possui membros”")
                            time.sleep(1.5)
                            break
                        print("> “Me fale o número do herói que quer ver” (referente à equipe)")
                        try:
                            i_heroi = int(input("> "))
                            if i_heroi in range(len(membros)):
                                self.menu_inventario_heroi(membros[i_heroi])
                            else:
                                print("> “Creio que esse valor não serve”")
                                time.sleep(1.5)
                                continue
                        except ValueError:
                            print("> “Creio que esse valor não serve”")
                            time.sleep(1.5)
                            continue
                        break
                    elif escolha2 == '2':
                        if roster == []:
                            print("> “Não temos heróis disponíveis!”")
                            time.sleep(1.5)
                            break
                        print("> “Qual o número do herói que quer ver?” (referente aos disponíveis na guilda)")
                        try:
                            i_heroi = int(input("> "))
                            if i_heroi in range(len(roster)):
                                self.menu_inventario_heroi(roster[i_heroi])
                            else:
                                print("> “Creio que esse valor não serve”")
                                time.sleep(1.5)
                                continue    
                        except ValueError:
                            print("> “Creio que esse valor não serve”")
                            time.sleep(1.5)
                            continue
                        break
                    else:
                        print("> “Continue tentando, chefe, uma hora você consegue!”")                
                        time.sleep(1.5)
            elif escolha == '2':
                if len(membros) == equipe.limite_membros:
                    print("> “Essa equipe já está cheia, senhor!”")
                    time.sleep(1.5)
                    continue
                while True:
                    if not roster:
                        print("> “Não há heróis disponíveis no roster!”")
                        time.sleep(1.5)
                        break
                    print("\n> “Fale o número do herói que quer adicionar”")
                    try:
                        i_heroi = int(input("> "))
                    except ValueError:
                        print("> “Creio que esse valor não serve”")
                        time.sleep(1.5)
                        continue
                    if i_heroi not in range(len(roster)):
                        print("> “Creio que esse valor não serve”")
                        time.sleep(1.5)
                        continue
                    heroi_escolhido = roster[i_heroi]
                    guilda.remover_heroi_roster(heroi_escolhido)
                    equipe.adicionar_membro(heroi_escolhido)
                    print(f"> “{heroi_escolhido.nome} foi adicionado à equipe com sucesso!”")
                    time.sleep(1.5)
                    break
            elif escolha == '3':
                if not membros:
                    print("> “Essa equipe não possui membros para remover!”")
                    time.sleep(1.5)
                    continue
                while True:
                    print("\n> “Fale o número do herói que quer remover da equipe”")
                    try:
                        i_heroi = int(input("> "))
                    except ValueError:
                        print("> “Creio que esse valor não serve”")
                        time.sleep(1.5)
                        continue
                    if i_heroi not in range(len(membros)):
                        print("> “Creio que esse valor não serve”")
                        time.sleep(1.5)
                        continue
                    heroi_escolhido = membros[i_heroi]
                    equipe.remover_membro(heroi_escolhido)
                    guilda.adicionar_heroi_roster(heroi_escolhido)
                    print(f"> “{heroi_escolhido.nome} foi removido da equipe com sucesso!”")
                    time.sleep(1.5)
                    break
            elif escolha == '4':
                confirmacao = input(f"> “Tem certeza que deseja desfazer a equipe {equipe.nome}? (S/N)”\n> ").strip().upper()
                if confirmacao == 'S':
                    # Return all members to the roster
                    for heroi in list(membros):
                        equipe.remover_membro(heroi)
                        guilda.adicionar_heroi_roster(heroi)
                    # Remove team from guilda active teams
                    guilda.equipes_ativas.remove(equipe)
                    print(f"> “Equipe {equipe.nome} foi desfeita com sucesso!”")
                    time.sleep(1.5)
                    break
                else:
                    print("> “Operação cancelada.”")
                    time.sleep(1.5)
            elif escolha == '0':
                break
            else:
                print("> “Temo que essa não seja uma opção válida, senhor”")
                time.sleep(1.5)
                
    def menu_bau(self):
        """
        Opção 3: Abrir o Baú da Guilda
           - Lista todos os itens guardados no inventário central.
           - Permite transferir itens do baú para a mochila de um herói selecionado.
           - Permite transferir itens da mochila de um herói para o baú.
           - Retorna ao Menu da Guilda.
        """
        guilda = self.__game_state.guilda
        bau = guilda.inventario_guilda
        
        while True:
            self.hud_global("Baú da Guilda")
            print(f"\n-== Inventário da Guilda: {guilda.nome} ==-")
            print(f"Capacidade: {len(bau.lista_itens)}/{bau.capacidade_max}\n")
            
            for i in range(len(bau.lista_itens)):
                item = bau.lista_itens[i]
                if isinstance(item, Equipamento):
                    slot_str = item.slot.replace('_', ' ').capitalize()
                    attr_name = item.modificador[0].replace('_', ' ').capitalize()
                    val = item.modificador[1]
                    sign = "+" if val >= 0 else ""
                    print(f"  {i+1}. {item.nome:<25} | Slot: {slot_str:<12} | Efeito: {attr_name} {sign}{val:<3} | Valor: {item.valor} Ouro")
                elif isinstance(item, Consumivel):
                    print(f"  {i+1}. {item.nome:<25} | Tipo: Consumível | Valor: {item.valor} Ouro")
            print("\n===------------------------------------------------------------------------------===")
            
            if len(bau.lista_itens) == 0:
                print("\n> “Parece que o nosso baú está vazio, não há muito o que fazer aqui!”")
                print("*Para sair, pressione qualquer botão*")
                input("> ")
                return
            
            print("\n> “Que tranqueira! Mas pelo menos é nossa tranqueira”")
            print("    1. Transferir item do baú para um herói")
            print("    2. Voltar ao menu anterior")
            escolha = input("> ")
            
            if escolha == '1':
                # Escolhendo o item
                print("> “Digite o número do item que deseja transferir”")
                try:
                    n_item = int(input("> "))
                except ValueError:
                    print("> “Isso não é um número, chefe”")
                    time.sleep(1.5)
                    continue
                if (n_item-1) not in range(len(bau.lista_itens)):
                    print("> “Não consegui achar isso no baú, tente de novo, por favor”")
                    time.sleep(1.5)
                    continue
                
                # Escolhendo o herói
                roster = guilda.roster_herois
                herois_equipes = []
                for equipe in guilda.equipes_ativas:
                    herois_equipes += equipe.membros
                herois = roster + herois_equipes
                
                print("\n")
                for i, heroi in enumerate(herois, 1):
                    atributos = heroi.atributos
                    inventario = heroi.inventario
                    
                    # Determine location
                    location = "Roster (Disponível)"
                    for eq in guilda.equipes_ativas:
                        if heroi in eq.membros:
                            location = f"Equipe: {eq.nome}"
                            break
                    
                    # Format equipped items descriptions
                    eq_list = []
                    for slot, eq_item in heroi.slots_equipados.items():
                        if eq_item:
                            eq_list.append(f"{slot.capitalize()}: {eq_item.nome}")
                    eq_str = ", ".join(eq_list) if eq_list else "Nenhum"
                    
                    # Format inventory items
                    inv_list = []
                    for inv_item in inventario.lista_itens:
                        inv_list.append(inv_item.nome)
                    inv_str = ", ".join(inv_list) if inv_list else "Vazio"
                    
                    print(f"{i}. {heroi.nome} ({location}):")
                    print(f"    - Atributos: HP:{atributos.valor_hp_atual}/{atributos.valor_hp_max} | F:{atributos.valor_forca} | D:{atributos.valor_destreza} | V:{atributos.valor_velocidade} | I:{atributos.valor_inteligencia}")
                    print(f"    - Equipados: [{eq_str}]")
                    print(f"    - Mochila: [{inv_str}]")
                    print("---\n")
                
                print("> “Digite o número do herói que quer transferir o item”")
                try:
                    n_heroi = int(input("> "))
                except ValueError:
                    print("> “Isso não é um número, chefe”")
                    time.sleep(1.5)
                    continue
                if (n_heroi-1) not in range(len(herois)):
                    print("> “Ué, acho que não temos esse herói! Tente novamente”")
                    time.sleep(1.5)
                    continue
                
                target_heroi = herois[n_heroi-1]
                temp = bau.remover_item(bau.lista_itens[n_item-1])
                if not target_heroi.adicionar_item(temp):
                    bau.adicionar_item(temp)
                    print(f"> “Mochila de {target_heroi.nome} está cheia! Tente outro herói.”")
                    time.sleep(1.5)
                    continue
                print(f"> “{temp.nome} transferido para a mochila de {target_heroi.nome} com sucesso!”")
                time.sleep(1.5)
                
            elif escolha == '2':
                break
            else:
                print("> “Não me parece que essa escolha estava nas opções”")
                time.sleep(1.5)

    def menu_batalha(self):
        """
        Opção 4: Ir para a Batalha (Expedições)
           - Solicita a seleção de uma Equipe previamente formada.
           - Exibe o sumário da missão ativa e pede confirmação.
           - Aciona o MotorDeCombate e a Missao, acumulando eventos numa fila.
           - Exibe a narrativa da batalha compassadamente (0.8s por ação).
           - Aplica as consequências (XP, ouro, reputação, mortes, baixas de equipe).
           - Retorna ao Menu da Guilda.
        """
        self.hud_global("Expedição / Batalha")
        guilda = self.__game_state.guilda

        # ---------------------------------------------------
        # 1. Seleção de Equipe
        # ---------------------------------------------------
        equipes = guilda.equipes_ativas
        if not equipes:
            print('\n> “Não há nenhuma equipe formada, senhor!\n  Forme uma equipe antes de partir para batalha.”')
            input('> [Enter para voltar]')
            return

        print('\n\n> “Qual equipe vai partir para a expedição?”\n')
        for i, eq in enumerate(equipes, 1):
            membros_vivos = [m for m in eq.membros if m._vivo]
            print(f'  {i}. {eq.nome} — {len(membros_vivos)}/{eq.limite_membros} heróis')
        print('  0. Voltar')

        try:
            escolha = int(input('\n> '))
        except ValueError:
            return

        if escolha == 0 or escolha not in range(1, len(equipes) + 1):
            return

        equipe = equipes[escolha - 1]
        membros_vivos = [m for m in equipe.membros if m._vivo]
        if not membros_vivos:
            print('> “Essa equipe não tem heróis vivos para partir!”')
            input('> [Enter para voltar]')
            return

        # ---------------------------------------------------
        # 2. Obtenção da Missão Ativa
        # ---------------------------------------------------
        missao = self.__game_state.obter_missao_ativa()
        if missao is None:
            print('\n> “A campanha está concluída, senhor! Não há mais missões disponíveis.”')
            input('> [Enter para voltar]')
            return

        # ---------------------------------------------------
        # 3. Apresentação e Confirmação
        # ---------------------------------------------------
        self.hud_global("Expedição / Batalha")
        print(f'\n\n===--- MISSÃO: {missao.nome} ---===')
        print(f'  Dificuldade : {missao.dificuldade}')
        print(f'  Descrição  : {missao.descricao}')
        print(f'  Recompensas : {missao.recompensa_ouro} Ouro | {missao.recompensa_xp} XP | {missao.recompensa_reputacao} Rep.')
        print(f'\n  Equipe      : {equipe.nome} ({len(membros_vivos)} heróis)')
        print('\n> “Partir para essa expedição? (S/N)”')
        confirmar = input('> ').strip().upper()
        if confirmar != 'S':
            return

        # ---------------------------------------------------
        # 4. Orquestração e Fila de Narrativa
        # ---------------------------------------------------
        fila_narrativa = []
        em = self.__event_manager

        def _cb_missao_iniciada(nome, descricao, dificuldade, **_):
            fila_narrativa.append('')
            fila_narrativa.append('══════════════════════════════════════════════════════════════════════')
            fila_narrativa.append(f'[EXPEDIÇÃO INICIADA] {nome}')
            fila_narrativa.append(f'  Descrição: {descricao}')
            fila_narrativa.append('══════════════════════════════════════════════════════════════════════')
            fila_narrativa.append('')

        def _cb_encontro_iniciado(tipo, **dados):
            fila_narrativa.append('──────────────────────────────────────────────────────────────────────')
            if tipo == 'combate':
                inimigos_str = ', '.join(dados.get('inimigos', []))
                fila_narrativa.append(f'[ENCONTRO: COMBATE] Inimigos avistados: {inimigos_str}')
            elif tipo == 'texto':
                fila_narrativa.append(f'[ENCONTRO: EVENTO] {dados.get("narrativa", "")}')
            fila_narrativa.append('')

        def _cb_evento_texto_processado(narrativa, efeitos, **_):
            for chave, valor in efeitos.items():
                if chave == 'dano_hp':
                    fila_narrativa.append(f'  [DANO] A equipe sofreu {valor} de dano!')
                elif chave == 'cura_hp':
                    fila_narrativa.append(f'  [CURA] A equipe recuperou {valor} de HP!')
                elif chave == 'ouro' and valor != 0:
                    sinal = '+' if valor > 0 else ''
                    fila_narrativa.append(f'  [RECOMPENSA] Ouro: {sinal}{valor}')

        def _cb_combate_iniciado(herois, inimigos, **_):
            fila_narrativa.append('[BATALHA] O combate começou!')
            fila_narrativa.append(f'  [ALIADOS]   {", ".join(herois)}')
            fila_narrativa.append(f'  [INIMIGOS]  {", ".join(inimigos)}')
            fila_narrativa.append('')

        def _cb_rodada_iniciada(numero_rodada, **_):
            fila_narrativa.append(f'[TURNO] ─── Rodada {numero_rodada} ───')

        def _cb_rodada_finalizada(herois, inimigos, **_):
            h_strs = [f"{h['nome']} [{h['hp']}/{h['hp_max']} HP]" for h in herois]
            i_strs = [f"{i['nome']} [{i['hp']}/{i['hp_max']} HP]" for i in inimigos]
            fila_narrativa.append(f'  [HP] Heróis: {" | ".join(h_strs)}')
            fila_narrativa.append(f'  [HP] Inimigos: {" | ".join(i_strs)}')
            fila_narrativa.append('')

        def _cb_acao_executada(origem, acao, alvo, detalhes, **_):
            if acao == 'atacar':
                dano = detalhes.get('dano_causado', '?')
                fila_narrativa.append(f'  [ATAQUE] {origem} ataca {alvo} causando {dano} de dano.')
            elif acao == 'curar':
                item = detalhes.get('item_usado', '?')
                fila_narrativa.append(f'  [CURA] {origem} usa {item} em {alvo}.')

        def _cb_morrer(id_morto, **dados):
            # Resolve o nome da entidade diretamente a partir do evento de morte, se fornecido
            nome_morto = dados.get("nome", None)
            if nome_morto is None:
                todos = list(equipe.membros)
                nome_morto = str(id_morto)
                for m in todos:
                    if str(m._id) == str(id_morto):
                        nome_morto = m.nome
                        break
            fila_narrativa.append(f'  [MORTE] 💀 {nome_morto} caiu em batalha!')

        def _cb_combate_finalizado(resultado, xp_acumulado, ouro_saqueado, **_):
            fila_narrativa.append('')
            status = 'VITÓRIA' if resultado == 'vitoria' else 'DERROTA'
            fila_narrativa.append(f'[COMBATE FINALIZADO] Status: {status}')
            fila_narrativa.append(f'  XP Acumulado: {xp_acumulado} | Ouro Saqueado: {ouro_saqueado}')
            fila_narrativa.append('')

        def _cb_missao_finalizada(resultado, nome, **dados):
            fila_narrativa.append('')
            fila_narrativa.append('══════════════════════════════════════════════════════════════════════')
            if resultado == 'vitoria':
                fila_narrativa.append(f'[EXPEDIÇÃO CONCLUÍDA] Sucesso em: {nome}')
                fila_narrativa.append(f'  Ouro ganho   : +{dados.get("recompensa_ouro", 0)}')
                fila_narrativa.append(f'  XP ganho     : +{dados.get("recompensa_xp", 0)}')
                fila_narrativa.append(f'  Reputação    : +{dados.get("recompensa_reputacao", 0)}')
            else:
                enc = dados.get('encontro', '?')
                fila_narrativa.append(f'[EXPEDIÇÃO FRACASSADA] Falha em: {nome}')
                fila_narrativa.append(f'  A equipe caiu no encontro {enc}.')
            fila_narrativa.append('══════════════════════════════════════════════════════════════════════')
            fila_narrativa.append('')

        em.inscrever('missao_iniciada',          _cb_missao_iniciada)
        em.inscrever('encontro_iniciado',         _cb_encontro_iniciado)
        em.inscrever('evento_texto_processado',   _cb_evento_texto_processado)
        em.inscrever('combate_iniciado',          _cb_combate_iniciado)
        em.inscrever('rodada_iniciada',           _cb_rodada_iniciada)
        em.inscrever('rodada_finalizada',         _cb_rodada_finalizada)
        em.inscrever('acao_executada',            _cb_acao_executada)
        em.inscrever('morrer',                    _cb_morrer)
        em.inscrever('combate_finalizado',        _cb_combate_finalizado)
        em.inscrever('missao_finalizada',         _cb_missao_finalizada)

        motor_combate = MotorDeCombate(em)
        resultado_expedicao = missao.executar(equipe, motor_combate, em)

        em.desinscrever('missao_iniciada',         _cb_missao_iniciada)
        em.desinscrever('encontro_iniciado',        _cb_encontro_iniciado)
        em.desinscrever('evento_texto_processado',  _cb_evento_texto_processado)
        em.desinscrever('combate_iniciado',         _cb_combate_iniciado)
        em.desinscrever('rodada_iniciada',          _cb_rodada_iniciada)
        em.desinscrever('rodada_finalizada',        _cb_rodada_finalizada)
        em.desinscrever('acao_executada',           _cb_acao_executada)
        em.desinscrever('morrer',                   _cb_morrer)
        em.desinscrever('combate_finalizado',       _cb_combate_finalizado)
        em.desinscrever('missao_finalizada',        _cb_missao_finalizada)

        # ---------------------------------------------------
        # 5. Exibição Compassada
        # ---------------------------------------------------
        os.system('cls' if os.name == 'nt' else 'clear')
        self.hud_global("Expedição / Batalha")
        for linha in fila_narrativa:
            print(linha)
            time.sleep(1.5)

        input('\n> [Enter para ver o resultado final]')

        # ---------------------------------------------------
        # 6. Aplicação de Consequências
        # ---------------------------------------------------
        resultado = resultado_expedicao['resultado']
        herois_mortos = resultado_expedicao.get('herois_mortos', [])

        if resultado == 'derrota':
            # Remove a equipe da guilda
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
                niveis_ganhos = heroi.ganhar_xp(xp_total)
                if niveis_ganhos > 0:
                    print(f'  [UP] {heroi.nome} subiu {niveis_ganhos} nível(is)! Agora está no nível {heroi.nivel}.')

            # Remove heróis mortos de suas equipes (mortes parciais em vitória)
            for heroi_morto in herois_mortos:
                for eq in guilda.equipes_ativas:
                    if heroi_morto in eq.membros:
                        eq.membros.remove(heroi_morto)
                        break

            # Marca a missão como concluída
            self.__game_state.registrar_missao_concluida(missao.nome)

        # Desenhar tabela com resumo ao final da batalha
        print("\n" + "="*58)
        print("┌────────────────────────────────────────────────────────┐")
        print("│                   RESUMO DA EXPEDIÇÃO                  │")
        print("├────────────────────────────────────────────────────────┤")
        if resultado == 'derrota':
            print("│ Resultado: DERROTA                                     │")
            print(f"│ Missão: {missao.nome:<46} │")
            print("├────────────────────────────────────────────────────────┤")
            print("│ A equipe foi totalmente aniquilada em combate.         │")
            print("│ Todos os heróis e pertences foram perdidos.            │")
        else:
            print("│ Resultado: VITÓRIA                                     │")
            print(f"│ Missão: {missao.nome:<46} │")
            print("├────────────────────────────────────────────────────────┤")
            print(f"│ Ouro ganho:      +{ouro_total:<37} │")
            print(f"│ Reputação:       +{reputacao:<37} │")
            print(f"│ XP distribuído:  +{xp_total:<37} │")
            print("├────────────────────────────────────────────────────────┤")
            print("│ Integrantes e Status:                                  │")
            sobreviventes = resultado_expedicao.get('herois_sobreviventes', [])
            for m in sobreviventes:
                status_str = f"  - {m.nome} (Nível {m.nivel}) [VIVO]"
                print(f"│ {status_str:<54} │")
            for m in herois_mortos:
                status_str = f"  - {m.nome} [MORTO]"
                print(f"│ {status_str:<54} │")
        print("└────────────────────────────────────────────────────────┘")
        print("="*58 + "\n")

    def menu_fim_dia(self):
        """
        Opção 5: Avançar o Tempo (Encerrar o Dia)
           - Invoca o GerenciadorDeTempo para passar o turno.
           - Atualiza o atributo __dia_atual no GameState.
           - Aciona a Taverna para descartar a vitrine antiga e gerar novos recrutas.
           - Retorna ao topo do loop, renderizando o Dia (n+1).
        """
        print("\n> Encerrando o dia...")
        
        # Cobrar taxa de manutenção diária de 10 de ouro
        guilda = self.__game_state.guilda
        if guilda.ouro >= 10:
            guilda.ouro -= 10
            print("> [MANUTENÇÃO] Foram deduzidos 10 de ouro para a manutenção da guilda.")
        else:
            guilda.ouro = 0
            print("> [MANUTENÇÃO] A guilda não tem ouro suficiente para a manutenção!")
            
        self.__time_manager.avancar_dia()
        print(f"> Um novo amanhecer! Bem-vindo ao Dia {self.__game_state.dia_atual}.")
        time.sleep(2.0)

    def menu_sistema(self):
        """
        Opção 6: Opções de Sistema
           - Salvar Jogo: Passa o GameState ao SaveManager, reescreve o slot, avisa "Jogo Salvo" e retorna ao Menu da Guilda.
           - Salvar e Sair: Executa o salvamento, altera self.__rodando = False (quebra o while) e encerra o script.
           - Sair (Sem Salvar): Confirma a intenção, altera self.__rodando = False e encerra o script.
        """
        self.hud_global("Opções de Sistema")
        print("\n\n===--- OPÇÕES DE SISTEMA ---===")
        print("1. Salvar Jogo")
        print("2. Salvar e Sair")
        print("3. Sair sem Salvar")
        print("0. Voltar")
        escolha = input("> ")
        if escolha == '1':
            print("\n> Salvando jogo...")
            self.__save_manager.salvar_estado(self.__game_state)
            print("> Jogo salvo com sucesso!")
            time.sleep(1.5)
        elif escolha == '2':
            print("\n> Salvando jogo...")
            self.__save_manager.salvar_estado(self.__game_state)
            print("> Jogo salvo. Saindo...")
            time.sleep(1.0)
            self.__rodando = False
        elif escolha == '3':
            confirmar = input("> Tem certeza que deseja sair sem salvar? (S/N): ").strip().upper()
            if confirmar == 'S':
                self.__rodando = False
        elif escolha == '0':
            return
        else:
            print("> Opção inválida!")
            time.sleep(1.0)

    # =====================================================
    # Auxiliares ------------------------------------------
    # =====================================================
    def processar_contratacao_taverna(self, heroi_escolhido):
        guilda = self.__game_state.guilda
        if guilda.contratar_heroi(heroi_escolhido, heroi_escolhido.valor):
            taverna = self.__game_state.taverna
            taverna.remover_heroi_comprado(heroi_escolhido)
            print(f"> “Contratação de {heroi_escolhido.nome} realizada com sucesso!”")
            time.sleep(1.5)
            return True
        else:
            print("> “Você não possui ouro suficiente!”")
            time.sleep(1.5)
            return False