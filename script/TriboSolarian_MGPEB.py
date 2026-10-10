# -*- coding: utf-8 -*-
"""TriboSolarian_MGPEB.py

# 🚀 **MGPEB | Módulo de Gerenciamento de Pouso e Estabilização de Base**

***Equipe Tribo Solarian.***

ESQUELETO, sem implementação. Este arquivo só organiza as seções (Partes 0 a 9) do
protótipo da Fase 2 (missão Aurora Siger). Cada parte tem uma célula de apresentação
(o que a seção faz e como vai funcionar) e, logo abaixo, o espaço onde o código será
escrito. As seções citadas (seção 2, seção 6 e assim por diante) são as do material de
apoio, `docs/MGPEB_material_apoio.docx`. Os itens citados (item 1 a item 4) são os do
enunciado da Fase 2. Os itens 5 (evolução da computação) e 6 (ESG) ficam só no relatório.

## Integrantes
- Cláudio Roberto Grillo Reis Silveira | RM575353
- Vitor Lima Montiel | RM575458
- Wallace Gabriel Américo Albuquerque | RM575435
- Victor Augusto dos Santos Souza | RM576021
- Thales Martins Olveira Barros | RM574664

## Como executar 
    python TriboSolarian_MGPEB.py
Somente biblioteca padrão do Python, nenhuma instalação.

## Sumário
- Parte 0, bibliotecas e configuração
- Parte 1, constantes, limiares e padrões (itens 1 e 2)
- Parte 2, módulos e estruturas lineares: fila, listas e pilha (item 1)
- Parte 3, entrada de dados manual
- Parte 4, simulação das leituras, média e oscilação
- Parte 5, classificação e regra de decisão (itens 2 e 3)
- Parte 6, ordenação e busca (item 3)
- Parte 7, modelos matemáticos (item 4)
- Parte 8, rodada de simulação e menu principal
- Parte 9, exemplos de execução
"""

"""## **Parte 0, Bibliotecas e configuração**

Material de apoio, seção 9 (bibliotecas) e seção 7 (limites de hardware).

Uso previsto.
- `random`, biblioteca padrão, para sortear a oscilação das leituras (Parte 4) e fixar
  a semente com `random.seed`, de modo que os resultados se repitam.
- `math`, biblioteca padrão, para a exponencial dos modelos da Parte 7.
- `input` e `print`, nativos do Python, para entrada e saída.
- Nada de `pandas`, `numpy`, `scikit-learn`, `colorama` ou `tabulate`, ao contrário da
  Fase 1. A tabela no terminal será montada com `print` e formatação de texto.

Justificativa de projeto (item 5 do enunciado): em Marte a memória e o processamento
são limitados, então o código usa listas simples e algoritmos fáceis de auditar.
"""

# TODO (Parte 0), imports e semente padrão

import random
import math

SEMENTE_PADRAO = 42


"""## **Parte 1, Constantes, limiares e padrões (itens 1 e 2)**

Material de apoio, seções 2 e 3.

Reúne em um só lugar tudo o que pode ser ajustado sem mexer na lógica.
- Limiares de cada variável, com as faixas verde, amarela e vermelha (combustível,
  sensores, vento e poeira), como nas tabelas das seções 2.3 a 2.6.
- Os 3 cenários de ambiente (calmo, moderado e tempestade), cada um com média e
  oscilação de vento e de poeira (seção 2.8).
- Padrão de cada módulo, com atributos fixos e médias e oscilações das leituras
  (seções 2.1 e 2.2).
- Faixas físicas permitidas, por exemplo de 0 a 100 para porcentagens.
- Constantes dos modelos matemáticos: gravidade de Marte, impulso específico,
  irradiância solar e demais valores da seção 6.

Convenção da equipe: constantes em MAIÚSCULAS e faixas em tuplas.
"""

# TODO (Parte 1), constantes, cenários e padrões por tipo

LIMIARES = {"combustivel": (30, 40), "sensores": (75, 90),
            "vento": (8, 15), "poeira": (1, 3)}
FAIXA_PERCENTUAL = (0, 100)
CENARIOS = {
    "calmo": {"vento": (5, 3), "poeira": (0.5, 0.3)},
    "moderado": {"vento": (11, 4), "poeira": (2, 0.8)},
    "tempestade": {"vento": (22, 6), "poeira": (4.5, 1)},
}
TIPOS = ("habitação", "energia", "laboratório", "logística", "suporte médico")
CRITICIDADES = ("baixa", "média", "alta", "vital")
PADROES = [
    ("HAB-01", TIPOS[0], 9.5, 2, "alta", "06:10", 70, 10, 95, 3),
    ("ENE-01", TIPOS[1], 7, 1, "vital", "06:25", 40, 12, 96, 3),
    ("LAB-01", TIPOS[2], 6, 3, "média", "06:40", 65, 10, 92, 4),
    ("LOG-01", TIPOS[3], 11, 3, "baixa", "06:05", 80, 8, 94, 4),
    ("MED-01", TIPOS[4], 4.5, 1, "vital", "07:00", 55, 10, 97, 2),
]
GRAVIDADE_MARTE = 3.73
GRAVIDADE_TERRA = 9.80665
IMPULSO_ESPECIFICO = 312
ALTURA_INICIAL = 1800
VELOCIDADE_INICIAL = -100
ACELERACAO = VELOCIDADE_INICIAL ** 2 / (2 * ALTURA_INICIAL)
IRRADIANCIA_SOLAR = 586.2
AREA_PAINEIS = 100
EFICIENCIA_SOLAR = 0.295
DURACAO_DIA_CLARO = 12.33
FRACAO_TANQUE = 0.4


