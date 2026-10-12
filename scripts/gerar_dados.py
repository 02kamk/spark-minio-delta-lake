"""Gera os CSVs de exemplo da academia na pasta data/.

O conjunto de dados é fictício e foi criado pelo grupo. Os 5 primeiros alunos, os 3 primeiros
planos e os 8 primeiros check-ins são os mesmos do Trabalho 1, para que os comandos DML do
Trabalho 1 possam ser reproduzidos sobre as tabelas Delta do bucket bronze.

A geração é determinística (semente fixa): rodar de novo produz exatamente os mesmos arquivos.

Uso (na raiz do projeto):
    uv run python scripts/gerar_dados.py
"""

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

random.seed(42)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

FIM_PERIODO = date(2024, 8, 31)


def salvar(nome, colunas, linhas):
    with open(DATA_DIR / f"{nome}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(colunas)
        w.writerows(linhas)
    print(f"{nome:<11} {len(linhas):>6} linhas")


# ------------------------------------------------------------------ unidades (NOVA)
unidades = [
    (1, "Centro", "Criciúma", "Centro", "2015-03-02"),
    (2, "Próspera", "Criciúma", "Próspera", "2018-08-13"),
    (3, "Pinheirinho", "Criciúma", "Pinheirinho", "2021-02-01"),
    (4, "Içara", "Içara", "Centro", "2023-05-15"),
]
salvar("unidades", ["id_unidade", "nome", "cidade", "bairro", "data_inauguracao"], unidades)

# ------------------------------------------------------------------ planos
planos = [
    (1, "Mensal", "99.90", 1),
    (2, "Trimestral", "269.70", 3),
    (3, "Anual", "899.00", 12),
    (4, "Semestral", "509.40", 6),
]
salvar("planos", ["id_plano", "nome", "valor_mensal", "duracao_meses"], planos)
valor_plano = {p[0]: float(p[2]) for p in planos}
duracao_plano = {p[0]: p[3] for p in planos}

# ------------------------------------------------------------------ alunos
alunos = [
    # os mesmos 5 alunos do Trabalho 1
    (1, "Ana Souza", "ana@email.com", "Criciúma", 1, "2024-01-10", True),
    (2, "Bruno Lima", "bruno@email.com", "Içara", 3, "2024-02-05", True),
    (3, "Carla Mendes", "carla@email.com", "Criciúma", 2, "2024-03-12", True),
    (4, "Diego Rocha", "diego@email.com", "Forquilhinha", 1, "2024-04-20", False),
    (5, "Elisa Martins", "elisa@email.com", "Criciúma", 3, "2024-05-02", True),
]
nomes = ["Lucas", "Mariana", "Pedro", "Juliana", "Rafael", "Camila", "Thiago", "Larissa", "Gustavo",
         "Beatriz", "Rodrigo", "Fernanda", "Leonardo", "Patrícia", "Matheus", "Aline", "Vinícius",
         "Bianca", "Eduardo", "Letícia", "Henrique", "Natália", "Diogo", "Isabela", "Marcelo",
         "Renata", "André", "Tatiane", "Caio", "Vanessa", "Otávio", "Priscila", "Samuel", "Jéssica"]
sobrenomes = ["Silva", "Santos", "Oliveira", "Pereira", "Ferreira", "Rodrigues", "Almeida",
              "Nascimento", "Carvalho", "Gomes", "Ribeiro", "Martins", "Rocha", "Barbosa", "Dias",
              "Teixeira", "Moreira", "Cardoso", "Vieira", "Machado", "Zanette", "De Luca"]
cidades = ["Criciúma"] * 6 + ["Içara"] * 2 + ["Forquilhinha", "Nova Veneza", "Morro da Fumaça"]
usados = {"Felipe Costa", "Gabriela Alves"}  # reservados para os INSERT/MERGE do notebook 03
inicio_mat = date(2023, 1, 2)
for id_aluno in range(6, 301):
    while True:
        nome = f"{random.choice(nomes)} {random.choice(sobrenomes)}"
        if nome not in usados:
            usados.add(nome)
            break
        if len(usados) > 600:
            break
    email = (nome.lower().replace(" ", ".")
             .translate(str.maketrans("áâãéêíóôõúç", "aaaeeiooouc")) + f"{id_aluno}@email.com")
    mat = inicio_mat + timedelta(days=random.randint(0, 545))
    alunos.append((id_aluno, nome, email, random.choice(cidades),
                   random.choices([1, 2, 3, 4], weights=[45, 20, 15, 20])[0],
                   mat.isoformat(), random.random() < 0.85))
salvar("alunos", ["id_aluno", "nome", "email", "cidade", "id_plano", "data_matricula", "ativo"], alunos)

# ------------------------------------------------------------------ checkins (agora com id_unidade)
checkins = [
    # os mesmos 8 check-ins do Trabalho 1 (Centro = 1, Próspera = 2)
    (1, 1, 1, "2024-06-03 07:15:00"),
    (2, 2, 2, "2024-06-03 18:40:00"),
    (3, 1, 1, "2024-06-04 07:05:00"),
    (4, 3, 1, "2024-06-04 19:10:00"),
    (5, 4, 2, "2024-06-05 06:50:00"),
    (6, 5, 1, "2024-06-05 12:30:00"),
    (7, 4, 2, "2024-06-06 06:55:00"),
    (8, 2, 2, "2024-06-06 18:20:00"),
]
gerados = []
inicio_ck = date(2024, 6, 1)
for (id_aluno, _n, _e, cidade, _p, mat, ativo) in alunos:
    if id_aluno == 4:          # Diego fica só com os 2 check-ins do Trabalho 1
        continue
    unidade_pref = 4 if cidade == "Içara" else random.choice([1, 2, 3])
    freq = random.uniform(1.0, 3.5) if ativo else random.uniform(0.0, 0.6)  # visitas por semana
    dia = max(inicio_ck, date.fromisoformat(mat))
    while dia <= FIM_PERIODO:
        if random.random() < freq / 7:
            hora = random.choice([6, 7, 8, 12, 17, 18, 19, 20])
            ts = datetime(dia.year, dia.month, dia.day, hora, random.randint(0, 59))
            unidade = unidade_pref if random.random() < 0.85 else random.randint(1, 4)
            gerados.append((id_aluno, unidade, ts))
        dia += timedelta(days=1)
gerados.sort(key=lambda r: r[2])
for i, (id_aluno, unidade, ts) in enumerate(gerados, start=9):
    checkins.append((i, id_aluno, unidade, ts.strftime("%Y-%m-%d %H:%M:%S")))
salvar("checkins", ["id_checkin", "id_aluno", "id_unidade", "data_hora"], checkins)

# ------------------------------------------------------------------ pagamentos (NOVA)
pagamentos = []
id_pag = 1
for (id_aluno, _n, _e, _c, id_plano, mat, ativo) in alunos:
    mat = date.fromisoformat(mat)
    comp = date(max(mat.year, 2024), 1 if mat.year < 2024 else mat.month, 1)
    meses = 0
    while comp <= date(2024, 8, 1):
        valor = round(valor_plano[id_plano] / duracao_plano[id_plano], 2)
        forma = random.choices(["PIX", "CARTAO", "BOLETO"], weights=[50, 35, 15])[0]
        if not ativo and meses >= 2:
            status, pago_em = "ATRASADO", ""
        elif comp == date(2024, 8, 1) and random.random() < 0.25:
            status, pago_em = "PENDENTE", ""
        else:
            status = "PAGO"
            pago_em = (comp + timedelta(days=random.randint(0, 12))).isoformat()
        pagamentos.append((id_pag, id_aluno, comp.isoformat(), pago_em, f"{valor:.2f}", forma, status))
        id_pag += 1
        meses += 1
        comp = date(comp.year + (comp.month // 12), comp.month % 12 + 1, 1)
salvar("pagamentos", ["id_pagamento", "id_aluno", "competencia", "data_pagamento", "valor",
                      "forma_pagamento", "status"], pagamentos)
