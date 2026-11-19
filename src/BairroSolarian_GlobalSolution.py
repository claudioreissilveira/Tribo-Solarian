"""
TRIBO SOLARIAN | FIAP ON - Ciência da Computação
Global Solution 2026.2 - CitizenTech
Neighborhood Action Dashboard - BAIRRO SOLARIAN

Integrantes:
    Cláudio Roberto Grillo Reis Silveira | RM575353
    Vitor Lima Montiel | RM575458
    Wallace Gabriel Américo Albuquerque | RM575435
    Victor Augusto dos Santos Souza | RM576021
    Thales Martins Oliveira Barros | RM574664

Simulação realista de um sistema de gestão comunitária. O projeto parte de
situações do cotidiano de um bairro e reproduz funcionalidades presentes em
serviços reais de atendimento ao cidadão: registro de ocorrências, triagem,
acompanhamento de cada etapa, apoio a registros existentes, indicadores e
agenda de eventos. O objetivo é compreender a rotina dos moradores e facilitar
a vida em comunidade por meio da organização das informações.

Como executar:  python src/BairroSolarian_GlobalSolution.py

Organização do arquivo:
    Parte 0  - Bibliotecas, configuração e cores do terminal
    Parte 1  - Categorias, situações, transições e limites
    Parte 2  - Base inicial do bairro e das ocorrências (dados fictícios)
    Parte 3  - Regras de validação dos registros
    Parte 4  - Banco de dados em JSON
    Parte 5  - Estruturas de dados (índice, fila, pilha, hierarquia, matriz)
    Parte 6  - Entrada de dados validada
    Parte 7  - Regras de cadastro, atualização de situação e agenda
    Parte 8  - Consultas, busca e ordenação
    Parte 9  - Indicadores
    Parte 10 - Exibição no terminal
    Parte 11 - Menus do morador e do gestor
    Parte 12 - Conferências e ponto de entrada
"""

# =============================================================================
# PARTE 0 - Bibliotecas, configuração e cores do terminal
# Apenas a biblioteca padrão: json (banco de dados), os e sys (arquivos),
# hashlib e getpass (senha do gestor).
# =============================================================================

import getpass
import hashlib
import json
import os
import sys

LARGURA = 84
NOME_BAIRRO = "Bairro Solarian"

PERFIL_MORADOR = "MORADOR"
PERFIL_GESTOR = "GESTOR"

# Apresentação do projeto, exibida no menu principal e na tela "Sobre".
RESUMO_PROJETO = "Simulação realista de um sistema de gestão comunitária de bairro"
APRESENTACAO = [
    "O Bairro Solarian é uma simulação realista de um sistema de gestão comunitária. "
    "O projeto parte de situações do cotidiano de um bairro, como a lâmpada apagada, "
    "a calçada sem acesso e o lixo acumulado, e reproduz funcionalidades presentes em "
    "serviços reais de atendimento ao cidadão: registro de ocorrências, triagem, "
    "acompanhamento de cada etapa, apoio a registros existentes, indicadores e agenda "
    "de eventos.",
    "O objetivo é compreender a rotina dos moradores e demonstrar como a organização "
    "das informações facilita a vida em comunidade, aproximando quem relata um "
    "problema de quem administra o bairro e tornando visível o andamento de cada "
    "solicitação.",
    "O bairro, os moradores e as ocorrências são fictícios, e o sistema não se "
    "comunica com órgãos públicos. O cenário foi construído com mapa, regras de "
    "convivência e rotina próprios, para que a simulação se aproxime do uso real.",
]

# Códigos de cor do terminal. A cor apenas reforça a informação escrita.
CORES = {
    "vermelho": "91", "verde": "92", "amarelo": "93", "azul": "94",
    "magenta": "95", "ciano": "96", "cinza": "90", "negrito": "1",
}

# Preferência de exibição, alterada pelo menu principal.
CONFIG = {"cores": True}


def pintar(texto, cor):
    if not CONFIG["cores"] or cor not in CORES:
        return texto
    return "\033[" + CORES[cor] + "m" + texto + "\033[0m"


# =============================================================================
# PARTE 1 - Categorias, situações, transições e limites
# Valores padronizados: o sistema armazena o identificador e exibe o nome.
# =============================================================================

CATEGORIAS = ["ILUMINACAO", "ACESSIBILIDADE", "LIMPEZA", "CONSERVACAO"]

NOMES_CATEGORIA = {
    "ILUMINACAO": "Iluminação",
    "ACESSIBILIDADE": "Acessibilidade",
    "LIMPEZA": "Limpeza",
    "CONSERVACAO": "Conservação",
}

SITUACOES = ["ABERTA", "EM_ANALISE", "EM_ATENDIMENTO", "CONCLUIDA", "RECUSADA"]

NOMES_SITUACAO = {
    "ABERTA": "Aberta",
    "EM_ANALISE": "Em análise",
    "EM_ATENDIMENTO": "Em atendimento",
    "CONCLUIDA": "Concluída",
    "RECUSADA": "Recusada",
}

SIGNIFICADO_SITUACAO = {
    "ABERTA": "registrada pelo morador e ainda não examinada pelo gestor",
    "EM_ANALISE": "examinada pelo gestor, que avalia se pode ser atendida",
    "EM_ATENDIMENTO": "aceita, com o serviço em andamento",
    "CONCLUIDA": "serviço finalizado",
    "RECUSADA": "encerrada sem atendimento, com o motivo registrado",
}

COR_SITUACAO = {
    "ABERTA": "amarelo",
    "EM_ANALISE": "ciano",
    "EM_ATENDIMENTO": "azul",
    "CONCLUIDA": "verde",
    "RECUSADA": "cinza",
}

# Cada situação aponta para as situações seguintes permitidas.
TRANSICOES = {
    "ABERTA": ["EM_ANALISE"],
    "EM_ANALISE": ["EM_ATENDIMENTO", "RECUSADA"],
    "EM_ATENDIMENTO": ["CONCLUIDA"],
    "CONCLUIDA": [],
    "RECUSADA": [],
}

# Uma ocorrência pendente há mais dias que este limite é considerada atrasada.
LIMITE_DIAS_ATRASO = 7

TAMANHO_MINIMO_DESCRICAO = 5
TAMANHO_MAXIMO_DESCRICAO = 200
TAMANHO_MINIMO_TITULO = 3
TAMANHO_MAXIMO_TITULO = 40

CAMPOS_OBRIGATORIOS = [
    "id", "categoria", "descricao", "setor", "local", "dia_abertura", "status",
]

# Senha do gestor: o código armazena apenas o resumo da senha.
RESUMO_SENHA_GESTOR = "5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5"
TENTATIVAS_SENHA = 3

# Agenda do bairro: tipos de evento que o gestor pode divulgar.
TIPOS_EVENTO = ["FESTA", "ENCONTRO", "REUNIAO", "MUTIRAO"]
NOMES_TIPO_EVENTO = {
    "FESTA": "Festa",
    "ENCONTRO": "Encontro",
    "REUNIAO": "Reunião do bairro",
    "MUTIRAO": "Mutirão",
}

# Regra do bairro: horário de silêncio das 22h às 8h.
HORA_FIM_SILENCIO = 8
HORA_INICIO_SILENCIO = 22


def nomes_de(codigos, nomes):
    lista = []
    for codigo in codigos:
        lista.append(nomes[codigo])
    return lista


# =============================================================================
# PARTE 2 - Base inicial do bairro e das ocorrências (dados fictícios)
# O bairro segue o mapa "Solarian - Bairro fictício": quarteirões (Q) e casas
# numeradas, cortados pela Avenida Sol Nascente, que separa os lados Oeste e Leste.
# =============================================================================

SETORES = ["OESTE", "LESTE"]

# Locais genéricos onde uma ocorrência pode ser registrada: ruas, espaços
# coletivos e pontos de referência (comércios e hospital, para a calçada em frente).
BAIRRO = {
    "OESTE": {
        "nome": "Lado Oeste",
        "locais": [
            "Avenida Sol Nascente",
            "Rua das Acácias",
            "Rua dos Ipês",
            "Rua dos Girassóis",
            "Rua das Laranjeiras",
            "Rua das Palmeiras",
            "Rua das Andorinhas",
            "Rua do Horizonte",
            "Escola Municipal Caminhos do Sol",
            "Mercado Solarian",
            "Padaria Pão de Sol",
        ],
    },
    "LESTE": {
        "nome": "Lado Leste",
        "locais": [
            "Avenida Sol Nascente",
            "Rua das Acácias",
            "Rua dos Ipês",
            "Rua dos Girassóis",
            "Rua das Laranjeiras",
            "Rua da Aurora",
            "Rua das Estrelas",
            "Praça dos Encontros",
            "Escola Municipal Novo Amanhecer",
            "Hospital Solarian",
            "Farmácia Aurora",
            "Papelaria das Estrelas",
        ],
    },
}

# Quarteirões residenciais: (código, lado, maior número de casa), conforme o mapa.
# Q06, Q19, Q25 e Q29 abrigam escolas, praça e hospital e não possuem casas.
QUARTEIROES = [
    ("Q01", "OESTE", 1), ("Q02", "OESTE", 4), ("Q03", "OESTE", 3), ("Q04", "OESTE", 1),
    ("Q05", "LESTE", 4), ("Q07", "LESTE", 1),
    ("Q08", "OESTE", 2), ("Q09", "OESTE", 6), ("Q10", "OESTE", 6), ("Q11", "OESTE", 2),
    ("Q12", "LESTE", 6), ("Q13", "LESTE", 8), ("Q14", "LESTE", 2),
    ("Q15", "OESTE", 3), ("Q16", "OESTE", 9), ("Q17", "OESTE", 8), ("Q18", "OESTE", 3),
    ("Q20", "LESTE", 12), ("Q21", "LESTE", 3),
    ("Q22", "OESTE", 2), ("Q23", "OESTE", 11), ("Q24", "OESTE", 2),
    ("Q26", "LESTE", 8), ("Q27", "LESTE", 2),
    ("Q28", "OESTE", 1), ("Q30", "OESTE", 1),
    ("Q31", "LESTE", 3), ("Q32", "LESTE", 4), ("Q33", "LESTE", 1),
]

# Moradores fictícios: (identificador, nome, e-mail, quarteirão, casa).
# O e-mail e a casa não são exibidos nas listagens do bairro.
CADASTRO_MORADORES = [
    ("USR001", "Ana Clara Martins", "ana.martins@example.com", "Q02", 1),
    ("USR002", "Bruno Henrique Costa", "bruno.costa@example.com", "Q03", 2),
    ("USR003", "Camila Ferreira Lima", "camila.lima@example.com", "Q04", 1),
    ("USR004", "Diego Rafael Santos", "diego.santos@example.com", "Q05", 2),
    ("USR005", "Elisa Moreira Alves", "elisa.alves@example.com", "Q08", 1),
    ("USR006", "Felipe Augusto Rocha", "felipe.rocha@example.com", "Q10", 3),
    ("USR007", "Gabriela Souza Ribeiro", "gabriela.ribeiro@example.com", "Q11", 2),
    ("USR008", "João Pedro Oliveira", "joao.oliveira@example.com", "Q18", 3),
    ("USR009", "Larissa Almeida Nunes", "larissa.nunes@example.com", "Q23", 6),
    ("USR010", "Marcos Vinícius Barbosa", "marcos.barbosa@example.com", "Q32", 4),
    ("USR011", "Beatriz Carvalho Mendes", "beatriz.mendes@example.com", "Q01", 1),
    ("USR012", "Carlos Eduardo Teixeira", "carlos.teixeira@example.com", "Q02", 2),
    ("USR013", "Daniela Cristina Lopes", "daniela.lopes@example.com", "Q03", 1),
    ("USR014", "Eduardo Henrique Castro", "eduardo.castro@example.com", "Q05", 1),
    ("USR015", "Fernanda Azevedo Pinto", "fernanda.pinto@example.com", "Q07", 1),
    ("USR017", "Helena Duarte Freitas", "helena.freitas@example.com", "Q10", 1),
    ("USR018", "Igor Matheus Correia", "igor.correia@example.com", "Q12", 2),
    ("USR019", "Juliana Batista Ramos", "juliana.ramos@example.com", "Q13", 1),
    ("USR020", "Lucas Gabriel Dias", "lucas.dias@example.com", "Q14", 2),
    ("USR021", "Mariana Campos Silveira", "mariana.silveira@example.com", "Q15", 3),
    ("USR022", "Nicolas André Monteiro", "nicolas.monteiro@example.com", "Q16", 1),
    ("USR023", "Patrícia Regina Moraes", "patricia.moraes@example.com", "Q17", 2),
    ("USR024", "Rafael Henrique Farias", "rafael.farias@example.com", "Q20", 10),
    ("USR025", "Renata Cristina Tavares", "renata.tavares@example.com", "Q21", 2),
    ("USR026", "Samuel Pereira Macedo", "samuel.macedo@example.com", "Q22", 1),
    ("USR027", "Tatiane Gomes Rezende", "tatiane.rezende@example.com", "Q24", 2),
    ("USR029", "Vanessa Cristina Melo", "vanessa.melo@example.com", "Q30", 1),
    ("USR030", "Vitor Hugo Fernandes", "vitor.fernandes@example.com", "Q31", 2),
]


