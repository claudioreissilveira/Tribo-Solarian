"""
# 🚀 **MGPEB | Módulo de Gerenciamento de Pouso e Estabilização de Base | SLR-33**

***Equipe Tribo Solarian.***

Protótipo da Fase 2 (missão Aurora Siger). O script está dividido em partes, e cada parte
tem uma apresentação (o que a seção faz e como funciona) acompanhada do código. As seções
citadas (seção 2, seção 6 e assim por diante) são as do material de apoio,
`docs/MGPEB_material_apoio.docx`. Os itens citados (item 1 a item 4) são os do enunciado
do projeto. Os diagramas das portas lógicas e os fluxogramas ficam na pasta `fluxograma/` e a
modelagem das funções na pasta `modelagem/`. 

###### **Repositório do projeto:**\n",
    "<https://github.com/claudioreissilveira/Tribo-Solarian/tree/pouso>\n"

## Integrantes
- Cláudio Roberto Grillo Reis Silveira | RM575353
- Vitor Lima Montiel | RM575458
- Wallace Gabriel Américo Albuquerque | RM575435
- Victor Augusto dos Santos Souza | RM576021
- Thales Martins Olveira Barros | RM574664

## Como executar
    python script/TriboSolarian_MGPEB.py

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

Bibliotecas usadas.
- `random`, biblioteca padrão, para sortear a oscilação das leituras (Parte 4), com
  semente fixa no modo de demonstração, de uma maneira na qual os resultados se repitam.
- `math`, biblioteca padrão, para a exponencial dos modelos da Parte 7.
- `input` e `print`, nativos do Python, para entrada e saída.

Justificativa de projeto: em Marte a memória e o processamento
são limitados, então o código usa listas simples e algoritmos fáceis de compilar.
"""

import math
import random

# Semente do modo de demonstração, para os sorteios se repetirem a cada execução
SEMENTE_PADRAO = 42


"""## **Parte 1, Constantes, limiares e padrões (itens 1 e 2)**

Material de apoio, seções 2 e 6.

Reúne em um só lugar tudo o que pode ser ajustado sem mexer na lógica.
- Limiares de cada variável, com as faixas verde, amarela e vermelha (combustível,
  sensores, vento e poeira).
- Os 3 cenários de ambiente (calmo, moderado e tempestade), cada um com média e
  oscilação de vento e de poeira.
- Padrão de cada módulo, com atributos fixos e médias e oscilações das leituras.
- Faixa física permitida para as porcentagens, de 0 a 100.
- Constantes dos modelos matemáticos: gravidade de Marte, impulso específico,
  irradiância solar e demais valores.
"""

# Combustível e sensores: (abaixo disso é vermelho, a partir disso é verde)
# Vento e poeira: (até isso é verde, acima disso é vermelho)
LIMIARES = {"combustivel": (30, 40), "sensores": (75, 90),
            "vento": (8, 15), "poeira": (1, 3)}

# Faixa física das leituras em porcentagem
FAIXA_PERCENTUAL = (0, 100)

# Cenários do ambiente: (média, oscilação) do vento em m/s e da poeira em τ
CENARIOS = {
    "calmo": {"vento": (5, 3), "poeira": (0.5, 0.3)},
    "moderado": {"vento": (11, 4), "poeira": (2, 0.8)},
    "tempestade": {"vento": (22, 6), "poeira": (4.5, 1)},
}

TIPOS = ("habitação", "energia", "laboratório", "logística", "suporte médico")
CRITICIDADES = ("baixa", "média", "alta", "vital")

# Padrão de cada módulo: id, tipo, massa final (t), prioridade, criticidade, chegada,
# média e oscilação do combustível (%), média e oscilação dos sensores (%)
PADROES = [
    ("HAB-01", TIPOS[0], 9.5, 2, "alta", "06:10", 70, 10, 95, 3),
    ("ENE-01", TIPOS[1], 7, 1, "vital", "06:25", 40, 12, 96, 3),
    ("LAB-01", TIPOS[2], 6, 3, "média", "06:40", 65, 10, 92, 4),
    ("LOG-01", TIPOS[3], 11, 3, "baixa", "06:05", 80, 8, 94, 4),
    ("MED-01", TIPOS[4], 4.5, 1, "vital", "07:00", 55, 10, 97, 2),
]

# Constantes dos modelos matemáticos
GRAVIDADE_MARTE = 3.73        # m/s²
GRAVIDADE_TERRA = 9.80665     # m/s², converte o impulso específico em velocidade
IMPULSO_ESPECIFICO = 312      # s, motor dos retrofoguetes
ALTURA_INICIAL = 1800         # m, altura em que os retrofoguetes acendem
VELOCIDADE_INICIAL = -100     # m/s, negativa porque o módulo desce
ACELERACAO = VELOCIDADE_INICIAL ** 2 / (2 * ALTURA_INICIAL)  # m/s², frenagem constante
IRRADIANCIA_SOLAR = 586.2     # W/m², luz do Sol que chega a Marte
AREA_PAINEIS = 100            # m²
EFICIENCIA_SOLAR = 0.295
DURACAO_DIA_CLARO = 12.33     # h
FRACAO_TANQUE = 0.4           # tanque cheio = 40% da massa do módulo


"""## **Parte 2, Módulos e estruturas lineares: fila, listas e pilha (item 1)**

Material de apoio, seções 2.1 e 5. Fortalece a estruturas de dados do relatório
e o diagrama `fluxograma/MGPEB_estruturas`.

Cada módulo é um dicionário com dois grupos de atributos.
- Fixos: id, tipo, massa, prioridade, criticidade da carga e horário de chegada à
  órbita.
- Dinâmicos: média e oscilação do combustível e da integridade dos sensores, mais a
  última leitura sorteada.

Estruturas usadas, todas guardadas em `estado`.
- `fila_pouso`, fila (FIFO), módulos aguardando autorização, em ordem de prioridade.
- `pousados`, lista, módulos que já pousaram.
- `espera`, lista, módulos adiados por condição temporária.
- `alerta`, lista, módulos com sensores em vermelho.
- `historico_eventos`, pilha (LIFO), cada movimento é empilhado e o último evento é o
  primeiro a ser consultado ou desfeito.

Funções desta parte.
- `horario_para_minutos` e `criar_modulo`, montam e validam os módulos.
- `enfileirar` e `ver_topo`, operações da fila.
- `empilhar`, `desempilhar` e `ver_topo_pilha`, operações da pilha.
- `criar_estado`, cria a fila, as listas e a pilha.
- `mover_modulo`, troca o módulo de estrutura e empilha o evento.
- `desfazer_ultimo_evento`, desempilha o último evento e devolve o módulo à fila.
"""

