"""
# 🚀 **Colônia em Marte | Sistema Integrado da Colônia | Fase 3**

***Equipe Tribo Solarian.***

Preparação do protótipo da Fase 3. Como nas fases anteriores, o arquivo está
dividido em partes temáticas: cada parte tem uma apresentação sobre sua função,
seguida pelo espaço onde a equipe escreverá o código correspondente.

As seções citadas são as do material de apoio `docs/Colonia_material_apoio.docx`.
Os documentos ficam em `docs/` e as evidências em `testes/`, quando produzidos.
Este arquivo ainda não contém a implementação.

## Repositório do projeto:
    URL>>

## Integrantes
- Cláudio Roberto Grillo Reis Silveira
- Vitor Lima Montiel
- Wallace Gabriel Américo Albuquerque
- Victor Augusto dos Santos Souza
- Thales Martins Oliveira Barros

## Como executar
    As instruções serão preenchidas no README após a implementação.

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
- Bloco 1, Montiel: fundação, solar e balanço energético, em 03/11/2026.
- Bloco 2, Souza: eólica e regressão, em 04/11/2026.
- Bloco 3, Cláudio: oxigênio e alimentos, em 05/11/2026.
- Bloco 4, Wallace: operações e recomendações, em 06/11/2026.
- Bloco 5, Thales: clima, riscos e integração, em 09 e 10/11/2026.

O desenvolvimento segue essa sequência, mas cada bloco contribui nas partes
temáticas pertinentes. Os comentários abaixo indicam os locais de implementação.
README e textos do relatório acompanham cada repasse; PDF e fechamento em 11/11.
"""


"""## **Parte 0, Bibliotecas e configuração**

Material de apoio, seção 10.3.

Reúne os imports e configurações compartilhadas pelo programa. Utilizar recursos
nativos e bibliotecas padrão quando necessários aos conteúdos trabalhados.
Cada integrante acrescenta apenas o que sua contribuição realmente utiliza.
"""

# Bloco 1 — Montiel: iniciar aqui os imports e a configuração comum.

import math  # math.isfinite confere se um número não é NaN nem infinito
# Blocos 2 a 5 — Souza, Cláudio, Wallace e Thales: complementar este mesmo local.


"""## **Parte 1, Constantes, limiares e padrões**

Material de apoio, seções 1 a 8.

Reúne os valores ajustáveis, separados da lógica: população, janela de análise,
parâmetros solares e eólicos, estoques, taxas, cargas, mínimos operacionais,
limiares ambientais e cenários. Manter as unidades e a origem dos dados.

Os parâmetros já estão no apoio. Referências publicadas, parâmetros do exercício
e dados modelados devem continuar identificados; não duplicar uma mesma carga.
"""

# Bloco 1 — Montiel: inserir aqui contexto, parâmetros solares e cargas comuns.

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
    "fator_solar": 1.00,   # P: de 0 a 1; já inclui a perda adotada, usar uma vez só
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

# Bloco 2 — Souza: inserir aqui parâmetros eólicos e pares para a regressão.


# Bloco 3 — Cláudio: inserir aqui estoques, taxas, entradas e limiares vitais.


# Bloco 4 — Wallace: inserir aqui dados das operações, mínimos e prioridades.


# Bloco 5 — Thales: inserir aqui parâmetros ambientais, limiares e cenários.


"""## **Parte 2, Módulos e estruturas de dados**

Material de apoio, seções 1 e 9.1.

Organiza os dados da colônia em listas, registros chave-valor e agrupamentos
hierárquicos. Energia contém solar/eólica; os demais grupos representam recursos
vitais, operações, clima e riscos. Cada integrante amplia a mesma base recebida.

As funções desta parte organizam e dão acesso aos dados. Cálculos ficam na
Parte 7, classificações na Parte 5 e interação com o usuário nas Partes 3 e 8.
"""

# Bloco 1 — Montiel: implementar aqui a estrutura comum e o acesso à hierarquia.