"""## **Parte 2, Módulos e estruturas lineares: fila, listas e pilha (item 1)**

Material de apoio, seções 2.1 e 5. Alimenta o Anexo de estruturas de dados do relatório.

Cada módulo guarda dois grupos de atributos.
- Fixos: id, tipo, massa, prioridade, criticidade da carga e horário de chegada à
  órbita.
- Dinâmicos: média e oscilação do combustível e da integridade dos sensores, mais a
  última leitura sorteada.

A estrutura de cada módulo (dicionário ou classe simples) será definida na hora de
implementar, mantendo o que foi visto na disciplina.

Estruturas previstas.
- `fila_pouso`, fila (FIFO), módulos aguardando autorização, em ordem de prioridade.
- `pousados`, lista, módulos que já pousaram.
- `espera`, lista, módulos adiados por condição temporária.
- `alerta`, lista, módulos com sensores em vermelho.
- `historico_eventos`, pilha (LIFO), cada decisão é empilhada e o último evento é o
  primeiro a ser consultado ou desfeito.

Funções previstas (nomes sugeridos).
- `criar_modulo(...)`, monta o módulo a partir do padrão e dos ajustes.
- `horario_para_minutos(texto)`, converte "HH:MM" em minutos, para poder ordenar.
- `enfileirar`, `desenfileirar`, `ver_topo`.
- `empilhar`, `desempilhar`, `ver_topo_pilha`.
- `mover_modulo(origem, destino, modulo)`, troca o módulo de lista e registra o evento.
"""

# TODO (Parte 2), estrutura do módulo e operações de fila, lista e pilha

def horario_para_minutos(texto):
    if len(texto) != 5 or texto[2] != ":" or not (texto[:2] + texto[3:]).isdigit():
        raise ValueError("Use HH:MM.")
    hora, minuto = map(int, texto.split(":"))
    if not (0 <= hora <= 23 and 0 <= minuto <= 59):
        raise ValueError("Horário fora da faixa.")
    return hora * 60 + minuto


def criar_modulo(id, tipo, massa, prioridade, criticidade, chegada,
                 combustivel_media, combustivel_oscilacao, sensores_media, sensores_oscilacao):
    horario_para_minutos(chegada)
    if not id.strip() or len(id) > 10 or tipo not in TIPOS or criticidade not in CRITICIDADES:
        raise ValueError("Identificação, tipo ou criticidade inválidos.")
    valores = (massa, prioridade, combustivel_media, combustivel_oscilacao,
               sensores_media, sensores_oscilacao)
    if not all(math.isfinite(v) for v in valores):
        raise ValueError("Os números devem ser finitos.")
    if massa <= 0 or not 1 <= prioridade <= 5 or int(prioridade) != prioridade:
        raise ValueError("Massa ou prioridade inválida.")
    if not (0 <= combustivel_media <= 100 and 0 <= sensores_media <= 100):
        raise ValueError("Percentuais devem estar entre 0 e 100.")
    if min(combustivel_oscilacao, sensores_oscilacao) < 0:
        raise ValueError("Oscilação não pode ser negativa.")
    return {"id": id, "tipo": tipo, "massa": massa, "prioridade": int(prioridade),
            "criticidade": criticidade, "chegada": chegada,
            "combustivel_media": combustivel_media, "combustivel_oscilacao": combustivel_oscilacao,
            "sensores_media": sensores_media, "sensores_oscilacao": sensores_oscilacao,
            "combustivel": combustivel_media, "sensores": sensores_media}


def enfileirar(fila, modulo):
    fila.append(modulo)


def desenfileirar(fila):
    return fila.pop(0) if fila else None


def ver_topo(fila):
    return fila[0] if fila else None


def empilhar(pilha, evento):
    pilha.append(evento)


def desempilhar(pilha):
    return pilha.pop() if pilha else None


def ver_topo_pilha(pilha):
    return pilha[-1] if pilha else None


def criar_estado(modulos=None, cenario="calmo", modo="demonstração"):
    cadastro = [criar_modulo(*p) for p in PADROES] if modulos is None else modulos
    if len({m["id"] for m in cadastro}) != len(cadastro):
        raise ValueError("IDs repetidos.")
    return {"cadastro": cadastro, "fila_pouso": list(cadastro), "pousados": [],
            "espera": [], "alerta": [], "historico_eventos": [], "rodada": 0,
            "area_ocupada": False, "cenario": dict(CENARIOS[cenario]) if isinstance(cenario, str) else dict(cenario),
            "modo": modo, "gerador": random.Random(SEMENTE_PADRAO if modo == "demonstração" else None)}


def mover_modulo(origem, destino, modulo, estado, decisao, motivos):
    indice = estado[origem].index(modulo)
    evento = {"rodada": estado["rodada"], "modulo": modulo["id"],
              "origem": origem, "destino": destino, "indice": indice,
              "decisao": decisao, "motivos": list(motivos),
              "area_anterior": estado["area_ocupada"]}
    estado[origem].remove(modulo)
    enfileirar(estado[destino], modulo)
    if destino == "pousados":
        estado["area_ocupada"] = True
    empilhar(estado["historico_eventos"], evento)
    return evento


def desfazer_ultimo_evento(estado):
    evento = ver_topo_pilha(estado["historico_eventos"])
    if evento is None:
        return None
    modulo = next(m for m in estado["cadastro"] if m["id"] == evento["modulo"])
    for nome in ("fila_pouso", "pousados", "espera", "alerta"):
        if modulo in estado[nome]:
            estado[nome].remove(modulo)
            break
    # Toda reversão devolve o módulo à fila, como exige o material de apoio.
    estado["fila_pouso"].insert(min(evento["indice"], len(estado["fila_pouso"])), modulo)
    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
    estado["area_ocupada"] = False
    return desempilhar(estado["historico_eventos"])


