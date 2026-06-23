# RpDesk

# Índice

- [Descrição do Projeto](#descrição-do-projeto)
    
- [Status do Projeto](#status-do-projeto)
    
- [Arquitetura e Funcionalidades Implementadas](#arquitetura-e-funcionalidades-implementadas)
    
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
    
- [Desenvolvedores do Projeto](#desenvolvedores-do-projeto)
    
- [Licença](#licença)
    

# Descrição do Projeto

O **RpDesk** é um motor de gerenciamento de RPG desenvolvido puramente em backend. O jogador assume o papel de diretor de uma guilda, responsável por recrutar heróis na Taverna, gerenciar inventários e baús, montar equipes de expedição e orquestrar expedições automatizadas com combates em turnos.

O motor foi projetado com um objetivo central: a aplicação prática e rigorosa da Programação Orientada a Objetos (POO). Este projeto atua como um laboratório arquitetural para consolidar os estudos e conhecimentos de engenharia de software desenvolvidos na Universidade de Brasília (UnB), garantindo um código altamente desacoplado e escalável. Os quatro pilares da POO (Herança, Polimorfismo, Encapsulamento e Abstração) são explorados em conjunto com relações de Composição, Agregação e Dependência.

# Status do Projeto

> ✔ MVP Concluído e Funcional ✔

A primeira versão do MVP (Minimum Viable Product) está totalmente implementada e pronta para jogar. Os sistemas principais de combate, gerenciamento de equipes, inventários, taverna, ciclo de dias e condições de Game Over foram testados e refinados para garantir uma experiência de jogo fluida e coesa através de uma Interface de Terminal (TUI) polida.

# Arquitetura e Funcionalidades Implementadas

O projeto foi construído sobre uma arquitetura orientada a objetos robusta, apresentando as seguintes funcionalidades:

- **Loop Principal de Jogo (Game Loop)**: Permite navegar entre os menus do jogo de forma interativa através do terminal com um HUD Global customizável que exibe a página atual, ouro, reputação e dia corrente em caixas cinzas de caixa dupla estilizadas.
- **Contratação na Taverna**: A Taverna renova os recrutas a cada dia. O custo básico para contratar um herói é de **50 moedas de ouro** (com escalonamento por reputação), contando com prompt de confirmação de compra antes da transação.
- **Gerenciamento de Equipes**:
  - Limite estrito de no máximo **3 equipes ativas** simultâneas.
  - Tela principal das equipes exibindo a lotação dos membros e o **XP médio dos integrantes** (com base no XP total acumulado: `xp + (nivel - 1) * 100`).
  - Menu de edição de equipes em formato de tabela elegante com detecção de cancelamento.
- **Transferência do Baú da Guilda**: Permite transitar itens livremente entre o baú central da guilda e o inventário dos heróis, sinalizando claramente o local de cada herói (`Roster (Disponível)` ou a equipe de expedição em que se encontra alocado).
- **Combate de Turnos e Expedições**:
  - Expedições automatizadas acionadas via motor de combate polimórfico com suporte para múltiplos encontros.
  - Narração compassada em terminal com delay de **1.5 segundos por ação** e prefixagem estruturada (ex: `[ATAQUE]`, `[CURA]`, `[MORTE]`, `[TURNO]`).
  - Resumo final da batalha renderizado em uma caixa de layout ASCII detalhada exibindo ouro ganho, reputação, XP, sobreviventes e baixas.
- **Ciclo de Dias e Game Over**:
  - O jogador pode encerrar o dia para atualizar a vitrine da taverna, pagando uma taxa de manutenção de **10 moedas de ouro**.
  - O estado de **Game Over** é disparado caso a guilda perca todos os seus heróis (0 heróis no roster e nas equipes) e não tenha ouro suficiente para contratar um novo recruta na taverna (menos de 50 de ouro).

# Tecnologias Utilizadas

- **Python 3.12.3**: Linguagem principal escolhida para aplicar os paradigmas da orientação a objetos.
- **Pytest**: Suíte de testes automatizados integrada para validação das regras de negócios de XP, combate e missões.
- **Mermaid / UML**: Utilizados para diagramação lógica e estrutural do sistema (disponíveis na pasta `docs/`).

# Desenvolvedores do Projeto

- **Pedro Oliveira Melo** - Arquiteto de Software e Desenvolvedor.

# Licença

Copyright (c) 2026 Pedro Oliveira Melo. Todos os direitos reservados.

O código-fonte e a arquitetura deste repositório são disponibilizados publicamente de forma exclusiva para fins de visualização acadêmica e avaliação de portfólio. Nenhuma permissão é concedida para a reprodução, modificação, distribuição ou utilização comercial de qualquer parte do projeto sem autorização expressa.
