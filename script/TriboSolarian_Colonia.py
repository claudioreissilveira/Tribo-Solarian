"""
# 🌱 **Colônia em Marte | Sistema Integrado da Colônia | Life Solarian**

***Equipe Tribo Solarian***

Protótipo da Fase 3 (Colônia em Marte). O script está dividido em partes,
cada parte tem uma apresentação (o que a seção faz e como funciona), seguida pelo espaço 
onde fica  o código correspondente. As seções citadas são as do material 
de apoio `docs/Colonia_material_apoio.docx`. Os documentos ficam em `docs/` e 
as prints ficam em `testes/`. 

## Repositório do projeto:
    <https://github.com/claudioreissilveira/Tribo-Solarian/tree/3-Colonia>

## Integrantes
- Cláudio Roberto Grillo Reis Silveira | RM575353
- Vitor Lima Montiel | RM575458
- Wallace Gabriel Américo Albuquerque | RM575435
- Victor Augusto dos Santos Souza | RM576021
- Thales Martins Oliveira Barros | RM574664

## Como executar
    python script/TriboSolarian_Colonia.py

## Sumário
- Parte 0, bibliotecas e configuração
- Parte 1, constantes, limiares e padrões
- Parte 2, módulos e estruturas de dados
- Parte 3, entrada de dados manual
- Parte 4, preparação do cenário e dos dados de avaliação
- Parte 5, classificação e regras de decisão
- Parte 6, prioridades e recomendações de equilíbrio
- Parte 7, modelos matemáticos e previsão
- Parte 8, avaliação integrada e menu principal
- Parte 9, exemplos de execução

## Contribuições por bloco
- Bloco 1, Montiel: fundação, solar e balanço energético.
- Bloco 2, Souza: eólica e regressão.
- Bloco 3, Cláudio: oxigênio e alimentos.
- Bloco 4, Thales: operações e recomendações.
- Bloco 5, Wallace: clima, riscos e integração.

O desenvolvimento segue essa sequência, mas cada bloco contribui nas partes
temáticas pertinentes. Os comentários abaixo indicam os locais de implementação.
README e textos do relatório acompanham cada repasse.
"""


"""## **Parte 0, Bibliotecas e configuração**

Material de apoio, seção 10.3.

Bibliotecas compartilhadas pelo programa. math fornece a verificação de números
finitos utilizada na validação das entradas e dos resultados dos modelos.
"""

# Bloco 1 — Montiel | Bibliotecas e configuração compartilhada

import math  


"""## **Parte 1, Constantes, limiares e padrões**

Material de apoio, seções 1 a 8.

Parâmetros da colônia: população, período de análise, energia solar/eólica,
cargas elétricas, estoques, entradas diárias e taxas dos recursos vitais.
Os limiares definem as faixas de cobertura elétrica e reserva dos estoques.
As unidades acompanham os campos; R, P e M identificam referências publicadas,
parâmetros do exercício e dados modelados.
"""

# Bloco 1 — Montiel | Contexto, parâmetros solares e cargas comuns

# Contexto comum (seção 1): todos os balanços usam a mesma população e janela.
POPULACAO_PADRAO = 50   # pessoas (P), editável pelo operador
PERIODO_H = 24          # horas terrestres (P); não é um sol marciano (24,6597 h)

# Convenção: a unidade fica no nome do campo
#   _kw = quilowatt, _kwh = quilowatt-hora, _h = horas
# Origem dos valores: R = referência publicada, P = parâmetro de projeto,
# M = dado modelado (seção 2 do apoio).

# Energia solar (seção 3.1)
SOLAR_PADRAO = {
    "pot_solar_kw": 120,   # P: potência elétrica de referência
    "horas_solares": 8,    # P: horas equivalentes em 24 h (não é a duração do dia)
    "fator_solar": 1.00,   # P: de 0 a 1; representa a perda adotada em um único fator
}

# Carga comum da energia (seção 5): controle e distribuição, protegida nas 24 h.
# Campos iguais aos de qualquer operação (seção 5.2).
CARGA_AUXILIARES = {
    "id": "AUX",
    "nome": "Auxiliares de energia",
    "pot_normal_kw": 2,          # P
    "minimo_protegido_kw": 2,    # P: essencial, não é reduzida
    "periodo_h": 24,
}

# Faixas da cobertura elétrica (seção 3.3), P
LIMIAR_COBERTURA_VERDE = 1.10    # cobertura >= 1,10
LIMIAR_COBERTURA_AMARELO = 1.00  # 1,00 <= cobertura < 1,10

# Bloco 2 — Souza | Parâmetros eólicos e pares da regressão

# Dados modelados do material de apoio: velocidade do vento (m/s) e potência (kW).
PARES_REGRESSAO_EOLICA = [
    [6, 1.2215],
    [7, 1.9396],
    [8, 2.8953],
    [9, 4.1224],
    [10, 5.6549],
]

# Configuração inicial da turbina; os valores podem ser editados no cenário.
EOLICA_PADRAO = {
    "ativa": 1,          # 1 = ligada; 0 = desligada
    "potencia_kw": 2.8953,  # potência atual informada ou estimada (kW)
    "horas": PERIODO_H,
    "vento_ms": 8,    # velocidade informada (m/s), quando disponível
}

# Bloco 3 — Cláudio | Estoques, taxas, entradas e limiares dos recursos vitais

# Recursos para a janela de 24 h (seção 4). As taxas individuais são R;
# estoques, entradas e cargas elétricas são parâmetros P do exercício.
OXIGENIO_PADRAO = {
    "estoque_kg": 134.25,
    "entrada_kg_dia": 45,
    "consumo_pessoa_kg_dia": 0.895,
    "carga": {
        "id": "O2",
        "nome": "Suporte de oxigênio",
        "pot_normal_kw": 12,
        "minimo_protegido_kw": 12,
        "periodo_h": PERIODO_H,
    },
}

ALIMENTOS_PADRAO = {
    "estoque_kg": 560,                # kg de alimento seco, sem embalagem
    "entrada_kg_dia": 30,             # colheita disponível ou abastecimento
    "consumo_pessoa_kg_dia": 0.800,    # kg seco por pessoa por 24 h
    "carga": {
        "id": "ALI",
        "nome": "Suporte de alimentos",
        "pot_normal_kw": 9,
        "minimo_protegido_kw": 9,
        "periodo_h": PERIODO_H,
    },
}

# Cobertura bruta do estoque, em dias: (a partir disso é verde, é amarelo).
# Políticas P das seções 4.1 e 4.2, não limites fisiológicos.
LIMIARES_RESERVAS = {"oxigenio": (2, 1), "alimentos": (7, 3)}


# Bloco 4 — Thales | Dados das operações complementares e mínimos protegidos

# Parâmetros P da seção 5. Prioridade 1 é a mais importante entre complementares.
OPERACOES_PADRAO = [
    {"id": "ARM", "nome": "Armazenamento e logística", "prioridade": 1,
     "pot_normal_kw": 4, "minimo_protegido_kw": 3, "periodo_h": PERIODO_H},
    {"id": "PES", "nome": "Pesquisa e experimentos", "prioridade": 2,
     "pot_normal_kw": 4, "minimo_protegido_kw": 1, "periodo_h": PERIODO_H},
    {"id": "MOB", "nome": "Mobilidade", "prioridade": 3,
     "pot_normal_kw": 3, "minimo_protegido_kw": 1, "periodo_h": PERIODO_H},
    {"id": "CON", "nome": "Conforto e áreas comuns", "prioridade": 4,
     "pot_normal_kw": 2, "minimo_protegido_kw": 0.5, "periodo_h": PERIODO_H},
]


# Bloco 5 — Wallace | Parâmetros ambientais e cenários

# Faixas ambientais (seção 6), P. Cada faixa é (limite, classe): a primeira
# condição verdadeira define a classe. Não são limites certificados de operação.
LIMIARES_VENTO = {"verde_max": 10, "amarelo_max": 15}            # m/s
LIMIARES_POEIRA = {"verde_max": 1, "amarelo_max": 3}             # tau, adimensional
LIMIARES_TEMPERATURA = {                                          # °C, externa
    "verde_min": -80, "verde_max": -20,
    "amarelo_min": -100, "amarelo_max": 0,
}

# Clima inicial (cenário NORMAL). O vento fica só em energia → eolica → vento_ms,
# para que clima e geração eólica usem sempre o mesmo valor (seção 7.3).
CLIMA_PADRAO = {
    "poeira_tau": 0.5,
    "temperatura_externa_c": -60,
}

# Cenários de entrada (seções 7.1 e 7.2), P. Só entradas: nenhum resultado pronto.
# o2 e alimentos: (estoque inicial kg, entrada disponível em 24 h kg).
CENARIOS = {
    "NORMAL": {
        "vento_ms": 8, "poeira_tau": 0.5, "temperatura_externa_c": -60,
        "fator_solar": 1.00, "eolica_ativa": 1,
        "o2": (134.25, 45), "alimentos": (560, 30),
    },
    "BAIXA_GERACAO": {
        "vento_ms": 6, "poeira_tau": 1.5, "temperatura_externa_c": -70,
        "fator_solar": 0.80, "eolica_ativa": 1,
        "o2": (134.25, 45), "alimentos": (560, 30),
    },
    "TEMPESTADE": {
        "vento_ms": 22, "poeira_tau": 4.5, "temperatura_externa_c": -80,
        "fator_solar": 0.10, "eolica_ativa": 0,
        "o2": (134.25, 45), "alimentos": (560, 30),
    },
    "SUPORTE_VIDA_EM_ALERTA": {
        "vento_ms": 8, "poeira_tau": 0.5, "temperatura_externa_c": -60,
        "fator_solar": 1.00, "eolica_ativa": 1,
        "o2": (22.375, 0), "alimentos": (80, 20),
    },
    "MULTIPLAS_RESTRICOES": {
        "vento_ms": 22, "poeira_tau": 4.5, "temperatura_externa_c": -80,
        "fator_solar": 0.10, "eolica_ativa": 0,
        "o2": (22.375, 0), "alimentos": (80, 20),
    },
}

# Lista para o menu: a ordem de exibição dos cenários.
ORDEM_CENARIOS = ["NORMAL", "BAIXA_GERACAO", "TEMPESTADE",
                  "SUPORTE_VIDA_EM_ALERTA", "MULTIPLAS_RESTRICOES"]

# Ordem de gravidade usada para ordenar os riscos (menor número = mais urgente).
GRAVIDADE = {"CRITICO": 0, "ALTO": 1, "ATENCAO": 2, "INFO": 3}


"""## **Parte 2, Módulos e estruturas de dados**

Material de apoio, seções 1 e 9.1.

Hierarquia da colônia em dicionários aninhados: contexto, energia, suporte à vida,
operações, clima e riscos. Listas representam os pares eólicos e as operações.
As cópias dos padrões mantêm os cadastros independentes; listar_cargas reúne
as cargas da hierarquia para o balanço energético.
"""

# Bloco 1 — Montiel | Estrutura comum e hierarquia da colônia