"""## **Parte 3, Entrada de dados manual**

Material de apoio, seções 2.1, 2.2, 2.8 e 4.1.

Como não há sensores físicos, os dados entram por `input`, em 3 etapas.
1. Escolha do cenário de ambiente: calmo, moderado, tempestade ou personalizado.
2. Escolha do modo: demonstração (semente fixa), determinístico (sem oscilação) ou
   aleatório livre.
3. Cadastro dos módulos: aceitar os padrões com Enter ou editar um módulo, campo a
   campo, com o padrão entre colchetes.

Regras de validação, como na Fase 1.
- Cada pergunta se repete até o valor ser válido (laço com tratamento de erro).
- Aceita vírgula ou ponto nos decimais.
- Porcentagem de 0 a 100, oscilação maior ou igual a 0, massa maior que 0, prioridade
  de 1 a 5, horário no formato HH:MM, tipo e criticidade dentro das opções, id com até
  10 caracteres e sem repetição.

Funções previstas (nomes sugeridos).
- `pedir_numero(mensagem, minimo, maximo, padrao)`.
- `pedir_opcao(mensagem, opcoes, padrao)`.
- `pedir_horario(mensagem, padrao)`.
- `escolher_cenario()`, `escolher_modo()`, `cadastrar_modulos()`.
"""

# TODO (Parte 3), funções de entrada com validação

# ============================================================
# FUNÇÃO: combust_rest
# Solicita o combustível restante e classifica sua condição.
# Verde: acima de 40%.
# Amarelo: de 30% até 40%.
# Vermelho: abaixo de 30%.
# ============================================================

# Integração: limiares centralizados seguem o material de apoio.
def combust_rest(padrao=None):
    combust = pedir_numero("Combustível restante (%)", 0, 100, padrao)
    classificacao = classificar_combustivel(combust).capitalize()
    print("Classificação:", classificacao)
    return combust, classificacao


# ============================================================
# FUNÇÃO: integ_sens
# Solicita a integridade dos sensores e classifica seu estado.
# Verde: 90% ou mais.
# Amarelo: de 75% até menos de 90%.
# Vermelho: abaixo de 75%.
# ============================================================

# Integração: limiares centralizados seguem o material de apoio.
def integ_sens(padrao=None):
    integ = pedir_numero("Integridade dos sensores (%)", 0, 100, padrao)
    classificacao = classificar_sensores(integ).capitalize()
    print("Classificação:", classificacao)
    return integ, classificacao


# ============================================================
# FUNÇÃO: veloc_vent
# Solicita a velocidade do vento em m/s e classifica o risco.
# Verde: até 7 m/s.
# Amarelo: acima de 7 até 15 m/s.
# Vermelho: acima de 15 m/s.
# ============================================================

# Integração: limiares centralizados seguem o material de apoio.
def veloc_vent(padrao=None):
    vent = pedir_numero("Velocidade do vento (m/s)", 0, None, padrao)
    classificacao = classificar_vento(vent).capitalize()
    print("Classificação:", classificacao)
    return vent, classificacao


# ============================================================
# FUNÇÃO: poeira_atm
# Solicita o nível de poeira atmosférica e classifica a condição.
# Verde: até 1.
# Amarelo: acima de 1 até 3.
# Vermelho: acima de 3.
# Os limites dependem da unidade de medição definida no projeto.
# ============================================================

# Integração: limiares centralizados seguem o material de apoio.
def poeira_atm(padrao=None):
    poeira = pedir_numero("Poeira atmosférica (τ)", 0, None, padrao)
    classificacao = classificar_poeira(poeira).capitalize()
    print("Classificação:", classificacao)
    return poeira, classificacao


# ============================================================
# FUNÇÃO: area_pouso
# Verifica se a área de pouso está disponível.
# Verde: área livre.
# Vermelho: área ocupada.
# ============================================================

def area_pouso():
    while True:
        print("A área de pouso está livre?")
        pouso = input("Digite 1 para Sim e 2 para Não: ")

        if pouso == "1":
            classificacao = "Verde"
            break
        elif pouso == "2":
            classificacao = "Vermelho"
            break
        else:
            print("Digite apenas 1 ou 2.")

    print("Classificação da área:", classificacao)
    return int(pouso), classificacao

def pedir_numero(mensagem, minimo=None, maximo=None, padrao=None, inteiro=False):
    while True:
        texto = input(f"{mensagem}" + (f" [{padrao}]" if padrao is not None else "") + ": ").strip()
        try:
            valor = float(str(padrao) if not texto and padrao is not None else texto.replace(",", "."))
            if not math.isfinite(valor) or (minimo is not None and valor < minimo) or (maximo is not None and valor > maximo):
                raise ValueError
            if inteiro and not valor.is_integer():
                raise ValueError
            return int(valor) if inteiro else valor
        except ValueError:
            print("Valor inválido. Verifique a faixa e o formato.")


def pedir_opcao(mensagem, opcoes, padrao=None):
    while True:
        texto = input(f"{mensagem} ({', '.join(opcoes)})" + (f" [{padrao}]" if padrao is not None else "") + ": ").strip().lower()
        texto = padrao if not texto and padrao is not None else texto
        if texto in opcoes:
            return texto
        print("Escolha uma das opções listadas.")


def pedir_horario(mensagem, padrao=None):
    while True:
        texto = input(f"{mensagem}" + (f" [{padrao}]" if padrao else "") + ": ").strip() or padrao
        try:
            horario_para_minutos(texto or "")
            return texto
        except ValueError as erro:
            print(erro)


