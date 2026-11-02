# 🚀 MISSÃO AURORA SIGER | MGPEB SLR-33 🌌

# Colônia em Marte — Fase 3

Equipe Tribo Solarian · versão 0.1

Programa em Python que acompanha a energia de uma colônia de 50 pessoas em Marte,
sempre olhando um período de **24 horas**. Ele calcula quanta energia é gerada, quanta é
consumida, mostra o saldo e classifica a situação em Verde, Amarelo ou Vermelho.


## Como rodar

Na pasta do repositório, no terminal:

```bash
python script/TriboSolarian_Colonia.py
```

### Exemplo de saída

```
-- NORMAL
Geração total: 960.00 kWh
Consumo total: 864.00 kWh
Saldo:         +96.00 kWh
Cobertura:     1.1111
Energia:       VERDE - margem de geração no período
  [OK] NORMAL saldo: obtido 96.0, esperado 96.0
  [OK] NORMAL classe: obtido 'VERDE', esperado 'VERDE'
...
Bloco 1: 29 de 29 conferências OK.
```

---

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
└── clima           vento, poeira, temperatura
```

Usamos três estruturas:
- **dicionário** para guardar atributos com nome (`"pot_solar_kw": 120`);
- **dicionário dentro de dicionário** para sistemas e subsistemas (energia → solar);
- **lista** para dados que se repetem (as 4 operações e os 5 pares vento × potência).

**Cenários.** Os cenários (NORMAL, BAIXA_GERACAO, TEMPESTADE, SUPORTE_VIDA_EM_ALERTA,
MULTIPLAS_RESTRICOES) entram no Bloco 5. `criar_colonia` já cria todos os grupos da
hierarquia; o Bloco 1 preenche o contexto, a energia solar e os auxiliares, e os outros
grupos são completados pelos blocos seguintes.

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

## Simplificações

- O balanço soma as 24 horas: saldo positivo não garante energia durante a noite.
- Baterias (reserva elétrica) não fazem parte do trabalho.
- Os valores de potência, estoques e limites são parâmetros escolhidos para o exercício,
  não medições reais.

