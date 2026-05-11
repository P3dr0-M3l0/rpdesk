# RpDesk

## Índice

- [Descrição do Projeto](##descrição-do-projeto)
    
- [Status do Projeto](##status-do-projeto)
    
- [Arquitetura e Funcionalidades Planejadas](##arquitetura-e-funcionalidades-planejadas)
    
- [Tecnologias Utilizadas](##tecnologias-utilizadas)
    
- [Desenvolvedores do Projeto](##desenvolvedores-do-projeto)
    
- [Licença](##licença)
    

## Descrição do Projeto

O **RpDesk** é um motor de gerenciamento de RPG desenvolvido puramente em backend. O jogador assume o papel de diretor de uma guilda, responsável por recrutar heróis, gerenciar inventários, montar equipes e orquestrar expedições automatizadas.

O motor foi projetado com um objetivo central: a aplicação prática e rigorosa da Programação Orientada a Objetos (POO). Este projeto atua como um laboratório arquitetural para consolidar os estudos e conhecimentos de engenharia de software desenvolvidos na Universidade de Brasília (UnB), garantindo um código altamente desacoplado e escalável. Os quatro pilares da POO (Herança, Polimorfismo, Encapsulamento e Abstração) são explorados, em conjunto com relações de Composição, Agregação e Dependência.

## Status do Projeto

> 🚧 Projeto em construção 🚧

O desenvolvimento encontra-se na etapa inicial. A fase de documentação UML (Diagramas de Classe, Casos de Uso e Sequência) e arquitetura estrutural está concluída. A implementação em código dos sistemas de núcleo e regras de negócio começará em breve.

## Arquitetura e Funcionalidades Planejadas

Como a estrutura está em sua primeira iteração e focada no design, a lista abaixo descreve a arquitetura baseada em POO que será transcrita para o Python:

- **Inteligência Distribuída e Polimorfismo**: Heróis e Inimigos não são controlados por uma classe centralizadora. Cada entidade decide sua própria ação em combate baseando-se em seus atributos e Traços de Personalidade polimórficos.
    
- **Arquitetura Orientada a Eventos**: Um `EventManager` gerenciará notificações assíncronas. Eventos globais ocorrem de forma  independente sem a necessidade de passarem pelo motor principal.
    
- **Padrões de Projeto (Factory)**: Delegação da criação de objetos complexos (como montagem de heróis com status variados e itens do inventário) para classes fábrica específicas.
    
- **Encapsulamento Estrito**: O núcleo de combate orquestra o jogo, mas dados sensíveis (como os pontos de vida) são restritos e protegidos dentro da classe `ConjuntoDeAtributos`.
    

## Tecnologias Utilizadas

- **Python 3.12.3**: Linguagem principal escolhida para aplicar os paradigmas da orientação a objetos.
    
- **Mermaid / UML**: Utilizados para diagramação lógica e estrutural do sistema (disponíveis na pasta `docs/`).
    

## Desenvolvedores do Projeto

- **Pedro Oliveira Melo** - Arquiteto de Software e Desenvolvedor.
    

## Licença

Copyright (c) 2026 Pedro Oliveira Melo. Todos os direitos reservados.

O código-fonte e a arquitetura deste repositório são disponibilizados publicamente de forma exclusiva para fins de visualização acadêmica e avaliação de portfólio. Nenhuma permissão é concedida para a reprodução, modificação, distribuição ou utilização comercial de qualquer parte do projeto sem autorização expressa.