def criar_colonia(populacao=POPULACAO_PADRAO):
    """Cria a estrutura comum da colônia em dicionários aninhados.

    A hierarquia reúne contexto, energia, recursos vitais, operações,
    clima e riscos. Os dados energéticos e vitais são inicializados;
    as operações recebem os padrões; o clima recebe os valores de NORMAL e
    os riscos são preenchidos pela avaliação integrada (Bloco 5).
    """
    colonia = {
        "contexto": {
            "cenario": "NORMAL",
            "populacao": populacao,
            "periodo_h": PERIODO_H,
        },
        "energia": {
            "solar": dict(SOLAR_PADRAO),         
            "eolica": criar_eolica(),  # Bloco 2
            "auxiliares": dict(CARGA_AUXILIARES),
        },
        "suporte_vida": criar_suporte_vida(),      # Bloco 3
        "operacoes": criar_operacoes(),           # Bloco 4: lista de registros
        "clima": criar_clima(),                   # Bloco 5
        "riscos": [],                             # Bloco 5: preenchida na avaliação
    }
    return colonia


def listar_cargas(colonia):
    """Junta numa lista todas as cargas elétricas cadastradas, cada uma uma vez.

    Cada carga fica guardada em um só lugar da hierarquia:
      - auxiliares em energia;
      - suporte de O2 e de alimentos em suporte_vida, na chave "carga";
      - operações complementares na lista operacoes.
    """
    cargas = [colonia["energia"]["auxiliares"]]
    for recurso in colonia["suporte_vida"].values():
        if "carga" in recurso:
            cargas.append(recurso["carga"])
    for operacao in colonia["operacoes"]:
        cargas.append(operacao)
    return cargas

# Bloco 2 — Souza | Estruturas dos dados eólicos


def criar_eolica():
    eolica = dict(EOLICA_PADRAO)
    eolica["pares_regressao"] = [par[:] for par in PARES_REGRESSAO_EOLICA]
    return eolica


# Bloco 3 — Cláudio | Registros de oxigênio e alimentos


def criar_suporte_vida():
    """Cria registros independentes, inclusive as cargas aninhadas.

    As cópias dos recursos e das cargas preservam os padrões e outras
    colônias. listar_cargas() recolhe a carga de cada recurso nesta estrutura.
    """
    oxigenio = dict(OXIGENIO_PADRAO)
    oxigenio["carga"] = dict(OXIGENIO_PADRAO["carga"])
    alimentos = dict(ALIMENTOS_PADRAO)
    alimentos["carga"] = dict(ALIMENTOS_PADRAO["carga"])
    return {"oxigenio": oxigenio, "alimentos": alimentos}


# Bloco 4 — Thales | Registros das operações complementares


def criar_operacoes():
    """Cria cópias independentes das quatro operações, sem alterar os padrões."""
    return [dict(operacao) for operacao in OPERACOES_PADRAO]


# Bloco 5 — Wallace | Registros de ambiente e resultados gerais

def criar_clima():
    """Cria o registro de clima (poeira e temperatura externa).

    O vento não é repetido aqui: fica em energia → eolica → vento_ms e é lido
    de lá pela avaliação do clima, garantindo um único valor para os módulos.
    """
    return dict(CLIMA_PADRAO)


def novo_risco(frente, nivel, dado, motivo, recomendacao, restricao=""):
    """Registro padrão de um risco (seção 9.1): dado, motivo, recomendação."""
    return {
        "frente": frente,              # Energia, Recursos vitais, Ambiente, Conjunta
        "nivel": nivel,                # CRITICO, ALTO, ATENCAO ou INFO
        "dado": dado,                  # valor que disparou a regra
        "motivo": motivo,              # por que a regra foi acionada
        "recomendacao": recomendacao,  # ação clara (saída)
        "restricao": restricao,        # o que continua limitado depois da ação
    }


"""## **Parte 3, Entrada de dados manual**

Material de apoio, seções 7 e 10.1.

Entrada, validação e edição dos campos de cada módulo, com unidades e domínios
definidos no apoio. A interação com o operador é separada dos cálculos.
"""

# Bloco 5 — Wallace | Leitura, validação e edição dos campos

def converter_numero(texto, inteiro=False):
    """Converte o texto digitado em número; aceita vírgula decimal ("0,8").

    Devolve None se o texto não for um número finito (ex.: "abc", "nan", "inf").
    """
    texto = texto.strip().replace(",", ".")
    try:
        valor = int(texto) if inteiro else float(texto)
    except ValueError:
        return None
    if not numero_valido(valor):
        return None
    return valor


def ler_numero(mensagem, atual, minimo=None, maximo=None, inteiro=False, ler=input):
    """Pede um número até receber um valor válido. Enter mantém o valor atual.

    'ler' é a função de leitura: input() no uso normal, ou uma lista simulada
    nos exemplos, para registrar entradas inválidas sem digitar.
    """
    faixa = ""
    if minimo is not None and maximo is not None:
        faixa = f" [{minimo} a {maximo}]"
    elif minimo is not None:
        faixa = f" [mínimo {minimo}]"
    while True:
        texto = ler(f"{mensagem}{faixa} (atual {atual}): ")
        if texto.strip() == "":
            return atual
        valor = converter_numero(texto, inteiro)
        if valor is None:
            tipo = "um número inteiro" if inteiro else "um número"
            print(f"  Entrada inválida: digite {tipo}.")
        elif not numero_valido(valor, minimo, maximo):
            print(f"  Fora do intervalo permitido{faixa}.")
        else:
            return valor


# Campos editáveis por módulo: (rótulo, caminho na hierarquia, mínimo, máximo, inteiro).
# O caminho é uma lista de chaves, navegada por obter_campo e definir_campo.
CAMPOS_EDITAVEIS = {
    "Contexto": [
        ("População (pessoas)", ["contexto", "populacao"], 1, None, True),
    ],
    "Energia solar": [
        ("Potência solar (kW)", ["energia", "solar", "pot_solar_kw"], 0, None, False),
        ("Horas equivalentes (h)", ["energia", "solar", "horas_solares"], 0, 24, False),
        ("Fator solar (0 a 1)", ["energia", "solar", "fator_solar"], 0, 1, False),
    ],
    "Energia eólica": [
        ("Eólica ativa (1 = sim, 0 = não)", ["energia", "eolica", "ativa"], 0, 1, True),
        ("Velocidade do vento (m/s)", ["energia", "eolica", "vento_ms"], 0, None, False),
    ],
    "Oxigênio": [
        ("Estoque de O2 (kg)", ["suporte_vida", "oxigenio", "estoque_kg"], 0, None, False),
        ("Entrada de O2 em 24 h (kg)", ["suporte_vida", "oxigenio", "entrada_kg_dia"], 0, None, False),
    ],
    "Alimentos": [
        ("Estoque de alimento (kg seco)", ["suporte_vida", "alimentos", "estoque_kg"], 0, None, False),
        ("Entrada de alimento em 24 h (kg seco)", ["suporte_vida", "alimentos", "entrada_kg_dia"], 0, None, False),
    ],
    "Clima": [
        ("Poeira (tau)", ["clima", "poeira_tau"], 0, None, False),
        ("Temperatura externa (°C)", ["clima", "temperatura_externa_c"], None, None, False),
    ],
}


def obter_campo(colonia, caminho):
    """Navega pela hierarquia: ["energia", "solar", "fator_solar"] -> valor."""
    nivel = colonia
    for chave in caminho:
        nivel = nivel[chave]
    return nivel


def definir_campo(colonia, caminho, valor):
    """Grava o valor no fim do caminho da hierarquia."""
    nivel = colonia
    for chave in caminho[:-1]:
        nivel = nivel[chave]
    nivel[caminho[-1]] = valor


def editar_modulo(colonia, modulo, ler=input):
    """Edita os campos de um módulo, validando unidade e domínio de cada um."""
    print(f"\n-- Editando: {modulo} (Enter mantém o valor atual)")
    for rotulo, caminho, minimo, maximo, inteiro in CAMPOS_EDITAVEIS[modulo]:
        atual = obter_campo(colonia, caminho)
        valor = ler_numero(rotulo, atual, minimo, maximo, inteiro, ler)
        definir_campo(colonia, caminho, valor)
    if modulo == "Energia eólica":
        editar_potencia_eolica(colonia, ler)
    colonia["contexto"]["cenario"] = "PERSONALIZADO"


def editar_potencia_eolica(colonia, ler=input):
    """Define a potência eólica atual e registra a sua origem (seção 7.3).

    1 = tabela M da seção 8 (só se o vento estiver na tabela);
    2 = estimativa da regressão (só entre 6 e 10 m/s);
    3 = valor informado pelo operador.
    """
    eolica = colonia["energia"]["eolica"]
    if eolica["ativa"] == 0:
        eolica["origem_potencia"] = "eólica indisponível no período"
        return
    print("Origem da potência eólica: 1 = tabela M | 2 = regressão | 3 = informar")
    while True:
        opcao = ler("Opção: ").strip()
        if opcao == "1":
            tabela = potencia_tabela(eolica["pares_regressao"], eolica["vento_ms"])
            if tabela is None:
                print("  O vento atual não está na tabela da seção 8 (6, 7, 8, 9 ou 10 m/s).")
                continue
            eolica["potencia_kw"] = tabela
            eolica["origem_potencia"] = "tabela M da seção 8"
            return
        if opcao == "2":
            previsao = previsao_eolica(colonia)
            if previsao["potencia_kw"] is None:
                print(f"  {previsao['aviso']}")
                continue
            eolica["potencia_kw"] = previsao["potencia_kw"]
            eolica["origem_potencia"] = "estimada pela regressão"
            return
        if opcao == "3":
            eolica["potencia_kw"] = ler_numero("Potência eólica (kW)", eolica["potencia_kw"],
                                               0, None, False, ler)
            eolica["origem_potencia"] = "informada pelo operador"
            return
        print("  Opção inválida: digite 1, 2 ou 3.")


def editar_operacoes(colonia, ler=input):
    """Edita a potência normal das operações; nunca abaixo do mínimo protegido."""
    print("\n-- Editando: Operações complementares (Enter mantém o valor atual)")
    for operacao in colonia["operacoes"]:
        operacao["pot_normal_kw"] = ler_numero(
            f"{operacao['nome']}, potência normal (kW)", operacao["pot_normal_kw"],
            operacao["minimo_protegido_kw"], None, False, ler)
    colonia["contexto"]["cenario"] = "PERSONALIZADO"


"""## **Parte 4, Preparação do cenário e dos dados de avaliação**

Material de apoio, seção 7.

Contexto comum de avaliação: cenário, população, período e dados dos sistemas.
Os cenários de referência representam condições normais e adversas; a edição
personalizada utiliza os valores de NORMAL como base.
"""

# Bloco 5 — Wallace | Preparação do contexto de avaliação

def potencia_tabela(pares, vento_ms):
    """Potência M da seção 8 para um vento da tabela; None se não estiver nela."""
    for vento, potencia in pares:
        if vento == vento_ms:
            return potencia
    return None


