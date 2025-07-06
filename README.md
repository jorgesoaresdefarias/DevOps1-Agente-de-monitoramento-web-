# High Level Design (HLD) — Sistema de Monitoramento Web em Containers Docker

---

## 1. Visão Geral do Sistema

O sistema tem como objetivo monitorar a qualidade de conexão e disponibilidade de alguns serviços web, realizando testes periódicos de ping, acesso HTTP e coleta de estatísticas de APIs externas como o **ViaIpe**. Os resultados são armazenados em banco de dados e visualizados em dashboards Grafana para análise.

## ⚠️ Aviso: Os prints de tela dos dashboards do Grafana estão localizados no diretório images.

## 2. Componentes Principais

### 2.1. Agent de Monitoramento (`monitor-agent`)

- **Descrição:** Aplicação Python que executa periodicamente testes de rede.
- **Funções:**
  - Realizar testes de ping em hosts (google.com, youtube.com, rnp.br) para medir latência (RTT) e perda de pacotes.
  - Realizar requisições HTTP para medir tempo de carregamento e status HTTP (códigos 200, 404, etc).
  - Inserir os dados coletados no banco de dados PostgreSQL.
- **Implantação:** Empacotado em um container Docker, executado continuamente com intervalo configurável.

### 2.2. Agent ViaIpe (`viaipe-agent`)

- **Descrição:** Aplicação Python separada, responsável por consultar a API externa ViaIpe.
- **Funções:**
  - Acessar periodicamente a API do ViaIpe.
  - Coletar métricas de disponibilidade por cliente.
  - Inserir os dados coletados na tabela `viaipe_stats` no banco de dados PostgreSQL.
- **Implantação:** Empacotado em um container Docker independente, com execução periódica configurável.

### 2.3. Banco de Dados (PostgreSQL)

- **Descrição:** Armazena os resultados dos testes realizados pelos agentes.
- **Estrutura:**
  - Tabela `ping_results`: armazenando `timestamp`, `host`, `RTT`, perda de pacotes.
  - Tabela `http_results`: armazenando `timestamp`, `URL`, tempo de carregamento, código HTTP.
  - Tabela `viaipe_stats`: armazenando `timestamp`, `cliente`, `disponibilidade` e outros campos extraídos da API do ViaIpe.
- **Implantação:** Rodando em container Docker com volume persistente para garantir durabilidade dos dados.

### 2.4. Visualização (Grafana)

- **Descrição:** Plataforma de dashboards para visualização dos dados coletados.
- **Funções:**
  - Conectar ao PostgreSQL para consulta dos dados.
  - Exibir gráficos de latência, perda de pacotes, tempos de carregamento e status HTTP.
  - Exibir dashboards com a **qualidade da conexão por cliente ao longo do tempo**, com base nos dados da API ViaIpe.
  - Permitir filtro de tempo e detalhamento por URL/host/cliente.
- **Implantação:** Container Docker configurado para expor interface web na porta 3000.
  - O resultado do dashboard principal está no arquivo `dashboard.json`.
  - O dashboard do ViaIpe está no arquivo `viaipe_dashboard.json`.

---

## 3. Fluxo de Dados

1. O `monitor-agent` executa testes de rede a cada intervalo configurado (ex: 60 segundos).
2. O `viaipe-agent` consulta periodicamente a API do ViaIpe e coleta métricas por cliente.
3. Os resultados são inseridos nas tabelas `ping_results`, `http_results` e `viaipe_stats` no banco PostgreSQL.
4. Grafana consulta periodicamente o banco e atualiza os dashboards com gráficos e tabelas.
5. Usuário acessa o Grafana via navegador para análise e monitoramento.

---

## 4. Arquitetura e Comunicação

```plaintext
                    +---------------------+
                    |    monitor-agent    |
                    |  (ping + HTTP)      |
                    +----------+----------+
                               |
                               | INSERTs
                               v
                    +----------+----------+
                    |    PostgreSQL DB    |
                    |    (via Docker)     |
                    +----------+----------+
                               ^
                               | INSERTs
                    +----------+----------+
                    |     viaipe-agent     |
                    |  (consulta à API)    |
                    +----------------------+

                    +----------------------+
                    |       Grafana        |
                    | (dashboards via web) |
                    +----------+-----------+
                               |
                               | Queries
                               v
                    +----------------------+
                    |    viaipe_stats      |
                    |   (PostgreSQL table) |
                    +----------------------+

```

Os containers estão orquestrados via Docker Compose, compartilhando uma rede virtual Docker.

Ambos os agentes (monitor-agent e viaipe-agent) conectam ao banco pelo hostname db.

Grafana conecta ao banco pelo mesmo hostname para leitura dos dados.

## 5. Tecnologias Utilizadas

| Componente     | Tecnologia / Ferramenta         |
| -------------- | ------------------------------- |
| monitor-agent  | Python 3.10, Requests, psycopg2 |
| viaipe-agent   | Python 3.10, Requests, psycopg2 |
| Banco de Dados | PostgreSQL 15                   |
| Visualização   | Grafana 10                      |
| Orquestração   | Docker, Docker Compose          |
| API Externa    | ViaIpe                          |

## 6. Requisitos Não Funcionais

Disponibilidade: O sistema deve rodar 24/7 com auto-recuperação via Docker.

Persistência: Dados armazenados devem ser preservados mesmo após reinício dos containers.

Escalabilidade: Fácil adição de novos hosts, URLs e clientes da API para monitoramento.

Segurança: Acesso ao Grafana protegido por senha.

## 7. Diagrama Simplificado

```
+------------------------+
|        Usuário         |
| (acesso via browser)   |
+-----------+------------+
            |
            v
+-----------+------------+               +---------------------------+
|         Grafana        | <-----------  |  viaipe_stats (PostgreSQL)|
| (dashboard e query SQL)|               +---------------------------+
+-----------+------------+
            |
            v
+-----------+------------+
|       PostgreSQL       |
|  (armazena resultados) |
+-----------+------------+
     ^            ^
     |            |
     |            |
+----+---+    +---+-----+
| monitor |    | viaipe |
|  agent  |    | agent  |
+-------- +    +--------+
```