def lado_do_quarteirao(codigo):
    for quarteirao, lado, casas in QUARTEIROES:
        if quarteirao == codigo:
            return lado
    return None


def casas_do_quarteirao(codigo):
    for quarteirao, lado, casas in QUARTEIROES:
        if quarteirao == codigo:
            return casas
    return 0


def montar_moradores():
    moradores = []
    for codigo, nome, email, quarteirao, casa in CADASTRO_MORADORES:
        moradores.append({
            "codigo": codigo, "nome": nome, "email": email,
            "setor": lado_do_quarteirao(quarteirao), "quarteirao": quarteirao, "casa": casa,
        })
    return moradores


MORADORES = montar_moradores()


def buscar_morador(codigo):
    for morador in MORADORES:
        if morador["codigo"] == codigo:
            return morador
    return None


# Regras de convivência: (tema, lista de itens), conforme descrito em docs/bairro-solarian.md.
REGRAS_BAIRRO = [
    ("Coleta de lixo comum", [
        "A coleta acontece às segundas, quartas e sextas-feiras, das 7h às 10h.",
        "Colocar os sacos bem fechados na frente do imóvel entre 6h e 7h, somente no dia da coleta.",
        "Manter os resíduos fora da faixa livre de circulação e das rampas de acessibilidade.",
    ]),
    ("Coleta seletiva", [
        "A coleta acontece às terças e quintas-feiras, das 8h às 11h.",
        "Separar papel, plástico, metal e vidro, mantendo os materiais limpos e secos.",
        "Disponibilizar os recicláveis até as 8h do dia da coleta.",
        "Embalar e identificar vidros quebrados para evitar acidentes.",
    ]),
    ("Entulho e móveis usados", [
        "O recolhimento acontece aos sábados, das 8h às 12h, mediante agendamento com a administração fictícia do bairro até quinta-feira, às 18h.",
        "Disponibilizar os materiais somente no dia confirmado, preservando a passagem de pedestres.",
    ]),
    ("Descarte irregular", [
        "É proibido descartar lixo, móveis, entulho ou óleo em terrenos, praças, bueiros e vias públicas.",
        "Não queimar resíduos nem despejar produtos nos ralos de rua.",
    ]),
    ("Horário de silêncio", [
        "O horário de silêncio vai das 22h às 8h.",
        "Nesse período, evitar música, festas, equipamentos e outras fontes de ruído que incomodem os vizinhos.",
        "Nos demais horários, manter música, televisão e conversas em volume moderado.",
    ]),
    ("Obras e reformas", [
        "Atividades com ruído podem ocorrer de segunda a sexta, das 8h às 18h, e aos sábados, das 9h às 13h.",
        "Aos domingos e feriados, somente reparos emergenciais.",
        "Manter materiais dentro do imóvel e evitar poeira ou resíduos nas casas vizinhas.",
        "Sinalizar intervenções que afetem a circulação e preservar uma passagem acessível.",
    ]),
    ("Festas e eventos", [
        "Eventos particulares devem respeitar o horário de silêncio e manter as vias desobstruídas.",
        "Eventos na Praça dos Encontros precisam de agendamento e autorização da administração fictícia do bairro.",
        "A organização deve informar o horário de início, cuidar da limpeza e preservar jardins e equipamentos.",
        "Acessos ao hospital, às escolas, aos imóveis e às rampas devem permanecer livres.",
    ]),
    ("Calçadas e acessibilidade", [
        "Manter a passagem livre para pedestres, cadeiras de rodas e carrinhos de bebê.",
        "Não bloquear calçadas ou rampas com veículos, materiais, lixo ou mobiliário comercial.",
    ]),
    ("Animais de estimação", [
        "Conduzir os animais com guia nos espaços públicos e recolher suas fezes.",
        "Evitar que circulem sozinhos pelas ruas.",
        "Preservar a segurança de crianças, pedestres e outros animais.",
    ]),
    ("Praça dos Encontros", [
        "Preservar jardins, bancos, fonte e playground.",
        "Não quebrar equipamentos, retirar plantas ou deixar resíduos no local.",
        "Crianças devem utilizar o playground com acompanhamento de um responsável.",
    ]),
    ("Trânsito próximo às escolas", [
        "Respeitar a sinalização e as travessias de pedestres.",
        "Não estacionar sobre faixas, calçadas ou em frente aos portões das escolas, mesmo durante embarque e desembarque.",
        "Redobrar a atenção nos horários de entrada e saída.",
    ]),
    ("Limpeza dos imóveis", [
        "Manter quintais e terrenos limpos, sem acúmulo de resíduos ou água parada.",
        "Cuidar da vegetação para que não bloqueie a circulação ou a visibilidade.",
        "Não direcionar água de lavagem e resíduos para imóveis vizinhos ou espaços públicos.",
    ]),
    ("Registro de ocorrências", [
        "Informar categoria, localização e descrição objetiva do problema.",
        "Indicar a localização pela rua ou por um ponto de referência do bairro.",
        "O sistema simulado recebe solicitações urbanas; situações com risco imediato devem seguir o atendimento de emergência.",
    ]),
    ("Respeito e privacidade", [
        "Não publicar ofensas, ameaças, acusações pessoais ou dados de terceiros.",
        "Descrever o problema sem identificar pessoas, pacientes, estudantes ou o interior de residências.",
        "Utilizar exclusivamente dados fictícios.",
    ]),
    ("Ocorrências duplicadas", [
        "Antes de abrir um registro, verificar se o mesmo problema já foi informado.",
        "Se houver uma ocorrência correspondente, apoiar o registro existente.",
        "Problemas diferentes no mesmo local podem ser registrados separadamente.",
    ]),
    ("Acesso ao Hospital Solarian", [
        "Manter livres a entrada principal e o acesso de ambulâncias do Q25.",
        "Evitar buzinas e ruídos desnecessários nas proximidades.",
        "Não ocupar acessos ou vagas sinalizadas para atendimento.",
    ]),
    ("Convivência com os comércios", [
        "Comerciantes devem manter a frente do estabelecimento limpa e a calçada acessível.",
        "Cargas, descargas e filas devem preservar a circulação e o acesso dos vizinhos.",
        "Resíduos comerciais não devem ser abandonados na rua.",
        "Propaganda sonora deve respeitar as regras de ruído do bairro.",
    ]),
]

DIA_INICIAL = 12

# Alterada quando a base do código muda; um banco de outra versão é recriado.
VERSAO_BASE = 5

# Registros de origem. Os três últimos possuem defeitos propositais, que a
# validação identifica e separa em "registros com problema".
REGISTROS_INICIAIS = [
    {"id": "OC-001", "categoria": "ILUMINACAO", "setor": "LESTE", "local": "Praça dos Encontros",
     "descricao": "Três postes apagados ao redor da fonte.", "dia_abertura": 1, "status": "ABERTA", "autor": "USR024"},
    {"id": "OC-002", "categoria": "LIMPEZA", "setor": "OESTE", "local": "Rua das Palmeiras",
     "descricao": "Entulho acumulado na calçada perto da esquina.", "dia_abertura": 1, "status": "ABERTA", "autor": "USR021"},
    {"id": "OC-003", "categoria": "ACESSIBILIDADE", "setor": "LESTE", "local": "Escola Municipal Novo Amanhecer",
     "descricao": "Rampa de acesso com piso quebrado.", "dia_abertura": 2, "status": "ABERTA", "autor": "USR019"},
    {"id": "OC-004", "categoria": "CONSERVACAO", "setor": "OESTE", "local": "Escola Municipal Caminhos do Sol",
     "descricao": "Alambrado da quadra solto em um dos lados.", "dia_abertura": 2, "status": "ABERTA", "autor": "USR009"},
    {"id": "OC-005", "categoria": "ILUMINACAO", "setor": "OESTE", "local": "Rua das Acácias",
     "descricao": "Lâmpada piscando durante a noite toda.", "dia_abertura": 3, "status": "ABERTA", "autor": "USR017"},
    {"id": "OC-006", "categoria": "LIMPEZA", "setor": "LESTE", "local": "Avenida Sol Nascente",
     "descricao": "Pedido de varrição da avenida três vezes ao dia.", "dia_abertura": 3, "status": "ABERTA", "autor": "USR018"},
    {"id": "OC-007", "categoria": "ACESSIBILIDADE", "setor": "OESTE", "local": "Escola Municipal Caminhos do Sol",
     "descricao": "Falta de piso tátil na entrada principal.", "dia_abertura": 4, "status": "ABERTA", "autor": "USR022"},
    {"id": "OC-008", "categoria": "CONSERVACAO", "setor": "LESTE", "local": "Praça dos Encontros",
     "descricao": "Bancos de madeira quebrados.", "dia_abertura": 5, "status": "ABERTA", "autor": "USR024"},
    {"id": "OC-009", "categoria": "ILUMINACAO", "setor": "OESTE", "local": "Rua do Horizonte",
     "descricao": "Trecho sem iluminação entre dois quarteirões.", "dia_abertura": 7, "status": "ABERTA", "autor": "USR008"},
    {"id": "OC-010", "categoria": "LIMPEZA", "setor": "LESTE", "local": "Praça dos Encontros",
     "descricao": "Lixeiras transbordando no fim de semana.", "dia_abertura": 9, "status": "ABERTA", "autor": "USR025"},
    {"id": "OC-011", "categoria": "ACESSIBILIDADE", "setor": "LESTE", "local": "Rua da Aurora",
     "descricao": "Calçada sem rebaixamento para cadeira de rodas.", "dia_abertura": 10, "status": "ABERTA", "autor": "USR020"},
    {"id": "OC-012", "categoria": "CONSERVACAO", "setor": "OESTE", "local": "Rua dos Girassóis",
     "descricao": "Buraco na calçada perto da esquina.", "dia_abertura": 11, "status": "ABERTA", "autor": "USR023"},
    # Defeito 1: categoria ausente.
    {"id": "OC-013", "categoria": "", "setor": "OESTE", "local": "Rua do Horizonte",
     "descricao": "Problema na rua, sem informar o tipo.", "dia_abertura": 8, "status": "ABERTA", "autor": "USR008"},
    # Defeito 2: situação desconhecida.
    {"id": "OC-014", "categoria": "LIMPEZA", "setor": "LESTE", "local": "Praça dos Encontros",
     "descricao": "Folhas acumuladas no parquinho.", "dia_abertura": 9, "status": "RESOLVENDO", "autor": "USR024"},
    # Defeito 3: código repetido.
    {"id": "OC-003", "categoria": "ILUMINACAO", "setor": "OESTE", "local": "Rua dos Girassóis",
     "descricao": "Poste inclinado.", "dia_abertura": 10, "status": "ABERTA", "autor": "USR023"},
]

# Atualizações simuladas: (dia, código, nova situação, observação).
EVENTOS_INICIAIS = [
    (2, "OC-001", "EM_ANALISE", "Vistoria agendada."),
    (3, "OC-001", "EM_ATENDIMENTO", "Troca das lâmpadas iniciada."),
    (3, "OC-002", "EM_ANALISE", "Volume de entulho avaliado."),
    (3, "OC-003", "EM_ANALISE", "Rampa vistoriada."),
    (4, "OC-002", "EM_ATENDIMENTO", "Caçamba solicitada."),
    (4, "OC-003", "EM_ATENDIMENTO", "Reparo do piso iniciado."),
    (4, "OC-004", "EM_ANALISE", "Alambrado avaliado."),
    (5, "OC-001", "CONCLUIDA", "Três postes religados."),
    (5, "OC-005", "EM_ANALISE", "Aguardando peça de reposição."),
    (5, "OC-006", "EM_ANALISE", "Pedido comparado com a rotina de limpeza."),
    (6, "OC-003", "CONCLUIDA", "Piso da rampa refeito."),
    (6, "OC-004", "EM_ATENDIMENTO", "Material comprado."),
    (6, "OC-007", "EM_ANALISE", "Projeto do piso tátil em avaliação."),
    (7, "OC-006", "RECUSADA", "A avenida já tem varrição diária."),
    (7, "OC-008", "EM_ANALISE", "Bancos vistoriados."),
    (8, "OC-002", "CONCLUIDA", "Entulho retirado."),
    (9, "OC-008", "EM_ATENDIMENTO", "Marcenaria comunitária acionada."),
]