def aplicar_cenario(nome, populacao=POPULACAO_PADRAO):
    """Cria uma colônia nova e cadastra as entradas do cenário (seção 7).

    População, cargas e taxas por pessoa ficam iguais às seções anteriores.
    Com a eólica ativa, a potência atual vem da tabela M do vento do cenário;
    com a eólica inativa, a geração atual é indisponível (não é previsão).
    PERSONALIZADO começa com os valores de NORMAL.
    """
    base = "NORMAL" if nome == "PERSONALIZADO" else nome
    if base not in CENARIOS:
        return None
    dados = CENARIOS[base]
    colonia = criar_colonia(populacao)
    colonia["contexto"]["cenario"] = nome

    colonia["energia"]["solar"]["fator_solar"] = dados["fator_solar"]
    eolica = colonia["energia"]["eolica"]
    eolica["vento_ms"] = dados["vento_ms"]
    eolica["ativa"] = dados["eolica_ativa"]
    if eolica["ativa"] == 1:
        eolica["potencia_kw"] = potencia_tabela(eolica["pares_regressao"], eolica["vento_ms"])
        eolica["origem_potencia"] = "tabela M da seção 8"
    else:
        eolica["potencia_kw"] = 0
        eolica["origem_potencia"] = "indisponível no período, decisão operacional P"

    colonia["clima"]["poeira_tau"] = dados["poeira_tau"]
    colonia["clima"]["temperatura_externa_c"] = dados["temperatura_externa_c"]

    oxigenio = colonia["suporte_vida"]["oxigenio"]
    oxigenio["estoque_kg"], oxigenio["entrada_kg_dia"] = dados["o2"]
    alimentos = colonia["suporte_vida"]["alimentos"]
    alimentos["estoque_kg"], alimentos["entrada_kg_dia"] = dados["alimentos"]
    return colonia


"""## **Parte 5, Classificação e regras de decisão**

Material de apoio, seções 3.3, 4, 6 e 9.2.

Classificações e diagnósticos dos resultados numéricos. A cobertura elétrica
relaciona geração e consumo; a reserva bruta relaciona estoque e demanda diária.
A suficiência dos recursos considera estoque mais entrada no período de 24 h,
separadamente da classificação da reserva. Os diagnósticos apresentam valores,
situação e motivos. Clima e riscos compõem as avaliações ambientais.
"""

# Bloco 1 — Montiel | Classificação e diagnóstico energético

def classificar_cobertura(cobertura):
    """Classifica a cobertura elétrica (seção 3.3), por escrito.

    VERDE: >= 1,10 | AMARELO: 1,00 a 1,10 | VERMELHO: < 1,00
    Cobertura None (consumo zero) -> NAO SE APLICA.
    """
    if cobertura is None:
        return "NAO SE APLICA"
    # round evita erro de arredondamento do computador:
    # 950,4 / 864 deveria dar 1,10, mas o Python calcula 1,0999999999999999
    cobertura = round(cobertura, 6)
    if cobertura >= LIMIAR_COBERTURA_VERDE:
        return "VERDE"
    elif cobertura >= LIMIAR_COBERTURA_AMARELO:
        return "AMARELO"
    else:
        return "VERMELHO"


def diagnostico_energetico(balanco):
    """Monta o texto do diagnóstico: saldo sempre junto da classificação."""
    leituras = {
        "VERDE": "margem de geração no período",
        "AMARELO": "atendimento com margem pequena; atenção à continuidade",
        "VERMELHO": "déficit no período; há demanda não atendida no balanço",
        "NAO SE APLICA": "consumo informado igual a zero; cobertura não calculada",
    }
    classe = balanco["classificacao"]
    linhas = [
        f"Geração total: {balanco['geracao_total_kwh']:.2f} kWh",
        f"Consumo total: {balanco['consumo_total_kwh']:.2f} kWh",
        f"Saldo:         {balanco['saldo_kwh']:+.2f} kWh",
    ]
    if balanco["cobertura"] is None:
        linhas.append("Cobertura:     não se aplica")
    else:
        linhas.append(f"Cobertura:     {balanco['cobertura']:.4f}")
    linhas.append(f"Energia:       {classe} - {leituras[classe]}")
    return "\n".join(linhas)

# Bloco 3 — Cláudio | Classificações e diagnósticos dos recursos vitais


def classificar_reserva(dias, limiar_verde, limiar_amarelo):
    """Classifica a cobertura bruta do estoque pelas faixas do apoio."""
    if not numero_valido(dias, minimo=0):
        return None
    if not numero_valido(limiar_amarelo, minimo=0):
        return None
    if not numero_valido(limiar_verde) or limiar_verde <= limiar_amarelo:
        return None
    dias = round(dias, 6)
    if dias >= limiar_verde:
        return "VERDE"
    elif dias >= limiar_amarelo:
        return "AMARELO"
    else:
        return "VERMELHO"


def avaliar_suporte_vida(colonia):
    """Avalia os dois recursos na janela comum de 24 h.

    suficiente descreve o atendimento do período; classificacao descreve
    apenas a cobertura bruta do estoque. Devolve None se houver dado inválido.
    Não altera estoques nem aplica reposição automaticamente à colônia.
    """
    if colonia["contexto"]["periodo_h"] != PERIODO_H:
        return None
    resultados = {}
    for nome in ("oxigenio", "alimentos"):
        recurso = colonia["suporte_vida"][nome]
        balanco = balanco_recurso(
            colonia["contexto"]["populacao"],
            recurso.get("estoque_kg"),
            recurso.get("entrada_kg_dia"),
            recurso.get("consumo_pessoa_kg_dia"),
        )
        if balanco is None:
            return None
        verde, amarelo = LIMIARES_RESERVAS[nome]
        balanco["classificacao"] = classificar_reserva(
            balanco["cobertura_dias"], verde, amarelo)
        resultados[nome] = balanco
    return resultados


def diagnostico_recurso(nome, balanco, unidade="kg"):
    """Explica o resultado de avaliar_suporte_vida, sem confundir os indicadores.

    O parâmetro unidade identifica a massa apresentada; "kg seco" corresponde
    aos alimentos. A massa de O2 não representa concentração ou pressão
    de oxigênio no ar do habitat.
    """
    if balanco["suficiente"]:
        situacao = "SUFICIENTE"
        motivo = "estoque e entrada atendem à demanda das 24 h"
    else:
        situacao = "INSUFICIENTE"
        motivo = "estoque e entrada não cobrem a demanda das 24 h"
    return "\n".join([
        f"{nome}: {situacao} - {motivo}",
        f"Demanda:       {balanco['demanda_kg_dia']:.3f} {unidade}/24 h",
        f"Disponível:    {balanco['disponivel_kg']:.3f} {unidade}",
        f"Saldo:         {balanco['saldo_kg']:+.3f} {unidade}",
        f"Reserva bruta: {balanco['cobertura_dias']:.2f} dias "
        f"- {balanco['classificacao']} (sem contar entradas futuras)",
    ])


# Bloco 5 — Wallace | Classificações de vento, poeira e temperatura

def classificar_vento(vento_ms):
    """Seção 6.1: VERDE 0 a 10 | AMARELO acima de 10 até 15 | VERMELHO acima de 15."""
    if not numero_valido(vento_ms, minimo=0):
        return None
    if vento_ms <= LIMIARES_VENTO["verde_max"]:
        return "VERDE"
    elif vento_ms <= LIMIARES_VENTO["amarelo_max"]:
        return "AMARELO"
    else:
        return "VERMELHO"


def classificar_poeira(tau):
    """Seção 6.2: VERDE 0 a 1 | AMARELO acima de 1 até 3 | VERMELHO acima de 3."""
    if not numero_valido(tau, minimo=0):
        return None
    if tau <= LIMIARES_POEIRA["verde_max"]:
        return "VERDE"
    elif tau <= LIMIARES_POEIRA["amarelo_max"]:
        return "AMARELO"
    else:
        return "VERMELHO"


def classificar_temperatura(temp_c):
    """Seção 6.3 (temperatura externa): VERDE de -80 a -20 °C;
    AMARELO de -100 até antes de -80, ou acima de -20 até 0; VERMELHO fora disso."""
    if not numero_valido(temp_c):
        return None
    t = LIMIARES_TEMPERATURA
    if t["verde_min"] <= temp_c <= t["verde_max"]:
        return "VERDE"
    elif t["amarelo_min"] <= temp_c < t["verde_min"] or t["verde_max"] < temp_c <= t["amarelo_max"]:
        return "AMARELO"
    else:
        return "VERMELHO"


def avaliar_clima(colonia):
    """Classifica o clima informado. Descreve o cenário; não prevê tempestades."""
    vento = colonia["energia"]["eolica"]["vento_ms"]
    poeira = colonia["clima"]["poeira_tau"]
    temperatura = colonia["clima"]["temperatura_externa_c"]
    resultado = {
        "vento": {"valor": vento, "unidade": "m/s", "classe": classificar_vento(vento)},
        "poeira": {"valor": poeira, "unidade": "tau", "classe": classificar_poeira(poeira)},
        "temperatura": {"valor": temperatura, "unidade": "°C",
                        "classe": classificar_temperatura(temperatura)},
    }
    for indicador in resultado.values():
        if indicador["classe"] is None:
            return None
    return resultado


# Bloco 5 — Wallace | Condições combinadas e avaliação dos riscos