# Converte "HH:MM" em minutos, para comparar os horários de chegada
def horario_para_minutos(texto):
    if len(texto) != 5 or texto[2] != ":" or not (texto[:2] + texto[3:]).isdigit():
        raise ValueError("Use o formato HH:MM.")
    hora = int(texto[:2])
    minuto = int(texto[3:])
    if hora > 23 or minuto > 59:
        raise ValueError("Horário fora da faixa.")
    return hora * 60 + minuto


# Monta o dicionário de um módulo, conferindo cada um dos campos
def criar_modulo(identificador, tipo, massa, prioridade, criticidade, chegada,
                 combustivel_media, combustivel_oscilacao, sensores_media, sensores_oscilacao):
    horario_para_minutos(chegada)
    if not identificador.strip() or len(identificador) > 10:
        raise ValueError("O ID deve ter de 1 a 10 caracteres.")
    if tipo not in TIPOS or criticidade not in CRITICIDADES:
        raise ValueError("Tipo ou criticidade inválidos.")
    for valor in (massa, prioridade, combustivel_media, combustivel_oscilacao,
                  sensores_media, sensores_oscilacao):
        if not math.isfinite(valor):
            raise ValueError("Os números devem ser finitos.")
    if massa <= 0 or not 1 <= prioridade <= 5 or int(prioridade) != prioridade:
        raise ValueError("Massa ou prioridade inválida.")
    if not (0 <= combustivel_media <= 100 and 0 <= sensores_media <= 100):
        raise ValueError("Percentuais devem estar entre 0 e 100.")
    if combustivel_oscilacao < 0 or sensores_oscilacao < 0:
        raise ValueError("Oscilação não pode ser negativa.")
    return {"id": identificador, "tipo": tipo, "massa": massa, "prioridade": int(prioridade),
            "criticidade": criticidade, "chegada": chegada,
            "combustivel_media": combustivel_media, "combustivel_oscilacao": combustivel_oscilacao,
            "sensores_media": sensores_media, "sensores_oscilacao": sensores_oscilacao,
            "combustivel": combustivel_media, "sensores": sensores_media}


# Fila: entra no fim e o próximo a sair é sempre o primeiro
def enfileirar(fila, modulo):
    fila.append(modulo)


def ver_topo(fila):
    if fila:
        return fila[0]
    return None


# Pilha: entra e sai pelo topo
def empilhar(pilha, evento):
    pilha.append(evento)


def desempilhar(pilha):
    if pilha:
        return pilha.pop()
    return None


def ver_topo_pilha(pilha):
    if pilha:
        return pilha[-1]
    return None


# Cria a fila, as listas, a pilha e os dados da simulação
def criar_estado(modulos=None, cenario="calmo", modo="demonstração"):
    if modulos is None:
        modulos = [criar_modulo(*padrao) for padrao in PADROES]
    ids = [modulo["id"] for modulo in modulos]
    if len(set(ids)) != len(ids):
        raise ValueError("IDs repetidos.")
    if isinstance(cenario, str):
        cenario = CENARIOS[cenario]
    # Sem semente, os sorteios mudam a cada execução
    semente = SEMENTE_PADRAO if modo == "demonstração" else None
    return {"cadastro": modulos, "fila_pouso": list(modulos), "pousados": [],
            "espera": [], "alerta": [], "historico_eventos": [], "rodada": 0,
            "area_ocupada": False, "cenario": dict(cenario), "modo": modo,
            "gerador": random.Random(semente)}


# Tira o módulo da estrutura de origem, põe na de destino e empilha o evento
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


# Desfaz o último evento: o módulo volta para a fila e a área volta ao estado anterior
def desfazer_ultimo_evento(estado):
    evento = ver_topo_pilha(estado["historico_eventos"])
    if evento is None:
        return None
    for modulo in estado["cadastro"]:
        if modulo["id"] == evento["modulo"]:
            break
    for nome in ("fila_pouso", "pousados", "espera", "alerta"):
        if modulo in estado[nome]:
            estado[nome].remove(modulo)
            break
    # Toda reversão devolve o módulo à fila, como define o material de apoio
    posicao = min(evento["indice"], len(estado["fila_pouso"]))
    estado["fila_pouso"].insert(posicao, modulo)
    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
    estado["area_ocupada"] = evento["area_anterior"]
    return desempilhar(estado["historico_eventos"])


"""## **Parte 3, Entrada de dados manual**

Material de apoio, seções 2.1, 2.2, 2.8 e 4.1.

Como não temos sensores físicos em atuação, os dados entram por `input`, em 3 etapas.
1. Escolha do cenário de ambiente: calmo, moderado, tempestade ou personalizado.
2. Escolha do modo: demonstração (semente fixa), determinístico (sem oscilação) ou
   aleatório livre.
3. Cadastro dos módulos: aceitar os padrões com Enter ou editar um módulo, campo a
   campo, com o padrão entre colchetes.

Antes de cada rodada, o operador também informa se a área de pouso está livre.

Regras de validação.
- Cada pergunta se repete até o valor ser válido.
- Aceita vírgula ou ponto nos decimais.
- Porcentagem de 0 a 100, oscilação maior ou igual a 0, massa maior que 0, prioridade
  de 1 a 5, horário no formato HH:MM, tipo e criticidade dentro das opções, id com até
  10 caracteres e sem repetição.

Funções desta parte.
- `pedir_numero`, `pedir_opcao` e `pedir_horario`, perguntas com validação.
- `pedir_combustivel`, `pedir_sensores`, `pedir_vento` e `pedir_poeira`, pedem a média
  de cada leitura e mostram a classificação.
- `pedir_area_livre`, pergunta se a área de pouso está livre.
- `escolher_cenario`, `escolher_modo`, `editar_dados_modulo` e `cadastrar_modulos`.
"""

