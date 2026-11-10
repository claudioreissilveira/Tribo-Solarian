# 🚀 MISSÃO AURORA SIGER | MGPEB SLR-33 🌌

# Colônia em Marte — Fase 3

Equipe Tribo Solarian · versão 0.1

Sistema integrado em Python que acompanha uma colônia de 50 pessoas em Marte, sempre
olhando um período de **24 horas**. Ele organiza os dados da colônia em uma hierarquia,
calcula a geração solar e eólica e o consumo, avalia oxigênio, alimentos e clima, estima
a potência eólica por regressão linear e transforma tudo em decisões claras: alertas,
reduções de consumo e recomendações ordenadas por urgência.

**Repositório público:** <https://github.com/claudioreissilveira/Tribo-Solarian/tree/3-Colonia>

## Como usar

```
python script/TriboSolarian_Colonia.py
```

Só usa Python padrão (biblioteca `math`). O menu mostra os cinco cenários (1 a 5), o modo
PERSONALIZADO (6) e as conferências de todos os blocos (7). No modo personalizado, escolha
o módulo, digite os novos valores (Enter mantém o atual) e use `A` para avaliar. Números
aceitam vírgula (`0,8`). Valor inválido ou fora da faixa é recusado e o programa pergunta
de novo.

Fluxo: **entrada** (cenário ou valores digitados) → **processamento** (balanços,
classificações, regressão, regras) → **saída** (diagnóstico, recomendações e riscos).

## Exemplo de entrada e saída

Entrada: opção `3` (TEMPESTADE: vento 22 m/s, poeira τ 4,5, fator solar 0,10, eólica
desligada). Saída resumida:

```
[1] Energia
Geração total: 96.00 kWh
Consumo total: 864.00 kWh
Saldo:         -768.00 kWh
Energia:       VERMELHO - déficit no período; há demanda não atendida no balanço

[1b] Operações complementares (Bloco 4)
Economia possível: 180.000 kWh
Economia proposta: 180.000 kWh
Déficit remanescente: 588.000 kWh. A economia não basta; é necessário recompor a geração.

[2] Previsão eólica (regressão linear, Bloco 2)
Aviso: vento de 22 m/s fora da faixa de ajuste (6 a 10 m/s): sem previsão numérica

[5] Riscos e recomendações (do mais urgente ao menos urgente)
1. [CRITICO] Energia: ALERTA: ativar modo economia - todas as complementares no mínimo protegido
   Dado: saldo -768.00 kWh, cobertura 0.1111
   Restrição: déficit de 588.00 kWh permanece com as cargas essenciais protegidas
4. [ALTO] Ambiente: Suspender atividades externas e mobilidade não essencial
   Dado: vento 22 m/s (VERMELHO), poeira tau 4.5 (VERMELHO)
```

Os resultados completos dos cinco cenários estão na pasta [testes/](testes/).

## Como os dados estão organizados

**Base comum.** Todos os módulos usam a mesma população (50 pessoas) e o mesmo período
(24 horas terrestres). A unidade de cada valor fica no nome do campo: `pot_solar_kw` está
em quilowatts, `estoque_kg` em quilos, `vento_ms` em metros por segundo.

**Hierarquia dos sistemas.** 

```
colonia
├── contexto        cenário, população, período
├── energia
│   ├── solar       potência, horas, fator solar
│   ├── eolica      vento, disponibilidade, pares vento x potência
│   └── auxiliares  carga de controle e distribuição
├── suporte_vida
│   ├── oxigenio    taxa por pessoa, estoque, reposição, carga elétrica
│   └── alimentos   taxa por pessoa, estoque, entrada, carga elétrica
├── operacoes       lista com as 4 operações complementares
├── clima           poeira, temperatura (o vento é lido da eólica)
└── riscos          lista de riscos gerada na avaliação
```

Usamos três estruturas:
- **dicionário** para guardar atributos com nome (`"pot_solar_kw": 120`);
- **dicionário dentro de dicionário** para sistemas e subsistemas (energia → solar);
- **lista** para dados que se repetem (as 4 operações e os 5 pares vento × potência).

