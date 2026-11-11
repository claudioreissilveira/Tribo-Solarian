# 🌱 Life Solarian — Colônia Aurora Siger

**FIAP ON · Ciência da Computação · Fase 3 · Equipe Tribo Solarian**

Sistema integrado em Python para analisar a operação de uma colônia de **50 pessoas em Marte**, em uma janela de **24 horas terrestres**. Organiza os dados em listas e dicionários hierárquicos, calcula geração solar e eólica, compara geração e consumo, avalia oxigênio, alimentos e clima e estima potência eólica por regressão linear.

O operador seleciona um cenário ou informa os dados por módulo. O sistema apresenta diagnósticos, riscos e recomendações para equilibrar os recursos, preservando as cargas essenciais e os mínimos operacionais. As recomendações são propostas: o cadastro e os estoques permanecem preservados após a avaliação, que registra a lista de riscos.

**Repositório público da Fase 3:** [Tribo-Solarian — branch 3-Colonia](https://github.com/claudioreissilveira/Tribo-Solarian/tree/3-Colonia).

## Como executar

Na pasta do projeto, com Python 3 instalado:

```bash
python script/TriboSolarian_Colonia.py
```

O programa utiliza somente a biblioteca padrão (`math`), sem instalação de dependências. Foi executado na validação final com Python 3.12 e 3.14.

| Opção | Funcionamento |
| --- | --- |
| `1` | NORMAL |
| `2` | BAIXA_GERACAO |
| `3` | TEMPESTADE |
| `4` | SUPORTE_VIDA_EM_ALERTA |
| `5` | MULTIPLAS_RESTRICOES |
| `6` | PERSONALIZADO, iniciado com os dados de NORMAL |
| `7` | Conferências dos cinco blocos |
| `0` | Encerrar |

No modo personalizado, escolha o módulo, informe os valores e use `A` para avaliar ou `0` para voltar. Enter mantém o valor atual; números decimais aceitam vírgula, como `0,8`. Estão disponíveis população, energia solar, energia eólica, oxigênio, alimentos, clima e potências das operações complementares.

Fluxo: **entrada → cálculos e classificações → regras e prioridades → diagnósticos e recomendações**.

## Exemplo de entrada e saída

Entrada: opção `3`, cenário TEMPESTADE. Os dados incluem vento de 22 m/s, poeira τ = 4,5, fator solar de 0,10 e eólica indisponível no período. Trechos da saída:

```text
[1] Energia
Geração total: 96.00 kWh
Consumo total: 864.00 kWh
Saldo:         -768.00 kWh
Cobertura:     0.1111
Energia:       VERMELHO - déficit no período; há demanda não atendida no balanço

Economia possível: 180.000 kWh
Economia proposta: 180.000 kWh
Déficit remanescente: 588.000 kWh. A economia não basta; é necessário recompor a geração.

[2] Previsão eólica (regressão linear, Bloco 2)
Aviso: vento de 22 m/s fora da faixa de ajuste (6 a 10 m/s): sem previsão numérica

1. [CRITICO] Energia: ALERTA: ativar modo economia - todas as complementares no mínimo protegido
```

Os resultados completos dos cinco cenários estão em [testes/](testes/). A proposta de economia preserva os mínimos, mas ainda deixa um déficit de 588 kWh nesse cenário.

## Organização do projeto

```text
Colonia/
├── README.md
├── docs/
│   ├── Colonia_material_apoio.docx
│   └── Relatorio_Colonia_TriboSolarian (1).pdf
├── script/
│   └── TriboSolarian_Colonia.py
└── testes/
    └── saídas dos cenários e conferências
```

- [Script Python](script/TriboSolarian_Colonia.py): sistema integrado, menu e conferências.
- [Material de apoio](docs/Colonia_material_apoio.docx): campos, unidades, parâmetros, cenários e referências.
- [Relatório PDF](docs/Relatorio_Colonia_TriboSolarian%20%281%29.pdf): organização dos dados, regras, previsão, uso de energia e resultados.

## Estrutura dos dados

```text
colonia
├── contexto        cenário, população e período de 24 h
├── energia
│   ├── solar       potência, horas equivalentes e fator solar
│   ├── eolica      vento, disponibilidade, potência atual, origem e pares
│   └── auxiliares  carga elétrica de controle e distribuição
├── suporte_vida
│   ├── oxigenio    estoque, entrada, taxa por pessoa e carga elétrica
│   └── alimentos   estoque, entrada, taxa por pessoa e carga elétrica
├── operacoes       quatro operações complementares
├── clima           poeira e temperatura externa
└── riscos          riscos registrados pela avaliação integrada
```

Os dicionários representam atributos e subsistemas; as listas reúnem operações, riscos e pares de vento × potência. As unidades aparecem nos nomes dos campos, como `pot_solar_kw`, `estoque_kg` e `vento_ms`.

A velocidade do vento fica em `energia → eolica → vento_ms` e também alimenta o módulo climático. Cada carga elétrica tem um único cadastro; `listar_cargas()` e `consumos_eletricos()` reúnem as sete cargas por identificador, com validação de duplicidades e períodos. Cada cenário recebe cópias independentes dos padrões.

O material de apoio distingue **R** (referência publicada), **P** (parâmetro de projeto) e **M** (dado modelado). Essa distinção identifica a origem dos valores usados no exercício.

## Energia e previsão eólica

As funções de cálculo utilizam as relações:

```text
Energia (kWh) = potência (kW) × tempo (h)
Geração solar = potência solar × horas equivalentes × fator solar
Geração eólica atual = potência atual × horas, quando a turbina está ativa
Saldo = geração total − consumo total
Cobertura = geração total ÷ consumo total
```

Em NORMAL, a geração solar é `120 × 8 × 1,00 = 960 kWh`. O fator solar, de 0 a 1, já representa a redução do cenário e é aplicado uma única vez. A eólica atual usa a tabela modelada do apoio: a 8 m/s, gera `2,8953 × 24 = 69,4872 kWh`.

O consumo normal das sete cargas é `(2 + 12 + 9 + 4 + 4 + 3 + 2) × 24 = 864 kWh`. A classificação identifica o déficit antes do arredondamento; nas coberturas a partir de 1,00, usa seis casas decimais para comparar as margens:

| Classe | Cobertura |
| --- | --- |
| VERDE | ≥ 1,10 |
| AMARELO | ≥ 1,00 e < 1,10 |
| VERMELHO | < 1,00 |
| NAO SE APLICA | Consumo igual a zero; cobertura `None` |

O saldo acompanha a classificação. Uma geração superior ao consumo pode continuar em AMARELO quando a margem é menor que 10%.

### Regressão linear

`ajustar_reta()` calcula uma reta por mínimos quadrados sobre os cinco pares modelados de vento × potência, entre 6 e 10 m/s:

```text
P(v) = a × v + b
a = 1,10496
b = −5,67294
P(8,5) = 3,71922 kW ≈ 89,26128 kWh em 24 h
```

`prever_potencia()` valida a estimativa, e `previsao_eolica()` apresenta a previsão integrada. Fora da faixa de 6 a 10 m/s, a apresentação traz um aviso sem estimativa numérica.

**Potência atual e previsão são distintas.** O balanço usa a potência atual cadastrada. No modo personalizado, sua origem pode ser a tabela modelada, a estimativa pela regressão ou um valor informado pelo operador; essa origem aparece na saída. Nos cenários de tempestade, a eólica está indisponível por decisão operacional do exercício.

## Oxigênio e alimentos

Para a população padrão de 50 pessoas:

| Recurso | Taxa por pessoa/24 h | Demanda/24 h | Estoque em NORMAL | Entrada/24 h em NORMAL |
| --- | ---: | ---: | ---: | ---: |
| Oxigênio | 0,895 kg | 44,75 kg | 134,25 kg | 45 kg |
| Alimento seco | 0,800 kg | 40 kg | 560 kg | 30 kg |

`avaliar_suporte_vida()` separa dois indicadores: **suficiência do período**, quando estoque + entrada atendem à demanda, e **reserva bruta**, calculada por estoque ÷ demanda diária, sem contar entradas futuras.

| Reserva bruta | VERDE | AMARELO | VERMELHO |
| --- | --- | --- | --- |
| Oxigênio | ≥ 2 dias | ≥ 1 e < 2 dias | < 1 dia |
| Alimento seco | ≥ 7 dias | ≥ 3 e < 7 dias | < 3 dias |

Em NORMAL, as reservas brutas são de 3 dias de O₂ e 14 dias de alimento. Em SUPORTE_VIDA_EM_ALERTA, o O₂ é insuficiente para as 24 h; o alimento atende ao período, mas tem reserva bruta de 2 dias, classificada VERMELHO.

A projeção condicional usa `estoque ÷ (demanda diária − entrada diária)` quando o consumo supera a entrada. Em NORMAL, o alimento duraria 56 dias se essas condições se mantivessem. Quando a entrada cobre a demanda, o sistema não calcula uma data de esgotamento. A massa de O₂ é um estoque de recurso, sem representar concentração ou pressão do ar do habitat.

## Operações e prioridades

Energia, oxigênio e alimentos são essenciais. As quatro operações complementares têm prioridades e mínimos definidos no apoio:

| ID | Operação | Prioridade | Normal (kW) | Mínimo (kW) | Economia máxima (kWh/24 h) |
| --- | --- | ---: | ---: | ---: | ---: |
| ARM | Armazenamento e logística | 1 | 4 | 3 | 24 |
| PES | Pesquisa e experimentos | 2 | 4 | 1 | 72 |
| MOB | Mobilidade | 3 | 3 | 1 | 48 |
| CON | Conforto e áreas comuns | 4 | 2 | 0,5 | 36 |

`recomendar_operacoes()` propõe reduções na ordem **conforto → mobilidade → pesquisa → armazenamento/logística** e para assim que cobre o déficit ou esgota a parcela ajustável. As cargas essenciais e os mínimos são preservados. O consumo mínimo integrado é de **684 kWh/24 h**, com economia máxima de **180 kWh/24 h**.

Em BAIXA_GERACAO, conforto passa de 2 para 0,5 kW e mobilidade de 3 para 1,7215 kW, economizando 66,684 kWh. O saldo proposto chega a zero, com cobertura 1,00 e classe AMARELO. Na tempestade, todas as complementares chegam aos mínimos e a saída informa o déficit residual.

O menu recebe o balanço atual, o balanço proposto, as recomendações e o déficit remanescente. A avaliação integrada combina esses resultados com os recursos vitais e o clima. Economizar eletricidade não repõe oxigênio ou alimentos.

## Clima e regras de decisão

O módulo climático classifica os dados informados:

| Indicador | VERDE | AMARELO | VERMELHO |
| --- | --- | --- | --- |
| Vento (m/s) | 0 a 10 | > 10 e ≤ 15 | > 15 |
| Poeira (τ) | 0 a 1 | > 1 e ≤ 3 | > 3 |
| Temperatura externa (°C) | −80 a −20, inclusive | −100 ≤ T < −80 ou −20 < T ≤ 0 | < −100 ou > 0 |

`avaliar_riscos()` aplica condições simples e combinadas. Cada risco informa frente, gravidade, dado, motivo, recomendação e eventual restrição. A lista é ordenada por **CRITICO → ALTO → ATENCAO → INFO**.

| Condição | Diagnóstico ou recomendação |
| --- | --- |
| Energia VERMELHO e economia suficiente | ALTO: reduzir consumo conforme a proposta |
| Energia VERMELHO e economia insuficiente | CRITICO: modo economia, com o déficit residual informado |
| Energia AMARELO | ATENCAO: adiar cargas não essenciais para recuperar margem |
| Energia VERDE | INFO: armazenar excedente ou programar cargas adiáveis |
| Fator solar < 0,5 e eólica inativa | ALTO: fontes comprometidas simultaneamente |
| O₂ ou alimento insuficiente para o período | CRITICO: providenciar reposição |
| Reserva vital curta, com atendimento no período | ALTO ou ATENCAO conforme a classificação da reserva |
| Vento ou poeira VERMELHO | ALTO: suspender atividades externas não essenciais |
| Temperatura externa AMARELO ou VERMELHO | ATENCAO ou ALTO: reduzir exposição externa |
| Duas ou mais frentes adversas reconhecidas pela regra conjunta | CRITICO: restrição conjunta |

A regra conjunta conta energia VERMELHO, recurso vital insuficiente ou com reserva VERMELHO e ambiente com vento, poeira ou temperatura VERMELHO. Quando há restrição vital combinada com outra frente, a recomendação trata em conjunto o equilíbrio energético e a reposição de O₂/alimentos, preservando os três sistemas essenciais.

## Resultados dos cinco cenários

Resultados integrados, incluindo solar e eólica, para consumo normal de **864 kWh/24 h**:

| Cenário | Geração (kWh) | Saldo inicial (kWh) | Economia proposta (kWh) | Saldo proposto (kWh) | Riscos gerados |
| --- | ---: | ---: | ---: | ---: | --- |
| NORMAL | 1.029,4872 | +165,4872 | 0 | +165,4872 | INFO |
| BAIXA_GERACAO | 797,3160 | −66,6840 | 66,6840 | 0 | ALTO, ATENCAO |
| TEMPESTADE | 96 | −768 | 180 | −588 | CRITICO, ALTO |
| SUPORTE_VIDA_EM_ALERTA | 1.029,4872 | +165,4872 | 0 | +165,4872 | CRITICO, ALTO, INFO |
| MULTIPLAS_RESTRICOES | 96 | −768 | 180 | −588 | CRITICO, ALTO |

## Conferências e validação

A opção `7` do menu executa `executar_exemplos()`, que reúne as conferências dos cinco blocos. Cada comparação informa `[OK]` ou `[FALHOU]`. Para executar a mesma suíte diretamente, a partir da pasta do projeto:

```bash
python -X utf8 -c "import runpy; projeto = runpy.run_path('script/TriboSolarian_Colonia.py'); assert projeto['executar_exemplos']()"
```

| Bloco | Escopo das conferências | Resultado em 10/11/2026 |
| --- | --- | ---: |
| 1 | Hierarquia, solar, balanço e limites energéticos | 29/29 |
| 2 | Eólica, regressão, domínio e disponibilidade | 18/18 |
| 3 | Demandas, suficiência, reservas e cargas vitais | 25/25 |
| 4 | Consumos, prioridades, mínimos e recomendações | 39/39 |
| 5 | Clima, cenários, riscos, entradas e integração | 61/61 |
| **Total** | **Conferências incluídas no script** | **172/172** |

A validação também inclui 26 verificações adicionais de funcionamento e nove testes direcionados aos refinamentos: combinação de temperatura crítica com déficit, tratamento conjunto dos essenciais, recuperação da entrada após um inteiro extremo, resultados finitos e recusa de previsão negativa.

As evidências da equipe estão em [conferencias_blocos1_a5.txt](testes/conferencias_blocos1_a5.txt), [entradas_invalidas.txt](testes/entradas_invalidas.txt) e nos arquivos dos cinco cenários em [testes/](testes/).

## Contribuições por bloco

| Bloco | Responsável | Implementação |
| --- | --- | --- |
| 1 | Vitor Lima Montiel | Base comum, hierarquia, geração solar e balanço energético |
| 2 | Victor Augusto dos Santos Souza | Geração eólica, ajuste da reta e previsão |
| 3 | Cláudio Roberto Grillo Reis Silveira | Oxigênio, alimentos, suficiência e reservas |
| 4 | Thales Martins Oliveira Barros | Operações, prioridades e propostas de economia |
| 5 | Wallace Gabriel Américo Albuquerque | Cenários, clima, riscos, entradas, menu e integração |

## Limites do modelo

- O balanço agrega 24 horas terrestres; um saldo positivo não garante fornecimento contínuo durante a noite. Baterias e reserva elétrica estão fora do modelo.
- Potências, estoques, limiares e cenários seguem as referências e escolhas didáticas identificadas no material de apoio. Os pares eólicos são modelados.
- A regressão é uma aproximação local, utilizada entre 6 e 10 m/s. A previsão permanece separada da geração atual.
- O clima descreve as entradas do cenário. A aplicação não prevê a chegada de tempestades nem controla sensores ou equipamentos.
- As validações recusam texto indevido, NaN, infinito, valores fora das faixas e operações abaixo dos mínimos. Inteiros que excedem a conversão numérica são recusados; o cálculo de energia e o balanço verificam resultados finitos, e a previsão integrada utiliza a validação de potência da regressão.