# Pede um número, aceita vírgula ou ponto e repete até o valor ser válido
def pedir_numero(mensagem, minimo=None, maximo=None, padrao=None, inteiro=False):
    if padrao is not None:
        mensagem += f" [{padrao}]"
    while True:
        texto = input(mensagem + ": ").strip().replace(",", ".")
        if not texto and padrao is not None:
            texto = str(padrao)
        try:
            valor = float(texto)
        except ValueError:
            print("Valor inválido. Digite um número.")
            continue
        if not math.isfinite(valor):
            print("Valor inválido. Digite um número finito.")
        elif minimo is not None and valor < minimo:
            print(f"O valor mínimo é {minimo}.")
        elif maximo is not None and valor > maximo:
            print(f"O valor máximo é {maximo}.")
        elif inteiro and not valor.is_integer():
            print("Digite um número inteiro.")
        elif inteiro:
            return int(valor)
        else:
            return valor


# Pede uma das opções listadas. Enter aceita o padrão
def pedir_opcao(mensagem, opcoes, padrao=None):
    mensagem += f" ({', '.join(opcoes)})"
    if padrao is not None:
        mensagem += f" [{padrao}]"
    while True:
        texto = input(mensagem + ": ").strip().lower()
        if not texto and padrao is not None:
            texto = padrao
        if texto in opcoes:
            return texto
        print("Escolha uma das opções listadas.")


# Pede um horário no formato HH:MM
def pedir_horario(mensagem, padrao=None):
    if padrao is not None:
        mensagem += f" [{padrao}]"
    while True:
        texto = input(mensagem + ": ").strip()
        if not texto and padrao is not None:
            texto = padrao
        try:
            horario_para_minutos(texto)
            return texto
        except ValueError as erro:
            print(erro)


# Pede a média do combustível e mostra a classificação
def pedir_combustivel(padrao=None):
    valor = pedir_numero("Média do combustível (%)", 0, 100, padrao)
    print("Classificação:", classificar_combustivel(valor))
    return valor


# Pede a média da integridade dos sensores e mostra a classificação
def pedir_sensores(padrao=None):
    valor = pedir_numero("Média da integridade dos sensores (%)", 0, 100, padrao)
    print("Classificação:", classificar_sensores(valor))
    return valor


# Pede a média do vento e mostra a classificação
def pedir_vento(padrao=None):
    valor = pedir_numero("Média do vento (m/s)", 0, None, padrao)
    print("Classificação:", classificar_vento(valor))
    return valor


# Pede a média da poeira e mostra a classificação
def pedir_poeira(padrao=None):
    valor = pedir_numero("Média da poeira (τ)", 0, None, padrao)
    print("Classificação:", classificar_poeira(valor))
    return valor


# Pergunta se a área de pouso está livre, não há padrão, o operador precisa confirmar
def pedir_area_livre():
    resposta = pedir_opcao("A área de pouso está livre?", ("sim", "não"))
    if resposta == "sim":
        print("Classificação da área: VERDE (livre)")
        return True
    print("Classificação da área: VERMELHO (ocupada)")
    return False


# Escolhe um cenário pronto ou monta um personalizado
def escolher_cenario():
    nome = pedir_opcao("Cenário", ("calmo", "moderado", "tempestade", "personalizado"), "calmo")
    if nome != "personalizado":
        return dict(CENARIOS[nome])
    vento = pedir_vento()
    oscilacao_vento = pedir_numero("Oscilação do vento", 0)
    poeira = pedir_poeira()
    oscilacao_poeira = pedir_numero("Oscilação da poeira", 0)
    return {"vento": (vento, oscilacao_vento), "poeira": (poeira, oscilacao_poeira)}


def escolher_modo():
    return pedir_opcao("Modo", ("demonstração", "determinístico", "aleatório livre"), "demonstração")


# Edita um módulo campo a campo. Enter mantém o valor atual
def editar_dados_modulo(modulo, ids_usados):
    while True:
        identificador = input(f"ID [{modulo['id']}]: ").strip().upper()
        if not identificador:
            identificador = modulo["id"]
        if len(identificador) <= 10 and identificador not in ids_usados:
            break
        print("O ID deve ser único e ter de 1 a 10 caracteres.")
    tipo = pedir_opcao("Tipo", TIPOS, modulo["tipo"])
    massa = pedir_numero("Massa final (t)", 0, padrao=modulo["massa"])
    while massa <= 0:
        print("A massa deve ser maior que zero.")
        massa = pedir_numero("Massa final (t)", 0, padrao=modulo["massa"])
    prioridade = pedir_numero("Prioridade (1 a 5)", 1, 5, modulo["prioridade"], inteiro=True)
    criticidade = pedir_opcao("Criticidade", CRITICIDADES, modulo["criticidade"])
    chegada = pedir_horario("Chegada (HH:MM)", modulo["chegada"])
    combustivel_media = pedir_combustivel(modulo["combustivel_media"])
    combustivel_oscilacao = pedir_numero("Oscilação do combustível", 0, padrao=modulo["combustivel_oscilacao"])
    sensores_media = pedir_sensores(modulo["sensores_media"])
    sensores_oscilacao = pedir_numero("Oscilação dos sensores", 0, padrao=modulo["sensores_oscilacao"])
    return criar_modulo(identificador, tipo, massa, prioridade, criticidade, chegada,
                        combustivel_media, combustivel_oscilacao, sensores_media, sensores_oscilacao)