def avaliar_riscos(colonia, energia, vitais, clima, plano):
    """Cruza energia, recursos vitais e clima (seção 9.2) e devolve a lista de riscos.

    Cada regra é uma condição simples ou combinada (and / or). A saída de cada
    risco traz o dado relevante, o motivo e a recomendação, não só uma cor.
    'plano' é o resultado de recomendar_operacoes (Bloco 4, Parte 6).
    """
    riscos = []
    solar = colonia["energia"]["solar"]
    eolica = colonia["energia"]["eolica"]
    classe_energia = energia["classificacao"]
    saldo = energia["saldo_kwh"]

    # Energia: déficit (consumo > geração) ---------------------------------------
    deficit = classe_energia == "VERMELHO"
    resolvido = plano is not None and plano["atende_periodo"]
    if deficit and resolvido:
        riscos.append(novo_risco(
            "Energia", "ALTO",
            f"saldo {saldo:+.2f} kWh, cobertura {energia['cobertura']:.4f}",
            "consumo maior que geração no período",
            "ALERTA: reduzir consumo - aplicar as reduções da Parte 6 "
            f"(economia de {plano['economia_proposta_kwh']:.2f} kWh)",
            "operações complementares funcionando em parte durante o período"))
    elif deficit:
        restante = plano["deficit_remanescente_kwh"] if plano else -saldo
        riscos.append(novo_risco(
            "Energia", "CRITICO",
            f"saldo {saldo:+.2f} kWh, cobertura {energia['cobertura']:.4f}",
            "consumo maior que geração e a economia possível não cobre o déficit",
            "ALERTA: ativar modo economia - todas as complementares no mínimo protegido",
            f"déficit de {restante:.2f} kWh permanece com as cargas essenciais protegidas"))
    elif classe_energia == "AMARELO":
        riscos.append(novo_risco(
            "Energia", "ATENCAO",
            f"saldo {saldo:+.2f} kWh, cobertura {energia['cobertura']:.4f}",
            "geração atende o consumo com margem menor que 10%",
            "ATENÇÃO: adiar cargas não essenciais para recuperar a margem"))
    elif classe_energia == "VERDE":
        riscos.append(novo_risco(
            "Energia", "INFO",
            f"saldo {saldo:+.2f} kWh, cobertura {energia['cobertura']:.4f}",
            "geração maior que consumo: possível desperdício",
            "SUGESTÃO: armazenar energia excedente ou programar cargas adiáveis "
            "neste período",
            "reserva elétrica (baterias) não faz parte do modelo"))

    # Fontes: as duas comprometidas ao mesmo tempo --------------------------------
    if solar["fator_solar"] < 0.5 and eolica["ativa"] == 0:
        riscos.append(novo_risco(
            "Energia", "ALTO",
            f"fator solar {solar['fator_solar']:.2f}, eólica indisponível",
            "solar reduzida e eólica fora de operação ao mesmo tempo",
            "Priorizar suporte à vida e auxiliares; não iniciar novas cargas",
            "sem segunda fonte para compensar a queda solar"))

    # Recursos vitais -------------------------------------------------------------
    nomes = {"oxigenio": "O2", "alimentos": "Alimentos"}
    for chave, rotulo in nomes.items():
        recurso = vitais[chave]
        unidade = "kg seco" if chave == "alimentos" else "kg"
        dado = (f"saldo {recurso['saldo_kg']:+.3f} {unidade}, "
                f"reserva {recurso['cobertura_dias']:.2f} dias")
        if not recurso["suficiente"]:
            riscos.append(novo_risco(
                "Recursos vitais", "CRITICO", dado,
                f"estoque e entrada de {rotulo} não cobrem a demanda de 24 h",
                f"ALERTA: providenciar reposição de {rotulo} imediatamente",
                "economia elétrica não repõe o recurso"))
        elif recurso["classificacao"] == "VERMELHO":
            riscos.append(novo_risco(
                "Recursos vitais", "ALTO", dado,
                f"{rotulo} atende o período, mas a reserva bruta está abaixo da política",
                f"Programar reposição de {rotulo} e acompanhar a entrada diária"))
        elif recurso["classificacao"] == "AMARELO":
            riscos.append(novo_risco(
                "Recursos vitais", "ATENCAO", dado,
                f"reserva curta de {rotulo}",
                f"Acompanhar a reposição de {rotulo}"))

    # Ambiente --------------------------------------------------------------------
    vento = clima["vento"]
    poeira = clima["poeira"]
    temperatura = clima["temperatura"]
    if vento["classe"] == "VERMELHO" or poeira["classe"] == "VERMELHO":
        riscos.append(novo_risco(
            "Ambiente", "ALTO",
            f"vento {vento['valor']} m/s ({vento['classe']}), "
            f"poeira tau {poeira['valor']} ({poeira['classe']})",
            "condição externa adversa no exercício",
            "Suspender atividades externas e mobilidade não essencial",
            "transporte de emergência e abastecimento vital mantidos"))
    elif vento["classe"] == "AMARELO" or poeira["classe"] == "AMARELO":
        riscos.append(novo_risco(
            "Ambiente", "ATENCAO",
            f"vento {vento['valor']} m/s ({vento['classe']}), "
            f"poeira tau {poeira['valor']} ({poeira['classe']})",
            "condição externa mais exigente",
            "Limitar saídas externas às necessárias"))
    if temperatura["classe"] != "VERDE":
        riscos.append(novo_risco(
            "Ambiente", "ATENCAO" if temperatura["classe"] == "AMARELO" else "ALTO",
            f"temperatura externa {temperatura['valor']} °C ({temperatura['classe']})",
            "fora da faixa externa de referência",
            "Reduzir a exposição de pessoas e equipamentos no exterior"))

    # Restrições conjuntas: problemas de natureza diferente ao mesmo tempo ---------
    energia_ruim = classe_energia == "VERMELHO"
    vital_ruim = (not vitais["oxigenio"]["suficiente"]
                  or not vitais["alimentos"]["suficiente"]
                  or vitais["oxigenio"]["classificacao"] == "VERMELHO"
                  or vitais["alimentos"]["classificacao"] == "VERMELHO")
    ambiente_ruim = vento["classe"] == "VERMELHO" or poeira["classe"] == "VERMELHO"
    frentes_adversas = [energia_ruim, vital_ruim, ambiente_ruim].count(True)
    if frentes_adversas >= 2:
        if vital_ruim:
            acao = "Tratar primeiro a reposição de O2/alimentos, depois a energia"
        else:
            acao = "Proteger suporte à vida e auxiliares; demais operações no mínimo"
        riscos.append(novo_risco(
            "Conjunta", "CRITICO",
            f"{frentes_adversas} frentes adversas "
            f"(energia: {energia_ruim}, vitais: {vital_ruim}, ambiente: {ambiente_ruim})",
            "problemas de natureza diferente acontecendo juntos",
            acao,
            "a economia elétrica não resolve falta de recurso vital nem o clima"))

    riscos.sort(key=lambda risco: GRAVIDADE[risco["nivel"]])
    return riscos


"""## **Parte 6, Prioridades e recomendações de equilíbrio**

Material de apoio, seção 5.

Prioridades das operações complementares: armazenamento/logística, pesquisa,
mobilidade e conforto, do mais importante ao menos importante. A ordem de
redução é inversa, com proteção das funções vitais e dos mínimos operacionais.
As recomendações relacionam os diagnósticos às possibilidades de economia.
"""

# Bloco 4 — Thales | Prioridades e recomendações das operações


def recomendar_operacoes(colonia):
    """Propõe economia para cobrir o déficit, sem alterar os dados da colônia.

    Reduz primeiro as complementares de menor importância, até o mínimo.
    Não corta cargas essenciais nem tenta obter margem de 10% por novos cortes.
    Retorna None quando os dados não permitem uma recomendação consistente.
    """
    operacoes = avaliar_operacoes(colonia)
    balanco = avaliar_energia(colonia)
    if operacoes is None or balanco is None:
        return None
    restante = max(0, -balanco["saldo_kwh"])
    consumos_propostos = consumos_eletricos(colonia)
    recomendacoes = []
    # Prioridades únicas e validadas; 4, 3, 2, 1 é a ordem de redução.
    for operacao in sorted(operacoes, key=lambda item: item["prioridade"], reverse=True):
        economia = min(restante, operacao["ajustavel_kwh"])
        if economia <= 0:
            continue
        consumo_proposto = operacao["consumo_normal_kwh"] - economia
        consumos_propostos[operacao["id"]] = consumo_proposto
        recomendacoes.append({
            "id": operacao["id"], "nome": operacao["nome"],
            "prioridade": operacao["prioridade"],
            "pot_atual_kw": operacao["pot_normal_kw"],
            "pot_recomendada_kw": max(operacao["minimo_protegido_kw"],
                                       consumo_proposto / operacao["periodo_h"]),
            "minimo_protegido_kw": operacao["minimo_protegido_kw"],
            "economia_kwh": economia,
            "motivo": "Reduzir o déficit preservando funções essenciais e mínimos",
        })
        restante = max(0, restante - economia)
    proposto = balanco_energetico(balanco["geracao_por_fonte_kwh"], consumos_propostos)
    return {
        "balanco_atual": balanco, "balanco_proposto": proposto,
        "operacoes": operacoes, "recomendacoes": recomendacoes,
        "economia_maxima_kwh": sum(item["ajustavel_kwh"] for item in operacoes),
        "economia_proposta_kwh": sum(item["economia_kwh"] for item in recomendacoes),
        "deficit_remanescente_kwh": max(0, -proposto["saldo_kwh"]),
        "atende_periodo": proposto["saldo_kwh"] >= -0.000000001,
    }


def diagnostico_operacoes(resultado):
    """Texto para o relatório e para o menu do Bloco 5; não aplica os cortes."""
    linhas = ["Recomendações de operações (proposta; cadastro preservado):"]
    for item in resultado["recomendacoes"]:
        linhas.append(
            f"{item['nome']}: {item['pot_atual_kw']:.4f} -> "
            f"{item['pot_recomendada_kw']:.4f} kW; "
            f"economia {item['economia_kwh']:.3f} kWh. {item['motivo']}.")
    if not resultado["recomendacoes"]:
        linhas.append("Sem redução necessária: o balanço atual atende ao período.")
    linhas.append(f"Economia possível: {resultado['economia_maxima_kwh']:.3f} kWh")
    linhas.append(f"Economia proposta: {resultado['economia_proposta_kwh']:.3f} kWh")
    linhas.append(diagnostico_energetico(resultado["balanco_proposto"]))
    if not resultado["atende_periodo"]:
        linhas.append(
            f"Déficit remanescente: {resultado['deficit_remanescente_kwh']:.3f} kWh. "
            "A economia não basta; é necessário recompor a geração. "
            "Não há reserva elétrica modelada nem cortes abaixo dos mínimos.")
    linhas.append("Economia elétrica não repõe oxigênio ou alimentos. "
                  "Atendimento agregado em 24 h não garante fornecimento contínuo.")
    return "\n".join(linhas)


"""## **Parte 7, Modelos matemáticos e previsão**

Material de apoio, seções 3, 4, 5 e 8.

Validação numérica, geração solar/eólica, balanço energético e indicadores de
oxigênio e alimentos. A regressão ajusta uma reta aos pares modelados de vento
e potência, com estimativas entre 6 e 10 m/s. A geração atual e a previsão
permanecem distintas. Os consumos das cargas cadastradas alimentam o balanço,
com verificação de identificadores repetidos e períodos incompatíveis.
"""

# Bloco 1 — Montiel | Modelos de geração solar e balanço energético

def numero_valido(valor, minimo=None, maximo=None):
    """True se 'valor' é um número finito dentro do intervalo (seção 10.1).

    Recusa texto ("120"), None, True/False, NaN e infinito.
    True/False são recusados porque o Python trata True como 1.
    """
    if type(valor) not in (int, float):
        return False
    if not math.isfinite(valor):
        return False
    if minimo is not None and valor < minimo:
        return False
    if maximo is not None and valor > maximo:
        return False
    return True


def energia_kwh(potencia_kw, horas):
    """Energia (kWh) = potência (kW) x tempo (h). None se a entrada for inválida."""
    if not numero_valido(potencia_kw, minimo=0):
        return None
    if not numero_valido(horas, minimo=0, maximo=PERIODO_H):
        return None
    return potencia_kw * horas


def geracao_solar(pot_solar_kw, horas_solares, fator_solar):
    """Energia solar do período, em kWh: potência x horas equivalentes x fator.

    O fator solar (0 a 1) já inclui a perda do cenário e é aplicado uma vez.
    Devolve None se alguma entrada for inválida.
    """
    if not numero_valido(fator_solar, minimo=0, maximo=1):
        return None
    energia = energia_kwh(pot_solar_kw, horas_solares)
    if energia is None:
        return None
    return energia * fator_solar


