# Contexto e arquitetura

Este trabalho leva o cenário da academia do [Trabalho 1](https://github.com/02kamk/apachespark) para uma arquitetura
mais próxima da realidade: os dados **nascem num banco relacional (SQL Server)**, são **extraídos para um Data Lake
(MinIO)** e lá viram **tabelas Delta Lake**, onde aplicamos os mesmos comandos DML do Trabalho 1.

!!! abstract "Objetivo"
    1. Extrair **todas as tabelas** de um banco SQL Server e gravá-las em **CSV** no bucket `landing-zone` do MinIO.
    2. Ler esses CSVs com o Spark e gravá-los em **Delta Lake** no bucket `bronze`.
    3. Reproduzir os **INSERT, UPDATE e DELETE** do Trabalho 1 nas tabelas Delta do bucket `bronze`.
    4. Analisar a diferença entre **tabelas gerenciadas e não gerenciadas**.

## Arquitetura

![Arquitetura do pipeline](assets/arquitetura.png)

Pense numa padaria. O SQL Server é o **caixa da loja**: registra cada venda na hora, com regras rígidas e sem erro.
Mas ninguém faz o relatório do mês dentro do caixa, porque isso atrapalharia o atendimento. Então, no fim do dia,
alguém copia os registros para o **depósito** (o Data Lake). Primeiro a cópia chega do jeito que veio, empilhada
na entrada (a **landing zone**). Depois ela é organizada em prateleiras com etiqueta e controle de entrada e saída
(a camada **bronze**, em Delta Lake). É sobre esse depósito organizado que os analistas trabalham.

Cada peça da imagem tem um papel:

| Peça | Papel no pipeline | Onde roda |
|---|---|---|
| **SQL Server 2025** | fonte relacional: o sistema "oficial" da academia, com PK e FK | container Docker, porta 1433 |
| **MinIO** | armazenamento de objetos compatível com Amazon S3: o Data Lake | container Docker, portas 9020 (API) e 9021 (console) |
| **Bucket `landing-zone`** | cópia bruta da fonte, 1 CSV por tabela | dentro do MinIO |
| **Bucket `bronze`** | mesmos dados em Delta Lake: ACID, histórico, DML | dentro do MinIO |
| **Apache Spark (PySpark)** | lê os CSVs, grava e altera as tabelas Delta | no Ubuntu, pelo ambiente `.venv` |

!!! info "Arquitetura medalhão"
    `landing-zone` e `bronze` são as primeiras camadas da chamada **arquitetura medalhão**. As próximas seriam a
    **silver** (dados limpos e padronizados) e a **gold** (tabelas prontas para relatórios), que não fazem parte deste trabalho.

## Roteiro dos notebooks

| Notebook | O que faz | Detalhes |
|---|---|---|
| `00_setup_sqlserver` | cria o banco `AcademiaDB` com 5 tabelas e carrega os CSVs da pasta `data/` | [SQL Server → Landing Zone](extracao.md) |
| `01_sqlserver_to_minio_csv` | extrai todas as tabelas do SQL Server para CSV no bucket `landing-zone` | [SQL Server → Landing Zone](extracao.md) |
| `02_csv_to_delta` | lê os CSVs e grava as tabelas em Delta Lake no bucket `bronze` | [Bronze: Delta Lake e DML](delta.md) |
| `03_dml_delta` | reproduz os DML do Trabalho 1 no bronze, mostra HISTORY e TIME TRAVEL | [Bronze: Delta Lake e DML](delta.md) |
| `04_gerenciadas_vs_nao_gerenciadas` | compara tabelas gerenciadas e externas na prática | [Gerenciadas × não gerenciadas](gerenciadas.md) |

## O que mudou em relação ao Trabalho 1

| | Trabalho 1 | Trabalho 2 |
|---|---|---|
| Origem dos dados | `INSERT` escrito no próprio notebook | banco **SQL Server**, extraído por código |
| Onde ficam as tabelas | pasta local `spark-warehouse/` | **MinIO** (buckets `landing-zone` e `bronze`) |
| Formatos | Delta Lake **e** Iceberg | só **Delta Lake** (o enunciado não pede Iceberg) |
| Tabelas | 3 (`planos`, `alunos`, `checkins`) | **5** (+ `unidades` e `pagamentos`) |
| Volume | 5 alunos, 8 check-ins | 300 alunos, 7.684 check-ins, 2.156 pagamentos |
| Infraestrutura | só o Spark | Spark + 2 containers Docker |

!!! tip "Como instalar e rodar"
    Os pré-requisitos, as versões e o passo a passo de instalação estão no **README** do repositório.
    Esta documentação explica **o que o projeto faz e por quê**.

## Integrantes

- Kamily Hilário das Luzes
- Kauã Lucas Alves Barbosa