# Cadastra os cinco módulos padrão, com a opção de editar cada um
def cadastrar_modulos():
    modulos = []
    for padrao in PADROES:
        modulo = criar_modulo(*padrao)
        ids_usados = [cadastrado["id"] for cadastrado in modulos]
        print(f"\nCadastro de {modulo['id']}: {modulo['tipo']}")
        if pedir_opcao("Editar campos?", ("sim", "não"), "não") == "sim":
            modulo = editar_dados_modulo(modulo, ids_usados)
        # Um ID editado antes pode coincidir com o padrão deste módulo
        while modulo["id"] in ids_usados:
            print("ID já cadastrado. Corrija o módulo.")
            modulo = editar_dados_modulo(modulo, ids_usados)
        modulos.append(modulo)
    return modulos


"""## **Parte 4, Simulação das leituras, média e oscilação**

Material de apoio, seção 4.

Cada leitura é a média mais um sorteio uniforme entre menos a oscilação e mais a
oscilação, limitada à faixa física.

    leitura = média + sorteio entre (-oscilação) e (+oscilação), dentro de [mínimo, máximo]

No modo determinístico a leitura é igual à média, sem sorteio. No modo demonstração a
semente é fixa (42), então os resultados se repetem a cada execução.

Funções desta parte.
- `ler_sensor`, devolve uma leitura.
- `ler_ambiente`, devolve o vento e a poeira da rodada, iguais para todos os módulos.
- `ler_modulo`, atualiza o combustível e a integridade dos sensores do módulo.
"""

# Sorteia uma leitura: média mais oscilação, limitada à faixa física
def ler_sensor(media, oscilacao, minimo, maximo, modo="aleatório livre", gerador=None):
    if gerador is None:
        gerador = random
    if modo == "determinístico":
        leitura = media
    else:
        leitura = media + gerador.uniform(-oscilacao, oscilacao)
    return max(minimo, min(maximo, leitura))


# Lê o vento e a poeira da rodada
def ler_ambiente(cenario, modo="aleatório livre", gerador=None):
    vento_media, vento_oscilacao = cenario["vento"]
    poeira_media, poeira_oscilacao = cenario["poeira"]
    vento = ler_sensor(vento_media, vento_oscilacao, 0, math.inf, modo, gerador)
    poeira = ler_sensor(poeira_media, poeira_oscilacao, 0, math.inf, modo, gerador)
    return {"vento": vento, "poeira": poeira}


# Atualiza a leitura de combustível e de sensores do módulo
def ler_modulo(modulo, modo="aleatório livre", gerador=None):
    minimo, maximo = FAIXA_PERCENTUAL
    modulo["combustivel"] = ler_sensor(modulo["combustivel_media"], modulo["combustivel_oscilacao"],
                                       minimo, maximo, modo, gerador)
    modulo["sensores"] = ler_sensor(modulo["sensores_media"], modulo["sensores_oscilacao"],
                                    minimo, maximo, modo, gerador)
    return modulo


"""## **Parte 5, Classificação e regra de decisão (itens 2 e 3)**

Material de apoio, seções 2.3 a 2.7 e 3. Espelha os diagramas `MGPEB_classificacao`,
`MGPEB_portas_logicas` e `MGPEB_tabela_verdade` da pasta `fluxograma/`.

Passo 1, classificar cada variável em verde, amarelo ou vermelho, com os limiares da
Parte 1. A classificação sempre aparece escrita, nunca só como cor.

Passo 2, converter em booleanos.
- `combustivel_ok`, `vento_ok`, `poeira_ok`: a variável não está em vermelho.
- `area_livre`: a área de pouso está livre.
- `erro_sensores`: sensores em vermelho.
- `amarelo_combustivel`, `amarelo_sensores`, `amarelo_vento`, `amarelo_poeira`: a
  variável está em amarelo.

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

Funções desta parte.
- `classificar_minimo` e `classificar_maximo`, as duas regras de faixa.
- `classificar_combustivel`, `classificar_sensores`, `classificar_vento` e
  `classificar_poeira`.
- `avaliar_booleanos`, aplica as portas lógicas.
- `decidir_pouso`, devolve a decisão e a lista de motivos.
- `autorizar_pouso`, junta os passos 1 a 4 para um módulo.
"""

# Leituras em que menor é pior (combustível e sensores)
def classificar_minimo(valor, campo):
    vermelho, verde = LIMIARES[campo]
    if valor >= verde:
        return "VERDE"
    elif valor >= vermelho:
        return "AMARELO"
    else:
        return "VERMELHO"


# Leituras em que maior é pior (vento e poeira)
def classificar_maximo(valor, campo):
    verde, vermelho = LIMIARES[campo]
    if valor <= verde:
        return "VERDE"
    elif valor <= vermelho:
        return "AMARELO"
    else:
        return "VERMELHO"


def classificar_combustivel(valor):
    return classificar_minimo(valor, "combustivel")


def classificar_sensores(valor):
    return classificar_minimo(valor, "sensores")


def classificar_vento(valor):
    return classificar_maximo(valor, "vento")


def classificar_poeira(valor):
    return classificar_maximo(valor, "poeira")


# Converte as classificações em booleanos e aplica as portas lógicas
def avaliar_booleanos(classificacoes, area_ocupada):
    booleanos = {}
    # Entradas de AUTORIZAR
    booleanos["combustivel_ok"] = classificacoes["combustivel"] != "VERMELHO"
    booleanos["vento_ok"] = classificacoes["vento"] != "VERMELHO"
    booleanos["poeira_ok"] = classificacoes["poeira"] != "VERMELHO"
    booleanos["area_livre"] = not area_ocupada
    booleanos["erro_sensores"] = classificacoes["sensores"] == "VERMELHO"
    # Entradas de ATENCAO
    booleanos["amarelo_combustivel"] = classificacoes["combustivel"] == "AMARELO"
    booleanos["amarelo_sensores"] = classificacoes["sensores"] == "AMARELO"
    booleanos["amarelo_vento"] = classificacoes["vento"] == "AMARELO"
    booleanos["amarelo_poeira"] = classificacoes["poeira"] == "AMARELO"
    # AUTORIZAR = combustivel_ok AND vento_ok AND poeira_ok AND area_livre AND NOT erro_sensores
    booleanos["AUTORIZAR"] = (booleanos["combustivel_ok"] and booleanos["vento_ok"]
                              and booleanos["poeira_ok"] and booleanos["area_livre"]
                              and not booleanos["erro_sensores"])
    # ATENCAO = amarelo_combustivel OR amarelo_sensores OR amarelo_vento OR amarelo_poeira
    booleanos["ATENCAO"] = (booleanos["amarelo_combustivel"] or booleanos["amarelo_sensores"]
                            or booleanos["amarelo_vento"] or booleanos["amarelo_poeira"])
    return booleanos