def balanco_energetico(geracoes, consumos):
    """Balanço do período a partir das gerações e dos consumos recebidos.

    geracoes: dicionário {fonte: kWh}, ex.: {"solar": 960}
    consumos: dicionário {carga: kWh}, ex.: {"AUX": 48, "O2": 288}
    Uma nova fonte (ex.: "eolica") entra como mais uma chave em geracoes,
    sem mudar esta função.

    Devolve um dicionário com totais, saldo, cobertura e classificação,
    ou None se algum valor for inválido.
    """
    geracao_total = 0
    for fonte in geracoes:
        if not numero_valido(geracoes[fonte], minimo=0):
            return None
        geracao_total = geracao_total + geracoes[fonte]

    consumo_total = 0
    for carga in consumos:
        if not numero_valido(consumos[carga], minimo=0):
            return None
        consumo_total = consumo_total + consumos[carga]

    saldo = geracao_total - consumo_total

    # Consumo zero: não divide; a cobertura não se aplica (seção 3.3)
    if consumo_total == 0:
        cobertura = None
    else:
        cobertura = geracao_total / consumo_total

    return {
        "geracao_por_fonte_kwh": dict(geracoes),
        "geracao_total_kwh": geracao_total,
        "consumo_total_kwh": consumo_total,
        "saldo_kwh": saldo,
        "cobertura": cobertura,
        "classificacao": classificar_cobertura(cobertura),
    }


def avaliar_energia(colonia):
    solar = colonia["energia"]["solar"]
    eolica = colonia["energia"]["eolica"]
    geracoes = {
        "solar": geracao_solar(solar["pot_solar_kw"], solar["horas_solares"], solar["fator_solar"]),
        "eolica": geracao_eolica(eolica["potencia_kw"], eolica["horas"], eolica["ativa"]),
    }
    if geracoes["solar"] is None or geracoes["eolica"] is None:
        return None
    consumos = consumos_eletricos(colonia)
    if consumos is None:
        return None
    return balanco_energetico(geracoes, consumos)


# Bloco 2 — Souza | Modelo de geração eólica

def geracao_eolica(pot_kw, horas, eolica_ativa):
    """Calcula a energia eólica gerada no período, em kWh.

    eolica_ativa aceita 1 (ligada) ou 0 (desligada).
    Retorna None se alguma entrada for inválida.
    """
    if type(eolica_ativa) is not int or eolica_ativa not in (0, 1):
        return None
    if not numero_valido(pot_kw, minimo=0):
        return None
    if not numero_valido(horas, minimo=0, maximo=PERIODO_H):
        return None

    if eolica_ativa == 1:
        return pot_kw * horas
    return 0


# Bloco 2 — Souza | Ajuste da regressão e estimativa de potência

def ajustar_reta(pares):
    """Calcula os coeficientes a e b da regressão linear por mínimos quadrados.

    Cada par contém (velocidade do vento em m/s, potência em kW).
    Retorna (a, b), correspondentes a potência = a * vento + b,
    ou None quando os dados não permitem o ajuste.
    """
    if not isinstance(pares, (list, tuple)) or len(pares) < 2:
        print("Erro: são necessários pelo menos dois pares.")
        return None

    ventos = []
    potencias = []

    for par in pares:
        if not isinstance(par, (list, tuple)) or len(par) != 2:
            print("Erro: cada par deve conter vento e potência.")
            return None

        vento, potencia = par
        if not numero_valido(vento, minimo=0):
            print("Erro: velocidade do vento inválida.")
            return None
        if not numero_valido(potencia, minimo=0):
            print("Erro: potência inválida.")
            return None

        ventos.append(vento)
        potencias.append(potencia)

    media_ventos = sum(ventos) / len(ventos)
    media_potencias = sum(potencias) / len(potencias)

    numerador = 0
    denominador = 0
    for i in range(len(ventos)):
        numerador += (
            (ventos[i] - media_ventos) *
            (potencias[i] - media_potencias)
        )
        denominador += (ventos[i] - media_ventos) ** 2

    if denominador == 0:
        print("Erro: não existe variação nas velocidades do vento.")
        return None

    a = numerador / denominador
    b = media_potencias - a * media_ventos
    return a, b


def prever_potencia(vento_ms, a, b):
    """Estima a potência eólica entre 6 e 10 m/s usando a reta ajustada."""
    if not numero_valido(vento_ms, minimo=6, maximo=10):
        print("Erro: velocidade fora da faixa de previsão (6 a 10 m/s).")
        return None
    if not numero_valido(a) or not numero_valido(b):
        print("Erro: coeficientes da regressão inválidos.")
        return None

    potencia = a * vento_ms + b
    if not numero_valido(potencia, minimo=0):
        print("Erro: a previsão resultou em potência inválida.")
        return None
    return potencia

# Bloco 3 — Cláudio | Balanços e indicadores de oxigênio e alimentos


def balanco_recurso(populacao, estoque_kg, entrada_kg_dia, consumo_pessoa_kg_dia):
    """Balanço de um recurso para 24 h, com cobertura bruta em dias.

    Compara estoque + entrada disponível com a demanda da população.
    A cobertura bruta considera somente estoque / demanda diária.
    Não representa autonomia líquida nem garantia de oferta a cada instante.
    """
    if type(populacao) is not int or populacao <= 0:
        return None
    for valor in (estoque_kg, entrada_kg_dia, consumo_pessoa_kg_dia):
        if not numero_valido(valor, minimo=0):
            return None
    if consumo_pessoa_kg_dia == 0:
        return None

    demanda = populacao * consumo_pessoa_kg_dia
    disponivel = estoque_kg + entrada_kg_dia
    if not numero_valido(demanda, minimo=0) or demanda == 0:
        return None
    if not numero_valido(disponivel, minimo=0):
        return None
    cobertura = estoque_kg / demanda
    if not numero_valido(cobertura, minimo=0):
        return None
    saldo = disponivel - demanda
    return {
        "estoque_kg": estoque_kg,
        "entrada_kg_dia": entrada_kg_dia,
        "demanda_kg_dia": demanda,
        "disponivel_kg": disponivel,
        "saldo_kg": saldo,
        "cobertura_dias": cobertura,
        "suficiente": saldo >= 0,
    }


def consumos_eletricos(colonia):
    """Converte as cargas cadastradas em {id: kWh} para o balanço existente.

    Inclui auxiliares, recursos vitais e operações que já estiverem cadastradas.
    Recusa identificador repetido, carga inválida ou janela diferente do contexto,
    em vez de somar duas vezes ou sobrescrever um consumo silenciosamente.
    """
    consumos = {}
    for carga in listar_cargas(colonia):
        identificador = carga.get("id")
        if not isinstance(identificador, str) or not identificador:
            return None
        if identificador in consumos:
            return None
        if carga.get("periodo_h") != colonia["contexto"]["periodo_h"]:
            return None
        minimo = carga.get("minimo_protegido_kw")
        normal = carga.get("pot_normal_kw")
        if not numero_valido(minimo, minimo=0) or not numero_valido(normal, minimo=0):
            return None
        if normal < minimo:
            return None
        consumo = energia_kwh(carga.get("pot_normal_kw"), carga.get("periodo_h"))
        if consumo is None:
            return None
        consumos[identificador] = consumo
    return consumos


# Bloco 4 — Thales | Consumos e parcelas ajustáveis das operações


def avaliar_operacoes(colonia):
    """Calcula consumo normal, protegido e ajustável de cada complementar.

    Exige os quatro IDs do apoio, prioridades inteiras únicas de 1 a 4 e
    período comum de 24 h. Consumos são informativos: listar_cargas já os
    inclui uma vez no balanço, sem somar esta lista novamente.
    """
    if colonia["contexto"].get("periodo_h") != PERIODO_H:
        return None
    operacoes = colonia.get("operacoes")
    if not isinstance(operacoes, list) or len(operacoes) != 4:
        return None
    resultados, ids, prioridades = [], [], []
    for operacao in operacoes:
        if not isinstance(operacao, dict):
            return None
        identificador = operacao.get("id")
        prioridade = operacao.get("prioridade")
        normal = operacao.get("pot_normal_kw")
        minimo = operacao.get("minimo_protegido_kw")
        if identificador not in ("ARM", "PES", "MOB", "CON") or identificador in ids:
            return None
        if type(prioridade) is not int or not 1 <= prioridade <= 4 or prioridade in prioridades:
            return None
        if prioridade != {"ARM": 1, "PES": 2, "MOB": 3, "CON": 4}[identificador]:
            return None
        if not isinstance(operacao.get("nome"), str) or not operacao["nome"].strip():
            return None
        if not numero_valido(normal, minimo=0) or not numero_valido(minimo, minimo=0):
            return None
        if normal < minimo or operacao.get("periodo_h") != PERIODO_H:
            return None
        consumo = energia_kwh(normal, PERIODO_H)
        protegido = energia_kwh(minimo, PERIODO_H)
        if not numero_valido(consumo, minimo=0) or not numero_valido(protegido, minimo=0):
            return None
        resultados.append(dict(operacao, consumo_normal_kwh=consumo,
                               protegido_kwh=protegido, ajustavel_kwh=consumo - protegido))
        ids.append(identificador)
        prioridades.append(prioridade)
    return resultados


# Bloco 5 — Wallace | Previsão integrada e projeção condicional dos estoques

def previsao_eolica(colonia):
    """Usa a reta do Bloco 2 para estimar a potência no vento atual.

    Fica separada da potência atual do cenário (seção 8.2). Fora de 6 a 10 m/s,
    devolve só um aviso, sem número, para não extrapolar a reta.
    """
    eolica = colonia["energia"]["eolica"]
    vento = eolica["vento_ms"]
    resultado = {"vento_ms": vento, "a": None, "b": None,
                 "potencia_kw": None, "energia_kwh": None, "aviso": ""}
    ajuste = ajustar_reta(eolica["pares_regressao"])
    if ajuste is None:
        resultado["aviso"] = "regressão não ajustada: pares inválidos"
        return resultado
    resultado["a"], resultado["b"] = ajuste
    if not numero_valido(vento, minimo=6, maximo=10):
        resultado["aviso"] = (f"vento de {vento} m/s fora da faixa de ajuste (6 a 10 m/s): "
                              "sem previsão numérica")
        return resultado
    a, b = ajuste
    potencia = a * vento + b
    resultado["potencia_kw"] = potencia
    resultado["energia_kwh"] = potencia * eolica["horas"]
    return resultado


def projecao_estoque(balanco):
    """Projeção condicional: em quantos dias o estoque acaba SE entrada e consumo
    se mantiverem iguais. Não é previsão de quando algo vai acontecer."""
    perda_dia = balanco["demanda_kg_dia"] - balanco["entrada_kg_dia"]
    if perda_dia <= 0:
        return None   # entrada cobre a demanda: o estoque não diminui
    return balanco["estoque_kg"] / perda_dia


"""## **Parte 8, Avaliação integrada e menu principal**

Material de apoio, seções 9 e 10.

Coordenação entre contexto, cálculos, classificações, riscos e recomendações.
Menu de cenários e edição de dados, com apresentação dos resultados, unidades,
motivos e limites dos modelos.
"""

# Bloco 5 — Wallace | Coordenação da avaliação e apresentação dos resultados