def escolher_cenario():
    nome = pedir_opcao("Cenário", tuple(CENARIOS) + ("personalizado",), "calmo")
    if nome != "personalizado":
        return dict(CENARIOS[nome])
    return {campo: ((veloc_vent if campo == "vento" else poeira_atm)()[0],
                    pedir_numero(f"Oscilação de {campo}", 0)) for campo in ("vento", "poeira")}


def escolher_modo():
    return pedir_opcao("Modo", ("demonstração", "determinístico", "aleatório livre"), "demonstração")


def editar_dados_modulo(modulo, ids):
    while True:
        identificador = input(f"ID [{modulo['id']}]: ").strip() or modulo["id"]
        if 1 <= len(identificador) <= 10 and identificador not in ids:
            break
        print("ID deve ser único e ter de 1 a 10 caracteres.")
    tipo = pedir_opcao("Tipo", TIPOS, modulo["tipo"])
    while True:
        massa = pedir_numero("Massa final (t)", 0, padrao=modulo["massa"])
        if massa > 0:
            break
        print("Massa deve ser maior que zero.")
    prioridade = pedir_numero("Prioridade", 1, 5, modulo["prioridade"], inteiro=True)
    criticidade = pedir_opcao("Criticidade", CRITICIDADES, modulo["criticidade"])
    chegada = pedir_horario("Chegada", modulo["chegada"])
    leituras = []
    for campo in ("combustivel", "sensores"):
        leituras.extend(((combust_rest if campo == "combustivel" else integ_sens)(modulo[campo + "_media"])[0],
                         pedir_numero(f"Oscilação de {campo}", 0, padrao=modulo[campo + "_oscilacao"])))
    return criar_modulo(identificador, tipo, massa, prioridade, criticidade, chegada, *leituras)


def cadastrar_modulos():
    modulos = []
    for padrao in PADROES:
        modulo = criar_modulo(*padrao)
        print(f"Cadastro de {modulo['id']}: {modulo['tipo']}")
        if pedir_opcao("Editar campos?", ("sim", "não"), "não") == "sim":
            modulo = editar_dados_modulo(modulo, {m["id"] for m in modulos})
        while modulo["id"] in {m["id"] for m in modulos}:
            print("ID já cadastrado. Corrija o módulo.")
            modulo = editar_dados_modulo(modulo, {m["id"] for m in modulos})
        modulos.append(modulo)
    return modulos


"""## **Parte 4, Simulação das leituras, média e oscilação**

Material de apoio, seção 4.

Cada leitura é a média mais um sorteio uniforme entre menos a oscilação e mais a
oscilação, limitada à faixa física.

    leitura = média + sorteio entre (-oscilação) e (+oscilação), dentro de [mínimo, máximo]

No modo determinístico a oscilação vale 0 e não há sorteio. No modo demonstração a
semente é fixa (42), então os resultados se repetem a cada execução.

Funções previstas (nomes sugeridos).
- `ler_sensor(media, oscilacao, minimo, maximo)`, devolve uma leitura.
- `ler_ambiente(cenario)`, devolve o vento e a poeira da rodada.
- `ler_modulo(modulo)`, atualiza o combustível e a integridade dos sensores do módulo.
"""

# TODO (Parte 4), sorteio das leituras

def ler_sensor(media, oscilacao, minimo, maximo, modo="aleatório livre", gerador=None):
    if modo == "determinístico":
        leitura = media
    else:
        leitura = media + (gerador or random).uniform(-oscilacao, oscilacao)
    return max(minimo, min(maximo, leitura))


def ler_ambiente(cenario, modo="aleatório livre", gerador=None):
    return {campo: ler_sensor(*cenario[campo], 0, math.inf, modo, gerador)
            for campo in ("vento", "poeira")}


def ler_modulo(modulo, modo="aleatório livre", gerador=None):
    for campo in ("combustivel", "sensores"):
        modulo[campo] = ler_sensor(modulo[campo + "_media"], modulo[campo + "_oscilacao"],
                                   *FAIXA_PERCENTUAL, modo, gerador)
    return modulo


"""## **Parte 5, Classificação e regra de decisão (itens 2 e 3)**

Material de apoio, seções 2.3 a 2.7 e 3. Espelha o diagrama de portas lógicas da pasta
`fluxograma/`.

Passo 1, classificar cada variável em verde, amarelo ou vermelho, com os limiares da
Parte 1. A classificação sempre aparece escrita, nunca só como cor.

Passo 2, converter em booleanos.
- `combustivel_ok`, `vento_ok`, `poeira_ok`: a variável não está em vermelho.
- `area_livre`: a área de pouso está livre.
- `erro_sensores`: sensores em vermelho.

Passo 3, combinar com as portas lógicas.
- `AUTORIZAR = combustivel_ok AND vento_ok AND poeira_ok AND area_livre AND NOT erro_sensores`
- `ATENCAO = amarelo_combustivel OR amarelo_sensores OR amarelo_vento OR amarelo_poeira`

Passo 4, decidir com `if`, `elif` e `else`, na ordem de prioridade, e devolver
`(decisao, motivos)`, como na Fase 1.
- Sensores em vermelho: ALERTA, o módulo vai para a lista de alerta.
- Qualquer outro item em vermelho ou área ocupada: POUSO ADIADO, o módulo vai para a
  lista de espera.
- Algum item amarelo: POUSO AUTORIZADO COM ATENÇÃO.
- Tudo verde: POUSO AUTORIZADO.

Funções previstas (nomes sugeridos).
- `classificar_combustivel`, `classificar_sensores`, `classificar_vento`,
  `classificar_poeira`.
- `avaliar_booleanos(classificacoes, area_ocupada)`.
- `decidir_pouso(booleanos, classificacoes)`, devolve a decisão e a lista de motivos.
"""

# TODO (Parte 5), classificação, booleanos e decisão