**Cenários.** Os cinco cenários (NORMAL, BAIXA_GERACAO, TEMPESTADE, SUPORTE_VIDA_EM_ALERTA,
MULTIPLAS_RESTRICOES) ficam no dicionário `CENARIOS`, só com as entradas da seção 7 do apoio.
`aplicar_cenario(nome)` cria uma colônia nova e cadastra essas entradas. O modo
PERSONALIZADO começa com os valores de NORMAL e permite editar um módulo por vez.

**Vento em um lugar só.** A velocidade do vento fica em `energia → eolica → vento_ms`.
O clima lê o vento de lá, então a geração eólica e a classificação do clima usam sempre
o mesmo valor.

**Cargas sem repetição.** Cada carga elétrica está guardada em um lugar só: auxiliares em
`energia`, suporte de oxigênio e de alimentos em `suporte_vida`, e as outras quatro em
`operacoes`. A função `listar_cargas` junta numa lista as cargas já cadastradas, então nenhuma é
somada duas vezes.

## Como a energia é calculada

Regra básica: **energia (kWh) = potência (kW) × tempo (h)**.

**1. Geração solar** — `geracao_solar(pot_solar_kw, horas_solares, fator_solar)`

```
energia solar = potência × horas equivalentes × fator solar
NORMAL:  120 × 8 × 1,00 = 960 kWh
```

O fator solar vai de 0 a 1 e já inclui a perda por poeira do cenário, então é usado uma
vez só.

**2. Consumo** — `energia_kwh(potencia_kw, horas)`

Cada carga consome `potência × 24 h`. Nos exemplos do Bloco 1, os consumos de referência
da seção 5 do apoio entram como dados de entrada:

```
normal: (2 + 12 + 9 + 4 + 4 + 3 + 2) kW × 24 h = 36 × 24 = 864 kWh
```

**3. Balanço** — `balanco_energetico(geracoes, consumos)`

Recebe dois dicionários: as gerações (`{"solar": 960}`) e os consumos. Calcula:

- **saldo** = geração total − consumo total
- **cobertura** = geração total ÷ consumo total
- **classificação**:
  - VERDE: cobertura ≥ 1,10 (sobra pelo menos 10%)
  - AMARELO: cobertura entre 1,00 e 1,10 (atende, mas com pouca folga)
  - VERMELHO: cobertura < 1,00 (falta energia)
- se o consumo for **zero**, não dá para dividir: a cobertura fica `None` e a
  classificação fica "NAO SE APLICA".

O saldo sempre aparece junto da cor, porque é possível sobrar energia e mesmo assim
estar no Amarelo (ex.: 900 kWh gerados para 864 consumidos).

Um detalhe: o computador calcula 950,4 ÷ 864 como 1,0999999999 em vez de 1,10. Por isso a
cobertura é arredondada com `round(cobertura, 6)` antes de comparar com os limites.

**Resultados conferidos com o documento de apoio** (só energia solar):

| Cenário | Geração | Consumo | Saldo | Cobertura | Classe |
|---|---:|---:|---:|---:|---|
| NORMAL | 960 | 864 | +96 | 1,1111 | VERDE |
| BAIXA_GERACAO | 768 | 864 | −96 | 0,8889 | VERMELHO |
| TEMPESTADE | 96 | 864 | −768 | 0,1111 | VERMELHO |

## Validação das entradas

A função `numero_valido` confere cada valor antes de calcular. Ela recusa texto
(`"120"`), `None`, `True`/`False`, NaN, infinito e números fora do intervalo permitido.
Quando uma entrada é inválida, as funções de cálculo devolvem `None` em vez de um número
errado. Regras:
- potências e energias não podem ser negativas;
- fator solar entre 0 e 1;
- horas entre 0 e 24.

## Testes

A função `exemplos_bloco1()`, na Parte 9 do script, confere: base comum, geração
solar, saldo, classificações (inclusive os limites exatos 1,10 e 1,00), consumo zero e
entradas inválidas. Cada conferência aparece como `[OK]` ou `[FALHOU]`; no final, o
programa mostra quantas deram certo.

Os exemplos acumulados dos quatro blocos podem ser executados a partir da raiz:

```bash
python -c "import runpy; projeto = runpy.run_path('script/TriboSolarian_Colonia.py'); assert projeto['exemplos_blocos1_a4']()"
```

O Bloco 2 verifica a geração eólica e a regressão sobre os pares modelados (M),
mantendo previsão e potência atual separadas. O Bloco 3 verifica demanda, saldo e
reserva bruta de oxigênio e alimento seco, com as taxas de referência (R) do apoio.
O Bloco 4 verifica cadastro independente, consumos, prioridades, mínimos, entradas
inválidas e recomendações sem alteração automática dos dados.

## Operações e recomendações — Bloco 4

Responsável: Thales Martins Oliveira Barros. As quatro operações são parâmetros de
projeto (P) da seção 5 do material de apoio, todos na janela de 24 horas terrestres.

| ID | Operação | Prioridade | Normal (kW) | Mínimo (kW) | Economia máxima (kWh/24 h) |
| --- | --- | ---: | ---: | ---: | ---: |
| ARM | Armazenamento e logística | 1 | 4 | 3 | 24 |
| PES | Pesquisa e experimentos | 2 | 4 | 1 | 72 |
| MOB | Mobilidade | 3 | 3 | 1 | 48 |
| CON | Conforto e áreas comuns | 4 | 2 | 0,5 | 36 |

`criar_colonia()` já inclui as operações. `listar_cargas()` e `consumos_eletricos()`
reúnem auxiliares, suporte vital e complementares uma única vez, por ID. O consumo
normal integrado é **864 kWh**, sendo 552 kWh essenciais e 312 kWh complementares.
O mínimo integrado é **684 kWh** e a economia máxima é **180 kWh**.

`avaliar_operacoes(colonia)` apresenta consumo normal, protegido e parcela ajustável.
`recomendar_operacoes(colonia)` calcula uma proposta, sem modificar a colônia, na ordem
**conforto → mobilidade → pesquisa → armazenamento/logística**. A redução para assim
que o déficit é coberto; não corta as cargas essenciais nem ultrapassa os mínimos.
O objetivo é atender ao período, sem prometer margem de 10% ou fornecimento contínuo.

Exemplo de uso com a condição BAIXA_GERACAO do apoio:

```python
colonia = criar_colonia()
colonia["contexto"]["cenario"] = "BAIXA_GERACAO"
colonia["energia"]["solar"]["fator_solar"] = 0.80
colonia["energia"]["eolica"].update(vento_ms=6, potencia_kw=1.2215, ativa=1)
proposta = recomendar_operacoes(colonia)
print(diagnostico_operacoes(proposta))
```

As potências eólicas atuais vêm da tabela modelada do apoio, sem usar a regressão
para substituir o cenário. A tempestade tem eólica indisponível por escolha
operacional do exercício; não é uma velocidade de corte certificada.

| Cenário | Geração (kWh) | Saldo inicial (kWh) | Economia proposta (kWh) | Saldo proposto (kWh) |
| --- | ---: | ---: | ---: | ---: |
| NORMAL | 1.029,4872 | +165,4872 | 0 | +165,4872 |
| BAIXA_GERACAO | 797,316 | −66,684 | 66,684 | 0 |
| TEMPESTADE | 96 | −768 | 180 | −588 |

Em baixa geração, conforto passa de 2 para 0,5 kW e mobilidade de 3 para
1,7215 kW. O saldo proposto chega a zero, com classificação AMARELO (cobertura 1,00).
Na tempestade, todas as complementares chegam aos mínimos e ainda faltam 588 kWh.
A saída declara essa limitação; não propõe cortes abaixo dos mínimos nem inventa
uma reserva elétrica. Economizar eletricidade não repõe oxigênio ou alimentos.

Os resultados executados estão em [testes/exemplos_blocos1_a4.txt](testes/exemplos_blocos1_a4.txt).

Para o repasse a Wallace, `recomendar_operacoes()` fornece `balanco_atual`,
`balanco_proposto`, `recomendacoes`, `economia_maxima_kwh`, `economia_proposta_kwh`,
`deficit_remanescente_kwh` e `atende_periodo`. O menu pode usar
`diagnostico_operacoes()` para apresentar a proposta. Clima e riscos devem combinar
esses dados com `avaliar_suporte_vida()`, sem atribuir reposição de recursos a cortes
elétricos. Os cenários, a edição interativa e o menu permanecem nos espaços do Bloco 5.