def avaliacao_integrada(colonia):
    """Entrada → processamento → saída: reúne todos os módulos numa só avaliação.

    Devolve um dicionário com energia, plano de redução, recursos vitais, clima,
    previsão eólica e riscos, ou None se algum dado estiver inválido.
    Não altera a colônia além de guardar a lista de riscos.
    """
    energia = avaliar_energia(colonia)
    vitais = avaliar_suporte_vida(colonia)
    clima = avaliar_clima(colonia)
    plano = recomendar_operacoes(colonia)          # Bloco 4
    if energia is None or vitais is None or clima is None or plano is None:
        return None
    previsao = previsao_eolica(colonia)
    riscos = avaliar_riscos(colonia, energia, vitais, clima, plano)
    colonia["riscos"] = riscos
    return {
        "energia": energia,
        "plano": plano,
        "vitais": vitais,
        "clima": clima,
        "previsao": previsao,
        "riscos": riscos,
    }


def apresentar_resultados(colonia, avaliacao):
    """Mostra a avaliação com unidades, motivos e limites dos modelos."""
    contexto = colonia["contexto"]
    eolica = colonia["energia"]["eolica"]
    print("\n" + "=" * 66)
    print(f"CENÁRIO {contexto['cenario']} | {contexto['populacao']} pessoas | "
          f"janela de {contexto['periodo_h']} h")
    print("=" * 66)

    print("\n[1] Energia")
    print(diagnostico_energetico(avaliacao["energia"]))
    print(f"Eólica atual:  {eolica['potencia_kw']:.4f} kW ({eolica.get('origem_potencia', 'padrão')})")

    print("\n[1b] Operações complementares (Bloco 4)")
    print(diagnostico_operacoes(avaliacao["plano"]))

    print("\n[2] Previsão eólica (regressão linear, Bloco 2)")
    previsao = avaliacao["previsao"]
    if previsao["a"] is not None:
        print(f"Reta: potência = {previsao['a']:.5f} x vento {previsao['b']:+.5f}")
    if previsao["potencia_kw"] is None:
        print(f"Aviso: {previsao['aviso']}")
    else:
        print(f"Vento {previsao['vento_ms']} m/s -> previsão de {previsao['potencia_kw']:.4f} kW "
              f"({previsao['energia_kwh']:.2f} kWh em {eolica['horas']} h)")

    print("\n[3] Recursos vitais")
    vitais = avaliacao["vitais"]
    print(diagnostico_recurso("Oxigênio", vitais["oxigenio"]))
    print(diagnostico_recurso("Alimentos", vitais["alimentos"], "kg seco"))
    for chave, rotulo in (("oxigenio", "O2"), ("alimentos", "Alimentos")):
        dias = projecao_estoque(vitais[chave])
        if dias is not None:
            print(f"Projeção condicional ({rotulo}): se entrada e consumo se mantiverem, "
                  f"o estoque dura {dias:.2f} dias")

    print("\n[4] Clima")
    for nome, indicador in avaliacao["clima"].items():
        print(f"{nome.capitalize():12} {indicador['valor']} {indicador['unidade']} - {indicador['classe']}")

    print("\n[5] Riscos e recomendações (do mais urgente ao menos urgente)")
    for numero, risco in enumerate(avaliacao["riscos"], start=1):
        print(f"{numero}. [{risco['nivel']}] {risco['frente']}: {risco['recomendacao']}")
        print(f"   Dado: {risco['dado']}")
        print(f"   Motivo: {risco['motivo']}")
        if risco["restricao"]:
            print(f"   Restrição: {risco['restricao']}")
    print("\nLimites: balanço agregado de 24 h, sem baterias; valores P/M do exercício.")


# Bloco 5 — Wallace | Menu e ponto de entrada do programa
# A definição das funções permanece separada de sua execução.

def avaliar_e_mostrar(colonia):
    avaliacao = avaliacao_integrada(colonia)
    if avaliacao is None:
        print("Não foi possível avaliar: há dado inválido no cadastro.")
        return None
    apresentar_resultados(colonia, avaliacao)
    return avaliacao


def menu_personalizado(colonia, ler=input):
    """Modo PERSONALIZADO: parte de NORMAL e edita um módulo por vez."""
    modulos = list(CAMPOS_EDITAVEIS) + ["Operações"]
    while True:
        print("\nPERSONALIZADO | escolha o módulo para editar")
        for numero, modulo in enumerate(modulos, start=1):
            print(f"  {numero}. {modulo}")
        print("  A. Avaliar  |  0. Voltar")
        opcao = ler("Opção: ").strip().upper()
        if opcao == "0":
            return
        if opcao == "A":
            avaliar_e_mostrar(colonia)
            continue
        numero = converter_numero(opcao, inteiro=True)
        if numero is None or not 1 <= numero <= len(modulos):
            print("  Opção inválida.")
            continue
        modulo = modulos[numero - 1]
        if modulo == "Operações":
            editar_operacoes(colonia, ler)
        else:
            editar_modulo(colonia, modulo, ler)


def menu_principal(ler=input):
    """Menu do sistema: cinco cenários, modo personalizado e conferências."""
    while True:
        print("\n=== COLÔNIA AURORA SIGER | Sistema integrado ===")
        for numero, nome in enumerate(ORDEM_CENARIOS, start=1):
            print(f"  {numero}. {nome}")
        print("  6. PERSONALIZADO (parte de NORMAL)")
        print("  7. Executar conferências (exemplos dos blocos)")
        print("  0. Sair")
        opcao = ler("Opção: ").strip()
        if opcao == "0":
            print("Encerrando o sistema.")
            return
        if opcao in ("1", "2", "3", "4", "5"):
            avaliar_e_mostrar(aplicar_cenario(ORDEM_CENARIOS[int(opcao) - 1]))
        elif opcao == "6":
            menu_personalizado(aplicar_cenario("PERSONALIZADO"), ler)
        elif opcao == "7":
            executar_exemplos()
        else:
            print("  Opção inválida: digite um número de 0 a 7.")


"""## **Parte 9, Exemplos de execução**

Material de apoio, seções 7 e 10.

Conferências reproduzíveis de estrutura, energia, regressão e recursos vitais.
A função conferir compara os valores obtidos e esperados e registra OK ou FALHOU.
Os exemplos abrangem condições normais, adversas, limites e entradas inválidas,
incluindo a conexão entre o suporte vital e o balanço solar/eólico.
"""

# Bloco 1 — Montiel | Exemplos da fundação e da parte energética

def conferir(descricao, obtido, esperado):
    """Mostra o resultado de uma conferência e devolve True se bateu."""
    if type(esperado) is float and type(obtido) in (int, float):
        ok = abs(obtido - esperado) < 0.0001
    else:
        ok = obtido == esperado
    situacao = "OK" if ok else "FALHOU"
    print(f"  [{situacao}] {descricao}: obtido {obtido!r}, esperado {esperado!r}")
    return ok


def exemplos_bloco1():
    """Exemplos reproduzíveis da fundação e da parte energética.

    Valores esperados conferidos à mão com o apoio:
      solar = 120 kW x 8 h x fator (seção 3.1)
      consumo de referência = 36 kW x 24 h = 864 kWh (seção 5)
    """
    resultados = []

    print("=== Bloco 1 | Estrutura comum ===")
    colonia = criar_colonia()
    resultados.append(conferir("população padrão", colonia["contexto"]["populacao"], 50))
    resultados.append(conferir("janela de análise (h)", colonia["contexto"]["periodo_h"], 24))
    resultados.append(conferir("cargas cadastradas até o Bloco 4",
                               len(listar_cargas(colonia)), 7))
    colonia["energia"]["solar"]["pot_solar_kw"] = 1
    resultados.append(conferir("editar uma colônia não muda o padrão",
                               SOLAR_PADRAO["pot_solar_kw"], 120))

    print("\n=== Bloco 1 | Geração solar (120 kW, 8 h) ===")
    resultados.append(conferir("NORMAL, fator 1,00", geracao_solar(120, 8, 1.00), 960.0))
    resultados.append(conferir("BAIXA_GERACAO, fator 0,80", geracao_solar(120, 8, 0.80), 768.0))
    resultados.append(conferir("TEMPESTADE, fator 0,10", geracao_solar(120, 8, 0.10), 96.0))

    # Consumos de referência da tabela da seção 5, recebidos como entrada.
    # Este exemplo usa as potências da tabela, independentemente das cargas cadastradas.
    potencias_referencia_kw = {"AUX": 2, "O2": 12, "ALI": 9,
                               "ARM": 4, "PES": 4, "MOB": 3, "CON": 2}
    consumos = {}
    for carga in potencias_referencia_kw:
        consumos[carga] = energia_kwh(potencias_referencia_kw[carga], PERIODO_H)

    print("\n=== Bloco 1 | Balanço energético (consumo de referência 864 kWh) ===")
    casos = [("NORMAL", 1.00, 96.0, "VERDE"),
             ("BAIXA_GERACAO", 0.80, -96.0, "VERMELHO"),
             ("TEMPESTADE", 0.10, -768.0, "VERMELHO")]
    for nome, fator, saldo_esperado, classe_esperada in casos:
        geracoes = {"solar": geracao_solar(120, 8, fator)}
        # Este caso considera somente geração solar; os exemplos seguintes
        # demonstram a eólica e sua conexão ao consumo do suporte vital.
        balanco = balanco_energetico(geracoes, consumos)
        print(f"-- {nome}")
        print(diagnostico_energetico(balanco))
        resultados.append(conferir(f"{nome} saldo", balanco["saldo_kwh"], saldo_esperado))
        resultados.append(conferir(f"{nome} classe", balanco["classificacao"], classe_esperada))

    print("\n=== Bloco 1 | Limites das classificações ===")
    resultados.append(conferir("cobertura 1,10", classificar_cobertura(1.10), "VERDE"))
    resultados.append(conferir("cobertura 1,00", classificar_cobertura(1.00), "AMARELO"))
    resultados.append(conferir("cobertura 0,99", classificar_cobertura(0.99), "VERMELHO"))
    resultados.append(conferir("950,4 / 864 (= 1,10)",
                               balanco_energetico({"solar": 950.4}, {"total": 864})["classificacao"],
                               "VERDE"))
    margem = balanco_energetico({"solar": 900}, {"total": 864})
    resultados.append(conferir("900 / 864: saldo positivo com AMARELO",
                               (margem["saldo_kwh"] > 0, margem["classificacao"]),
                               (True, "AMARELO")))

    print("\n=== Bloco 1 | Consumo zero ===")
    zero = balanco_energetico({"solar": 960}, {"total": 0})
    resultados.append(conferir("cobertura", zero["cobertura"], None))
    resultados.append(conferir("classificação", zero["classificacao"], "NAO SE APLICA"))
    resultados.append(conferir("saldo", zero["saldo_kwh"], 960))

    print("\n=== Bloco 1 | Entradas inválidas (devem devolver None) ===")
    resultados.append(conferir("potência em texto", geracao_solar("120", 8, 1.0), None))
    resultados.append(conferir("potência True", geracao_solar(True, 8, 1.0), None))
    resultados.append(conferir("potência NaN", geracao_solar(math.nan, 8, 1.0), None))
    resultados.append(conferir("potência negativa", geracao_solar(-1, 8, 1.0), None))
    resultados.append(conferir("fator 1,5", geracao_solar(120, 8, 1.5), None))
    resultados.append(conferir("25 horas", geracao_solar(120, 25, 1.0), None))
    resultados.append(conferir("geração negativa no balanço",
                               balanco_energetico({"solar": -5}, {"total": 864}), None))
    resultados.append(conferir("consumo infinito no balanço",
                               balanco_energetico({"solar": 960}, {"total": math.inf}), None))

    print(f"\nBloco 1: {resultados.count(True)} de {len(resultados)} conferências OK.")
    return all(resultados)

