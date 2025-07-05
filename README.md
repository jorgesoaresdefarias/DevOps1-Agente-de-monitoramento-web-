# High Level Design (HLD) — Sistema de Monitoramento Web em Containers Docker

---

## 1. Visão Geral do Sistema

O sistema tem como objetivo monitorar a qualidade de conexão e disponibilidade de alguns serviços web, realizando testes periódicos de ping e acesso HTTP a URLs específicas. Os resultados são armazenados em banco de dados e visualizados em dashboards Grafana para análise.

---

## 2. Componentes Principais

### 2.1. Agent de Monitoramento (monitor-agent)

- **Descrição:** Aplicação Python que executa periodicamente testes de rede.
- **Funções:**
  - Realizar testes de ping em hosts (google.com, youtube.com, rnp.br) para medir latência (RTT) e perda de pacotes.
  - Realizar requisições HTTP para medir tempo de carregamento e status HTTP (códigos 200, 404, etc).
  - Inserir os dados coletados no banco de dados PostgreSQL.
- **Implantação:** Empacotado em um container Docker, executado continuamente com intervalo configurável.

---

### 2.2. Banco de Dados (PostgreSQL)

- **Descrição:** Armazena os resultados dos testes realizados pelo agent.
- **Estrutura:**
  - Tabela `ping_results`: armazenando timestamp, host, RTT, perda de pacotes.
  - Tabela `http_results`: armazenando timestamp, URL, tempo de carregamento, código HTTP.
- **Implantação:** Rodando em container Docker com volume persistente para garantir durabilidade dos dados.

---

### 2.3. Visualização (Grafana)

- **Descrição:** Plataforma de dashboards para visualização dos dados coletados.
- **Funções:**
  - Conectar ao PostgreSQL para consulta dos dados.
  - Exibir gráficos de latência, perda de pacotes, tempos de carregamento e status HTTP.
  - Permitir filtro de tempo e detalhamento por URL/host.
- **Implantação:** Container Docker configurado para expor interface web na porta 3000.
  - O resultado do dashboard grafana pode ser encontrado no arquivo dashboard.json.

---

## 3. Fluxo de Dados

1. O `monitor-agent` executa os testes a cada intervalo (ex: 60 segundos).
2. Resultados são inseridos nas tabelas `ping_results` e `http_results` no banco PostgreSQL.
3. Grafana consulta periodicamente o banco e atualiza dashboards com gráficos e tabelas.
4. Usuário acessa o Grafana via navegador para análise e monitoramento.

---

## 4. Arquitetura e Comunicação

```
+-------------------+           +-------------------+           +-------------------+
|                   |  Inserts  |                   |  Queries  |                   |
|   monitor-agent    +---------->   PostgreSQL      +---------->     Grafana        |
| (Docker Container) |          | (Docker Container)|           | (Docker Container)|
+-------------------+           +-------------------+           +-------------------+
```

- Os containers estão orquestrados via Docker Compose, compartilhando uma rede virtual Docker.
- `monitor-agent` conecta ao banco pelo hostname `db` (nome do serviço Docker).
- Grafana conecta ao banco pelo mesmo hostname para leitura dos dados.

---

## 5. Tecnologias Utilizadas

| Componente     | Tecnologia / Ferramenta         |
| -------------- | ------------------------------- |
| Agent          | Python 3.10, Requests, psycopg2 |
| Banco de Dados | PostgreSQL 15                   |
| Visualização   | Grafana 10                      |
| Orquestração   | Docker, Docker Compose          |

---

## 6. Requisitos Não Funcionais

- **Disponibilidade:** O sistema deve rodar 24/7 com auto-recuperação via Docker.
- **Persistência:** Dados armazenados devem ser preservados mesmo após reinício do container.
- **Escalabilidade:** Fácil adição de novos hosts URLs para monitoramento.
- **Segurança:** Acesso ao Grafana protegido por senha.

---

## 7. Diagrama Simplificado

```plaintext
+------------------------+
|        Usuário         |
| (acesso via browser)   |
+-----------+------------+
            |
            v
+-----------+------------+
|         Grafana        |
| (dashboard e query SQL)|
+-----------+------------+
            |
            v
+-----------+------------+
|       PostgreSQL       |
|  (armazena resultados) |
+-----------+------------+
            ^
            |
+-----------+------------+
|    monitor-agent       |
| (realiza testes e insere dados) |
+------------------------+
```
