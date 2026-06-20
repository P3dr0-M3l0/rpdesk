import os
from game_state import GameState
from src.itens.equipamento import Equipamento
from src.itens.consumivel import Consumivel

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
        pass
    
    def __parar_motor(self, dados:dict = None):
        pass
    
    # =====================================================
    # Menus -----------------------------------------------
    # =====================================================
    def hud_global(self):
        # Informações HUD
        nome_guilda = self.__game_state.guilda.nome
        ouro = self.__game_state.guilda.ouro
        reputacao = self.__game_state.guilda.reputacao
        dia_atual = self.__game_state.dia_atual
        
        # HUD GLOBAL
        os.system('cls' if os.name == 'nt' else 'clear')   
        print("=====================================================================================")
        print(f"::-- {nome_guilda} // Ouro: {ouro} // Reputação: {reputacao} // Dia: {dia_atual} -->")
    
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
           - Solicita a seleção de uma Equipe previamente formada.
           - Solicita a escolha do mapa/missão (define os inimigos).
           - Aciona o MotorDeCombate.
           - Loop de combate processa a IA (traços de personalidade) e os turnos.
           - Em caso de vitória: repassa espólios ao baú da Guilda e XP aos heróis.
           - Retorna ao Menu da Guilda.
           
           Opção 5: Avançar o Tempo (Encerrar o Dia)
           - Invoca o GerenciadorDeTempo para passar o turno.
           - Atualiza o atributo __dia_atual no GameState.
           - Aciona a Taverna para descartar a vitrine antiga e gerar novos recrutas.
           - Retorna ao topo do loop, renderizando o Dia (n+1).
           
           Opção 6: Opções de Sistema
           - Salvar Jogo: Passa o GameState ao SaveManager, reescreve o slot, avisa "Jogo Salvo" e retorna ao Menu da Guilda.
           - Salvar e Sair: Executa o salvamento, altera self.__rodando = False (quebra o while) e encerra o script.
           - Sair (Sem Salvar): Confirma a intenção, altera self.__rodando = False e encerra o script.
        """
        while self.__rodando:
            self.hud_global()
            
            # Menu da GUILDA
            print('\n\n> “Gerente, o que deseja fazer?”\n')
            print("1. Ir para a taverna;\n2. Gerenciar Equipes e Heróis;\n3. Abrir o Baú da Guilda;")
            print("4. Ir para a batalha;\n5. Encerrar o Dia;\n6. Opções do Sistema")
            escolha = input("> “Digite o número da opção desejada”\n> ")
            
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
        # Informações Heróis
        lista_herois = self.__game_state.taverna.obter_vitrine()
        
        # Menu da Taverna
        print("\n> “Bem Vindo à Taverna!”")
        print("\n  +====================+\n  |    Heróis do Dia   |\n  +====================+")
        print("\n===------------------------------------------------------------------------------===")
        for i in range(len(lista_herois)):
            atributos = lista_herois[i].atributos
            print(f"---- Herói -== {i} ==-")
            print(f"Atributos:\n    - Forca: {atributos.forca}\n    - Destreza: {atributos.destreza}")
            print(f"    - Inteligencia: {atributos.inteligencia}")
            print(f"    - Velocidade: {atributos.velocidade}\n    - HP Máximo: {atributos.hp_max}")
            
            print("Traços:")
            tracos = lista_herois[i].lista_tracos
            for j in range(len(tracos)):
                t_nome = tracos[j].nome
                t_descricao = tracos[j].descricao
                print(f"    {j}. {t_nome}\n        {t_descricao}")
                
            print(f"\nValor: {lista_herois[i].valor} Moedas de Ouro")
        print("===------------------------------------------------------------------------------===")
        
        while True:
            print("\n> “Deseja comprar algum desses heróis?”\n> “Se sim, digite o número do herói”")
            print("> “Se não, volte ao Menu da Guilda digitando * 0 *”")
            escolha = int(input("> "))
            
            if escolha in range(len(1, lista_herois+1)):
                self.processar_contratacao_taverna(lista_herois[escolha-1])
            elif escolha == 0:
                break
            else:
                print("Entrada Inválida, tente novamente!")
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
        
        self.hud_global()
        
        print("> “Como vamos organizar os heróis hoje, senhor?”")
        print("    1. Listar Heróis disponíveis para alocação")
        print("    2. Editar equipes existentes")
        print("    3. Criar equipe nova")
        print("    0. Voltar ao menu anterior")
        escolha = input("> ")

        while True:
            if escolha == '1':
                self.menu_roster_guilda(guilda, True)
            elif escolha == '2':
                equipes = guilda.equipes_ativas
                for i in range(len(equipes)):
                    print(f"{i+1}. {equipes[i].nome} - {len(equipes[i].mebros)}/{equipes[i].limite_membros} membros")
                print("> “Qual dessas equipes tu queres gerenciar?”")
                try:
                    i_equipe = int(input("> "))
                    if i_equipe in range(len(equipes)):
                        self.menu_equipe_individual(equipes[i_equipe], guilda)
                except ValueError:
                    print("> “Acho que isso não é um número válido”")
            elif escolha == '3':
                print("> “Uhhh, uma equipe nova é?!”")
                print("> “Sempre fico animado!”")
                print("> “Qual o nome que o senhor vai escolher dessa vez?”")
                while True:
                    nome = input("> ")
                    if len(nome) > 20:
                        print("\n> “Que nome grande, chefe, tente algo com menos de 20 linhas”")
                    else:
                        break
                print("\n> “Hm, achei que seria melhor”")
                self.menu_equipe_individual(guilda.formar_equipe(nome, []), guilda)
            elif escolha == '0':
                break
            else:
                print("> “Não quer tentar de novo, senhor?”")
        
        
    def menu_roster_guilda(self, guilda, flag_inv_herois: bool):
        """
        Opção 2.1: Lista todos os heróis recrutados no roster da Guilda
        """
        roster = guilda.roster_herois
        print("\n-== Heróis Disponíveis para Alocação:")
        for i in range(len(roster)):
            atributos = roster[i].atributos
            tracos = roster[i].lista_tracos
            print(f"{i}. {roster[i].nome}")
            print(f"  - HP Atual: {atributos.valor_hp_atual}/{atributos.valor_hp_max} ", end='')
            print(f"- Força: {atributos.valor_forca} - Velocidade: {atributos.valor_velocidade} ", end='')
            print(f"- Destreza: {atributos.valor_destreza} - Inteligencia: {atributos.valor_inteligencia}")
            print("  - Tracos: ", end='')
            for i in range(len(tracos)):
                print(f"{tracos[i].nome}", end="")
                if i != len(tracos)-1:
                    print("/", end="")
            print("\n")
        
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
        inventario = heroi.inventario
        lista_itens = inventario.lista_itens
        slots_equipados = heroi.slots_equipados
        
        self.hud_global()
        print(f"\n-== Inventário de {heroi.nome} ==-")
        print(f"Lotação do inventário: {len(lista_itens)}/{inventario.capacidade_max}")
        for i in range(len(lista_itens)):
            item = lista_itens[i]
            if isinstance(item, Equipamento):
                print(f"{i+1}. {item.nome}-{item.modificador[0]}/{item.modificador[1]}/{item.modificador[2]}-{item.valor}")
            elif isinstance(item, Consumivel):
                print(f"{i+1}. {item.nome}-{item.valor}")
        print(f"\n-== Itens equipados em {heroi.nome} ==-")
        for key in slots_equipados:
            print(f"Slot: {key} - Item: {slots_equipados[key].nome}")
                
        while True:
            print("\n> “O que deseja fazer?”")
            print("\n    1. Equipar item ao Héroi\n    2. Desequipar item")
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
                    if heroi.equipar_item(lista_itens[i_item]):
                        print("> “Ah, agora sim! Equipamento novinho em folha”")
                    else:
                        print("> “Parece que esse herói já tem um item equipado nesse slot”")
                else:
                    print("> “Não existe um item com essa numeração!”")
            elif escolha == '2':
                print("> “De qual slot quer tirar o item?”")
                slot  = input("> ")
                slot = slot.lower()
                if slot not in slots_equipados:
                    print("> “Isso não é um slot válido!\n*Tente escrever exatamente como na lista de itens equipados*”")
                if not heroi.desequipar_item(slot):
                    print("> “Parece que o nosso herói está com o inventário cheio! Vamos tentar desequipar esse item depois”")
                print("> “Vamos por algo no lugar?”")
            elif escolha == '3':
                print("> “Qual o número do item do item a ser equipado?”")
                try:
                    i_item = int(input("> "))-1
                except ValueError:
                    i_item = -1
                if i_item in range(len(lista_itens)):
                    if not self.__game_state.guilda.adicionar_item_bau(lista_itens[i_item], heroi):
                        print("> “Parece que o baú da guilda está cheio, chefe!”")
                    print("> “Mais um item para o baú!”")
                else:
                    print("> “Não existe um item com essa numeração”")
            elif escolha == '0':
                break
            else:
                print("\n> “Essa é uma opção inválida chefe, tente mais uma vez!”")
    
    def menu_equipe_individual(self, equipe, guilda):
        """
        Opção 2.3: Permite editar equipes existentes ou equipes novas
        """
        membros = equipe.membros
        roster = guilda.roster

        while True:
            self.hud_global()

            print(f"\n-== Equipe {equipe.nome} ==-")
            print(f"Heróis ativos: {len(membros)}/{equipe.limite_membros}")
            for i in range(len(membros)):
                atributos = membros[i].atributos
                tracos = membros[i].lista_tracos
                print(f"{i}. {membros[i].nome}")
                print(f"  - HP Atual: {atributos.valor_hp_atual}/{atributos.valor_hp_max} ", end='')
                print(f"- Força: {atributos.valor_forca} - Velocidade: {atributos.valor_velocidade} ", end='')
                print(f"- Destreza: {atributos.valor_destreza} - Inteligencia: {atributos.valor_inteligencia}")
                print("  - Tracos: ", end='')
                for i in range(len(tracos)):
                    print(f"{tracos[i].nome}", end="")
                    if i != len(tracos)-1:
                        print("/", end="")
                print("\n")
            print("=============================-------------------------------------------------------")
            self.menu_roster_guilda(guilda, False)
            print("=============================-------------------------------------------------------")
            print("> “O que deseja fazer nessa equipe?”\n")
            print("    1. Acessar inventário de um Herói")
            print("    2. Adicionar novo Herói")
            print("    3. Remover um Herói")
            print("    0. Voltar ao menu anterior")
            escolha = input("> ")
            
            if escolha == '1':
                while True:
                    print("> “Os da equipe(*1*) ou os disponíveis(*2*)?”")
                    escolha2 = input("> ")
                    if escolha2 == '1':
                        if membros == []:
                            print("> “Essa equipe ainda não possui membros”")
                            break
                        print("> “Me fale o número do herói que quer ver” (referente à equipe)")
                        try:
                            i_heroi = int(input("> "))-1
                            if i_heroi in range(len(membros)):
                                self.menu_inventario_heroi(membros[i_heroi])
                            else:
                                print("> “Creio que esse valor não serve”")
                                continue
                        except ValueError:
                            print("> “Creio que esse valor não serve”")
                            continue
                        break
                    elif escolha2 == '2':
                        if roster == []:
                            print("> “Não temos heróis disponíveis!”")
                            break
                        print("> “Qual o número do herói que quer ver?” (referente aos disponíveis na guilda)")
                        try:
                            i_heroi = int(input("> "))-1
                            if i_heroi in range(len(roster)):
                                self.menu_inventario_heroi(roster[i_heroi])
                            else:
                                print("> “Creio que esse valor não serve”")
                                continue    
                        except ValueError:
                            print("> “Creio que esse valor não serve”")
                            continue
                        break
                    else:
                        print("> “Continue tentando, chefe, uma hora você consegue!”")                
            elif escolha == '2':
                if len(membros) == equipe.limite_membros:
                    print("> “Essa equipe já está cheia, senhor!”")
                    continue
                while True:
                    print("\n> “Fale o número do herói que quer adicionar”")
                    try:
                        i_heroi = int(input("> "))-1  
                    except ValueError:
                        print("> “Creio que esse valor não serve”")
                        continue
                    if i_heroi not in range(len(roster)):
                        print("> “Creio que esse valor não serve”")
                    guilda.remover_heroi_roster(roster[i_heroi])
                    equipe.adicionar_membro(roster[i_heroi])
                    break
            elif escolha == '3':
                while True:
                    print("\n> “Fale o número do herói que quer remover da equipe”")
                    try:
                        i_heroi = int(input("> "))-1  
                    except ValueError:
                        print("> “Creio que esse valor não serve”")
                        continue
                    if i_heroi not in range(len(membros)):
                        print("> “Creio que esse valor não serve”")
                    equipe.remover_membro(membros[i_heroi])
                    guilda.adicionar_heroi_roster(membros[i_heroi])
                    break
            elif escolha == '0':
                break
            else:
                print("> “Temo que essa não seja uma opção válida, senhor”")
                
    def menu_bau(self, guilda):
        """
        Opção 3: Abrir o Baú da Guilda
           - Lista todos os itens guardados no inventário central.
           - Permite transferir itens do baú para a mochila de um herói selecionado.
           - Permite transferir itens da mochila de um herói para o baú.
           - Retorna ao Menu da Guilda.
        """
        self.hud_global()
        
        print(f"\n-== Inventário da Guilda: {guilda.nome} ==-\n")
        
        bau = guilda.inventario_guilda
        for i in range(len(bau.lista_itens)):
            item = bau[i]
            if isinstance(item, Equipamento):
                print(f"{i+1}. {item.nome}-{item.modificador[0]}/{item.modificador[1]}/{item.modificador[2]}-{item.valor}")
            elif isinstance(item, Consumivel):
                print(f"{i+1}. {item.nome}-{item.valor}")
        print("\n===------------------------------------------------------------------------------===")
        
        if len(bau) == 0:
            print("\n> “Parece que o nosso baú está vazio, não há muito o que fazer aqui!”")
            print("*Para sair, pressione qualquer botão*")
            input("> ")
            return
        
        print("\n> “Que tranqueira! Mas pelo menos é nossa tranqueira”")
        while True:
            print("    1. Transferir item do baú para um herói")
            print("    2. Voltar ao menu anterior")
            escolha = input("> ")
            
            if escolha == '1':
                # Escolhendo o item
                print("> “Digite o número do item que deseja transferir”")
                try:
                    n_item = int(input("> "))
                except TypeError:
                    print("> “Isso não é um número, chefe”")
                    print("===------------------------------------------------------------------------------===")
                    continue
                if (n_item-1) not in range(len(bau.listar_itens)):
                    print("> “Não consegui achar isso no baú, tente de novo, por favor”")
                    print("===------------------------------------------------------------------------------===")
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
                    print(f"{i}. {heroi.nome}:")
                    print("    - Atributos: ", end='')
                    print(f"V:{atributos.valor_hp_max}/F:{atributos.valor_forca}/", end='')
                    print(f"D:{atributos.valor_destreza}/V:{atributos.valor_velocidade}/", end='')
                    print(f"I:{atributos.valor_inteligencia}")
                    print(f"    - Itens: ", end='')
                    for item in inventario.lista_itens:
                        if isinstance(item, Equipamento):
                            print(f"{item.nome}-{item.slot}/", end='')
                        elif isinstance(item, Consumivel):
                            print(f"{item.nome}/", end='')
                    print("---\n")
                
                print("> “Digite o número do herói que quer transferir o item”")
                try:
                    n_heroi = int(input("> "))
                except TypeError:
                    print("> “Isso não é um número, chefe”")
                    print("===------------------------------------------------------------------------------===")
                    continue
                if (n_heroi-1) not in range(len(herois)):
                    print("> “Ué, acho que não temos esse herói! Tente novamente”")
                    print("===------------------------------------------------------------------------------===")
                    continue
                temp = bau.remover_item(bau.lista_itens[n_item-1])
                if not herois[n_heroi-1].adicionar_item(temp):
                    bau.adicionar_item(temp)
                    print("> “Tente outro herói!”")
                    print("===------------------------------------------------------------------------------===")
                    continue
                print("> “Transferência realizada com sucesso!”")
                print("===------------------------------------------------------------------------------===")
                
            elif escolha == '2':
                break
            else:
                print("> “Não me parece que essa escolha estava nas opções”")
            
            
    # =====================================================
    # Auxiliares ------------------------------------------
    # =====================================================
    def processar_contratacao_taverna(self, heroi_escolhido):
        guilda = self.__game_state.guilda
        if not guilda.contratar_heroi(heroi_escolhido, heroi_escolhido.valor):
            print("Você não possui ouro suficiente!")
        
        taverna = self.__game_state.taverna
        taverna.remover_heroi_comprado(heroi_escolhido)