## Clima, riscos e integração — Bloco 5

Responsável: Wallace Gabriel Américo Albuquerque.

**Clima** (seção 6 do apoio). Cada indicador recebe uma classe:

| Indicador | VERDE | AMARELO | VERMELHO |
|---|---|---|---|
| Vento (m/s) | 0 a 10 | acima de 10 até 15 | acima de 15 |
| Poeira (τ) | 0 a 1 | acima de 1 até 3 | acima de 3 |
| Temperatura externa (°C) | −80 a −20 | −100 a −80 ou −20 a 0 | abaixo de −100 ou acima de 0 |

O clima só descreve o cenário informado. O programa não prevê tempestades.

**Riscos.** `avaliar_riscos` cruza energia, a proposta do Bloco 4 (`recomendar_operacoes`),
recursos vitais e clima, com condições simples e combinadas. Cada risco mostra o **dado**,
o **motivo**, a **recomendação** e a **restrição** que continua depois da ação. A lista sai
ordenada do mais urgente (CRITICO) ao menos urgente (INFO). Principais regras:

- consumo > geração **e** as reduções do Bloco 4 cobrem o déficit → `ALERTA: reduzir consumo`;
- consumo > geração **e** as reduções não bastam → `ALERTA: ativar modo economia` (CRITICO),
  informando o déficit que sobra;
- geração > consumo → `SUGESTÃO: armazenar energia excedente`;
- fator solar < 0,5 **e** eólica indisponível → as duas fontes comprometidas;
- O₂ ou alimento insuficiente → reposição imediata (a economia elétrica não repõe recurso);
- vento **ou** poeira em VERMELHO → suspender atividades externas;
- duas ou mais frentes adversas (energia, vitais, ambiente) → restrição conjunta (CRITICO).

| Cenário | Energia | Recursos vitais | Clima | Riscos gerados |
|---|---|---|---|---|
| NORMAL | VERDE, +165,49 kWh | suficientes | VERDE | INFO: excedente |
| BAIXA_GERACAO | VERMELHO, −66,68 kWh (resolvido com 66,68 kWh de economia) | suficientes | poeira AMARELO | ALTO, ATENCAO |
| TEMPESTADE | VERMELHO, −768 kWh (sobram 588 kWh) | suficientes | vento e poeira VERMELHO | CRITICO, ALTO |
| SUPORTE_VIDA_EM_ALERTA | VERDE, +165,49 kWh | O₂ insuficiente, alimento com reserva curta | VERDE | CRITICO, ALTO, INFO |
| MULTIPLAS_RESTRICOES | VERMELHO, −768 kWh (sobram 588 kWh) | O₂ insuficiente | vento e poeira VERMELHO | CRITICO, ALTO |

**Previsão integrada.** A reta do Bloco 2 estima a potência eólica para o vento atual,
sempre separada da potência atual do cenário. Fora de 6 a 10 m/s, o programa mostra um
aviso em vez de um número. Para O₂ e alimentos há uma projeção condicional: em quantos
dias o estoque acaba **se** entrada e consumo continuarem iguais.

**Entradas.** `ler_numero` repete a pergunta até receber um número finito dentro da faixa
do campo (aceita vírgula; Enter mantém o valor). População só aceita inteiro positivo, e a
potência de uma operação nunca fica abaixo do mínimo protegido. No modo personalizado, a
potência eólica pode vir da tabela M, da regressão ou ser informada, e a origem é exibida.

`exemplos_bloco5()` confere os limites de vento, poeira e temperatura, os cinco cenários,
as regras combinadas, a previsão fora da faixa, entradas digitadas inválidas e o modo
personalizado. A opção 7 do menu roda as conferências dos cinco blocos (172 no total).

## Simplificações

- O balanço soma as 24 horas: saldo positivo não garante energia durante a noite.
- Baterias (reserva elétrica) não fazem parte do trabalho.
- Os valores de potência, estoques e limites são parâmetros escolhidos para o exercício,
  não medições reais.

