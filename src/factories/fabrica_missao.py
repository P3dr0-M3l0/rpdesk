"""
fabrica_missao.py
-----------------
Fábrica procedural para geração de missões Roguelike dinâmicas e balanceadas.
Garante a diversificação total e unicidade de encontros, nomes e recompensas.
"""

import random
from gestao.missao import Missao
from gestao.encontro_combate import EncontroCombate
from gestao.encontro_texto import EncontroTexto


class FabricaDeMissoes:
    """
    Gera missões dinâmicas com progressão escalonada baseada na reputação da guilda
    e no dia atual, misturando encontros narrativos de escolha e combates desafiadores.
    """

    def __init__(self, fabrica_inimigos, fabrica_itens):
        self.__fabrica_inimigos = fabrica_inimigos
        self.__fabrica_itens = fabrica_itens

        # Banco de dados de modelos de Encontros de Escolha Narrativos
        self.__modelos_eventos = [
            {
                "narrativa": "A equipe encontra um bau antigo trancado e coberto de musgo sob as raizes de uma arvore.",
                "opcoes": [
                    {
                        "texto": "Forçar a fechadura",
                        "narrativa_resultado": "A equipe força o bau! A fechadura se rompe, mas uma nuvem de gas venenoso eh liberada.",
                        "efeitos": {"dano_hp": 6, "ouro": 40}
                    },
                    {
                        "texto": "Barganhar reagente de abertura (-15g)",
                        "narrativa_resultado": "Ganhando foco, o grupo usa reagentes para derreter o trinco e abre o bau com segurança.",
                        "efeitos": {"ouro": 25, "ouro_custo": -15}
                    },
                    {
                        "texto": "Ignorar e seguir",
                        "narrativa_resultado": "A equipe decide que o risco nao compensa e segue a trilha principal com segurança.",
                        "efeitos": {}
                    }
                ]
            },
            {
                "narrativa": "Uma bela fonte magica emana uma luz celestial azulada e calma no centro de uma clareira silenciosa.",
                "opcoes": [
                    {
                        "texto": "Beber da agua purificadora",
                        "narrativa_resultado": "A agua fresca cura as feridas fisicas e revigora os espiritos de todos os guerreiros vivos.",
                        "efeitos": {"cura_hp": 15}
                    },
                    {
                        "texto": "Investigar o fundo da fonte",
                        "narrativa_resultado": "Vasculhando entre as pedras submersas, os herois encontram moedas de ouro perdidas.",
                        "efeitos": {"ouro": 30}
                    },
                    {
                        "texto": "Passar direto",
                        "narrativa_resultado": "O grupo respeita a quietude do santuario mistico e segue caminho sem toca-lo.",
                        "efeitos": {}
                    }
                ]
            },
            {
                "narrativa": "Um mercador ambulante encapuzado e misterioso oferece barganhas interessantes a margem da estrada.",
                "opcoes": [
                    {
                        "texto": "Comprar suprimentos medicos (-25g)",
                        "narrativa_resultado": "O grupo compra bandagens raras do mercador, curando instantaneamente seus combatentes.",
                        "efeitos": {"cura_hp": 20, "ouro_custo": -25}
                    },
                    {
                        "texto": "Vender reliquias de sucata",
                        "narrativa_resultado": "O mercador aceita sucatas de ferro que o grupo carregava em troca de moedas cintilantes.",
                        "efeitos": {"ouro": 25}
                    },
                    {
                        "texto": "Ignorar o mercador",
                        "narrativa_resultado": "Desconfiados dos olhos vermelhos sob o capuz, os aventureiros apenas acenam e passam reto.",
                        "efeitos": {}
                    }
                ]
            },
            {
                "narrativa": "Uma estatua de gargula de pedra assustadora guarda a entrada de uma ruina abandonada. Seus olhos piscam.",
                "opcoes": [
                    {
                        "texto": "Oferecer uma oferenda de sangue",
                        "narrativa_resultado": "Os herois tocam o altar de pedra. Uma fraqueza consome o sangue deles, mas o bau da gargula se abre.",
                        "efeitos": {"dano_hp": 4, "ouro": 50}
                    },
                    {
                        "texto": "Pegar atalho pela floresta",
                        "narrativa_resultado": "Para evitar a gargula, a equipe caminha por horas sob galhos espinhosos, cansando-se.",
                        "efeitos": {"dano_hp": 2}
                    },
                    {
                        "texto": "Ignorar e recuar",
                        "narrativa_resultado": "A guilda recua da entrada da ruina com cuidado, decidindo seguir pelas rotas normais.",
                        "efeitos": {}
                    }
                ]
            },
            {
                "narrativa": "Um antigo altar de pedra esculpido com inscriçoes celestiais irradia energia pacifica.",
                "opcoes": [
                    {
                        "texto": "Meditar no altar",
                        "narrativa_resultado": "A quietude celestial acalma a mente dos herois, restaurando suas forças.",
                        "efeitos": {"cura_hp": 10}
                    },
                    {
                        "texto": "Pilar da energia (-10g de oferenda)",
                        "narrativa_resultado": "Colocando ouro no altar, uma bençao de luz concede cura intensa a equipe.",
                        "efeitos": {"cura_hp": 25, "ouro_custo": -10}
                    },
                    {
                        "texto": "Seguir adiante",
                        "narrativa_resultado": "O grupo faz uma reverencia silenciosa e continua a marcha.",
                        "efeitos": {}
                    }
                ]
            },
            {
                "narrativa": "Uma fenda nas rochas brilha com cristais instaveis de energia magica concentrada.",
                "opcoes": [
                    {
                        "texto": "Extrair cristais com cuidado",
                        "narrativa_resultado": "A equipe minera com cuidado, vendendo os cristais coletados por ouro extra.",
                        "efeitos": {"ouro": 35}
                    },
                    {
                        "texto": "Canalizar energia nos guerreiros",
                        "narrativa_resultado": "Os cristais explodem em po magico! A energia causa queimaduras leves mas cura fadiga.",
                        "efeitos": {"dano_hp": 3, "cura_hp": 12}
                    },
                    {
                        "texto": "Apenas afastar-se",
                        "narrativa_resultado": "Temendo uma explosao arcana, o grupo contorna a fenda e segue a trilha segura.",
                        "efeitos": {}
                    }
                ]
            }
        ]

        # Nomes medievais para gerar missões procedurais
        self.__prefixos = ["Incursao na", "Limpeza da", "Investigacao na", "Emboscada na", "Ruina da", "Resgate na"]
        self.__locais = ["Floresta de Goblins", "Cripta Esquecida", "Mesa dos Orcs", "Mina de Ferro Runico", "Torre Obscura", "Caverna Fria"]

    def obter_evento_por_indice(self, idx_evento: int) -> EncontroTexto:
        """Retorna uma instância de EncontroTexto baseada em um modelo estável do banco."""
        modelo = self.__modelos_eventos[idx_evento % len(self.__modelos_eventos)]
        encontro = EncontroTexto(
            narrativa=modelo["narrativa"],
            efeitos={"opcoes": modelo["opcoes"]}
        )
        return encontro

    def gerar_missao_procedural(self, reputacao: int, dia: int, indice_opcao: int) -> Missao:
        """
        Gera uma missão dinâmica e escalonada de acordo com o progresso do jogador.
        Garante a diversidade e unicidade dos nomes, encontros e recompensas das 3 opções.
        """
        # Define a dificuldade estritamente escalonada baseada no índice da opção (0=Fácil, 1=Médio, 2=Difícil)
        if indice_opcao == 0:
            dificuldade = max(1, 1 + int(reputacao // 15) + int(dia // 12))
            nome_sufixo = " (Fácil)"
        elif indice_opcao == 1:
            dificuldade = max(2, 2 + int(reputacao // 12) + int(dia // 10))
            nome_sufixo = " (Médio)"
        else:
            dificuldade = max(3, 3 + int(reputacao // 8) + int(dia // 6))
            nome_sufixo = " (Difícil)"

        # Nomes completamente únicos usando aritmética modular com o dia e o índice da opção
        prefixo = self.__prefixos[(indice_opcao + dia) % len(self.__prefixos)]
        local = self.__locais[(indice_opcao * 2 + dia) % len(self.__locais)]
        nome = f"{prefixo} {local}{nome_sufixo}"

        # Escalonamento e variabilidade randômica de recompensas
        ouro_base = 30 + (dificuldade * 20)
        xp_base = 20 + (dificuldade * 15)
        rep_base = 4 + (dificuldade * 4)

        # Variabilidade dinâmica de +-15% para ouro e +-10% para XP
        variacao_ouro = random.uniform(0.85, 1.15)
        variacao_xp = random.uniform(0.90, 1.10)

        recompensa_ouro = int(ouro_base * (1.0 + 0.05 * reputacao + 0.02 * dia) * variacao_ouro)
        recompensa_xp = int(xp_base * (1.0 + 0.03 * reputacao) * variacao_xp)
        recompensa_reputacao = rep_base

        # Descrição variada conforme a dificuldade
        descricoes = [
            f"Batedores avistaram criaturas corrompidas rondando a regiao de {local}. Limpe a area antes que os vilarejos vizinhos sofram mais ataques.",
            f"Rumores contam que uma reliquia magica do Mestre anterior foi vista em {local}. Adentre as ruinas com extremo cuidado.",
            f"Um portal menor de Nifl-Karr abriu-se em {local}, liberando orcs agressivos. Feche-o e elimine a guarda de elite inimiga."
        ]
        descricao = descricoes[min(len(descricoes) - 1, dificuldade - 1)]

        # Montagem dos encontros da missão
        encontros = []

        # Encontro 1: Narrativa interativo único (Diferente para cada uma das 3 missões do dia)
        encontros.append(self.obter_evento_por_indice(indice_opcao + dia * 3))

        # Encontro 2: Combate contra inimigos escalonados
        inimigos_combate = []
        qtd_inimigos = min(3, 1 + (dificuldade // 2) + random.randint(0, 1))
        rep_escalada_inimigos = max(0, reputacao + (dificuldade * 3) - 2)

        for _ in range(qtd_inimigos):
            inimigo = self.__fabrica_inimigos.gerar_inimigo(rep_escalada_inimigos)
            inimigos_combate.append(inimigo)
        encontros.append(EncontroCombate(inimigos_combate))

        # Encontro 3: Desafio extra para dificuldades médias e difíceis
        if dificuldade >= 2:
            if indice_opcao == 2:  # Difícil sempre tem um combate contra chefe campeão
                chefe = self.__fabrica_inimigos.gerar_inimigo(rep_escalada_inimigos + 3)
                chefe._nome = f"{chefe.nome.split()[0]} Campeão (Chefe)"
                encontros.append(EncontroCombate([chefe]))
            else:
                # Médio tem chance de 2º encontro de narrativa único
                encontros.append(self.obter_evento_por_indice(indice_opcao + 1 + dia * 3))

        missao = Missao(
            nome=nome,
            descricao=descricao,
            dificuldade=dificuldade,
            encontros=encontros,
            recompensa_ouro=recompensa_ouro,
            recompensa_xp=recompensa_xp,
            recompensa_reputacao=recompensa_reputacao
        )

        return missao