# ============================================================
# FUNÇÃO: autorizar_pouso
# Avalia inicialmente a condição do combustível de um módulo.
# Registra problemas quando o combustível está Amarelo ou
# Vermelho.
#
# IMPORTANTE:
# Esta é uma versão inicial. A autorização definitiva do pouso
# deverá considerar também vento, poeira, sensores e área livre.
# ============================================================
    # Classifica o combustível sem alterar o valor no dicionário.
    # Registra avisos ou problemas relacionados ao combustível.
    # Apresenta o resultado da avaliação do combustível.
# Integração: avaliação completa; AMARELO autoriza com atenção.
def autorizar_pouso(modulo, ambiente, area_ocupada=False):
    classificacoes = {
        "combustivel": classificar_combustivel(modulo["combustivel"]),
        "sensores": classificar_sensores(modulo["sensores"]),
        "vento": classificar_vento(ambiente["vento"]),
        "poeira": classificar_poeira(ambiente["poeira"]),
    }
    decisao, motivos = decidir_pouso(avaliar_booleanos(classificacoes, area_ocupada), classificacoes)
    return decisao, motivos, classificacoes


def classificar_minimo(valor, campo):
    vermelho, verde = LIMIARES[campo]
    return "VERDE" if valor >= verde else "AMARELO" if valor >= vermelho else "VERMELHO"


def classificar_maximo(valor, campo):
    verde, amarelo = LIMIARES[campo]
    return "VERDE" if valor <= verde else "AMARELO" if valor <= amarelo else "VERMELHO"


def classificar_combustivel(valor):
    return classificar_minimo(valor, "combustivel")


def classificar_sensores(valor):
    return classificar_minimo(valor, "sensores")


def classificar_vento(valor):
    return classificar_maximo(valor, "vento")


def classificar_poeira(valor):
    return classificar_maximo(valor, "poeira")


def avaliar_booleanos(classificacoes, area_ocupada):
    booleanos = {campo + "_ok": classificacoes[campo] != "VERMELHO"
                 for campo in ("combustivel", "vento", "poeira")}
    booleanos["area_livre"] = not area_ocupada
    booleanos["erro_sensores"] = classificacoes["sensores"] == "VERMELHO"
    booleanos["AUTORIZAR"] = (booleanos["combustivel_ok"] and booleanos["vento_ok"]
                              and booleanos["poeira_ok"] and booleanos["area_livre"]
                              and not booleanos["erro_sensores"])
    booleanos["ATENCAO"] = any(cor == "AMARELO" for cor in classificacoes.values())
    return booleanos


def decidir_pouso(booleanos, classificacoes):
    if booleanos["erro_sensores"]:
        return "ALERTA", ["Sensores em VERMELHO"]
    elif not booleanos["AUTORIZAR"]:
        motivos = [f"{campo}: VERMELHO" for campo in ("combustivel", "vento", "poeira")
                   if classificacoes[campo] == "VERMELHO"]
        if not booleanos["area_livre"]:
            motivos.append("Área de pouso ocupada")
        return "POUSO ADIADO", motivos
    elif booleanos["ATENCAO"]:
        return "POUSO AUTORIZADO COM ATENÇÃO", [f"{campo}: AMARELO" for campo, cor in classificacoes.items() if cor == "AMARELO"]
    else:
        return "POUSO AUTORIZADO", ["Todas as condições em VERDE"]


"""## **Parte 6, Ordenação e busca (item 3)**

Material de apoio, seção 5.

Ordenação da fila antes de cada rodada, por critério composto: prioridade (1 é a mais
urgente) e, em caso de empate, horário de chegada mais cedo. Algoritmo principal,
ordenação por inserção. A ordenação por seleção entra só como comparação no relatório.

Buscas previstas.
- Busca sequencial: módulo com menor combustível, módulo de maior prioridade e todos os
  módulos de um determinado tipo de carga.
- Busca binária: módulo por id, sobre o cadastro ordenado por id.

Funções previstas (nomes sugeridos).
- `chave_de_ordenacao(modulo)`, devolve (prioridade, horário em minutos).
- `ordenar_por_insercao(lista, chave)`, `ordenar_por_selecao(lista, chave)`.
- `buscar_menor_combustivel(lista)`, `buscar_maior_prioridade(lista)`.
- `buscar_por_tipo(lista, tipo)`.
- `busca_binaria_por_id(lista_ordenada, id_procurado)`.
"""

# TODO (Parte 6), ordenação e buscas

# ============================================================
# FUNÇÃO: mostrar_modulos
# Exibe os dados dos módulos em formato de tabela.
# Recebe uma lista de módulos como parâmetro.
# ============================================================

def mostrar_modulos(modulos):
    tabela = []

    for modulo in modulos:
        linha = [
            modulo.get("nome", modulo.get("tipo", modulo.get("id", ""))),
            modulo["prioridade"],
            modulo["combustivel"],
            modulo["massa"] * 1000 if "id" in modulo else modulo["massa"],
            modulo["criticidade"],
            modulo["chegada"]
        ]
        tabela.append(linha)

    cabecalho = [
        "Nome",
        "Prioridade",
        "Combustível (%)",
        "Massa (kg)",
        "Criticidade",
        "Chegada"
    ]

    # A tabela da equipe usa apenas a biblioteca padrão nesta integração.
    tabela = [[str(valor) for valor in linha] for linha in tabela]
    larguras = [max([len(titulo)] + [len(linha[i]) for linha in tabela])
                for i, titulo in enumerate(cabecalho)]
    separador = "+" + "+".join("-" * (largura + 2) for largura in larguras) + "+"
    print(separador)
    for linha in [cabecalho] + tabela:
        print("| " + " | ".join(valor.ljust(larguras[i]) for i, valor in enumerate(linha)) + " |")
        print(separador)