# =============================================================================
# PARTE 3 - Regras de validação dos registros
# Aplicadas na carga da base e no cadastro pelo terminal.
# =============================================================================

def categoria_valida(categoria):
    return categoria in CATEGORIAS


def situacao_valida(situacao):
    return situacao in SITUACOES


def local_valido(setor, local):
    return setor in BAIRRO and local in BAIRRO[setor]["locais"]


def campo_vazio(valor):
    return valor is None or str(valor).strip() == ""


# Devolve a lista de inconsistências do registro; lista vazia indica registro válido.
def validar_registro(registro, indice):
    problemas = []

    for campo in CAMPOS_OBRIGATORIOS:
        if campo_vazio(registro.get(campo)):
            problemas.append("campo obrigatório ausente: " + campo)

    codigo = registro.get("id")
    categoria = registro.get("categoria")
    situacao = registro.get("status")
    setor = registro.get("setor")
    local = registro.get("local")

    if not campo_vazio(codigo) and codigo in indice:
        problemas.append("código repetido: " + codigo)
    if not campo_vazio(categoria) and not categoria_valida(categoria):
        problemas.append("categoria desconhecida: " + categoria)
    if not campo_vazio(situacao) and not situacao_valida(situacao):
        problemas.append("situação desconhecida: " + situacao)
    if not campo_vazio(setor) and not campo_vazio(local) and not local_valido(setor, local):
        problemas.append("local não pertence ao lado informado")

    return problemas


# =============================================================================
# PARTE 4 - Banco de dados em JSON
# O arquivo armazena os dados de origem: dia simulado, ocorrências, histórico,
# fila de triagem, registros rejeitados e agenda. O bairro e os moradores são
# definidos no código. As demais estruturas são reconstruídas na Parte 5.
# =============================================================================

def novo_banco_vazio():
    return {
        "versao": VERSAO_BASE,
        "dia_atual": 1,
        "proximo_numero": 1,
        "ocorrencias": [],
        "historico": [],
        "fila_triagem": [],
        "rejeitados": [],
        "agenda": [],
        "proximo_evento": 1,
    }


def nova_ocorrencia(codigo, categoria, setor, local, descricao, dia_abertura, autor):
    return {
        "id": codigo,
        "categoria": categoria,
        "descricao": descricao.strip(),
        "setor": setor,
        "local": local,
        "dia_abertura": dia_abertura,
        "status": "ABERTA",
        "dia_conclusao": None,
        "autor": autor,
        "apoios": [],
    }


# Constrói a base inicial: valida os registros e aplica as atualizações simuladas.
def criar_banco_inicial():
    estado = novo_estado(novo_banco_vazio(), None)
    banco = estado["banco"]

    for registro in REGISTROS_INICIAIS:
        problemas = validar_registro(registro, estado["indice"])
        if problemas:
            banco["rejeitados"].append({"registro": registro, "problemas": problemas})
        else:
            ocorrencia = nova_ocorrencia(
                registro["id"], registro["categoria"], registro["setor"], registro["local"],
                registro["descricao"], registro["dia_abertura"], registro["autor"],
            )
            banco["ocorrencias"].append(ocorrencia)
            banco["fila_triagem"].append(ocorrencia["id"])
            estado["indice"][ocorrencia["id"]] = ocorrencia

    banco["proximo_numero"] = len(REGISTROS_INICIAIS)

    for dia, codigo, nova_situacao, observacao in EVENTOS_INICIAIS:
        banco["dia_atual"] = dia
        atualizar_situacao(estado, PERFIL_GESTOR, codigo, nova_situacao, observacao)

    banco["dia_atual"] = DIA_INICIAL
    return banco


# O banco fica na pasta "dados" do projeto; no executável, ao lado do arquivo .exe.
def caminho_banco():
    if getattr(sys, "frozen", False):
        pasta = os.path.dirname(sys.executable)
    else:
        pasta = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(pasta, "dados", "banco.json")