def criar_colonia(populacao=POPULACAO_PADRAO):
    """Cria a estrutura comum da colônia em dicionários aninhados.

    sistema -> subsistema -> campos. Os grupos vazios são preenchidos
    pelos blocos seguintes, sem criar outra estrutura.
    """
    colonia = {
        "contexto": {
            "cenario": "NORMAL",
            "populacao": populacao,
            "periodo_h": PERIODO_H,
        },
        "energia": {
            "solar": dict(SOLAR_PADRAO),          # cópia: editar não muda o padrão
            "eolica": {},                         # Bloco 2
            "auxiliares": dict(CARGA_AUXILIARES),
        },
        "suporte_vida": {
            "oxigenio": {},                       # Bloco 3
            "alimentos": {},                      # Bloco 3
        },
        "operacoes": [],                          # Bloco 4: lista de registros
        "clima": {},                              # Bloco 5
        "riscos": [],                             # Bloco 5
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

# Bloco 2 — Souza: acrescentar aqui as estruturas dos dados e pares eólicos.


# Bloco 3 — Cláudio: acrescentar aqui os registros de oxigênio e alimentos.


# Bloco 4 — Wallace: acrescentar aqui os registros das quatro operações.


# Bloco 5 — Thales: acrescentar aqui os registros de ambiente e resultados gerais.


"""## **Parte 3, Entrada de dados manual**

Material de apoio, seções 7 e 10.1.

Reúne a leitura e validação de entradas por módulo. Cada pergunta identifica
a unidade e os valores aceitos. O operador pode aceitar os dados do cenário
ou editar os campos; erros de entrada devem ser explicados para nova tentativa.

Esta parte fornece dados às funções, sem misturar perguntas com os cálculos.
Até o bloco final, os exemplos de cada contribuição usam entradas de conferência.
"""

# Bloco 5 — Thales: implementar aqui leitura, validação e edição dos campos.


"""## **Parte 4, Preparação do cenário e dos dados de avaliação**

Material de apoio, seção 7.

Prepara o contexto a ser avaliado a partir do cenário escolhido e das entradas
manuais. Os sistemas devem usar a mesma população, janela e condição ambiental.
Os cenários são os do apoio; PERSONALIZADO parte dos valores de NORMAL.

Ao contrário das leituras simuladas do pouso, esta fase utiliza os dados
informados, sem acrescentar sorteios ou sensores que não fazem parte do escopo.
"""

# Bloco 5 — Thales: implementar aqui a preparação e atualização do contexto comum.


"""## **Parte 5, Classificação e regras de decisão**

Material de apoio, seções 3.3, 4, 6 e 9.2.

Transforma os dados e os resultados dos modelos em classificações e diagnósticos
com motivos. As faixas devem aparecer por escrito, sem depender apenas de cores.
Condições simples e combinadas relacionam energia, recursos e ambiente.

Os resultados numéricos vêm da Parte 7. A recomendação de ajustes respeita
a prioridade das operações, tratada separadamente na Parte 6.
"""

# Bloco 1 — Montiel: implementar aqui classificação e diagnóstico energético.

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

# Bloco 3 — Cláudio: implementar aqui classificações e diagnósticos dos recursos.


# Bloco 5 — Thales: implementar aqui classificações de vento, poeira e temperatura.


# Bloco 5 — Thales: implementar aqui condições combinadas e avaliação dos riscos.


"""## **Parte 6, Prioridades e recomendações de equilíbrio**

Material de apoio, seção 5.

Organiza as recomendações de redução das operações complementares por importância,
preservando funções essenciais e mínimos protegidos. Utiliza os consumos calculados
na Parte 7 e os diagnósticos da Parte 5 para explicar os ajustes e suas limitações.

O programa orienta o operador, sem alterar automaticamente as entradas. A falta
de oxigênio ou alimento não é resolvida apenas por uma economia de energia.
"""

# Bloco 4 — Wallace: implementar aqui prioridades e recomendações das operações.


"""## **Parte 7, Modelos matemáticos e previsão**

Material de apoio, seções 3, 4, 5 e 8.

Reúne os cálculos solares e eólicos, o balanço energético, os balanços dos recursos,
os consumos das operações e a regressão simples. Cada função recebe os dados
necessários e devolve resultados com unidades, sem solicitar entradas ao usuário.

A estimativa por regressão utiliza os pares modelados do apoio e deve ser
identificada separadamente da geração atual. Respeitar a faixa de ajuste,
as limitações dos dados e as conferências necessárias antes de calcular.
"""

# Bloco 1 — Montiel: implementar aqui geração solar e balanço energético.

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


# Bloco 2 — Souza: implementar aqui geração eólica do período.


# Bloco 2 — Souza: implementar aqui ajuste da regressão e estimativa.


# Bloco 3 — Cláudio: implementar aqui balanços e indicadores de oxigênio/alimentos.


# Bloco 4 — Wallace: implementar aqui consumos e parcelas ajustáveis das operações.


"""## **Parte 8, Avaliação integrada e menu principal**

Material de apoio, seções 9 e 10.

Reúne as funções anteriores em uma avaliação única: prepara o contexto, realiza
os cálculos, obtém classificações, cruza riscos e apresenta recomendações.
O menu permite selecionar cenário, editar dados e reavaliar a colônia.

Mostrar os dados avaliados, unidades, resultados, motivos, limitações e previsão
quando aplicável. Utilizar as funções dos blocos recebidos. A ordem das chamadas
do programa é diferente da sequência de construção dos integrantes.
"""

# Bloco 5 — Thales: implementar aqui a avaliação integrada e sua apresentação.


# Bloco 5 — Thales: implementar aqui o menu e o ponto de entrada do programa.
# Manter o início da execução separado das definições, sem abrir menu na importação.


"""## **Parte 9, Exemplos de execução**

Material de apoio, seções 7 e 10.

Reúne exemplos reproduzíveis com entrada, saída obtida e conferência realizada.
Cada bloco acrescenta seus casos e mantém os exemplos das contribuições recebidas.
Incluir situações normais, adversas, limites e entradas inválidas pertinentes.

Ao final, conferir os cenários em uma execução integrada e usar os resultados
reais no README e no relatório. Não há saídas resolvidas neste roteiro.
"""

# Bloco 1 — Montiel: inserir aqui exemplos da fundação e da parte energética.

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
    resultados.append(conferir("cargas cadastradas até o Bloco 1",
                               len(listar_cargas(colonia)), 1))
    colonia["energia"]["solar"]["pot_solar_kw"] = 1
    resultados.append(conferir("editar uma colônia não muda o padrão",
                               SOLAR_PADRAO["pot_solar_kw"], 120))

    print("\n=== Bloco 1 | Geração solar (120 kW, 8 h) ===")
    resultados.append(conferir("NORMAL, fator 1,00", geracao_solar(120, 8, 1.00), 960.0))
    resultados.append(conferir("BAIXA_GERACAO, fator 0,80", geracao_solar(120, 8, 0.80), 768.0))
    resultados.append(conferir("TEMPESTADE, fator 0,10", geracao_solar(120, 8, 0.10), 96.0))

    # Consumos de referência da tabela da seção 5, recebidos como entrada.
    # Quando os Blocos 3 e 4 existirem, virão de listar_cargas().
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
        # Ponto de conexão da geração eólica (Bloco 2):
        # geracoes["eolica"] = <energia eólica do período em kWh>
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

# Bloco 2 — Souza: inserir aqui exemplos de eólica, regressão e ligação energética.


# Bloco 3 — Cláudio: inserir aqui exemplos dos recursos vitais e suas cargas.


# Bloco 4 — Wallace: inserir aqui exemplos das operações, mínimos e recomendações.


# Bloco 5 — Thales: inserir aqui exemplos de clima, riscos e funcionamento integrado.