# Decide o pouso pela ordem de prioridade e devolve (decisao, motivos)
def decidir_pouso(booleanos, classificacoes):
    # Regra 1, sensores em vermelho
    if booleanos["erro_sensores"]:
        return "ALERTA", ["Sensores em VERMELHO"]
    # Regra 2, algum bloqueio
    elif not booleanos["AUTORIZAR"]:
        motivos = []
        for campo in ("combustivel", "vento", "poeira"):
            if classificacoes[campo] == "VERMELHO":
                motivos.append(f"{campo}: VERMELHO")
        if not booleanos["area_livre"]:
            motivos.append("Área de pouso ocupada")
        return "POUSO ADIADO", motivos
    # Regra 3, atenção
    elif booleanos["ATENCAO"]:
        motivos = []
        for campo in ("combustivel", "sensores", "vento", "poeira"):
            if classificacoes[campo] == "AMARELO":
                motivos.append(f"{campo}: AMARELO")
        return "POUSO AUTORIZADO COM ATENÇÃO", motivos
    # Regra 4, nominal
    else:
        return "POUSO AUTORIZADO", ["Todas as condições em VERDE"]


# Classifica as leituras de um módulo, aplica as portas e decide o pouso
def autorizar_pouso(modulo, ambiente, area_ocupada=False):
    classificacoes = {
        "combustivel": classificar_combustivel(modulo["combustivel"]),
        "sensores": classificar_sensores(modulo["sensores"]),
        "vento": classificar_vento(ambiente["vento"]),
        "poeira": classificar_poeira(ambiente["poeira"]),
    }
    booleanos = avaliar_booleanos(classificacoes, area_ocupada)
    decisao, motivos = decidir_pouso(booleanos, classificacoes)
    return decisao, motivos, classificacoes


"""## **Parte 6, Ordenação e busca (item 3)**

Material de apoio, seção 5.

Ordenação da fila antes de cada rodada, por critério composto: prioridade (1 é a mais
urgente) e, em caso de empate, horário de chegada mais cedo. Algoritmo principal,
ordenação por inserção. A ordenação por seleção entra só como comparação (opção 4 do
menu).

Buscas.
- Busca sequencial: módulo com menor combustível, módulo de maior prioridade e todos os
  módulos de um determinado tipo de carga.
- Busca binária: módulo por id, sobre uma cópia do cadastro ordenada por id.

Funções desta parte.
- `chave_de_ordenacao` e `chave_por_id`, critérios de ordenação.
- `ordenar_por_insercao` e `ordenar_por_selecao`.
- `buscar_menor_combustivel`, `buscar_maior_prioridade`, `buscar_por_tipo` e
  `busca_binaria_por_id`.
- `mostrar_modulos`, `situacao_combustivel` e `analisar_modulos`, mostram os resultados.
"""

# Critério da fila: prioridade e, no empate, horário de chegada
def chave_de_ordenacao(modulo):
    return modulo["prioridade"], horario_para_minutos(modulo["chegada"])


# Critério da busca binária: o próprio id
def chave_por_id(modulo):
    return modulo["id"]


# Ordenação por inserção: cada módulo é inserido na posição certa da parte já ordenada
def ordenar_por_insercao(lista, chave):
    for i in range(1, len(lista)):
        atual = lista[i]
        j = i - 1
        while j >= 0 and chave(lista[j]) > chave(atual):
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = atual
    return lista


# Ordenação por seleção: a cada volta, o menor restante vai para a frente
def ordenar_por_selecao(lista, chave):
    for i in range(len(lista)):
        menor = i
        for j in range(i + 1, len(lista)):
            if chave(lista[j]) < chave(lista[menor]):
                menor = j
        lista[i], lista[menor] = lista[menor], lista[i]
    return lista


# Busca sequencial do módulo com menos combustível
def buscar_menor_combustivel(lista):
    encontrado = None
    for modulo in lista:
        if encontrado is None or modulo["combustivel"] < encontrado["combustivel"]:
            encontrado = modulo
    return encontrado


# Busca sequencial do módulo de maior prioridade (menor número e chegada mais cedo)
def buscar_maior_prioridade(lista):
    encontrado = None
    for modulo in lista:
        if encontrado is None or chave_de_ordenacao(modulo) < chave_de_ordenacao(encontrado):
            encontrado = modulo
    return encontrado


# Busca sequencial de todos os módulos de um tipo de carga
def buscar_por_tipo(lista, tipo):
    encontrados = []
    for modulo in lista:
        if modulo["tipo"] == tipo:
            encontrados.append(modulo)
    return encontrados


# Busca binária por id; a lista precisa estar ordenada por id
def busca_binaria_por_id(lista_ordenada, id_procurado):
    inicio = 0
    fim = len(lista_ordenada) - 1
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


# Mostra os módulos em tabela, montada só com print
def mostrar_modulos(modulos):
    if not modulos:
        print("(vazia)")
        return
    linhas = [["ID", "Tipo", "Prioridade", "Combustível (%)", "Massa (kg)", "Criticidade", "Chegada"]]
    for modulo in modulos:
        linhas.append([modulo["id"], modulo["tipo"], str(modulo["prioridade"]),
                       f"{modulo['combustivel']:.2f}", f"{modulo['massa'] * 1000:.0f}",
                       modulo["criticidade"], modulo["chegada"]])
    # Cada coluna fica com a largura do maior texto dela
    larguras = []
    for coluna in range(len(linhas[0])):
        larguras.append(max(len(linha[coluna]) for linha in linhas))
    separador = "+" + "+".join("-" * (largura + 2) for largura in larguras) + "+"
    print(separador)
    for linha in linhas:
        celulas = []
        for coluna, valor in enumerate(linha):
            celulas.append(valor.ljust(larguras[coluna]))
        print("| " + " | ".join(celulas) + " |")
        print(separador)


