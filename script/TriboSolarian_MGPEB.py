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


# TODO: chamar o menu principal quando o código estiver implementado