# Bloco 2 — Souza | Exemplos de geração eólica e regressão

def exemplos_bloco2():
    """Exemplos reproduzíveis de regressão e geração eólica."""
    resultados = []
    colonia = criar_colonia()
    eolica = colonia["energia"]["eolica"]

    print("\n=== Bloco 2 | Regressão eólica ===")
    ajuste = ajustar_reta(eolica["pares_regressao"])

    if ajuste is not None:
        a, b = ajuste
        print(f"Coeficiente a: {a:.6f}")
        print(f"Coeficiente b: {b:.6f}")

        previsao = prever_potencia(8.5, a, b)
        print(f"Potência prevista para 8,5 m/s: {previsao:.4f} kW")
        resultados.append(conferir(
            "previsão em 8,5 m/s é numérica",
            numero_valido(previsao, minimo=0),
            True
        ))
        resultados.append(conferir("coeficiente angular da reta", a, 1.10496))
        resultados.append(conferir("coeficiente linear da reta", b, -5.67294))
        resultados.append(conferir("potência prevista para 8,5 m/s (kW)", previsao, 3.71922))
        resultados.append(conferir(
            "vento fora da faixa de previsão",
            prever_potencia(22, a, b),
            None
        ))
    else:
        print("Não foi possível realizar os testes da previsão.")
        resultados.append(False)

    print("\n=== Bloco 2 | Geração eólica ===")
    resultados.append(conferir(
        "turbina ligada: 3,7192 kW por 24 h",
        geracao_eolica(3.7192, 24, 1),
        89.2608
    ))
    resultados.append(conferir(
        "turbina desligada",
        geracao_eolica(3.7192, 24, 0),
        0
    ))
    resultados.append(conferir(
        "estado inválido da turbina",
        geracao_eolica(3.7192, 24, 2),
        None
    ))
    resultados.append(conferir(
        "potência negativa",
        geracao_eolica(-3, 24, 1),
        None
    ))
    resultados.append(conferir(
        "período acima de 24 horas",
        geracao_eolica(3.7192, 25, 1),
        None
    ))

    print("\n=== Bloco 2 | Validação da regressão ===")
    resultados.append(conferir(
        "velocidade negativa nos pares",
        ajustar_reta([[-1, 2], [7, 3]]),
        None
    ))
    resultados.append(conferir(
        "potência negativa nos pares",
        ajustar_reta([[6, 2], [7, -3]]),
        None
    ))
    resultados.append(conferir(
        "velocidades repetidas",
        ajustar_reta([[8, 2], [8, 3]]),
        None
    ))

    print("\n=== Bloco 2 | Cadastro e ligação ao balanço energético ===")
    copia_eolica = criar_eolica()
    copia_eolica["pares_regressao"][0][1] = 999
    resultados.append(conferir("pares independentes entre cadastros",
                               criar_eolica()["pares_regressao"][0][1], 1.2215))
    casos = [("NORMAL", 1.00, 8, 1, 165.4872, "VERDE"),
             ("TEMPESTADE", 0.10, 22, 0, -768.0, "VERMELHO")]
    for nome, fator, vento, ativa, saldo_esperado, classe_esperada in casos:
        colonia = criar_colonia()
        colonia["energia"]["solar"]["fator_solar"] = fator
        colonia["energia"]["eolica"].update(vento_ms=vento, ativa=ativa)
        balanco = avaliar_energia(colonia)
        print(f"-- {nome}")
        print(diagnostico_energetico(balanco))
        resultados.append(conferir(f"{nome}, saldo com cargas cadastradas (kWh)",
                                   balanco["saldo_kwh"], saldo_esperado))
        resultados.append(conferir(f"{nome}, classificação energética",
                                   balanco["classificacao"], classe_esperada))

    print(f"\nBloco 2: {resultados.count(True)} de {len(resultados)} conferências OK.")
    return all(resultados)

# Bloco 3 — Cláudio | Exemplos dos recursos vitais e da conexão energética


def exemplos_bloco3():
    """Conferências dos recursos vitais e de sua conexão aos modelos de energia."""
    resultados = []
    colonia = criar_colonia()
    recursos = avaliar_suporte_vida(colonia)

    print("\n=== Bloco 3 | Recursos nas condições normais ===")
    print(diagnostico_recurso("Oxigênio", recursos["oxigenio"]))
    print(diagnostico_recurso("Alimentos", recursos["alimentos"], "kg seco"))
    resultados.append(conferir("demanda diária de O2 (kg)",
                               recursos["oxigenio"]["demanda_kg_dia"], 44.75))
    resultados.append(conferir("saldo de O2 (kg)", recursos["oxigenio"]["saldo_kg"], 134.5))
    resultados.append(conferir("estoque de O2 em dias", recursos["oxigenio"]["cobertura_dias"], 3.0))
    resultados.append(conferir("demanda de alimento seco (kg/dia)",
                               recursos["alimentos"]["demanda_kg_dia"], 40.0))
    resultados.append(conferir("saldo de alimento seco (kg)",
                               recursos["alimentos"]["saldo_kg"], 550.0))
    resultados.append(conferir("estoque de alimentos em dias",
                               recursos["alimentos"]["cobertura_dias"], 14.0))

    print("\n=== Bloco 3 | Energia com as cargas já cadastradas ===")
    # Inclui as quatro operações do Bloco 4: 552 + 312 = 864 kWh.
    consumos = consumos_eletricos(colonia)
    resultados.append(conferir("consumos por carga (kWh)", consumos,
                               {"AUX": 48, "O2": 288, "ALI": 216,
                                "ARM": 96, "PES": 96, "MOB": 72, "CON": 48}))
    solar = colonia["energia"]["solar"]
    # Valor atual modelado do apoio para vento de 8 m/s; não é a previsão.
    colonia["energia"]["eolica"]["potencia_kw"] = 2.8953
    eolica = colonia["energia"]["eolica"]
    geracoes = {
        "solar": geracao_solar(solar["pot_solar_kw"], solar["horas_solares"], solar["fator_solar"]),
        "eolica": geracao_eolica(eolica["potencia_kw"], eolica["horas"], eolica["ativa"]),
    }
    balanco = balanco_energetico(geracoes, consumos)
    print(diagnostico_energetico(balanco))
    resultados.append(conferir("consumo sem repetição (kWh)", balanco["consumo_total_kwh"], 864))
    resultados.append(conferir("saldo solar/eólica com suporte (kWh)",
                               balanco["saldo_kwh"], 165.4872))

    print("\n=== Bloco 3 | Falta no período e reserva curta ===")
    colonia["suporte_vida"]["oxigenio"].update(estoque_kg=22.375, entrada_kg_dia=0)
    colonia["suporte_vida"]["alimentos"].update(estoque_kg=80, entrada_kg_dia=20)
    alerta = avaliar_suporte_vida(colonia)
    print(diagnostico_recurso("Oxigênio", alerta["oxigenio"]))
    print(diagnostico_recurso("Alimentos", alerta["alimentos"], "kg seco"))
    resultados.append(conferir("O2 insuficiente", alerta["oxigenio"]["suficiente"], False))
    resultados.append(conferir("reserva de alimento curta",
                               alerta["alimentos"]["classificacao"], "VERMELHO"))
    resultados.append(conferir("alimento atende às 24 h",
                               alerta["alimentos"]["suficiente"], True))

    print("\n=== Bloco 3 | Limites das reservas ===")
    for nome, verde, amarelo in [("O2", 2, 1), ("alimentos", 7, 3)]:
        for dias, esperado in [(verde, "VERDE"), (amarelo, "AMARELO"), (0, "VERMELHO")]:
            resultados.append(conferir(f"{nome}, estoque para {dias} dias",
                                       classificar_reserva(dias, verde, amarelo), esperado))

    print("\n=== Bloco 3 | Entradas inválidas ===")
    for descricao, dados in [
        ("população zero", (0, 134.25, 45, 0.895)),
        ("população fracionada", (50.5, 134.25, 45, 0.895)),
        ("estoque negativo", (50, -1, 45, 0.895)),
        ("entrada em texto", (50, 134.25, "45", 0.895)),
        ("estoque NaN", (50, math.nan, 45, 0.895)),
        ("entrada infinita", (50, 134.25, math.inf, 0.895)),
        ("taxa zero", (50, 134.25, 45, 0)),
    ]:
        resultados.append(conferir(descricao, balanco_recurso(*dados), None))

    print(f"\nBloco 3: {resultados.count(True)} de {len(resultados)} conferências OK.")
    return all(resultados)


# Bloco 4 — Thales | Exemplos das operações e recomendações


def exemplos_bloco4():
    """Conferências integradas, sem depender do menu ou dos cenários do Bloco 5."""
    resultados = []
    colonia = criar_colonia()
    colonia["operacoes"][0]["pot_normal_kw"] = 99
    resultados.append(conferir("cadastros independentes", criar_operacoes()[0]["pot_normal_kw"], 4))
    casos = [
        ("NORMAL", 1.00, 8, 2.8953, 1, 165.4872, 0.0, 0.0),
        ("BAIXA_GERACAO", 0.80, 6, 1.2215, 1, -66.684, 66.684, 0.0),
        ("TEMPESTADE", 0.10, 22, 0, 0, -768.0, 180.0, 588.0),
    ]
    for nome, fator, vento, potencia, ativa, saldo, economia, deficit in casos:
        colonia = criar_colonia()
        colonia["contexto"]["cenario"] = nome
        colonia["energia"]["solar"]["fator_solar"] = fator
        colonia["energia"]["eolica"].update(vento_ms=vento, potencia_kw=potencia, ativa=ativa)
        # Potência atual M da tabela, não resultado da regressão; tempestade indisponível.
        antes = repr(colonia)
        proposta = recomendar_operacoes(colonia)
        print(f"\n=== Bloco 4 | {nome} ===")
        print(diagnostico_operacoes(proposta))
        resultados.append(conferir(f"{nome}, consumo total", proposta["balanco_atual"]["consumo_total_kwh"], 864))
        resultados.append(conferir(f"{nome}, saldo atual", proposta["balanco_atual"]["saldo_kwh"], saldo))
        resultados.append(conferir(f"{nome}, economia máxima", proposta["economia_maxima_kwh"], 180.0))
        resultados.append(conferir(f"{nome}, economia proposta", proposta["economia_proposta_kwh"], economia))
        resultados.append(conferir(f"{nome}, déficit restante", proposta["deficit_remanescente_kwh"], deficit))
        resultados.append(conferir(f"{nome}, cadastro preservado", repr(colonia) == antes, True))
        resultados.append(conferir(f"{nome}, mínimos respeitados", all(
            item["pot_recomendada_kw"] >= item["minimo_protegido_kw"]
            for item in proposta["recomendacoes"]), True))
        if nome == "BAIXA_GERACAO":
            resultados.append(conferir("ordem da redução parcial",
                [item["id"] for item in proposta["recomendacoes"]], ["CON", "MOB"]))
            resultados.append(conferir("mobilidade recomendada (kW)",
                proposta["recomendacoes"][1]["pot_recomendada_kw"], 1.7215))
            resultados.append(conferir("cobertura sem margem",
                proposta["balanco_proposto"]["classificacao"], "AMARELO"))
        if nome == "TEMPESTADE":
            resultados.append(conferir("ordem completa da redução",
                [item["id"] for item in proposta["recomendacoes"]], ["CON", "MOB", "PES", "ARM"]))
            resultados.append(conferir("consumo mínimo (kWh)", proposta["balanco_proposto"]["consumo_total_kwh"], 684.0))

    print("\n=== Bloco 4 | Validação e limites ===")
    for campo, valor in [("pot_normal_kw", -1), ("pot_normal_kw", math.nan),
                         ("minimo_protegido_kw", math.inf), ("minimo_protegido_kw", 5),
                         ("periodo_h", 12), ("prioridade", True), ("id", "AUX")]:
        colonia = criar_colonia()
        colonia["operacoes"][0][campo] = valor
        resultados.append(conferir(f"operação inválida: {campo}={valor}", recomendar_operacoes(colonia), None))
    colonia = criar_colonia()
    colonia["operacoes"][1]["id"] = "ARM"
    resultados.append(conferir("ID duplicado", recomendar_operacoes(colonia), None))
    colonia = criar_colonia()
    colonia["contexto"]["periodo_h"] = 12
    resultados.append(conferir("janela incompatível", recomendar_operacoes(colonia), None))
    colonia = criar_colonia()
    colonia["energia"]["solar"]["pot_solar_kw"] = 0
    colonia["energia"]["eolica"]["ativa"] = 0
    for operacao in colonia["operacoes"]:
        operacao["pot_normal_kw"] = operacao["minimo_protegido_kw"]
    proposta = recomendar_operacoes(colonia)
    resultados.append(conferir("sem parcela ajustável", proposta["economia_proposta_kwh"], 0.0))
    resultados.append(conferir("déficit com geração zero e mínimos", proposta["deficit_remanescente_kwh"], 684.0))
    colonia = criar_colonia()
    colonia["suporte_vida"]["oxigenio"].update(estoque_kg=22.375, entrada_kg_dia=0)
    recomendar_operacoes(colonia)
    resultados.append(conferir("economia não repõe O2", avaliar_suporte_vida(colonia)["oxigenio"]["suficiente"], False))
    print(f"\nBloco 4: {resultados.count(True)} de {len(resultados)} conferências OK.")
    return all(resultados)