# Situação do combustível escrita por extenso, a partir da classificação
def situacao_combustivel(modulo):
    classificacao = classificar_combustivel(modulo["combustivel"])
    if classificacao == "VERDE":
        return "combustível adequado"
    elif classificacao == "AMARELO":
        return "combustível baixo"
    else:
        return "combustível crítico"


# Mostra a tabela e a situação de cada módulo, destacando a carga vital
def analisar_modulos(modulos):
    mostrar_modulos(modulos)
    print("\nAnálise dos módulos")
    for modulo in modulos:
        texto = f"{modulo['id']} | criticidade {modulo['criticidade']} | {situacao_combustivel(modulo)}"
        if modulo["criticidade"] == "vital":
            texto += " | carga vital"
        print(texto)


"""## **Parte 7, Modelos matemáticos (item 4)**

Material de apoio, seção 6. A descrição completa, com fórmulas, gráficos e análise, está
em `modelagem/MGPEB_modelagem.ipynb`.

Três modelos, cada um como uma função pequena.
- Altura em função do tempo de descida (função quadrática): dá o tempo até o vértice e
  a altura de acionamento dos retrofoguetes.
- Combustível necessário em função da variação de velocidade (função exponencial):
  usa o tempo da função anterior e justifica o limiar de combustível.
- Potência solar em função da hora do dia (função quadrática, com o pico reduzido pela
  poeira): dá a energia gerada por dia.

Funções desta parte.
- `altura_em_funcao_do_tempo`, `tempo_ate_o_vertice` e `altura_de_acionamento`.
- `combustivel_necessario`.
- `potencia_de_pico`, `potencia_solar` e `energia_diaria`.
- `resumo_modelos`, calcula os valores mostrados ao fim de cada rodada.
"""

# h(t) = h0 + v0·t + a·t²/2
def altura_em_funcao_do_tempo(h0, v0, a, t):
    return h0 + v0 * t + a * t ** 2 / 2


# Vértice da parábola: o instante em que a velocidade chega a zero
def tempo_ate_o_vertice(v0, a):
    if a <= 0 or v0 > 0:
        raise ValueError("Use frenagem positiva e velocidade inicial de descida.")
    return -v0 / a


# Altura em que os retrofoguetes precisam acender para tocar o solo com velocidade zero
def altura_de_acionamento(v0, a):
    if a <= 0:
        raise ValueError("A aceleração deve ser positiva.")
    return v0 ** 2 / (2 * a)


# m_comb = m_f·(e^(Δv/ve) - 1), com a massa final em kg
def combustivel_necessario(massa_final, delta_v, velocidade_exaustao):
    if massa_final <= 0 or delta_v < 0 or velocidade_exaustao <= 0:
        raise ValueError("Parâmetros de combustível inválidos.")
    return massa_final * (math.exp(delta_v / velocidade_exaustao) - 1)


# P_max = G·A·η·e^(-τ), em W
def potencia_de_pico(poeira, area=AREA_PAINEIS, eficiencia=EFICIENCIA_SOLAR):
    if poeira < 0 or area <= 0 or not 0 <= eficiencia <= 1:
        raise ValueError("Parâmetros solares inválidos.")
    return IRRADIANCIA_SOLAR * area * eficiencia * math.exp(-poeira)


# Parábola da potência ao longo do dia; a hora conta a partir do nascer do Sol
def potencia_solar(hora, p_max, duracao_dia=DURACAO_DIA_CLARO):
    if duracao_dia <= 0 or p_max < 0:
        raise ValueError("Duração ou potência inválida.")
    if hora < 0 or hora > duracao_dia:
        return 0.0
    meio_dia = duracao_dia / 2
    return p_max * (1 - ((hora - meio_dia) / meio_dia) ** 2)


# Área sob a parábola: 2/3 do pico vezes a duração do dia, em kWh
def energia_diaria(p_max, duracao_dia=DURACAO_DIA_CLARO):
    if p_max < 0 or duracao_dia <= 0:
        raise ValueError("Duração ou potência inválida.")
    return (2 / 3) * p_max * duracao_dia / 1000


# Calcula os três modelos com os valores do projeto e a poeira da rodada
def resumo_modelos(modulos, poeira):
    tempo = tempo_ate_o_vertice(VELOCIDADE_INICIAL, ACELERACAO)
    # O Δv soma a perda por gravidade durante a frenagem
    delta_v = abs(VELOCIDADE_INICIAL) + GRAVIDADE_MARTE * tempo
    velocidade_exaustao = IMPULSO_ESPECIFICO * GRAVIDADE_TERRA
    combustivel_kg = {}
    for modulo in modulos:
        combustivel_kg[modulo["id"]] = combustivel_necessario(modulo["massa"] * 1000, delta_v,
                                                              velocidade_exaustao)
    # Parte do tanque gasta no pouso; é igual para todos os módulos
    uso_tanque = 100 * (math.exp(delta_v / velocidade_exaustao) - 1) / FRACAO_TANQUE
    pico = potencia_de_pico(poeira)
    return {"tempo": tempo,
            "altura_acionamento": altura_de_acionamento(VELOCIDADE_INICIAL, ACELERACAO),
            "delta_v": delta_v, "uso_tanque": uso_tanque, "combustivel_kg": combustivel_kg,
            "potencia_pico_kw": pico / 1000, "energia_kwh": energia_diaria(pico)}