# ============================================================
# FUNÇÃO: ordenar_modulos
# Ordena os módulos pela prioridade crescente.
# Em caso de empate, utiliza o horário de chegada.
# ============================================================

def ordenar_modulos(modulos):
    ordenados = ordenar_por_insercao(list(modulos), chave_de_ordenacao)

    mostrar_modulos(ordenados)
    return ordenados


# ============================================================
# FUNÇÃO: verificar_critic
# Analisa especificamente os módulos de criticidade Vital.
# Classifica sua condição com base no combustível cadastrado.
# ============================================================

def verificar_critic(modulos):
    for modulo in modulos:
        if modulo["criticidade"].lower() == "vital":
            combustivel = modulo["combustivel"]

            if classificar_combustivel(combustivel) == "VERDE":
                situacao = "Combustível adequado"
            elif classificar_combustivel(combustivel) == "AMARELO":
                situacao = "Baixo combustível"
            else:
                situacao = "Combustível crítico"

            print(modulo.get("nome", modulo.get("id", "")), "-", situacao)

# ============================================================
# FUNÇÃO: analisar_modulos
# Ordena os módulos, exibe a tabela e apresenta uma análise
# individual da situação do combustível de cada módulo.
# ============================================================

def analisar_modulos(modulos):
    ordenados = ordenar_por_insercao(list(modulos), chave_de_ordenacao)

    mostrar_modulos(ordenados)

    print("\n--- Análise dos módulos ---")

    for modulo in ordenados:
        combustivel = modulo["combustivel"]

        if classificar_combustivel(combustivel) == "VERDE":
            situacao = "Combustível adequado"
        elif classificar_combustivel(combustivel) == "AMARELO":
            situacao = "Baixo combustível"
        else:
            situacao = "Combustível crítico"

        print(
            modulo.get("nome", modulo.get("id", "")),
            "- Criticidade:", modulo["criticidade"],
            "-", situacao
        )

def chave_de_ordenacao(modulo):
    return modulo["prioridade"], horario_para_minutos(modulo["chegada"])


def ordenar_por_insercao(lista, chave):
    for i in range(1, len(lista)):
        atual = lista[i]
        j = i - 1
        while j >= 0 and chave(lista[j]) > chave(atual):
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = atual
    return lista


def ordenar_por_selecao(lista, chave):
    for i in range(len(lista)):
        menor = i
        for j in range(i + 1, len(lista)):
            if chave(lista[j]) < chave(lista[menor]):
                menor = j
        lista[i], lista[menor] = lista[menor], lista[i]
    return lista


def buscar_menor_combustivel(lista):
    encontrado = None
    for modulo in lista:
        if encontrado is None or modulo["combustivel"] < encontrado["combustivel"]:
            encontrado = modulo
    return encontrado


def buscar_maior_prioridade(lista):
    encontrado = None
    for modulo in lista:
        if encontrado is None or chave_de_ordenacao(modulo) < chave_de_ordenacao(encontrado):
            encontrado = modulo
    return encontrado


def buscar_por_tipo(lista, tipo):
    return [modulo for modulo in lista if modulo["tipo"] == tipo]


def busca_binaria_por_id(lista_ordenada, id_procurado):
    inicio, fim = 0, len(lista_ordenada) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        modulo = lista_ordenada[meio]
        if modulo["id"] == id_procurado:
            return modulo
        if modulo["id"] < id_procurado:
            inicio = meio + 1
        else:
            fim = meio - 1
    return None


"""## **Parte 7, Modelos matemáticos (item 4)**

Material de apoio, seção 6. Gráficos na pasta `graficos/`.

Três modelos, cada um como uma função pequena e pura.
- Altura em função do tempo de descida (função quadrática): dá o tempo até o vértice e
  a altura de acionamento dos retrofoguetes.
- Combustível necessário em função da variação de velocidade (função exponencial):
  usa o tempo da função anterior e justifica o limiar de combustível.
- Potência solar em função da hora do dia (função quadrática): apoia a análise da
  janela de energia no relatório.

Funções previstas (nomes sugeridos).
- `altura_em_funcao_do_tempo(h0, v0, a, t)`.
- `tempo_ate_o_vertice(v0, a)`, `altura_de_acionamento(v0, a)`.
- `combustivel_necessario(massa_final, delta_v, velocidade_exaustao)`.
- `potencia_solar(hora, p_max, duracao_dia)`.
"""

# TODO (Parte 7), funções matemáticas

def altura_em_funcao_do_tempo(h0, v0, a, t):
    return h0 + v0 * t + a * t ** 2 / 2


def tempo_ate_o_vertice(v0, a):
    if a <= 0 or v0 > 0:
        raise ValueError("Use frenagem positiva e velocidade inicial de descida.")
    return -v0 / a


def altura_de_acionamento(v0, a):
    if a <= 0:
        raise ValueError("A aceleração deve ser positiva.")
    return v0 ** 2 / (2 * a)


def combustivel_necessario(massa_final, delta_v, velocidade_exaustao):
    if massa_final <= 0 or delta_v < 0 or velocidade_exaustao <= 0:
        raise ValueError("Parâmetros de combustível inválidos.")
    return massa_final * math.expm1(delta_v / velocidade_exaustao)


def potencia_de_pico(poeira, area=AREA_PAINEIS, eficiencia=EFICIENCIA_SOLAR):
    if poeira < 0 or area <= 0 or not 0 <= eficiencia <= 1:
        raise ValueError("Parâmetros solares inválidos.")
    return IRRADIANCIA_SOLAR * area * eficiencia * math.exp(-poeira)


