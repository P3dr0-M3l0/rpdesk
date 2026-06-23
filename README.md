<h1 align="center">RpDesk ⚔️</h1>

<p align="center">
  <img src="https://img.shields.io/badge/STATUS-MVP%20CONCLU%C3%8DDO-brightgreen?style=for-the-badge" alt="Status MVP Concluído">
  <img src="https://img.shields.io/badge/Python-3.12.3-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Tests-Pytest-brightgreen?style=for-the-badge&logo=pytest&logoColor=white" alt="Tests Pytest">
  <img src="https://img.shields.io/badge/License-Propriet%C3%A1ria-orange?style=for-the-badge" alt="Licença Proprietária">
</p>

O **RpDesk** é um motor de gerenciamento de guilda de RPG desenvolvido inteiramente em Python para execução via terminal. Nele, você assume o papel de diretor de uma guilda de heróis, lidando com contratações, gerenciamento de recursos, distribuição de equipamentos e missões automáticas narradas com combate em turnos.

O projeto serve como laboratório prático para consolidar conceitos de engenharia de software e Programação Orientada a Objetos (POO), aplicando os quatro pilares (Herança, Polimorfismo, Encapsulamento e Abstração) e relações como Composição, Agregação e Dependência de forma rigorosa e desacoplada.

---

## 📌 Índice

- [Descrição do Projeto](#-descrição-do-projeto)
- [Status do Projeto](#-status-do-projeto)
- [Funcionalidades e Recursos](#️-funcionalidades-e-recursos)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Como Rodar o Projeto](#-como-rodar-o-projeto)
- [Como Rodar os Testes](#-como-rodar-os-testes)
- [Autores](#-autores)
- [Licença](#-licença)

---

## 📖 Descrição do Projeto

O RpDesk foi planejado para ser um motor de simulação de RPG rodando em linha de comando (TUI). O jogador gerencia os recursos de sua guilda (ouro, reputação, membros e baú de itens) com o objetivo de treinar e manter heróis para realizar expedições lucrativas.

O grande diferencial do projeto está na aplicação limpa da arquitetura de software:
- **Desacoplamento por Eventos**: Comunicação assíncrona orientada a eventos para atualizar estados do jogo.
- **Polimorfismo em Combates/Encontros**: Estruturação modular de encontros textuais e encontros de combate herdando de classes abstratas comuns.
- **Fábricas Abstratas**: Criação de heróis, inimigos e itens padronizados através de fábricas estruturadas.

---

## ⚡ Status do Projeto

> 🟢 **MVP (Minimum Viable Product) Concluído e Funcional**

A primeira versão está estável e completamente jogável, cobrindo o loop de jogo diário, gerenciamento de equipes, combate de turnos dinâmico, baú de itens da guilda e as condições de Game Over.

---

## 🛠️ Funcionalidades e Recursos

*   **Game Loop Interativo**: Menu de terminal polido com exibição de HUD persistente estilizado em caracteres de caixa dupla ASCII (exibindo dia, ouro, reputação e página ativa).
*   **Recrutamento na Taverna**: A vitrine da taverna se renova diariamente trazendo novos heróis disponíveis para contratação por um custo ajustável segundo a reputação da guilda.
*   **Gestão de Equipes**:
    *   Criação e gerenciamento de até **3 equipes ativas** simultâneas de heróis.
    *   Exibição de nível de experiência médio dos integrantes em tabelas formatadas no terminal.
*   **Baú Central da Guilda**: Sistema de armazenamento compartilhado que permite mover itens consumíveis e equipamentos de forma bidirecional entre o baú central e o inventário de heróis específicos.
*   **Combate por Turnos Dinâmico**:
    *   Execução automática de missões baseada em múltiplos encontros (histórias e batalhas contra inimigos).
    *   Combates por turnos com narração compassada e tags visuais.
    *   Resumo final com balanço detalhado de XP, ouro e reputação adquiridos, além do saldo de sobreviventes e baixas.
*   **Ciclo de Dias e Manutenção**: Mudança de dia que atualiza a taverna ao custo de taxa fixa diária de manutenção da guilda.
*   **Condição de Game Over**: Disparado caso a guilda perca todos os seus heróis e não tenha moedas suficientes para novas contratações na taverna.

---

## 📁 Estrutura do Projeto

O código está organizado de forma modular e limpa dentro do diretório `src/`:

```text
src/
├── core/         # Gerenciadores de estado, eventos, tempo e salvamento
├── entidades/    # Classes de heróis, inimigos e inventários
├── factories/    # Fábricas de heróis, inimigos e itens
├── gestao/       # Definições de guilda, taverna e missões
├── itens/        # Equipamentos, consumíveis e definições de itens
├── motor/        # Motor de batalha e execução de encontros
└── main.py       # Ponto de entrada do jogo
```

---

## 💻 Tecnologias Utilizadas

- **Python 3.12.3**
- **Pytest 9.0.3** (Suite de testes unitários)
- **Mermaid / UML** (Para mapeamento das relações e arquitetura de classes)

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
- Python instalado (versão recomendada: **3.12.x**)

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/P3dr0-M3l0/rpdesk.git
   cd rpdesk
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Linux/macOS
   # ou
   .venv\Scripts\activate     # No Windows
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o jogo:**
   ```bash
   python src/main.py
   ```

---

## 🧪 Como Rodar os Testes

Para garantir que todas as regras de negócios, combate e sistemas de XP estejam operacionais:

```bash
pytest
```

---

## 👤 Autores

| [<img src="https://avatars.githubusercontent.com/u/223511182?v=4" width=115><br><sub>Pedro Oliveira Melo</sub>](https://github.com/P3dr0-M3l0) |
| :---: |

---

## 📄 Licença

Copyright © 2026 Pedro Oliveira Melo. Todos os direitos reservados.

O código-fonte e a arquitetura contidos neste repositório são disponibilizados de forma exclusiva para fins de visualização acadêmica e portfólio. Nenhuma permissão é concedida para reprodução, modificação, distribuição ou uso comercial de qualquer parte do projeto sem autorização prévia por escrito.