"""## **Parte 8, Rodada de simulação e menu principal**

Material de apoio, seções 3, 4 e 5. Espelha o diagrama `fluxograma/MGPEB_fluxograma`.

Uma rodada executa, nesta ordem.
1. Lê o ambiente e as leituras dos módulos (Parte 4).
2. Devolve os módulos em espera para a fila.
3. Ordena a fila (Parte 6).
4. Avalia sempre o primeiro da fila (Parte 5) até a fila esvaziar. Depois do primeiro
   pouso a área fica ocupada, então no máximo um módulo pousa por rodada.
5. Move cada módulo para a lista de destino e empilha o evento (Parte 2).
6. Mostra o resultado da rodada na tela, com a classificação escrita.

Menu em laço, com as opções.
1. Executar a próxima rodada.
2. Mostrar a fila, as listas e o último evento da pilha.
3. Buscar módulo (menor combustível, maior prioridade, por tipo ou por id).
4. Comparar as ordenações por inserção e por seleção e analisar os módulos.
5. Editar um módulo ou trocar o cenário de ambiente.
6. Desfazer o último evento ou liberar um módulo da lista de alerta.
7. Rodar os exemplos de execução (Parte 9).
8. Sair.

Funções desta parte.
- `executar_rodada` e `mostrar_rodada`.
- `descrever_evento` e `mostrar_estado`.
- `selecionar_modulo` e `liberar_alerta`.
- `menu_principal`.
"""

# Executa uma rodada completa e devolve o resultado para ser mostrado
def executar_rodada(estado, area_livre=True):
    estado["rodada"] += 1
    # A rodada começa com a descida anterior concluída
    estado["area_ocupada"] = not area_livre
    ambiente = ler_ambiente(estado["cenario"], estado["modo"], estado["gerador"])
    for modulo in estado["fila_pouso"] + estado["espera"]:
        ler_modulo(modulo, estado["modo"], estado["gerador"])
    # Os módulos em espera voltam para a fila e são avaliados de novo
    for modulo in list(estado["espera"]):
        mover_modulo("espera", "fila_pouso", modulo, estado, "RETORNO À FILA", ["Nova avaliação"])
    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
    resultados = []
    # Avalia sempre o primeiro da fila; cada módulo avaliado sai dela
    while estado["fila_pouso"]:
        modulo = ver_topo(estado["fila_pouso"])
        decisao, motivos, classificacoes = autorizar_pouso(modulo, ambiente, estado["area_ocupada"])
        if decisao == "ALERTA":
            destino = "alerta"
        elif decisao == "POUSO ADIADO":
            destino = "espera"
        else:
            destino = "pousados"
        mover_modulo("fila_pouso", destino, modulo, estado, decisao, motivos)
        resultados.append({"modulo": modulo["id"], "decisao": decisao, "motivos": motivos,
                           "classificacoes": classificacoes,
                           "combustivel": modulo["combustivel"], "sensores": modulo["sensores"]})
    return {"rodada": estado["rodada"], "ambiente": ambiente, "resultados": resultados,
            "modelos": resumo_modelos(estado["cadastro"], ambiente["poeira"])}


# Mostra as decisões da rodada e os resultados dos modelos
def mostrar_rodada(resultado):
    ambiente = resultado["ambiente"]
    print(f"\nRodada {resultado['rodada']} | vento: {ambiente['vento']:.2f} m/s | poeira: {ambiente['poeira']:.2f} τ")
    if not resultado["resultados"]:
        print("Nenhum módulo aguardando avaliação.")
    for item in resultado["resultados"]:
        print(f"{item['modulo']}: {item['decisao']} | combustível {item['combustivel']:.2f}% | sensores {item['sensores']:.2f}%")
        cores = []
        for campo, cor in item["classificacoes"].items():
            cores.append(f"{campo}: {cor}")
        print("  " + " | ".join(cores))
        print("  Motivos: " + "; ".join(item["motivos"]))
    modelos = resultado["modelos"]
    print(f"Frenagem: {modelos['tempo']:.2f} s | acionamento: {modelos['altura_acionamento']:.2f} m")
    print(f"Combustível no pouso: {modelos['uso_tanque']:.1f}% do tanque")
    combustiveis = []
    for identificador, quilos in modelos["combustivel_kg"].items():
        combustiveis.append(f"{identificador}: {quilos:.2f}")
    print("Combustível necessário (kg): " + ", ".join(combustiveis))
    print(f"Energia: pico {modelos['potencia_pico_kw']:.2f} kW | {modelos['energia_kwh']:.2f} kWh/sol")


# Texto curto de um evento da pilha
def descrever_evento(evento):
    return (f"rodada {evento['rodada']}, {evento['modulo']} de {evento['origem']} "
            f"para {evento['destino']} ({evento['decisao']})")


# Mostra a fila, as listas e o topo da pilha de eventos
def mostrar_estado(estado):
    for nome in ("fila_pouso", "pousados", "espera", "alerta"):
        print(f"\n{nome}:")
        mostrar_modulos(estado[nome])
    print("\nÁrea ocupada:", "sim" if estado["area_ocupada"] else "não")
    evento = ver_topo_pilha(estado["historico_eventos"])
    if evento is None:
        print("Histórico vazio.")
    else:
        print("Último evento:", descrever_evento(evento))
        print("Eventos na pilha:", len(estado["historico_eventos"]))


# Pede um id e localiza o módulo com busca binária; aceita letras minúsculas
def selecionar_modulo(estado):
    identificador = input("ID do módulo: ").strip().upper()
    # A busca binária precisa da lista ordenada por id, então ordena uma cópia do cadastro
    cadastro_por_id = ordenar_por_insercao(list(estado["cadastro"]), chave_por_id)
    modulo = busca_binaria_por_id(cadastro_por_id, identificador)
    if modulo is None:
        print("Módulo não encontrado.")
    return modulo


# Devolve um módulo da lista de alerta para a fila, depois da confirmação do operador
def liberar_alerta(estado, modulo):
    if modulo not in estado["alerta"]:
        return False
    mover_modulo("alerta", "fila_pouso", modulo, estado, "ALERTA LIBERADO",
                 ["Confirmação do operador; sensores serão reavaliados"])
    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
    return True