def potencia_solar(hora, p_max, duracao_dia=DURACAO_DIA_CLARO):
    # Hora é medida a partir do nascer do Sol; potência em W.
    if duracao_dia <= 0 or p_max < 0:
        raise ValueError("Duração ou potência inválida.")
    if hora < 0 or hora > duracao_dia:
        return 0.0
    return max(0.0, p_max * (1 - ((hora - duracao_dia / 2) / (duracao_dia / 2)) ** 2))


def energia_diaria(p_max, duracao_dia=DURACAO_DIA_CLARO):
    if p_max < 0 or duracao_dia <= 0:
        raise ValueError("Duração ou potência inválida.")
    return (2 / 3) * p_max * duracao_dia / 1000  # kWh


def resumo_modelos(modulos, poeira):
    tempo = tempo_ate_o_vertice(VELOCIDADE_INICIAL, ACELERACAO)
    delta_v = abs(VELOCIDADE_INICIAL) + GRAVIDADE_MARTE * tempo
    pico = potencia_de_pico(poeira)
    return {"tempo": tempo, "altura_acionamento": altura_de_acionamento(VELOCIDADE_INICIAL, ACELERACAO),
            "delta_v": delta_v, "potencia_pico_kw": pico / 1000,
            "energia_kwh": energia_diaria(pico),
            "combustivel_kg": {m["id"]: combustivel_necessario(m["massa"] * 1000, delta_v,
                                IMPULSO_ESPECIFICO * GRAVIDADE_TERRA) for m in modulos}}


"""## **Parte 8, Rodada de simulação e menu principal**

Material de apoio, seções 3, 4 e 5.

Uma rodada executa, nesta ordem.
1. Lê o ambiente e as leituras dos módulos (Parte 4).
2. Devolve os módulos em espera para a fila.
3. Ordena a fila (Parte 6).
4. Avalia os módulos da fila (Parte 5). Se o do topo é bloqueado, avalia o próximo.
   No máximo um módulo pousa por rodada.
5. Move cada módulo para a lista de destino e empilha o evento (Parte 2).
6. Mostra o resultado da rodada na tela, com a classificação escrita.

Menu em laço, com as opções previstas.
1. Executar a próxima rodada.
2. Mostrar a fila, as listas e o último evento da pilha.
3. Buscar módulo (menor combustível, maior prioridade, por tipo ou por id).
4. Reordenar a fila e comparar os critérios.
5. Editar um módulo ou trocar o cenário de ambiente.
6. Desfazer o último evento ou liberar um módulo da lista de alerta.
7. Sair.

Funções previstas (nomes sugeridos).
- `executar_rodada(estado)`, `mostrar_rodada(resultado)`.
- `mostrar_estado(estado)`, `menu_principal()`.
"""

# TODO (Parte 8), rodada de simulação e menu

def executar_rodada(estado, area_disponivel=True):
    estado["rodada"] += 1
    # Uma rodada representa a conclusão da descida anterior.
    estado["area_ocupada"] = not area_disponivel
    ambiente = ler_ambiente(estado["cenario"], estado["modo"], estado["gerador"])
    for modulo in estado["fila_pouso"] + estado["espera"]:
        ler_modulo(modulo, estado["modo"], estado["gerador"])
    for modulo in list(estado["espera"]):
        mover_modulo("espera", "fila_pouso", modulo, estado, "RETORNO À FILA", ["Nova avaliação"])
    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
    resultados = []
    for modulo in list(estado["fila_pouso"]):
        decisao, motivos, classificacoes = autorizar_pouso(modulo, ambiente, estado["area_ocupada"])
        destino = "alerta" if decisao == "ALERTA" else "espera" if decisao == "POUSO ADIADO" else "pousados"
        evento = mover_modulo("fila_pouso", destino, modulo, estado, decisao, motivos)
        resultados.append({**evento, "classificacoes": classificacoes,
                           "combustivel": modulo["combustivel"], "sensores": modulo["sensores"]})
    return {"rodada": estado["rodada"], "ambiente": ambiente, "resultados": resultados,
            "modelos": resumo_modelos(estado["cadastro"], ambiente["poeira"])}


def mostrar_rodada(resultado):
    print(f"\nRodada {resultado['rodada']} | vento: {resultado['ambiente']['vento']:.2f} m/s | poeira: {resultado['ambiente']['poeira']:.2f} τ")
    for item in resultado["resultados"]:
        print(f"{item['modulo']}: {item['decisao']} | combustível {item['combustivel']:.2f}% | sensores {item['sensores']:.2f}%")
        print("  " + " | ".join(f"{campo}: {cor}" for campo, cor in item["classificacoes"].items()))
        print("  Motivos: " + "; ".join(item["motivos"]))
    if not resultado["resultados"]:
        print("Nenhum módulo aguardando avaliação.")
    modelos = resultado["modelos"]
    print(f"Frenagem: {modelos['tempo']:.2f} s | acionamento: {modelos['altura_acionamento']:.2f} m")
    print(f"Energia: pico {modelos['potencia_pico_kw']:.2f} kW | {modelos['energia_kwh']:.2f} kWh/sol")
    print("Combustível necessário (kg): " + ", ".join(f"{id}: {kg:.2f}" for id, kg in modelos["combustivel_kg"].items()))


def mostrar_estado(estado):
    for nome in ("fila_pouso", "pousados", "espera", "alerta"):
        print(f"{nome}:")
        mostrar_modulos(estado[nome])
    print("Área ocupada:", "sim" if estado["area_ocupada"] else "não")
    print("Último evento:", ver_topo_pilha(estado["historico_eventos"]))


def selecionar_modulo(estado):
    identificador = input("ID do módulo: ").strip()
    cadastro = ordenar_por_insercao(list(estado["cadastro"]), lambda m: m["id"])
    modulo = busca_binaria_por_id(cadastro, identificador)
    if modulo is None:
        print("Módulo não encontrado.")
    return modulo


