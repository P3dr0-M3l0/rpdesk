# Documentação Arquitetural - RpDesk

Este documento descreve a arquitetura de software do projeto RpDesk, um motor de gerenciamento de guilda em formato auto-battler. A estrutura foi construída utilizando puramente **Programação Orientada a Objetos (POO)** em Python, com forte ênfase no desacoplamento entre sistemas através de padrões de projeto consagrados.

---

## 1. Visão Geral: Casos de Uso
O diagrama de Casos de Uso mapeia as interações do Jogador/Diretor com o Sistema/Engine.

![Diagrama de Casos de Uso](./uml/diagrama-casos-uso.pdf)

As interações principais englobam a gestão de recursos e o desencadeamento de rotinas automatizadas pelo motor:
* **Gestão e Preparação:** O jogador atua ativamente para Gerenciar a Guilda, Formar Equipe, Gerenciar Inventário e Equipamentos, além de Recrutar/Demitir Heróis.
* **Controle de Fluxo e Persistência:** Ações globais como Avançar Turno/Tempo, Iniciar Expedição/Missão e Salvar e Carregar Jogo.
* **Automações do Motor:** Em resposta às ações do jogador, o sistema se encarrega de Gerar Entidades via Fábricas, Processar Lógica de Combate e Disparar/Resolver Eventos Reativos.

---

## 2. Visão Estática: Diagrama de Classes
A fundação do sistema é baseada em responsabilidades restritas (SOLID) e forte proteção de dados (Encapsulamento).

![Diagrama de Classes](./uml/diagrama-classes.pdf)

### Núcleo do Sistema (Core)
* **`GameController`**: Mantém as instâncias do `GerenciadorDeTempo`, `GameState` e `SaveManager`, conduzindo o loop principal do jogo.
* **`EventManager`**: Implementa a arquitetura *Pub/Sub*. Permite que métodos se inscrevam (`inscrever`) para ouvir callbacks e que o motor dispare eventos (`emitir_evento`) com carga de dados.

### Gestão e Fábricas
* **`Guilda`**: O contêiner de domínio. Gerencia os Heróis contratados e a reputação.
* **`Taverna`**: Ouve eventos de passagem de tempo para disponibilizar uma lista rotativa de novos Heróis.
* **Fábricas (`FabricaDeHerois`, `FabricaDeInimigos`, `FabricaDeItens`)**: Ocultam a complexidade de instanciar objetos compostos. A `FabricaDeHerois`, por exemplo, monta os atributos e injeta traços de personalidade aleatórios baseados na reputação da guilda.

### Entidades e Combate
* **`Entidade (ABC)`**: Classe abstrata base. Delega a proteção de dados vitais ao `ConjuntoDeAtributos` e a inteligência de ação para implementações filhas via `decidir_acao(contexto)`.
* **`ConjuntoDeAtributos`**: Encapsula e blinda atributos como `__vida`, permitindo alterações apenas através de métodos seguros como `receber_dano(valor)` e `curar(valor)`.
* **`Item (ABC)`**: Engloba instâncias como `Arma`, `PocaoCura` e itens que interagem indiretamente com o jogo, como o `AmuletoReativo`, que ouve o `EventManager`.

---

## 3. Visão Dinâmica: Diagramas de Sequência
Os diagramas abaixo ilustram como as classes colaboram durante as operações mais complexas do sistema, assegurando que o Polimorfismo e a Injeção de Dependência sejam respeitados.

### 3.1. Passagem de Tempo e Recrutamento
Descreve a atualização do cenário do jogo ao final de um turno. O padrão *Factory* é importante ao instanciar personagens sem acoplar a lógica na controladora.

![Sequência: Passagem de Tempo](./uml/diag-sequencia-tempo.pdf)
1. O `GameController` comanda o avanço chamando `avancar_dia()`.
2. O `GerenciadorDeTempo` notifica globalmente o "NovoDiaIniciado".
3. A `Taverna`, previamente inscrita, reage acionando `gerar_pool_recrutamento()`.
4. Dentro de um loop iterativo, a `Taverna` solicita instâncias à `FabricaDeHerois`, que constrói e retorna os novos recrutas.

### 3.2. Orquestração de Expedição
Demonstra o uso de Injeção de Dependências. A missão não instancia sua própria lógica de conflito; ela recebe o motor de fora, mantendo seu propósito restrito a gerenciar o mapa e relatar o fim da viagem.

![Sequência: Início de Expedição](./uml/diag-sequencia-expedicao.pdf)
1. O `GameController` solicita à `Guilda` a formação da `Equipe`.
2. O controlador invoca a `Missao` e injeta a `equipe` e o `motor_de_combate`.
3. A `Missao` itera sobre seu `_mapa_encontros`. Quando detecta combate, cede controle temporário, invocando `rodar_turno()` do motor.
4. Ao concluir, a `Missao` avisa o `EventManager` com o status "ExpedicaoFinalizada", retornando o controle passivamente via callbacks.

### 3.3. Ciclo de Combate e Resolução de Dano
O gargalo lógico do projeto. Aplica Polimorfismo distribuído (quem toma as decisões são as entidades) e uma arquitetura baseada em eventos para reações automatizadas de itens.

![Sequência: Ciclo de Combate](./uml/diag-sequencia-combate.pdf)
1. No início da Fila de Iniciativa, o `MotorDeCombate` exige a intenção polimórfica com `decidir_acao(contexto)`.
2. Se a entidade for um Herói com `TracoPersonalidade`, ele usa `avaliar_situacao` para enviar um modificador de decisão e estruturar o retorno.
3. O motor calcula e aplica `receber_dano(valor)` aos `Atributos (Alvo)`.
4. Os atributos blindam a variável e notificam "EntidadeDanoRecebido" no `EventManager`.
5. Caso equipado, o `AmuletoReativo` escuta a notificação e aciona autonomamente o método `curar()`.

### 3.4. Persistência de Dados (Save/Load)
Evidencia a delegação de responsabilidades na conversão de memória para disco.

![Sequência: Processo de Save](./uml/diag-sequencia-save.pdf)
1. Ativado por `salvar_jogo(estado_atual)`, o `SaveManager` exige os dados em cascata invocando `get_estado_para_save()` no `GameState`.
2. O `GameState` delega as partes específicas: chama `serializar()` na `Guilda`, que converte seus atributos locais e a lista de heróis em dicionário.
3. O `GameState` empacota tudo e entrega ao `SaveManager`.
4. O `SaveManager` executa a operação final de entrada e saída (I/O) formatando em JSON e gravando no HD, avisando que o jogo foi salvo com sucesso via evento.