# Arquivo ausente, ilegível ou de outra versão resulta em nova base inicial.
def carregar_banco(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                banco = json.load(arquivo)
            if banco.get("versao") == VERSAO_BASE:
                return banco
        except (OSError, ValueError, AttributeError):
            pass
        mensagem_atencao("Banco de dados ilegível ou de outra versão: base inicial recriada.")
    return criar_banco_inicial()


def salvar_banco(estado):
    caminho = estado["caminho"]
    if caminho is None:
        return
    try:
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(estado["banco"], arquivo, ensure_ascii=False, indent=2)
    except OSError:
        mensagem_erro("Não foi possível gravar o banco de dados em " + caminho)


# =============================================================================
# PARTE 5 - Estruturas de dados
#   lista       banco["ocorrencias"]   conjunto completo, percorrido nas consultas
#   dicionário  estado["indice"]       acesso direto pelo código
#   fila        banco["fila_triagem"]  abertas ainda não examinadas (entra no fim, sai do início)
#   pilha       estado["pilha"]        atualizações; a mais recente fica no topo
#   hierarquia  estado["hierarquia"]   bairro -> lado -> categoria -> códigos
#   matriz      estado["matriz"]       linhas = categorias, colunas = situações
# =============================================================================

def novo_estado(banco, caminho):
    estado = {"banco": banco, "caminho": caminho}
    reconstruir_estruturas(estado)
    return estado


def montar_indice(ocorrencias):
    indice = {}
    for ocorrencia in ocorrencias:
        indice[ocorrencia["id"]] = ocorrencia
    return indice


def montar_pilha(historico):
    pilha = []
    for evento in historico:
        pilha.append(evento)
    return pilha


def montar_hierarquia(ocorrencias):
    lados = {}
    for setor in SETORES:
        lados[setor] = {}
        for categoria in CATEGORIAS:
            lados[setor][categoria] = []
    for ocorrencia in ocorrencias:
        lados[ocorrencia["setor"]][ocorrencia["categoria"]].append(ocorrencia["id"])
    return {NOME_BAIRRO: lados}


def montar_matriz(ocorrencias):
    matriz = []
    for categoria in CATEGORIAS:
        matriz.append([0] * len(SITUACOES))
    for ocorrencia in ocorrencias:
        linha_matriz = CATEGORIAS.index(ocorrencia["categoria"])
        coluna = SITUACOES.index(ocorrencia["status"])
        matriz[linha_matriz][coluna] += 1
    return matriz


def reconstruir_estruturas(estado):
    banco = estado["banco"]
    estado["indice"] = montar_indice(banco["ocorrencias"])
    estado["pilha"] = montar_pilha(banco["historico"])
    estado["hierarquia"] = montar_hierarquia(banco["ocorrencias"])
    estado["matriz"] = montar_matriz(banco["ocorrencias"])


# Após cada mudança: atualiza hierarquia e matriz e grava o banco.
def registrar_alteracao(estado):
    estado["hierarquia"] = montar_hierarquia(estado["banco"]["ocorrencias"])
    estado["matriz"] = montar_matriz(estado["banco"]["ocorrencias"])
    salvar_banco(estado)


# =============================================================================
# PARTE 6 - Entrada de dados validada
# As escolhas são feitas por número; apenas descrições e títulos são digitados.
# =============================================================================

# Repete a leitura até receber um número inteiro dentro do intervalo.
def ler_opcao(mensagem, minimo, maximo):
    while True:
        texto = input(mensagem).strip()
        if texto.isdigit() and len(texto) <= 4 and minimo <= int(texto) <= maximo:
            return int(texto)
        mensagem_erro("Opção inválida. Digite um número de " + str(minimo) + " a " + str(maximo) + ".")


# Remove espaços repetidos e espaços nas extremidades.
def limpar_texto(texto):
    return " ".join(texto.split())


# Devolve o texto validado, ou None quando o usuário digita 0 para cancelar.
def ler_texto(mensagem, minimo, maximo):
    while True:
        texto = limpar_texto(input(mensagem))
        if texto == "0":
            return None
        if len(texto) < minimo:
            mensagem_erro("Texto muito curto. Escreva pelo menos " + str(minimo) + " caracteres, ou 0 para cancelar.")
        elif len(texto) > maximo:
            mensagem_erro("Texto muito longo. O limite é de " + str(maximo) + " caracteres.")
        else:
            return texto


def confirmar(mensagem):
    return ler_opcao(mensagem + " (1 = sim, 0 = não): ", 0, 1) == 1


# Devolve a posição escolhida na lista, ou None quando o usuário volta.
def escolher(titulo_menu, opcoes):
    print()
    print(pintar(titulo_menu, "negrito"))
    for posicao in range(len(opcoes)):
        mostrar_opcao(posicao + 1, opcoes[posicao])
    mostrar_opcao(0, "Voltar")
    escolha = ler_opcao("Escolha: ", 0, len(opcoes))
    if escolha == 0:
        return None
    return escolha - 1


# Converte "14" ou "oc14" para o padrão OC-014; devolve None se for inválido.
def normalizar_id(texto):
    digitos = texto.strip().upper().replace("OC", "").replace("-", "").strip()
    if digitos.isdigit() and 1 <= len(digitos) <= 3:
        return "OC-" + digitos.zfill(3)
    return None


def ler_codigo():
    while True:
        texto = input("Código da ocorrência (exemplo: 14 ou OC-014; 0 para voltar): ").strip()
        if texto == "0":
            return None
        codigo = normalizar_id(texto)
        if codigo is not None:
            return codigo
        mensagem_erro("Código inválido. Use o número da ocorrência, de 1 a 999.")


def pausar():
    input(pintar("\nPressione Enter para continuar...", "cinza"))


# O resumo (hash) permite conferir a senha sem armazená-la no código.
def resumo_da_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def senha_gestor_correta(senha):
    return resumo_da_senha(senha) == RESUMO_SENHA_GESTOR


# Até três tentativas; a digitação não aparece na tela e a entrada em branco cancela.
def autenticar_gestor():
    print()
    print("Acesso restrito ao gestor do bairro. A senha não é exibida durante a digitação.")
    print("Deixe em branco e tecle Enter para voltar.")
    tentativa = 1
    while tentativa <= TENTATIVAS_SENHA:
        senha = getpass.getpass("Senha do gestor: ")
        if senha == "":
            return False
        elif senha_gestor_correta(senha):
            mensagem_ok("Acesso liberado.")
            return True
        else:
            restantes = TENTATIVAS_SENHA - tentativa
            if restantes > 0:
                mensagem_erro("Senha incorreta. Tentativas restantes: " + str(restantes) + ".")
            else:
                mensagem_erro("Senha incorreta. Limite de tentativas atingido.")
        tentativa += 1
    return False


# =============================================================================
# PARTE 7 - Regras de cadastro, atualização de situação e agenda
# =============================================================================

# Pendente: não concluída nem recusada.
def esta_pendente(ocorrencia):
    return not (ocorrencia["status"] == "CONCLUIDA" or ocorrencia["status"] == "RECUSADA")


def dias_em_acompanhamento(ocorrencia, dia_atual):
    if ocorrencia["dia_conclusao"] is not None:
        return ocorrencia["dia_conclusao"] - ocorrencia["dia_abertura"]
    return dia_atual - ocorrencia["dia_abertura"]


# Atrasada: pendente e aberta há mais dias que o limite.
def esta_atrasada(ocorrencia, dia_atual):
    return esta_pendente(ocorrencia) and (dia_atual - ocorrencia["dia_abertura"]) > LIMITE_DIAS_ATRASO


# Ocorrência pendente de mesma categoria no mesmo local.
def procurar_duplicata(estado, categoria, setor, local):
    for ocorrencia in estado["banco"]["ocorrencias"]:
        mesma_categoria = ocorrencia["categoria"] == categoria
        mesmo_local = ocorrencia["setor"] == setor and ocorrencia["local"] == local
        if mesma_categoria and mesmo_local and esta_pendente(ocorrencia):
            return ocorrencia
    return None


# Devolve (True, ocorrência) ou (False, lista de inconsistências).
def cadastrar_ocorrencia(estado, categoria, setor, local, descricao, autor):
    banco = estado["banco"]
    codigo = "OC-" + str(banco["proximo_numero"]).zfill(3)
    registro = {
        "id": codigo, "categoria": categoria, "descricao": descricao, "setor": setor,
        "local": local, "dia_abertura": banco["dia_atual"], "status": "ABERTA",
    }
    problemas = validar_registro(registro, estado["indice"])
    if problemas:
        return False, problemas

    ocorrencia = nova_ocorrencia(codigo, categoria, setor, local, descricao, banco["dia_atual"], autor)
    banco["ocorrencias"].append(ocorrencia)      # lista: entra no conjunto
    estado["indice"][codigo] = ocorrencia         # dicionário: acesso pelo código
    banco["fila_triagem"].append(codigo)          # fila: entra no fim
    banco["proximo_numero"] += 1
    registrar_alteracao(estado)
    return True, ocorrencia


def apoiar_ocorrencia(estado, codigo, codigo_morador):
    ocorrencia = estado["indice"].get(codigo)
    if ocorrencia is None:
        return False, "Ocorrência " + codigo + " não encontrada."
    elif not esta_pendente(ocorrencia):
        return False, "Esta ocorrência já foi encerrada e não recebe mais apoios."
    elif ocorrencia["autor"] == codigo_morador:
        return False, "A ocorrência foi registrada por este morador e já contempla a sua solicitação."
    elif codigo_morador in ocorrencia["apoios"]:
        return False, "Este morador já registrou apoio a esta ocorrência."
    else:
        ocorrencia["apoios"].append(codigo_morador)
        salvar_banco(estado)
        return True, "Apoio registrado em " + codigo + ". Total de apoios: " + str(len(ocorrencia["apoios"])) + "."


def transicao_valida(situacao_atual, nova_situacao):
    return nova_situacao in TRANSICOES[situacao_atual]


# Expressão booleana da atualização de situação, documentada no README.
def pode_atualizar(estado, perfil, codigo, nova_situacao):
    perfil_gestor = perfil == PERFIL_GESTOR
    id_existe = codigo in estado["indice"]
    situacao_conhecida = situacao_valida(nova_situacao)
    return (
        perfil_gestor
        and id_existe
        and situacao_conhecida
        and transicao_valida(estado["indice"][codigo]["status"], nova_situacao)
    )


# Altera a situação e registra o evento no histórico e na pilha.
def atualizar_situacao(estado, perfil, codigo, nova_situacao, observacao):
    banco = estado["banco"]

    if not pode_atualizar(estado, perfil, codigo, nova_situacao):
        if perfil != PERFIL_GESTOR:
            return False, "Somente o gestor pode alterar a situação de uma ocorrência."
        elif codigo not in estado["indice"]:
            return False, "Ocorrência " + codigo + " não encontrada."
        elif not situacao_valida(nova_situacao):
            return False, "Situação desconhecida: " + nova_situacao + "."
        else:
            atual = estado["indice"][codigo]["status"]
            permitidas = nomes_de(TRANSICOES[atual], NOMES_SITUACAO)
            if nova_situacao == atual:
                return False, "A ocorrência já está em: " + NOMES_SITUACAO[atual] + "."
            elif len(permitidas) == 0:
                return False, "Ocorrência encerrada (" + NOMES_SITUACAO[atual] + "): não aceita novas alterações."
            else:
                return False, (
                    "Mudança não permitida: de " + NOMES_SITUACAO[atual] + " só é possível ir para "
                    + " ou ".join(permitidas) + "."
                )

    ocorrencia = estado["indice"][codigo]
    evento = {
        "dia": banco["dia_atual"],
        "id": codigo,
        "de": ocorrencia["status"],
        "para": nova_situacao,
        "responsavel": perfil,
        "observacao": limpar_texto(observacao),
    }
    ocorrencia["status"] = nova_situacao
    if nova_situacao == "CONCLUIDA":
        ocorrencia["dia_conclusao"] = banco["dia_atual"]
    if codigo in banco["fila_triagem"]:
        banco["fila_triagem"].remove(codigo)      # deixou de estar "não examinada"
    banco["historico"].append(evento)
    estado["pilha"].append(evento)                # pilha: empilha no topo
    registrar_alteracao(estado)
    return True, codigo + ": " + NOMES_SITUACAO[evento["de"]] + " -> " + NOMES_SITUACAO[nova_situacao] + "."


# Desempilha o evento mais recente e restaura a situação anterior.
def desfazer_ultima(estado, perfil):
    banco = estado["banco"]
    if perfil != PERFIL_GESTOR:
        return False, "Somente o gestor pode desfazer uma atualização."
    elif len(estado["pilha"]) == 0:
        return False, "Não há atualizações para desfazer."
    else:
        evento = estado["pilha"].pop()            # pilha: sai o último que entrou
        banco["historico"].pop()
        ocorrencia = estado["indice"][evento["id"]]
        ocorrencia["status"] = evento["de"]
        if evento["para"] == "CONCLUIDA":
            ocorrencia["dia_conclusao"] = None
        if evento["de"] == "ABERTA" and evento["id"] not in banco["fila_triagem"]:
            banco["fila_triagem"].insert(0, evento["id"])
        registrar_alteracao(estado)
        return True, (
            "Desfeito: " + evento["id"] + " voltou de " + NOMES_SITUACAO[evento["para"]]
            + " para " + NOMES_SITUACAO[evento["de"]] + "."
        )


# Fila: a primeira ocorrência passa para o fim.
def adiar_triagem(estado):
    fila = estado["banco"]["fila_triagem"]
    if len(fila) > 1:
        fila.append(fila.pop(0))
        salvar_banco(estado)


def avancar_dia(estado, dias):
    estado["banco"]["dia_atual"] += dias
    salvar_banco(estado)


# O evento só pode começar fora do horário de silêncio: das 8h até antes das 22h.
def hora_permitida(hora):
    return hora >= HORA_FIM_SILENCIO and hora < HORA_INICIO_SILENCIO


# Devolve (True, evento) ou (False, motivo da recusa).
def criar_evento_bairro(estado, perfil, tipo, titulo_evento, setor, local, dia, hora, descricao):
    banco = estado["banco"]
    titulo_limpo = limpar_texto(titulo_evento)
    descricao_limpa = limpar_texto(descricao)
    if perfil != PERFIL_GESTOR:
        return False, "Somente o gestor pode criar eventos do bairro."
    elif tipo not in TIPOS_EVENTO:
        return False, "Tipo de evento desconhecido: " + tipo + "."
    elif len(titulo_limpo) < TAMANHO_MINIMO_TITULO or len(titulo_limpo) > TAMANHO_MAXIMO_TITULO:
        return False, "O título deve ter de " + str(TAMANHO_MINIMO_TITULO) + " a " + str(TAMANHO_MAXIMO_TITULO) + " caracteres."
    elif not local_valido(setor, local):
        return False, "O local não pertence ao lado informado do bairro."
    elif dia < banco["dia_atual"]:
        return False, "O dia do evento não pode ser anterior ao dia atual (" + str(banco["dia_atual"]) + ")."
    elif not hora_permitida(hora):
        return False, (
            "Horário não permitido: o bairro tem silêncio das " + str(HORA_INICIO_SILENCIO) + "h às "
            + str(HORA_FIM_SILENCIO) + "h. O evento deve começar entre " + str(HORA_FIM_SILENCIO) + "h e "
            + str(HORA_INICIO_SILENCIO - 1) + "h."
        )
    else:
        evento = {
            "id": "EV-" + str(banco["proximo_evento"]).zfill(3),
            "tipo": tipo, "titulo": titulo_limpo, "setor": setor, "local": local,
            "dia": dia, "hora": hora, "descricao": descricao_limpa, "cancelado": False,
        }
        banco["agenda"].append(evento)
        banco["proximo_evento"] += 1
        salvar_banco(estado)
        return True, evento


def buscar_evento_bairro(estado, codigo):
    for evento in estado["banco"]["agenda"]:
        if evento["id"] == codigo:
            return evento
    return None


# O evento cancelado permanece na agenda, marcado, para ciência dos moradores.
def cancelar_evento_bairro(estado, perfil, codigo):
    evento = buscar_evento_bairro(estado, codigo)
    if perfil != PERFIL_GESTOR:
        return False, "Somente o gestor pode cancelar eventos do bairro."
    elif evento is None:
        return False, "Evento " + codigo + " não encontrado."
    elif evento["cancelado"]:
        return False, "Este evento já estava cancelado."
    else:
        evento["cancelado"] = True
        salvar_banco(estado)
        return True, "Evento " + codigo + " cancelado. Ele permanece na agenda, marcado como cancelado."


# Eventos de hoje em diante, do mais próximo para o mais distante.
def proximos_eventos(estado):
    dia_atual = estado["banco"]["dia_atual"]
    futuros = []
    datas = []
    for evento in estado["banco"]["agenda"]:
        if evento["dia"] >= dia_atual:
            futuros.append(evento)
            datas.append((evento["dia"], evento["hora"], evento["id"]))
    return ordenar_por_insercao(futuros, datas)


# =============================================================================
# PARTE 8 - Consultas, busca e ordenação
# =============================================================================

def buscar_por_id(estado, codigo):
    return estado["indice"].get(codigo)


# Busca binária sobre lista ordenada por código.
def busca_binaria_por_id(ocorrencias_ordenadas, codigo):
    inicio = 0
    fim = len(ocorrencias_ordenadas) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        atual = ocorrencias_ordenadas[meio]["id"]
        if atual == codigo:
            return ocorrencias_ordenadas[meio]
        elif atual < codigo:
            inicio = meio + 1
        else:
            fim = meio - 1
    return None


# Busca sequencial; filtros não informados não restringem o resultado.
def filtrar(estado, categoria=None, situacao=None, setor=None, autor=None,
            somente_pendentes=False, somente_atrasadas=False):
    dia_atual = estado["banco"]["dia_atual"]
    encontradas = []
    for ocorrencia in estado["banco"]["ocorrencias"]:
        atende = (
            (categoria is None or ocorrencia["categoria"] == categoria)
            and (situacao is None or ocorrencia["status"] == situacao)
            and (setor is None or ocorrencia["setor"] == setor)
            and (autor is None or ocorrencia["autor"] == autor)
            and (not somente_pendentes or esta_pendente(ocorrencia))
            and (not somente_atrasadas or esta_atrasada(ocorrencia, dia_atual))
        )
        if atende:
            encontradas.append(ocorrencia)
    return encontradas


# Ordenação por inserção. "valores" traz, na mesma posição, o valor de comparação
# de cada item. Devolve nova lista de itens, do menor valor para o maior.
def ordenar_por_insercao(itens, valores):
    itens = list(itens)
    valores = list(valores)
    for i in range(1, len(itens)):
        item_atual = itens[i]
        valor_atual = valores[i]
        j = i - 1
        while j >= 0 and valores[j] > valor_atual:
            itens[j + 1] = itens[j]
            valores[j + 1] = valores[j]
            j -= 1
        itens[j + 1] = item_atual
        valores[j + 1] = valor_atual
    return itens


def ordenar_por_codigo(ocorrencias):
    valores = []
    for ocorrencia in ocorrencias:
        valores.append(ocorrencia["id"])
    return ordenar_por_insercao(ocorrencias, valores)


# Mais antiga primeiro; no empate de dia, prevalece o menor código.
def ordenar_por_antiguidade(ocorrencias):
    valores = []
    for ocorrencia in ocorrencias:
        valores.append((ocorrencia["dia_abertura"], ocorrencia["id"]))
    return ordenar_por_insercao(ocorrencias, valores)


# Mais apoios primeiro (por isso o sinal negativo); no empate, a mais antiga.
def ordenar_por_apoios(ocorrencias):
    valores = []
    for ocorrencia in ocorrencias:
        valores.append((-len(ocorrencia["apoios"]), ocorrencia["dia_abertura"], ocorrencia["id"]))
    return ordenar_por_insercao(ocorrencias, valores)


def eventos_da_ocorrencia(estado, codigo):
    encontrados = []
    for evento in estado["banco"]["historico"]:
        if evento["id"] == codigo:
            encontrados.append(evento)
    return encontrados


def codigos_de(itens):
    lista = []
    for item in itens:
        lista.append(item["id"])
    return lista


# =============================================================================
# PARTE 9 - Indicadores
# Calculados com laços e operações aritméticas sobre a matriz e a lista.
# =============================================================================

# Percentual de parte em total; total zero resulta em 0.
def proporcao(parte, total):
    if total == 0:
        return 0.0
    return parte / total * 100


# Total por categoria.
def somar_linhas(matriz):
    totais = []
    for linha_matriz in matriz:
        soma = 0
        for valor in linha_matriz:
            soma += valor
        totais.append(soma)
    return totais


# Total por situação.
def somar_colunas(matriz):
    totais = [0] * len(SITUACOES)
    for linha_matriz in matriz:
        for coluna in range(len(SITUACOES)):
            totais[coluna] += linha_matriz[coluna]
    return totais


def calcular_indicadores(estado):
    ocorrencias = estado["banco"]["ocorrencias"]
    dia_atual = estado["banco"]["dia_atual"]

    por_categoria = somar_linhas(estado["matriz"])
    por_situacao = somar_colunas(estado["matriz"])
    total = len(ocorrencias)

    pendentes = 0
    atrasadas = 0
    mais_antiga = None
    por_local = {}
    soma_dias = 0
    concluidas = 0
    soma_categoria = [0] * len(CATEGORIAS)
    concluidas_categoria = [0] * len(CATEGORIAS)

    for ocorrencia in ocorrencias:
        local = ocorrencia["local"]
        por_local[local] = por_local.get(local, 0) + 1

        if esta_pendente(ocorrencia):
            pendentes += 1
            if esta_atrasada(ocorrencia, dia_atual):
                atrasadas += 1
            if mais_antiga is None or ocorrencia["dia_abertura"] < mais_antiga["dia_abertura"]:
                mais_antiga = ocorrencia

        # tempo até a conclusão = dia da conclusão - dia da abertura
        if ocorrencia["status"] == "CONCLUIDA":
            dias = ocorrencia["dia_conclusao"] - ocorrencia["dia_abertura"]
            posicao = CATEGORIAS.index(ocorrencia["categoria"])
            soma_dias += dias
            concluidas += 1
            soma_categoria[posicao] += dias
            concluidas_categoria[posicao] += 1

    tempo_medio = None
    if concluidas > 0:
        tempo_medio = soma_dias / concluidas

    tempo_medio_categoria = []
    for posicao in range(len(CATEGORIAS)):
        if concluidas_categoria[posicao] > 0:
            tempo_medio_categoria.append(soma_categoria[posicao] / concluidas_categoria[posicao])
        else:
            tempo_medio_categoria.append(None)

    local_mais_citado = None
    for local in por_local:
        if local_mais_citado is None or por_local[local] > por_local[local_mais_citado]:
            local_mais_citado = local

    return {
        "total": total,
        "por_categoria": por_categoria,
        "por_situacao": por_situacao,
        "pendentes": pendentes,
        "atrasadas": atrasadas,
        "mais_antiga": mais_antiga,
        "concluidas": concluidas,
        "soma_dias": soma_dias,
        "tempo_medio": tempo_medio,
        "tempo_medio_categoria": tempo_medio_categoria,
        "local_mais_citado": local_mais_citado,
        "quantidade_local": por_local.get(local_mais_citado, 0),
    }


def interpretar_indicadores(indicadores):
    frases = []
    total = indicadores["total"]
    if total == 0:
        return ["Ainda não há ocorrências registradas no bairro."]

    maior = 0
    for posicao in range(len(CATEGORIAS)):
        if indicadores["por_categoria"][posicao] > indicadores["por_categoria"][maior]:
            maior = posicao
    empate = indicadores["por_categoria"].count(indicadores["por_categoria"][maior]) > 1
    if empate:
        frases.append("As categorias estão equilibradas: nenhuma concentra sozinha a maior parte dos registros.")
    else:
        frases.append("A categoria com mais registros é " + NOMES_CATEGORIA[CATEGORIAS[maior]] + ".")

    if proporcao(indicadores["pendentes"], total) > 50:
        frases.append("Mais da metade das ocorrências permanece pendente: o volume de registros supera o de conclusões.")
    elif indicadores["pendentes"] == 0:
        frases.append("Não há pendências: todas as ocorrências foram encerradas.")
    else:
        frases.append("A maior parte das ocorrências já foi encerrada.")

    if indicadores["atrasadas"] > 0:
        frases.append(
            str(indicadores["atrasadas"]) + " pendência(s) passaram de " + str(LIMITE_DIAS_ATRASO)
            + " dias e devem ser priorizadas."
        )
    if indicadores["tempo_medio"] is not None:
        frases.append(
            "Quando concluída, uma ocorrência levou em média "
            + formatar_numero(indicadores["tempo_medio"]) + " dia(s)."
        )
    frases.append("Os dados são simulados: demonstram a leitura do painel, e não a situação de um bairro real.")
    return frases


# =============================================================================
# PARTE 10 - Exibição no terminal
# A situação é sempre escrita por extenso; a cor apenas reforça a informação.
# =============================================================================

# Uma casa decimal, com vírgula.
def formatar_numero(valor):
    return ("%.1f" % valor).replace(".", ",")


def linha(caractere="-"):
    print(pintar(caractere * LARGURA, "cinza"))


def titulo(texto):
    print()
    linha("=")
    print(pintar(texto.upper(), "negrito"))
    linha("=")


def cabecalho(estado, identificacao):
    print()
    linha("=")
    print(pintar(NOME_BAIRRO.upper() + " - PAINEL COMUNITÁRIO DE OCORRÊNCIAS", "ciano"))
    print("Perfil: " + pintar(identificacao, "negrito") + "   |   Dia simulado: "
          + pintar(str(estado["banco"]["dia_atual"]), "negrito"))
    linha("=")


def mostrar_opcao(numero, texto):
    print("  " + pintar("[" + str(numero) + "]", "ciano") + " " + texto)


def mensagem_ok(texto):
    print(pintar("[OK] " + texto, "verde"))


def mensagem_erro(texto):
    print(pintar("[ERRO] " + texto, "vermelho"))


def mensagem_atencao(texto):
    print(pintar("[ATENÇÃO] " + texto, "amarelo"))


def mostrar_resultado(sucesso, mensagem):
    if sucesso:
        mensagem_ok(mensagem)
    else:
        mensagem_erro(mensagem)


# Ajusta o valor à largura da coluna; números ficam alinhados à direita.
def ajustar(valor, largura):
    texto = str(valor)
    if len(texto) > largura:
        texto = texto[:largura - 3] + "..."
    if isinstance(valor, int):
        return texto.rjust(largura)
    return texto.ljust(largura)


# Nomes de situação recebem a cor correspondente; os demais valores ficam sem cor.
def cor_da_celula(valor):
    for situacao in SITUACOES:
        if valor == NOMES_SITUACAO[situacao]:
            return COR_SITUACAO[situacao]
    return None


def linha_tabela(valores, larguras, negrito):
    texto = "|"
    for posicao in range(len(valores)):
        celula = ajustar(valores[posicao], larguras[posicao])
        if negrito:
            celula = pintar(celula, "negrito")
        else:
            celula = pintar(celula, cor_da_celula(valores[posicao]))
        texto += " " + celula + " |"
    return texto


# Com total_no_fim=True, a última linha é separada por uma divisória.
def mostrar_tabela(cabecalhos, larguras, linhas, total_no_fim=False):
    borda = "+"
    for largura in larguras:
        borda += "-" * (largura + 2) + "+"

    print(borda)
    print(linha_tabela(cabecalhos, larguras, True))
    print(borda)
    for posicao in range(len(linhas)):
        if total_no_fim and posicao == len(linhas) - 1:
            print(borda)
        print(linha_tabela(linhas[posicao], larguras, False))
    print(borda)


def barra_proporcao(percentual, cor):
    tamanho = 24
    cheios = int(round(percentual / 100 * tamanho))
    return pintar("#" * cheios, cor) + pintar("." * (tamanho - cheios), "cinza")


# Listagem pública: não identifica o autor do registro.
def listar_ocorrencias(ocorrencias, mensagem_vazia):
    if len(ocorrencias) == 0:
        print(mensagem_vazia)
        return
    linhas = []
    for ocorrencia in ocorrencias:
        linhas.append([
            ocorrencia["id"],
            NOMES_CATEGORIA[ocorrencia["categoria"]],
            ocorrencia["local"],
            NOMES_SITUACAO[ocorrencia["status"]],
        ])
    mostrar_tabela(["Código", "Categoria", "Local", "Situação"], [6, 14, 37, 14], linhas)
    print("Total listado: " + str(len(ocorrencias)))


# O autor do registro é exibido somente ao gestor.
def mostrar_ocorrencia(estado, ocorrencia, perfil):
    dia_atual = estado["banco"]["dia_atual"]
    situacao = ocorrencia["status"]
    linha()
    print("Código:     " + ocorrencia["id"])
    print("Categoria:  " + NOMES_CATEGORIA[ocorrencia["categoria"]])
    print("Local:      " + ocorrencia["local"] + " (" + BAIRRO[ocorrencia["setor"]]["nome"] + ")")
    print("Descrição:  " + ocorrencia["descricao"])
    print("Situação:   " + pintar(NOMES_SITUACAO[situacao], COR_SITUACAO[situacao])
          + " - " + SIGNIFICADO_SITUACAO[situacao])
    print("Abertura:   dia " + str(ocorrencia["dia_abertura"]))
    if ocorrencia["dia_conclusao"] is not None:
        print("Conclusão:  dia " + str(ocorrencia["dia_conclusao"]))
    print("Acompanhamento: " + str(dias_em_acompanhamento(ocorrencia, dia_atual)) + " dia(s)")
    if esta_atrasada(ocorrencia, dia_atual):
        mensagem_atencao("pendente há mais de " + str(LIMITE_DIAS_ATRASO) + " dias.")
    print("Apoios de outros moradores: " + str(len(ocorrencia["apoios"])))
    if perfil == PERFIL_GESTOR:
        autor = buscar_morador(ocorrencia["autor"])
        print("Registrada por: " + autor["codigo"] + ", " + autor["quarteirao"] + " casa "
              + str(autor["casa"]).zfill(2) + " (visível somente ao gestor)")
    eventos = eventos_da_ocorrencia(estado, ocorrencia["id"])
    print("Histórico:")
    if len(eventos) == 0:
        print("  (sem atualizações)")
    for evento in eventos:
        print(
            "  dia " + str(evento["dia"]) + ": " + NOMES_SITUACAO[evento["de"]] + " -> "
            + NOMES_SITUACAO[evento["para"]] + ". " + evento["observacao"]
        )
    linha()


def mostrar_eventos(eventos):
    if len(eventos) == 0:
        print("Nenhuma atualização registrada.")
        return
    linhas = []
    for evento in eventos:
        linhas.append([
            "dia " + str(evento["dia"]), evento["id"],
            NOMES_SITUACAO[evento["de"]] + " -> " + NOMES_SITUACAO[evento["para"]],
            evento["observacao"],
        ])
    mostrar_tabela(["Quando", "Código", "Mudança", "Observação"], [7, 6, 30, 28], linhas)


def mostrar_matriz(estado, indicadores):
    cabecalhos = ["Categoria", "Aberta", "Em análise", "Em atend.", "Concluída", "Recusada", "Total"]
    larguras = [15, 6, 10, 9, 9, 8, 5]
    linhas = []
    for posicao in range(len(CATEGORIAS)):
        linhas.append(
            [NOMES_CATEGORIA[CATEGORIAS[posicao]]] + estado["matriz"][posicao]
            + [indicadores["por_categoria"][posicao]]
        )
    linhas.append(["Total"] + indicadores["por_situacao"] + [indicadores["total"]])
    mostrar_tabela(cabecalhos, larguras, linhas, total_no_fim=True)
    print("Em atend. = Em atendimento")


def linha_proporcao(nome, quantidade, total, cor):
    percentual = proporcao(quantidade, total)
    print(
        "  " + ajustar(nome, 15) + barra_proporcao(percentual, cor) + " "
        + str(quantidade).rjust(3) + " de " + str(total) + " = " + formatar_numero(percentual).rjust(5) + "%"
    )


# Com completo=True (gestor), exibe também as proporções e os tempos por categoria.
def mostrar_painel(estado, completo):
    indicadores = calcular_indicadores(estado)
    total = indicadores["total"]
    titulo("Painel do " + NOME_BAIRRO + " - dia " + str(estado["banco"]["dia_atual"]))

    print(pintar("Ocorrências por categoria e por situação", "negrito"))
    mostrar_matriz(estado, indicadores)

    print()
    print("Proporção por situação  (fórmula: quantidade / total x 100)")
    for posicao in range(len(SITUACOES)):
        situacao = SITUACOES[posicao]
        linha_proporcao(NOMES_SITUACAO[situacao], indicadores["por_situacao"][posicao], total, COR_SITUACAO[situacao])

    if completo:
        print()
        print("Proporção por categoria  (fórmula: quantidade / total x 100)")
        for posicao in range(len(CATEGORIAS)):
            linha_proporcao(NOMES_CATEGORIA[CATEGORIAS[posicao]], indicadores["por_categoria"][posicao], total, "magenta")

    print()
    print("Pendências (nem concluídas nem recusadas): " + str(indicadores["pendentes"]))
    print("Pendências atrasadas (mais de " + str(LIMITE_DIAS_ATRASO) + " dias): " + str(indicadores["atrasadas"]))
    if indicadores["mais_antiga"] is not None:
        antiga = indicadores["mais_antiga"]
        print("Pendência mais antiga: " + antiga["id"] + ", aberta no dia " + str(antiga["dia_abertura"]) + ".")

    print()
    if indicadores["tempo_medio"] is None:
        print("Tempo médio até a conclusão: ainda não há ocorrências concluídas.")
    else:
        print(
            "Tempo médio até a conclusão: " + formatar_numero(indicadores["tempo_medio"]) + " dia(s)"
            + "  (soma dos dias " + str(indicadores["soma_dias"]) + " / " + str(indicadores["concluidas"])
            + " concluídas)"
        )
        if completo:
            for posicao in range(len(CATEGORIAS)):
                media = indicadores["tempo_medio_categoria"][posicao]
                if media is None:
                    texto = "sem ocorrências concluídas"
                else:
                    texto = formatar_numero(media) + " dia(s)"
                print("  " + ajustar(NOMES_CATEGORIA[CATEGORIAS[posicao]], 15) + texto)

    if completo and indicadores["local_mais_citado"] is not None:
        print()
        print(
            "Local com mais ocorrências: " + indicadores["local_mais_citado"] + " ("
            + str(indicadores["quantidade_local"]) + ")."
        )

    print()
    print(pintar("O que os números sugerem:", "negrito"))
    for frase in interpretar_indicadores(indicadores):
        print("  - " + frase)


def mostrar_hierarquia(estado):
    lados = estado["hierarquia"][NOME_BAIRRO]
    print(NOME_BAIRRO)
    for setor in SETORES:
        print("  " + BAIRRO[setor]["nome"])
        for categoria in CATEGORIAS:
            codigos = lados[setor][categoria]
            if len(codigos) > 0:
                print("    " + ajustar(NOMES_CATEGORIA[categoria], 15) + ", ".join(codigos))


def quando_evento(estado, evento):
    falta = evento["dia"] - estado["banco"]["dia_atual"]
    if falta == 0:
        distancia = "hoje"
    elif falta == 1:
        distancia = "amanhã"
    else:
        distancia = "em " + str(falta) + " dias"
    return "dia " + str(evento["dia"]) + ", " + str(evento["hora"]) + "h (" + distancia + ")"


def mostrar_agenda(estado):
    titulo("Agenda do " + NOME_BAIRRO)
    eventos = proximos_eventos(estado)
    if len(eventos) == 0:
        print("Nenhum evento marcado de hoje em diante.")
        return
    for evento in eventos:
        if evento["cancelado"]:
            situacao = pintar("CANCELADO", "vermelho")
        else:
            situacao = pintar("CONFIRMADO", "verde")
        print(pintar(evento["id"] + " - " + NOMES_TIPO_EVENTO[evento["tipo"]] + ": " + evento["titulo"], "ciano")
              + "  [" + situacao + "]")
        print("    Quando: " + quando_evento(estado, evento))
        print("    Onde:   " + evento["local"] + " (" + BAIRRO[evento["setor"]]["nome"] + ")")
        for trecho in quebrar_texto(evento["descricao"], LARGURA - 12):
            print("    " + trecho)
        print()
    print("Eventos listados: " + str(len(eventos)))


# Exibe, no menu do morador, o próximo evento confirmado.
def aviso_proximo_evento(estado):
    for evento in proximos_eventos(estado):
        if not evento["cancelado"]:
            print("  Próximo evento do bairro: " + pintar(evento["titulo"], "negrito") + ", "
                  + quando_evento(estado, evento) + ", " + evento["local"] + ".")
            print()
            return


# Divide o texto em linhas que cabem na largura, sem cortar palavras.
def quebrar_texto(texto, largura):
    linhas = []
    atual = ""
    for palavra in texto.split():
        if atual == "":
            atual = palavra
        elif len(atual) + 1 + len(palavra) <= largura:
            atual = atual + " " + palavra
        else:
            linhas.append(atual)
            atual = palavra
    if atual != "":
        linhas.append(atual)
    return linhas


def mostrar_regras():
    titulo("Regras de convivência do " + NOME_BAIRRO)
    for posicao in range(len(REGRAS_BAIRRO)):
        tema, itens = REGRAS_BAIRRO[posicao]
        print(pintar(str(posicao + 1).rjust(2) + ". " + tema, "ciano"))
        for item in itens:
            trechos = quebrar_texto(item, LARGURA - 8)
            print("      - " + trechos[0])
            for trecho in trechos[1:]:
                print("        " + trecho)
    print()
    print("Regras de um bairro fictício, elaboradas para a simulação.")


def mostrar_sobre():
    titulo("Sobre o " + NOME_BAIRRO)
    for paragrafo in APRESENTACAO:
        for trecho in quebrar_texto(paragrafo, LARGURA):
            print(trecho)
        print()
    print("Projeto da equipe Tribo Solarian.")
    print()
    print("O mapa tem " + str(len(QUARTEIROES)) + " quarteirões com casas e " + str(len(MORADORES))
          + " moradores fictícios cadastrados.")
    print()
    print("Lados e locais:")
    for setor in SETORES:
        print("  " + pintar(BAIRRO[setor]["nome"], "negrito"))
        for local in BAIRRO[setor]["locais"]:
            print("    - " + local)
    print()
    print("Categorias: " + ", ".join(nomes_de(CATEGORIAS, NOMES_CATEGORIA)) + ".")
    print()
    print("Situações de uma ocorrência:")
    for situacao in SITUACOES:
        print("  " + ajustar(NOMES_SITUACAO[situacao], 15) + SIGNIFICADO_SITUACAO[situacao] + ".")
    print()
    print("Caminho de uma ocorrência:")
    for situacao in SITUACOES:
        proximas = nomes_de(TRANSICOES[situacao], NOMES_SITUACAO)
        if len(proximas) > 0:
            print("  " + NOMES_SITUACAO[situacao] + " -> " + " ou ".join(proximas))
    print()
    print("Privacidade: a ocorrência mostra apenas o local genérico (rua ou espaço coletivo).")
    print("A casa e o nome de quem registrou não aparecem nas listagens do bairro.")


# =============================================================================
# PARTE 11 - Menus do morador e do gestor
# =============================================================================

def escolher_categoria():
    posicao = escolher("Categoria:", nomes_de(CATEGORIAS, NOMES_CATEGORIA))
    if posicao is None:
        return None
    return CATEGORIAS[posicao]


def escolher_situacao():
    posicao = escolher("Situação:", nomes_de(SITUACOES, NOMES_SITUACAO))
    if posicao is None:
        return None
    return SITUACOES[posicao]


def escolher_setor():
    nomes = []
    for setor in SETORES:
        nomes.append(BAIRRO[setor]["nome"])
    posicao = escolher("Lado do bairro (a Avenida Sol Nascente divide os dois):", nomes)
    if posicao is None:
        return None
    return SETORES[posicao]


# Devolve (lado, local) escolhidos, ou None quando o usuário volta.
def escolher_local(pergunta):
    setor = escolher_setor()
    if setor is None:
        return None
    posicao = escolher(pergunta + " no " + BAIRRO[setor]["nome"] + ":", BAIRRO[setor]["locais"])
    if posicao is None:
        return None
    return setor, BAIRRO[setor]["locais"][posicao]


def tela_registrar(estado, morador):
    titulo("Registrar ocorrência")
    categoria = escolher_categoria()
    if categoria is None:
        return
    escolha = escolher_local("Local do problema")
    if escolha is None:
        return
    setor, local = escolha

    # Regra das ocorrências duplicadas: oferece apoiar o registro já existente.
    parecida = procurar_duplicata(estado, categoria, setor, local)
    if parecida is not None:
        print()
        mensagem_atencao("Já existe uma ocorrência pendente desta categoria neste local:")
        print("  " + parecida["id"] + " - " + parecida["descricao"])
        print("  As regras do bairro orientam apoiar a ocorrência existente, em vez de duplicá-la.")
        mostrar_opcao(1, "Apoiar a ocorrência " + parecida["id"])
        mostrar_opcao(2, "Registrar uma nova mesmo assim")
        mostrar_opcao(0, "Cancelar")
        decisao = ler_opcao("Escolha: ", 0, 2)
        if decisao == 0:
            print("Registro cancelado.")
            return
        elif decisao == 1:
            sucesso, mensagem = apoiar_ocorrencia(estado, parecida["id"], morador["codigo"])
            mostrar_resultado(sucesso, mensagem)
            return

    print()
    print("Descreva o problema de forma objetiva. Não informe nomes, telefones nem")
    print("números de casa. Digite 0 para cancelar.")
    descricao = ler_texto("Descrição: ", TAMANHO_MINIMO_DESCRICAO, TAMANHO_MAXIMO_DESCRICAO)
    if descricao is None:
        print("Registro cancelado.")
        return

    sucesso, resultado = cadastrar_ocorrencia(estado, categoria, setor, local, descricao, morador["codigo"])
    if sucesso:
        print()
        mensagem_ok("Ocorrência registrada com o código " + resultado["id"] + ". Utilize este código para acompanhar o andamento.")
        mostrar_ocorrencia(estado, resultado, PERFIL_MORADOR)
    else:
        mensagem_erro("Não foi possível registrar:")
        for problema in resultado:
            print("  - " + problema)


# Devolve a ocorrência consultada, ou None se o usuário voltar ou o código não existir.
def tela_consultar_codigo(estado, perfil):
    codigo = ler_codigo()
    if codigo is None:
        return None
    ocorrencia = buscar_por_id(estado, codigo)
    if ocorrencia is None:
        mensagem_erro("Ocorrência " + codigo + " não encontrada. Verifique o código informado.")
        return None
    mostrar_ocorrencia(estado, ocorrencia, perfil)
    return ocorrencia


# O gestor dispõe de três opções adicionais de consulta.
def tela_filtros(estado, perfil):
    opcoes = ["Todas", "Por categoria", "Por situação", "Por lado do bairro", "Somente pendentes"]
    if perfil == PERFIL_GESTOR:
        opcoes.append("Pendentes atrasadas")
        opcoes.append("Pendentes da mais antiga para a mais recente")
        opcoes.append("Pendentes da mais apoiada para a menos apoiada")
    escolha = escolher("Ocorrências do bairro - o que deseja ver?", opcoes)
    if escolha is None:
        return
    if escolha == 0:
        encontradas = filtrar(estado)
    elif escolha == 1:
        categoria = escolher_categoria()
        if categoria is None:
            return
        encontradas = filtrar(estado, categoria=categoria)
    elif escolha == 2:
        situacao = escolher_situacao()
        if situacao is None:
            return
        encontradas = filtrar(estado, situacao=situacao)
    elif escolha == 3:
        setor = escolher_setor()
        if setor is None:
            return
        encontradas = filtrar(estado, setor=setor)
    elif escolha == 4:
        encontradas = filtrar(estado, somente_pendentes=True)
    elif escolha == 5:
        encontradas = filtrar(estado, somente_atrasadas=True)
    elif escolha == 6:
        encontradas = ordenar_por_antiguidade(filtrar(estado, somente_pendentes=True))
    else:
        encontradas = ordenar_por_apoios(filtrar(estado, somente_pendentes=True))
    print()
    listar_ocorrencias(encontradas, "Nenhuma ocorrência atende a este filtro.")


# O morador escolhe o lado do bairro e, em seguida, o próprio cadastro.
def identificar_morador():
    setor = escolher_setor()
    if setor is None:
        return None
    do_setor = []
    opcoes = []
    for morador in MORADORES:
        if morador["setor"] == setor:
            do_setor.append(morador)
            opcoes.append(
                morador["codigo"] + " - " + morador["nome"] + " (" + morador["quarteirao"]
                + ", casa " + str(morador["casa"]).zfill(2) + ")"
            )
    posicao = escolher("Identificação do morador (cadastro fictício do " + BAIRRO[setor]["nome"] + ")", opcoes)
    if posicao is None:
        return None
    return do_setor[posicao]


def tela_apoiar(estado, morador):
    titulo("Apoiar uma ocorrência já registrada")
    print("Ocorrências pendentes do bairro:")
    listar_ocorrencias(filtrar(estado, somente_pendentes=True), "Não há ocorrências pendentes.")
    codigo = ler_codigo()
    if codigo is None:
        return
    sucesso, mensagem = apoiar_ocorrencia(estado, codigo, morador["codigo"])
    mostrar_resultado(sucesso, mensagem)


def menu_morador(estado):
    morador = identificar_morador()
    if morador is None:
        return
    while True:
        cabecalho(estado, morador["nome"] + " (" + morador["codigo"] + ", morador fictício)")
        aviso_proximo_evento(estado)
        mostrar_opcao(1, "Registrar ocorrência")
        mostrar_opcao(2, "Minhas ocorrências")
        mostrar_opcao(3, "Consultar ocorrência pelo código")
        mostrar_opcao(4, "Ocorrências do bairro")
        mostrar_opcao(5, "Apoiar uma ocorrência já registrada")
        mostrar_opcao(6, "Painel do bairro")
        mostrar_opcao(7, "Regras de convivência do bairro")
        mostrar_opcao(8, "Agenda do bairro (festas, encontros e reuniões)")
        mostrar_opcao(0, "Sair do perfil")
        opcao = ler_opcao("Escolha: ", 0, 8)
        if opcao == 0:
            return
        elif opcao == 1:
            tela_registrar(estado, morador)
        elif opcao == 2:
            titulo("Minhas ocorrências")
            listar_ocorrencias(filtrar(estado, autor=morador["codigo"]), "Não há ocorrências registradas por este morador.")
        elif opcao == 3:
            tela_consultar_codigo(estado, PERFIL_MORADOR)
        elif opcao == 4:
            tela_filtros(estado, PERFIL_MORADOR)
        elif opcao == 5:
            tela_apoiar(estado, morador)
        elif opcao == 6:
            mostrar_painel(estado, False)
        elif opcao == 7:
            mostrar_regras()
        else:
            mostrar_agenda(estado)
        pausar()


def tela_criar_evento(estado):
    titulo("Novo evento do bairro")
    posicao = escolher("Tipo de evento:", nomes_de(TIPOS_EVENTO, NOMES_TIPO_EVENTO))
    if posicao is None:
        return
    tipo = TIPOS_EVENTO[posicao]
    titulo_evento = ler_texto("Título do evento (0 para cancelar): ", TAMANHO_MINIMO_TITULO, TAMANHO_MAXIMO_TITULO)
    if titulo_evento is None:
        return
    escolha = escolher_local("Local do evento")
    if escolha is None:
        return
    setor, local = escolha
    dia_atual = estado["banco"]["dia_atual"]
    dia = ler_opcao("Dia simulado do evento (hoje é " + str(dia_atual) + "; de " + str(dia_atual) + " a "
                    + str(dia_atual + 60) + "): ", dia_atual, dia_atual + 60)
    print("O bairro tem horário de silêncio das " + str(HORA_INICIO_SILENCIO) + "h às " + str(HORA_FIM_SILENCIO) + "h.")
    hora = ler_opcao("Hora de início (0 a 23): ", 0, 23)
    descricao = ler_texto("Descrição para os moradores (0 para cancelar): ", TAMANHO_MINIMO_DESCRICAO,
                          TAMANHO_MAXIMO_DESCRICAO)
    if descricao is None:
        return
    sucesso, resultado = criar_evento_bairro(estado, PERFIL_GESTOR, tipo, titulo_evento, setor, local, dia, hora, descricao)
    if sucesso:
        mensagem_ok("Evento " + resultado["id"] + " criado. Ele já consta na agenda dos moradores.")
    else:
        mensagem_erro(resultado)


def tela_cancelar_evento(estado):
    mostrar_agenda(estado)
    ativos = []
    nomes_ativos = []
    for evento in proximos_eventos(estado):
        if not evento["cancelado"]:
            ativos.append(evento)
            nomes_ativos.append(evento["id"] + " - " + evento["titulo"])
    if len(ativos) == 0:
        print("Não há evento confirmado para cancelar.")
        return
    posicao = escolher("Qual evento cancelar?", nomes_ativos)
    if posicao is None:
        return
    if confirmar("Cancelar o evento " + ativos[posicao]["id"] + "?"):
        sucesso, mensagem = cancelar_evento_bairro(estado, PERFIL_GESTOR, ativos[posicao]["id"])
        mostrar_resultado(sucesso, mensagem)


def tela_agenda_gestor(estado):
    opcoes = ["Ver a agenda", "Criar evento (festa, encontro, reunião ou mutirão)", "Cancelar um evento"]
    escolha = escolher("Agenda do bairro:", opcoes)
    if escolha == 0:
        mostrar_agenda(estado)
    elif escolha == 1:
        tela_criar_evento(estado)
    elif escolha == 2:
        tela_cancelar_evento(estado)


def tela_triagem(estado):
    titulo("Triagem - fila de ocorrências não examinadas")
    fila = estado["banco"]["fila_triagem"]
    if len(fila) == 0:
        print("A fila está vazia: todas as ocorrências abertas já foram examinadas.")
        return
    print("Na fila, por ordem de registro: " + ", ".join(fila))
    ocorrencia = estado["indice"][fila[0]]
    print("Próxima da fila:")
    mostrar_ocorrencia(estado, ocorrencia, PERFIL_GESTOR)
    mostrar_opcao(1, "Colocar em análise")
    mostrar_opcao(2, "Examinar depois (vai para o fim da fila)")
    mostrar_opcao(0, "Voltar sem alterar")
    opcao = ler_opcao("Escolha: ", 0, 2)
    if opcao == 1:
        observacao = ler_texto("Observação (0 para deixar em branco): ", 0, TAMANHO_MAXIMO_DESCRICAO)
        if observacao is None or observacao == "":
            observacao = "Triagem realizada."
        sucesso, mensagem = atualizar_situacao(estado, PERFIL_GESTOR, ocorrencia["id"], "EM_ANALISE", observacao)
        mostrar_resultado(sucesso, mensagem)
    elif opcao == 2:
        adiar_triagem(estado)
        print(ocorrencia["id"] + " foi para o fim da fila.")


# Oferece somente as situações permitidas a partir da situação atual.
def tela_atualizar(estado):
    titulo("Atualizar situação")
    ocorrencia = tela_consultar_codigo(estado, PERFIL_GESTOR)
    if ocorrencia is None:
        return
    proximas = TRANSICOES[ocorrencia["status"]]
    if len(proximas) == 0:
        print("Ocorrência encerrada: não aceita novas alterações.")
        return
    posicao = escolher("Nova situação:", nomes_de(proximas, NOMES_SITUACAO))
    if posicao is None:
        return
    observacao = ler_texto("Observação (0 para deixar em branco): ", 0, TAMANHO_MAXIMO_DESCRICAO)
    if observacao is None:
        observacao = ""
    sucesso, mensagem = atualizar_situacao(estado, PERFIL_GESTOR, ocorrencia["id"], proximas[posicao], observacao)
    mostrar_resultado(sucesso, mensagem)


# Percorre a pilha do topo para a base e exibe as oito atualizações mais recentes.
def tela_ultimas_atualizacoes(estado):
    titulo("Últimas atualizações (pilha: a mais recente primeiro)")
    pilha = estado["pilha"]
    recentes = []
    posicao = len(pilha) - 1
    while posicao >= 0 and len(recentes) < 8:
        recentes.append(pilha[posicao])
        posicao -= 1
    mostrar_eventos(recentes)
    print("Atualizações registradas no total: " + str(len(pilha)))
    if len(pilha) > 0 and confirmar("Desfazer a atualização mais recente?"):
        sucesso, mensagem = desfazer_ultima(estado, PERFIL_GESTOR)
        mostrar_resultado(sucesso, mensagem)


def tela_rejeitados(estado):
    titulo("Registros com problema")
    rejeitados = estado["banco"]["rejeitados"]
    if len(rejeitados) == 0:
        print("Nenhum registro foi rejeitado.")
        return
    print("Os registros abaixo não integram o painel por não atenderem às regras de validação:")
    for item in rejeitados:
        registro = item["registro"]
        print()
        print("  Registro " + registro["id"])
        for campo in ["categoria", "local", "status", "descricao"]:
            valor = registro[campo]
            if campo_vazio(valor):
                valor = "(vazio)"
            print("    " + ajustar(campo + ":", 11) + valor)
        print("    Motivo da rejeição:")
        for problema in item["problemas"]:
            print("    - " + problema)


def tela_dados(estado):
    opcoes = [
        "Salvar agora",
        "Restaurar a base inicial do bairro (apaga as alterações)",
        "Executar as conferências do sistema",
        "Ver a organização bairro -> lado -> categoria",
    ]
    escolha = escolher("Dados do sistema:", opcoes)
    if escolha == 0:
        salvar_banco(estado)
        mensagem_ok("Banco gravado em " + estado["caminho"])
    elif escolha == 1:
        if confirmar("Confirma a restauração? Todas as alterações realizadas serão descartadas."):
            estado["banco"] = criar_banco_inicial()
            reconstruir_estruturas(estado)
            salvar_banco(estado)
            mensagem_ok("Base inicial restaurada.")
        else:
            print("Operação cancelada. Nenhum dado foi alterado.")
    elif escolha == 2:
        executar_conferencias()
    elif escolha == 3:
        titulo("Organização hierárquica")
        mostrar_hierarquia(estado)


def menu_gestor(estado):
    while True:
        cabecalho(estado, "Gestor do bairro")
        print("  Na fila de triagem: " + str(len(estado["banco"]["fila_triagem"])) + " ocorrência(s)")
        print()
        mostrar_opcao(1, "Triagem: examinar a próxima da fila")
        mostrar_opcao(2, "Atualizar a situação de uma ocorrência")
        mostrar_opcao(3, "Últimas atualizações e desfazer")
        mostrar_opcao(4, "Consultar ocorrência pelo código")
        mostrar_opcao(5, "Ocorrências do bairro (filtros e ordenação)")
        mostrar_opcao(6, "Painel de indicadores")
        mostrar_opcao(7, "Registros com problema")
        mostrar_opcao(8, "Avançar o dia simulado")
        mostrar_opcao(9, "Dados do sistema")
        mostrar_opcao(10, "Agenda do bairro: ver, criar e cancelar eventos")
        mostrar_opcao(0, "Sair do perfil")
        opcao = ler_opcao("Escolha: ", 0, 10)
        if opcao == 0:
            return
        elif opcao == 1:
            tela_triagem(estado)
        elif opcao == 2:
            tela_atualizar(estado)
        elif opcao == 3:
            tela_ultimas_atualizacoes(estado)
        elif opcao == 4:
            tela_consultar_codigo(estado, PERFIL_GESTOR)
        elif opcao == 5:
            tela_filtros(estado, PERFIL_GESTOR)
        elif opcao == 6:
            mostrar_painel(estado, True)
        elif opcao == 7:
            tela_rejeitados(estado)
        elif opcao == 8:
            dias = ler_opcao("Avançar quantos dias? (1 a 30; 0 para voltar): ", 0, 30)
            if dias > 0:
                avancar_dia(estado, dias)
                mensagem_ok("Agora é o dia " + str(estado["banco"]["dia_atual"]) + ".")
        elif opcao == 9:
            tela_dados(estado)
        else:
            tela_agenda_gestor(estado)
        pausar()


def menu_principal(estado):
    while True:
        cabecalho(estado, "nenhum (escolha abaixo)")
        print("  " + RESUMO_PROJETO + ".")
        print()
        mostrar_opcao(1, "Entrar como morador")
        mostrar_opcao(2, "Entrar como gestor do bairro")
        mostrar_opcao(3, "Sobre o bairro, as categorias e as situações")
        mostrar_opcao(4, "Regras de convivência do bairro")
        if CONFIG["cores"]:
            mostrar_opcao(5, "Desativar as cores")
        else:
            mostrar_opcao(5, "Ativar as cores")
        mostrar_opcao(0, "Encerrar")
        opcao = ler_opcao("Escolha: ", 0, 5)
        if opcao == 0:
            print("Sistema encerrado. Os dados foram gravados.")
            return
        elif opcao == 1:
            menu_morador(estado)
        elif opcao == 2:
            if autenticar_gestor():
                menu_gestor(estado)
            else:
                pausar()
        elif opcao == 3:
            mostrar_sobre()
            pausar()
        elif opcao == 4:
            mostrar_regras()
            pausar()
        else:
            CONFIG["cores"] = not CONFIG["cores"]


# =============================================================================
# PARTE 12 - Conferências e ponto de entrada
# As conferências operam sobre uma cópia em memória da base inicial e não alteram o banco.
# =============================================================================

# Compara o valor obtido com o esperado e registra o resultado na lista.
def conferir(descricao, obtido, esperado, resultados):
    correto = obtido == esperado
    resultados.append(correto)
    if correto:
        print(pintar("[OK]     ", "verde") + descricao)
    else:
        print(pintar("[FALHOU] " + descricao + " | obtido: " + str(obtido) + " | esperado: " + str(esperado), "vermelho"))


def executar_conferencias():
    titulo("Conferências do sistema")
    r = []
    estado = novo_estado(criar_banco_inicial(), None)
    banco = estado["banco"]

    print("Carga e validação")
    conferir("12 ocorrências válidas na lista", len(banco["ocorrencias"]), 12, r)
    conferir("3 registros defeituosos separados", len(banco["rejeitados"]), 3, r)
    conferir("defeito 1: categoria ausente", banco["rejeitados"][0]["problemas"], ["campo obrigatório ausente: categoria"], r)
    conferir("defeito 2: situação desconhecida", banco["rejeitados"][1]["problemas"], ["situação desconhecida: RESOLVENDO"], r)
    conferir("defeito 3: código repetido", banco["rejeitados"][2]["problemas"], ["código repetido: OC-003"], r)
    conferir("17 atualizações no histórico", len(banco["historico"]), 17, r)
    conferir("próximo código livre é o 15", banco["proximo_numero"], 15, r)

    print("Bairro, moradores e regras")
    conferir("28 moradores fictícios cadastrados", len(MORADORES), 28, r)
    casas_validas = 0
    for morador in MORADORES:
        if 1 <= morador["casa"] <= casas_do_quarteirao(morador["quarteirao"]):
            casas_validas += 1
    conferir("toda casa de morador existe no mapa", casas_validas, 28, r)
    conferir("morador USR009 fica no Lado Oeste", buscar_morador("USR009")["setor"], "OESTE", r)
    conferir("17 regras de convivência", len(REGRAS_BAIRRO), 17, r)
    maior_trecho = 0
    for trecho in quebrar_texto(REGRAS_BAIRRO[0][1][0], 40):
        if len(trecho) > maior_trecho:
            maior_trecho = len(trecho)
    conferir("quebra de texto respeita a largura", maior_trecho <= 40, True, r)

    print("Estruturas")
    conferir("dicionário alcança OC-007", buscar_por_id(estado, "OC-007")["local"], "Escola Municipal Caminhos do Sol", r)
    conferir("código inexistente devolve None", buscar_por_id(estado, "OC-999"), None, r)
    conferir("fila de triagem por ordem de registro", banco["fila_triagem"], ["OC-009", "OC-010", "OC-011", "OC-012"], r)
    conferir("topo da pilha é a atualização mais recente", estado["pilha"][-1]["id"], "OC-008", r)
    conferir("hierarquia Lado Leste > Acessibilidade", estado["hierarquia"][NOME_BAIRRO]["LESTE"]["ACESSIBILIDADE"], ["OC-003", "OC-011"], r)
    conferir("matriz: linha de Conservação", estado["matriz"][3], [1, 0, 2, 0, 0], r)
    conferir("matriz: linha de Limpeza", estado["matriz"][2], [1, 0, 0, 1, 1], r)

    print("Busca, filtros e ordenação")
    invertida = list(reversed(banco["ocorrencias"]))
    ordenadas = ordenar_por_codigo(invertida)
    conferir("ordenação por código", codigos_de(ordenadas)[:3], ["OC-001", "OC-002", "OC-003"], r)
    conferir("ordenação não altera a lista original", invertida[0]["id"], "OC-012", r)
    conferir("busca binária encontra o mesmo que o dicionário", busca_binaria_por_id(ordenadas, "OC-010") is buscar_por_id(estado, "OC-010"), True, r)
    conferir("busca binária: código inexistente", busca_binaria_por_id(ordenadas, "OC-500"), None, r)
    conferir("filtro: abertas de iluminação", codigos_de(filtrar(estado, categoria="ILUMINACAO", situacao="ABERTA")), ["OC-009"], r)
    conferir("filtro: pendentes", len(filtrar(estado, somente_pendentes=True)), 8, r)
    conferir("filtro: atrasadas", codigos_de(filtrar(estado, somente_atrasadas=True)), ["OC-004", "OC-005", "OC-007"], r)
    conferir("ordenação: mais antiga primeiro", codigos_de(ordenar_por_antiguidade(invertida))[:3], ["OC-001", "OC-002", "OC-003"], r)

    print("Indicadores")
    ind = calcular_indicadores(estado)
    conferir("total de ocorrências", ind["total"], 12, r)
    conferir("totais por categoria", ind["por_categoria"], [3, 3, 3, 3], r)
    conferir("totais por situação", ind["por_situacao"], [4, 2, 2, 3, 1], r)
    conferir("soma das situações = total", sum(ind["por_situacao"]), ind["total"], r)
    conferir("pendências", ind["pendentes"], 8, r)
    conferir("pendências atrasadas", ind["atrasadas"], 3, r)
    conferir("tempo médio até a conclusão = (4 + 7 + 4) / 3", ind["tempo_medio"], 5.0, r)
    conferir("tempo médio por categoria", ind["tempo_medio_categoria"], [4.0, 4.0, 7.0, None], r)
    conferir("pendência mais antiga", ind["mais_antiga"]["id"], "OC-004", r)
    conferir("local mais citado é a Praça dos Encontros", ind["local_mais_citado"], "Praça dos Encontros", r)
    conferir("proporção de abertas", formatar_numero(proporcao(4, 12)), "33,3", r)
    conferir("proporção com total zero", proporcao(1, 0), 0.0, r)

    print("Regras de atualização")
    conferir("morador não altera situação", atualizar_situacao(estado, PERFIL_MORADOR, "OC-009", "EM_ANALISE", "")[0], False, r)
    conferir("código inexistente é recusado", atualizar_situacao(estado, PERFIL_GESTOR, "OC-999", "EM_ANALISE", "")[0], False, r)
    conferir("situação desconhecida é recusada", atualizar_situacao(estado, PERFIL_GESTOR, "OC-009", "RESOLVIDA", "")[0], False, r)
    conferir("não pula de Aberta para Concluída", atualizar_situacao(estado, PERFIL_GESTOR, "OC-009", "CONCLUIDA", "")[0], False, r)
    conferir("ocorrência concluída não muda mais", atualizar_situacao(estado, PERFIL_GESTOR, "OC-001", "EM_ANALISE", "")[0], False, r)
    conferir("Aberta -> Em análise é aceita", atualizar_situacao(estado, PERFIL_GESTOR, "OC-009", "EM_ANALISE", "teste")[0], True, r)
    conferir("a ocorrência saiu da fila", banco["fila_triagem"], ["OC-010", "OC-011", "OC-012"], r)
    conferir("evento empilhado", estado["pilha"][-1]["id"], "OC-009", r)
    conferir("matriz atualizada (Iluminação)", estado["matriz"][0], [0, 2, 0, 1, 0], r)
    conferir("desfazer devolve a situação anterior", desfazer_ultima(estado, PERFIL_GESTOR)[0], True, r)
    conferir("situação restaurada", buscar_por_id(estado, "OC-009")["status"], "ABERTA", r)
    conferir("voltou para o início da fila", banco["fila_triagem"][0], "OC-009", r)
    conferir("histórico voltou a 17 eventos", len(banco["historico"]), 17, r)
    adiar_triagem(estado)
    conferir("adiar manda a primeira para o fim da fila", banco["fila_triagem"], ["OC-010", "OC-011", "OC-012", "OC-009"], r)

    print("Cadastro")
    sucesso, nova = cadastrar_ocorrencia(estado, "LIMPEZA", "OESTE", "Rua das Andorinhas", "Folhas acumuladas na calçada.", "USR006")
    conferir("cadastro válido é aceito", sucesso, True, r)
    conferir("código gerado em sequência", nova["id"], "OC-015", r)
    conferir("nova ocorrência entra no fim da fila", banco["fila_triagem"][-1], "OC-015", r)
    conferir("cadastro sem categoria é recusado", cadastrar_ocorrencia(estado, "", "OESTE", "Rua das Andorinhas", "Sem categoria.", "USR006")[0], False, r)
    conferir("categoria desconhecida é recusada", cadastrar_ocorrencia(estado, "TRANSITO", "OESTE", "Rua das Andorinhas", "Semáforo quebrado.", "USR006")[0], False, r)
    conferir("local de outro lado é recusado", cadastrar_ocorrencia(estado, "LIMPEZA", "OESTE", "Praça dos Encontros", "Local trocado.", "USR006")[0], False, r)
    conferir("descrição em branco é recusada", cadastrar_ocorrencia(estado, "LIMPEZA", "OESTE", "Rua das Andorinhas", "   ", "USR006")[0], False, r)
    conferir("duplicata pendente é percebida", procurar_duplicata(estado, "LIMPEZA", "OESTE", "Rua das Andorinhas")["id"], "OC-015", r)
    conferir("local sem pendência não acusa duplicata", procurar_duplicata(estado, "ILUMINACAO", "LESTE", "Rua das Estrelas"), None, r)

    print("Apoios")
    conferir("apoio de outro morador é aceito", apoiar_ocorrencia(estado, "OC-015", "USR017")[0], True, r)
    conferir("o mesmo morador não apoia duas vezes", apoiar_ocorrencia(estado, "OC-015", "USR017")[0], False, r)
    conferir("o autor não apoia a própria ocorrência", apoiar_ocorrencia(estado, "OC-015", "USR006")[0], False, r)
    conferir("ocorrência encerrada não recebe apoio", apoiar_ocorrencia(estado, "OC-001", "USR017")[0], False, r)
    conferir("apoio em código inexistente é recusado", apoiar_ocorrencia(estado, "OC-999", "USR017")[0], False, r)
    conferir("a mais apoiada vem primeiro na ordenação", ordenar_por_apoios(filtrar(estado, somente_pendentes=True))[0]["id"], "OC-015", r)

    print("Entrada de dados e senha")
    conferir("código '14' vira OC-014", normalizar_id("14"), "OC-014", r)
    conferir("código 'oc-7' vira OC-007", normalizar_id("oc-7"), "OC-007", r)
    conferir("código com letras é inválido", normalizar_id("abc"), None, r)
    conferir("texto: remove espaços repetidos", limpar_texto("  poste   apagado  "), "poste apagado", r)
    conferir("senha correta é aceita", senha_gestor_correta("12345"), True, r)
    conferir("senha errada é recusada", senha_gestor_correta("123456"), False, r)
    conferir("o código armazena o resumo de 64 caracteres, e não a senha", len(RESUMO_SENHA_GESTOR), 64, r)

    print("Agenda do bairro")
    conferir("morador não cria evento", criar_evento_bairro(estado, PERFIL_MORADOR, "FESTA", "Festa junina", "LESTE", "Praça dos Encontros", 15, 18, "Confraternização.")[0], False, r)
    conferir("tipo desconhecido é recusado", criar_evento_bairro(estado, PERFIL_GESTOR, "SHOW", "Show", "LESTE", "Praça dos Encontros", 15, 18, "Música ao vivo.")[0], False, r)
    conferir("evento em dia passado é recusado", criar_evento_bairro(estado, PERFIL_GESTOR, "FESTA", "Festa junina", "LESTE", "Praça dos Encontros", 3, 18, "Confraternização.")[0], False, r)
    conferir("evento às 23h fere o horário de silêncio", criar_evento_bairro(estado, PERFIL_GESTOR, "FESTA", "Festa junina", "LESTE", "Praça dos Encontros", 15, 23, "Confraternização.")[0], False, r)
    conferir("evento às 7h fere o horário de silêncio", criar_evento_bairro(estado, PERFIL_GESTOR, "MUTIRAO", "Mutirão", "LESTE", "Praça dos Encontros", 15, 7, "Limpeza da praça.")[0], False, r)
    conferir("local de outro lado é recusado", criar_evento_bairro(estado, PERFIL_GESTOR, "FESTA", "Festa junina", "OESTE", "Praça dos Encontros", 15, 18, "Confraternização.")[0], False, r)
    sucesso, festa = criar_evento_bairro(estado, PERFIL_GESTOR, "FESTA", "Festa junina", "LESTE", "Praça dos Encontros", 20, 18, "Confraternização.")
    conferir("festa válida é criada", sucesso, True, r)
    conferir("código do evento em sequência", festa["id"], "EV-001", r)
    criar_evento_bairro(estado, PERFIL_GESTOR, "REUNIAO", "Reunião de moradores", "OESTE", "Escola Municipal Caminhos do Sol", 14, 19, "Pauta: iluminação.")
    conferir("agenda em ordem de data", codigos_de(proximos_eventos(estado)), ["EV-002", "EV-001"], r)
    conferir("morador não cancela evento", cancelar_evento_bairro(estado, PERFIL_MORADOR, "EV-001")[0], False, r)
    conferir("gestor cancela evento", cancelar_evento_bairro(estado, PERFIL_GESTOR, "EV-001")[0], True, r)
    conferir("evento cancelado permanece na agenda, marcado", buscar_evento_bairro(estado, "EV-001")["cancelado"], True, r)
    conferir("cancelar duas vezes é recusado", cancelar_evento_bairro(estado, PERFIL_GESTOR, "EV-001")[0], False, r)

    print("Banco em JSON")
    copia = json.loads(json.dumps(banco))
    conferir("gravar e ler devolve os mesmos dados", copia, banco, r)

    aprovadas = r.count(True)
    print()
    linha()
    print("Conferências aprovadas: " + str(aprovadas) + " de " + str(len(r)))
    linha()
    return aprovadas == len(r)


def principal():
    if os.name == "nt":
        os.system("")  # ativa a interpretação das cores no terminal do Windows

    caminho = caminho_banco()
    estado = novo_estado(carregar_banco(caminho), caminho)
    salvar_banco(estado)
    try:
        menu_principal(estado)
    except (EOFError, KeyboardInterrupt):
        print()
        print("Entrada encerrada. Os dados já estavam gravados.")


if __name__ == "__main__":
    principal()