def liberar_alerta(estado, modulo):
    if modulo not in estado["alerta"]:
        return False
    mover_modulo("alerta", "fila_pouso", modulo, estado, "ALERTA LIBERADO", ["Confirmação do operador; sensores serão reavaliados"])
    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
    return True


def menu_principal():
    print("MGPEB — Aurora Siger")
    cenario = escolher_cenario()
    modo = escolher_modo()
    estado = criar_estado(cadastrar_modulos(), cenario, modo)
    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
    while True:
        print("\n1. Próxima rodada\n2. Estado e histórico\n3. Buscar módulo\n4. Comparar ordenações\n5. Editar módulo/cenário\n6. Desfazer/liberar alerta\n7. Sair")
        opcao = pedir_opcao("Opção", tuple(str(i) for i in range(1, 8)))
        if opcao == "1":
            disponibilidade, _ = area_pouso()
            mostrar_rodada(executar_rodada(estado, disponibilidade == 1))
        elif opcao == "2":
            mostrar_estado(estado)
        elif opcao == "3":
            criterio = pedir_opcao("Busca", ("combustível", "prioridade", "tipo", "id"), "id")
            if criterio == "combustível":
                print(buscar_menor_combustivel(estado["cadastro"]))
            elif criterio == "prioridade":
                print(buscar_maior_prioridade(estado["cadastro"]))
            elif criterio == "tipo":
                print(buscar_por_tipo(estado["cadastro"], pedir_opcao("Tipo", TIPOS)))
            else:
                print(selecionar_modulo(estado))
        elif opcao == "4":
            insercao = ordenar_por_insercao(list(estado["fila_pouso"]), chave_de_ordenacao)
            selecao = ordenar_por_selecao(list(estado["fila_pouso"]), chave_de_ordenacao)
            print("Inserção:", [m["id"] for m in insercao])
            print("Seleção:", [m["id"] for m in selecao])
            estado["fila_pouso"][:] = ordenar_modulos(estado["fila_pouso"])
            analisar_modulos(estado["fila_pouso"])
            verificar_critic(estado["fila_pouso"])
        elif opcao == "5":
            if pedir_opcao("Editar", ("módulo", "cenário"), "módulo") == "cenário":
                estado["cenario"] = escolher_cenario()
            else:
                modulo = selecionar_modulo(estado)
                if modulo is not None:
                    novos = editar_dados_modulo(modulo, {m["id"] for m in estado["cadastro"] if m is not modulo})
                    # IDs registrados no histórico precisam acompanhar uma renomeação.
                    for evento in estado["historico_eventos"]:
                        if evento["modulo"] == modulo["id"]:
                            evento["modulo"] = novos["id"]
                    modulo.update(novos)
                    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
        elif opcao == "6":
            acao = pedir_opcao("Ação", ("desfazer", "liberar"), "desfazer")
            if acao == "desfazer":
                print(desfazer_ultimo_evento(estado) or "Histórico vazio.")
            else:
                modulo = selecionar_modulo(estado)
                if modulo is not None:
                    if modulo not in estado["alerta"]:
                        print("Módulo não está em alerta.")
                    elif pedir_opcao("Confirmar liberação?", ("sim", "não"), "não") == "sim":
                        liberar_alerta(estado, modulo)
        else:
            print("Simulação encerrada.")
            return estado


"""## **Parte 9, Exemplos de execução**

Material de apoio, seções 2.8 e 5. Os prints desta parte vão para a pasta `testes/` e
para as figuras do relatório.

Exemplos simples, no modo determinístico ou com semente fixa, para o resultado ser
sempre o mesmo.
1. Cenário calmo: todos os módulos autorizados, na ordem da fila.
2. Cenário moderado: módulo adiado por combustível e autorizado em outra rodada.
3. Cenário tempestade: pouso adiado por vento e poeira.
4. Módulo com sensores em vermelho, enviado para a lista de alerta.
5. Busca e ordenação mostradas na tela.
"""

# TODO (Parte 9), exemplos de execução

def exemplos_de_execucao():
    resultados = {}
    estado = criar_estado(modo="determinístico")
    resultados["calmo"] = [executar_rodada(estado) for _ in PADROES]
    estado = criar_estado(cenario="moderado", modo="determinístico")
    energia = next(m for m in estado["cadastro"] if m["id"] == "ENE-01")
    energia["combustivel_media"] = 20
    primeira = executar_rodada(estado)
    energia["combustivel_media"] = 40  # Correção manual da média de medição.
    resultados["moderado"] = [primeira, executar_rodada(estado)]
    resultados["tempestade"] = [executar_rodada(criar_estado(cenario="tempestade", modo="determinístico"))]
    estado = criar_estado(modo="determinístico")
    estado["cadastro"][0]["sensores_media"] = 60
    resultados["sensores"] = [executar_rodada(estado)]
    for nome, rodadas in resultados.items():
        print(f"\nExemplo: {nome}")
        for resultado in rodadas:
            mostrar_rodada(resultado)
    cadastro = ordenar_por_insercao(list(estado["cadastro"]), chave_de_ordenacao)
    print("Ordenação:", [m["id"] for m in cadastro])
    print("Menor combustível:", buscar_menor_combustivel(cadastro)["id"])
    por_id = ordenar_por_insercao(list(cadastro), lambda m: m["id"])
    print("Busca binária:", busca_binaria_por_id(por_id, "ENE-01")["id"])
    return resultados


# TODO: chamar o menu principal quando o código estiver implementado

if __name__ == "__main__":
    try:
        menu_principal()
    except (EOFError, KeyboardInterrupt):
        print("\nSimulação encerrada pelo operador.")