def exemplos_blocos1_a4():
    """Executa as evidências acumuladas para o repasse ao Bloco 5."""
    resultados = [exemplos_bloco1(), exemplos_bloco2(), exemplos_bloco3(), exemplos_bloco4()]
    return all(resultados)


# Bloco 5 — Wallace | Exemplos de clima, riscos e integração completa

def leitor_simulado(respostas):
    """Simula o teclado: devolve uma resposta por chamada e mostra o que foi 'digitado'."""
    fila = list(respostas)

    def ler(mensagem):
        resposta = fila.pop(0)
        print(f"{mensagem}{resposta}")
        return resposta
    return ler


def exemplos_bloco5():
    """Conferências de clima, cenários, riscos combinados, entradas e integração."""
    resultados = []

    print("\n=== Bloco 5 | Limites das classificações ambientais ===")
    for vento, esperado in [(0, "VERDE"), (10, "VERDE"), (10.1, "AMARELO"),
                            (15, "AMARELO"), (15.1, "VERMELHO"), (22, "VERMELHO")]:
        resultados.append(conferir(f"vento {vento} m/s", classificar_vento(vento), esperado))
    for tau, esperado in [(1, "VERDE"), (1.5, "AMARELO"), (3, "AMARELO"), (4.5, "VERMELHO")]:
        resultados.append(conferir(f"poeira tau {tau}", classificar_poeira(tau), esperado))
    for temp, esperado in [(-80, "VERDE"), (-20, "VERDE"), (-80.1, "AMARELO"),
                           (-100, "AMARELO"), (-19, "AMARELO"), (0, "AMARELO"),
                           (-101, "VERMELHO"), (1, "VERMELHO")]:
        resultados.append(conferir(f"temperatura {temp} °C",
                                   classificar_temperatura(temp), esperado))
    for descricao, valor in [("vento negativo", classificar_vento(-1)),
                             ("poeira em texto", classificar_poeira("2")),
                             ("temperatura NaN", classificar_temperatura(math.nan))]:
        resultados.append(conferir(descricao, valor, None))

    print("\n=== Bloco 5 | Cinco cenários de referência ===")
    # (cenário, saldo de energia kWh, classe, déficit após reduções, níveis esperados)
    casos = [
        ("NORMAL", 165.4872, "VERDE", 0, {"INFO"}),
        ("BAIXA_GERACAO", -66.684, "VERMELHO", 0, {"ALTO", "ATENCAO"}),
        ("TEMPESTADE", -768.0, "VERMELHO", 588.0, {"CRITICO", "ALTO"}),
        ("SUPORTE_VIDA_EM_ALERTA", 165.4872, "VERDE", 0, {"CRITICO", "ALTO", "INFO"}),
        ("MULTIPLAS_RESTRICOES", -768.0, "VERMELHO", 588.0, {"CRITICO", "ALTO"}),
    ]
    for nome, saldo, classe, restante, niveis in casos:
        colonia = aplicar_cenario(nome)
        avaliacao = avaliacao_integrada(colonia)
        print(f"-- {nome}")
        resultados.append(conferir(f"{nome}, saldo (kWh)", avaliacao["energia"]["saldo_kwh"], saldo))
        resultados.append(conferir(f"{nome}, classe energética",
                                   avaliacao["energia"]["classificacao"], classe))
        resultados.append(conferir(f"{nome}, déficit após reduções (kWh)",
                                   float(avaliacao["plano"]["deficit_remanescente_kwh"]), float(restante)))
        obtidos = set(risco["nivel"] for risco in avaliacao["riscos"])
        resultados.append(conferir(f"{nome}, níveis de risco", obtidos, niveis))

    print("\n=== Bloco 5 | Regras combinadas ===")
    tempestade = avaliacao_integrada(aplicar_cenario("TEMPESTADE"))
    frentes = [risco["frente"] for risco in tempestade["riscos"]]
    resultados.append(conferir("TEMPESTADE: solar baixa AND eólica inativa gera risco",
                               any("eólica indisponível" in r["dado"] for r in tempestade["riscos"]),
                               True))
    resultados.append(conferir("TEMPESTADE: energia + ambiente = restrição conjunta",
                               "Conjunta" in frentes, True))
    multiplas = avaliacao_integrada(aplicar_cenario("MULTIPLAS_RESTRICOES"))
    resultados.append(conferir("MULTIPLAS: primeiro risco é CRITICO",
                               multiplas["riscos"][0]["nivel"], "CRITICO"))
    resultados.append(conferir("MULTIPLAS: três frentes adversas",
                               any(r["dado"].startswith("3 frentes") for r in multiplas["riscos"]),
                               True))
    alerta = avaliacao_integrada(aplicar_cenario("SUPORTE_VIDA_EM_ALERTA"))
    resultados.append(conferir("SUPORTE_VIDA: O2 aponta que economia não repõe",
                               any("não repõe" in r["restricao"] for r in alerta["riscos"]), True))

    print("\n=== Bloco 5 | Previsão e potência atual separadas ===")
    normal = aplicar_cenario("NORMAL")
    normal["energia"]["eolica"]["vento_ms"] = 8.5
    previsao = previsao_eolica(normal)
    resultados.append(conferir("previsão em 8,5 m/s (kW)", previsao["potencia_kw"], 3.71922))
    resultados.append(conferir("potência atual não muda com a previsão (kW)",
                               normal["energia"]["eolica"]["potencia_kw"], 2.8953))
    resultados.append(conferir("22 m/s: sem previsão numérica",
                               previsao_eolica(aplicar_cenario("TEMPESTADE"))["potencia_kw"], None))
    alerta_o2 = alerta["vitais"]["oxigenio"]
    resultados.append(conferir("projeção condicional do O2 (dias)",
                               projecao_estoque(alerta_o2), 0.5))
    resultados.append(conferir("projeção com entrada cobrindo a demanda",
                               projecao_estoque(avaliacao_integrada(aplicar_cenario("NORMAL"))
                                                ["vitais"]["oxigenio"]), None))

    print("\n=== Bloco 5 | Entradas digitadas inválidas ===")
    ler = leitor_simulado(["abc", "nan", "1,5", "0,8"])
    resultados.append(conferir("fator solar após 3 tentativas inválidas",
                               ler_numero("Fator solar (0 a 1)", 1.0, 0, 1, False, ler), 0.8))
    ler = leitor_simulado(["0", "50.5", "-3", "60"])
    resultados.append(conferir("população só aceita inteiro positivo",
                               ler_numero("População (pessoas)", 50, 1, None, True, ler), 60))
    ler = leitor_simulado([""])
    resultados.append(conferir("Enter mantém o valor atual",
                               ler_numero("Poeira (tau)", 0.5, 0, None, False, ler), 0.5))
    personalizado = aplicar_cenario("PERSONALIZADO")
    editar_operacoes_teste = personalizado["operacoes"][3]
    ler = leitor_simulado(["", "", "", "0,2", "0,5"])
    editar_operacoes(personalizado, ler)
    resultados.append(conferir("conforto não fica abaixo do mínimo (kW)",
                               editar_operacoes_teste["pot_normal_kw"], 0.5))

    print("\n=== Bloco 5 | Modo personalizado ===")
    personalizado = aplicar_cenario("PERSONALIZADO")
    resultados.append(conferir("PERSONALIZADO parte de NORMAL",
                               personalizado["energia"]["eolica"]["potencia_kw"], 2.8953))
    ler = leitor_simulado(["1", "8,5", "1", "2"])
    editar_modulo(personalizado, "Energia eólica", ler)
    eolica = personalizado["energia"]["eolica"]
    resultados.append(conferir("8,5 m/s fora da tabela: usa a regressão (kW)",
                               eolica["potencia_kw"], 3.71922))
    resultados.append(conferir("origem da potência registrada",
                               eolica["origem_potencia"], "estimada pela regressão"))
    resultados.append(conferir("clima usa o mesmo vento da eólica",
                               avaliar_clima(personalizado)["vento"]["valor"], 8.5))
    resultados.append(conferir("cenário inexistente", aplicar_cenario("MARTE_FELIZ"), None))
    resultados.append(conferir("cenário editado continua independente do padrão",
                               CENARIOS["NORMAL"]["vento_ms"], 8))

    print(f"\nBloco 5: {resultados.count(True)} de {len(resultados)} conferências OK.")
    return all(resultados)


def executar_exemplos():
    """Roda as conferências de todos os blocos."""
    resultados = [exemplos_blocos1_a4(), exemplos_bloco5()]
    print("\nResumo: todos os blocos OK." if all(resultados)
          else "\nResumo: há conferências com FALHOU; ver acima.")
    return all(resultados)


if __name__ == "__main__":
    try:
        menu_principal()
    except (KeyboardInterrupt, EOFError):
        print("\nEntrada interrompida. Encerrando o sistema.")
