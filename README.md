# 🚀 MISSÃO AURORA SIGER | MGPEB SLR-33 🌌

# Colônia em Marte — Fase 3

Equipe Tribo Solarian · versão 0.1

Programa em Python que acompanha a energia de uma colônia de 50 pessoas em Marte,
sempre olhando um período de **24 horas**. Ele calcula quanta energia é gerada, quanta é
consumida, mostra o saldo e classifica a situação em Verde, Amarelo ou Vermelho.


## Como rodar

Abra a pasta `Colonia` no VS Code (Arquivo → Abrir Pasta) e, no terminal:

```bash
python script/colonia.py          # mostra o balanço de todos os cenários
python testes/testar_energia.py   # roda os testes
```

### Exemplo de saída

```
=== Cenário NORMAL ===
  Geração solar: 960.00 kWh
  Geração total: 960.00 kWh
  Consumo total: 864.00 kWh
  Saldo:         +96.00 kWh
  Cobertura:     1.1111
  Classificação: VERDE
```

---

## Como os dados estão organizados

O arquivo `colonia.py` é dividido em partes: **dados**, **validação**, **cálculos** e
**programa principal**.

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

**Cenários.** O dicionário `CENARIOS` guarda os valores que mudam em cada situação
(NORMAL, BAIXA_GERACAO, TEMPESTADE, SUPORTE_VIDA_EM_ALERTA, MULTIPLAS_RESTRICOES).
`criar_colonia` pega esses valores e coloca cada um no lugar certo. O vento do cenário vai
para o clima e para a eólica ao mesmo tempo, para os dois usarem o mesmo valor.

**Cargas sem repetição.** Cada carga elétrica está guardada em um lugar só: auxiliares em
`energia`, suporte de oxigênio e de alimentos em `suporte_vida`, e as outras quatro em
`operacoes`. A função `listar_cargas` junta as 7 numa lista, então nenhuma é somada duas
vezes.

## Como a energia é calculada

Regra básica: **energia (kWh) = potência (kW) × tempo (h)**.

**1. Geração solar** — `geracao_solar(pot_solar_kw, horas_solares, fator_solar)`

```
energia solar = potência × horas equivalentes × fator solar
NORMAL:  120 × 8 × 1,00 = 960 kWh
```

O fator solar vai de 0 a 1 e já inclui a perda por poeira do cenário, então é usado uma
vez só.

**2. Consumo** — `consumo_das_cargas(cargas, modo)`

Cada carga consome `potência × 24 h`. No modo `"normal"` usa a potência normal; no modo
`"minimo"` usa o mínimo protegido.

```
normal: (2 + 12 + 9 + 4 + 4 + 3 + 2) kW × 24 h = 36 × 24 = 864 kWh
mínimo: (2 + 12 + 9 + 3 + 1 + 1 + 0,5) kW × 24 h = 28,5 × 24 = 684 kWh
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
- horas entre 0 e 24;
- potência normal de uma carga não pode ser menor que o mínimo protegido.

## Testes

`testes/testar_energia.py` confere: base comum, geração solar, consumo, saldo,
classificações (inclusive os limites exatos 1,10 e 1,00), consumo zero e entradas
inválidas. Se algum `assert` falhar, o Python mostra a linha; se tudo der certo, aparece
"Todos os testes passaram."

## Simplificações

- O balanço soma as 24 horas: saldo positivo não garante energia durante a noite.
- Baterias (reserva elétrica) não fazem parte do trabalho.
- Os valores de potência, estoques e limites são parâmetros escolhidos para o exercício,
  não medições reais.