# Menu em laço: configura a simulação e executa as opções até o operador sair
def menu_principal():
    print("MGPEB | Missão Aurora Siger")
    cenario = escolher_cenario()
    modo = escolher_modo()
    estado = criar_estado(cadastrar_modulos(), cenario, modo)
    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
    while True:
        print("\n1. Próxima rodada")
        print("2. Estado e histórico")
        print("3. Buscar módulo")
        print("4. Comparar ordenações")
        print("5. Editar módulo ou cenário")
        print("6. Desfazer ou liberar alerta")
        print("7. Exemplos de execução")
        print("8. Sair")
        opcao = pedir_opcao("Opção", ("1", "2", "3", "4", "5", "6", "7", "8"))
        if opcao == "1":
            area_livre = pedir_area_livre()
            mostrar_rodada(executar_rodada(estado, area_livre))
        elif opcao == "2":
            mostrar_estado(estado)
        elif opcao == "3":
            criterio = pedir_opcao("Busca", ("combustível", "prioridade", "tipo", "id"), "id")
            if criterio == "combustível":
                mostrar_modulos([buscar_menor_combustivel(estado["cadastro"])])
            elif criterio == "prioridade":
                mostrar_modulos([buscar_maior_prioridade(estado["cadastro"])])
            elif criterio == "tipo":
                mostrar_modulos(buscar_por_tipo(estado["cadastro"], pedir_opcao("Tipo", TIPOS)))
            else:
                modulo = selecionar_modulo(estado)
                if modulo is not None:
                    mostrar_modulos([modulo])
        elif opcao == "4":
            # Usa o cadastro inteiro, porque a fila esvazia ao fim de cada rodada
            insercao = ordenar_por_insercao(list(estado["cadastro"]), chave_de_ordenacao)
            selecao = ordenar_por_selecao(list(estado["cadastro"]), chave_de_ordenacao)
            print("Inserção:", [modulo["id"] for modulo in insercao])
            print("Seleção:", [modulo["id"] for modulo in selecao])
            analisar_modulos(insercao)
        elif opcao == "5":
            if pedir_opcao("Editar", ("módulo", "cenário"), "módulo") == "cenário":
                estado["cenario"] = escolher_cenario()
            else:
                modulo = selecionar_modulo(estado)
                if modulo is not None:
                    ids_usados = []
                    for outro in estado["cadastro"]:
                        if outro is not modulo:
                            ids_usados.append(outro["id"])
                    novos_dados = editar_dados_modulo(modulo, ids_usados)
                    # Se o id mudar, os eventos do histórico acompanham
                    for evento in estado["historico_eventos"]:
                        if evento["modulo"] == modulo["id"]:
                            evento["modulo"] = novos_dados["id"]
                    modulo.update(novos_dados)
                    ordenar_por_insercao(estado["fila_pouso"], chave_de_ordenacao)
        elif opcao == "6":
            acao = pedir_opcao("Ação", ("desfazer", "liberar"), "desfazer")
            if acao == "desfazer":
                evento = desfazer_ultimo_evento(estado)
                if evento is None:
                    print("Histórico vazio.")
                else:
                    print("Desfeito:", descrever_evento(evento))
            else:
                modulo = selecionar_modulo(estado)
                if modulo is not None:
                    if modulo not in estado["alerta"]:
                        print("Módulo não está em alerta.")
                    elif pedir_opcao("Confirmar liberação?", ("sim", "não"), "não") == "sim":
                        liberar_alerta(estado, modulo)
                        print(f"{modulo['id']} voltou para a fila_pouso.")
        elif opcao == "7":
            exemplos_de_execucao()
        else:
            print("Simulação encerrada.")
            return estado


"""## **Parte 9, Exemplos de execução**

Material de apoio, seções 2.8 e 5. Os prints desta parte vão para a pasta `testes/` e
para as figuras do relatório. Rodam pela opção 7 do menu.

Exemplos simples, no modo determinístico, para o resultado ser sempre o mesmo.
1. Cenário calmo: todos os módulos autorizados, um por rodada, na ordem da fila.
2. Cenário moderado: ENE-01 adiado por combustível e autorizado em outra rodada.
3. Cenário tempestade: pouso adiado por vento e poeira.
4. Módulo com sensores em vermelho (HAB-01), enviado para a lista de alerta.
5. Busca e ordenação mostradas na tela.
"""

# Roda os exemplos fixos e mostra cada rodada
def exemplos_de_execucao():
    resultados = {}

    # 1. Calmo: cinco rodadas, um pouso por rodada
    estado = criar_estado(modo="determinístico")
    resultados["calmo"] = []
    for _ in PADROES:
        resultados["calmo"].append(executar_rodada(estado))

    # 2. Moderado: ENE-01 com 20% de combustível é adiado; corrigido para 40%, pousa
    estado = criar_estado(cenario="moderado", modo="determinístico")
    for modulo in estado["cadastro"]:
        if modulo["id"] == "ENE-01":
            energia = modulo
    energia["combustivel_media"] = 20
    primeira = executar_rodada(estado)
    energia["combustivel_media"] = 40
    resultados["moderado"] = [primeira, executar_rodada(estado)]

    # 3. Tempestade: vento e poeira em vermelho adiam todos
    resultados["tempestade"] = [executar_rodada(criar_estado(cenario="tempestade", modo="determinístico"))]

    # 4. Sensores: HAB-01 com 60% de integridade vai para alerta
    estado = criar_estado(modo="determinístico")
    estado["cadastro"][0]["sensores_media"] = 60
    resultados["sensores"] = [executar_rodada(estado)]

    for nome, rodadas in resultados.items():
        print(f"\nExemplo: {nome}")
        for resultado in rodadas:
            mostrar_rodada(resultado)

    # 5. Busca e ordenação
    cadastro = ordenar_por_insercao(list(estado["cadastro"]), chave_de_ordenacao)
    print("\nOrdenação:", [modulo["id"] for modulo in cadastro])
    print("Menor combustível:", buscar_menor_combustivel(cadastro)["id"])
    cadastro_por_id = ordenar_por_insercao(list(cadastro), chave_por_id)
    print("Busca binária:", busca_binaria_por_id(cadastro_por_id, "ENE-01")["id"])
    return resultados


if __name__ == "__main__":
    try:
        menu_principal()
    except (EOFError, KeyboardInterrupt):
        print("\nSimulação encerrada pelo operador.")
