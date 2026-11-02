# 🚀 MISSÃO AURORA SIGER | MGPEB SLR-33 🌌

# Colônia — Sistema integrado (Fase 3)

Equipe Tribo Solarian · versão **0.1.0** (base comum + energia solar + balanço energético)

Sistema em Python padrão (sem dependências externas) que acompanha os recursos de uma
colônia de 50 pessoas em Marte numa janela de **24 horas terrestres**: calcula, compara,
classifica e recomenda. O programa não opera equipamentos nem altera dados sozinho.

> Status desta versão: base de dados, geração solar e balanço energético prontos e
> testados. Geração eólica (regressão), oxigênio/alimentos, clima e riscos ainda serão
> conectados.


## ⚙️ Como executar

Requer Python 3.8 ou superior. A partir da pasta `Colonia`:

```bash
python script/main.py                 # todos os cenários
python script/main.py TEMPESTADE      # um cenário
python -m unittest discover -s testes -v
```

### Exemplo de entrada e saída

Entrada: cenário `NORMAL` (120 kW solares, 8 h equivalentes, fator 1,00; cargas normais).

```
=== Cenário NORMAL | população 50 | janela 24 h ===
(geração eólica ainda não conectada)

-- Cargas em modo normal --
Geração por fonte:
  solar            960.00 kWh
Geração total      960.00 kWh
Consumo total      864.00 kWh
Saldo              +96.00 kWh (EXCEDENTE)
Cobertura          1.1111
Classificação  VERDE - Margem de geração no período.
```

Uso das funções diretamente:

```python
from base import montar_colonia, listar_cargas
from energia import geracao_solar_kwh, consumos_por_carga, balanco_energetico

colonia  = montar_colonia("BAIXA_GERACAO")
geracoes = {"solar": geracao_solar_kwh(120, 8, 0.80)}           # 768 kWh
consumos = consumos_por_carga(listar_cargas(colonia), "normal")  # 864 kWh
balanco_energetico(geracoes, consumos)
# saldo -96 kWh, cobertura 0,8889, VERMELHO
```

---

## Organização dos dados

**Base comum.** Todos os módulos compartilham o mesmo `CONTEXTO`: cenário, população
(50 pessoas, editável, inteiro positivo) e período de análise (24 h terrestres — não um sol
marciano de 24,6597 h). Toda grandeza leva a unidade no nome do campo (`pot_solar_kw`,
`horas_solares`, `estoque_o2_kg`, `vento_ms`, `temperatura_externa_c`), o que evita somar
potência com energia ou kg de O₂ com kg de alimento.

**Hierarquia.** Os sistemas são dicionários aninhados (sistema → subsistema → campos):

| Grupo | Conteúdo | Estrutura |
|---|---|---|
| `CONTEXTO` | cenário, população, período | chave-valor |
| `ENERGIA` → `solar` / `eolica` / `auxiliares` | potências, horas, fatores, disponibilidade; pares de referência da regressão | dicionário aninhado; pares em **lista** de dicionários |
| `SUPORTE_VIDA` → `oxigenio` / `alimentos` | taxas por pessoa, estoques, entradas e a carga elétrica de cada um | dicionário aninhado |
| `OPERACOES_COMPLEMENTARES` | armazenamento, pesquisa, mobilidade, conforto | **lista** de registros com os mesmos campos |
| `CLIMA` | vento, poeira τ, temperatura externa | chave-valor |
| `CENARIOS` | entradas de NORMAL, BAIXA_GERACAO, TEMPESTADE, SUPORTE_VIDA_EM_ALERTA, MULTIPLAS_RESTRICOES | dicionário de dicionários |

Regra usada: listas para dados repetidos (operações e pares vento/potência), chave-valor
para atributos, aninhamento para sistemas e subsistemas.

**Cada carga elétrica pertence a um único bloco**, para que a consolidação não duplique
parcelas: auxiliares ficam em `ENERGIA`, o suporte elétrico de O₂ e de alimentos fica em
`SUPORTE_VIDA` e as quatro complementares ficam em `OPERACOES_COMPLEMENTARES`. A função
`listar_cargas()` reúne as sete cargas numa lista única, e `consumos_por_carga()` recusa
identificador repetido. Todo registro de carga tem os mesmos campos: `id`, `nome`,
`pot_normal_kw`, `minimo_protegido_kw`, `periodo_h` (e `prioridade` nas complementares,
1 = mais importante).

**Cenários.** `montar_colonia(cenario, populacao)` faz uma cópia profunda da base e grava
cada campo do cenário no seu lugar da hierarquia, conforme a tabela
`DESTINO_CAMPOS_CENARIO`. O vento é gravado ao mesmo tempo em `CLIMA` e em
`ENERGIA.eolica`, para que clima e eólica usem sempre o mesmo valor. `PERSONALIZADO`
parte do NORMAL. Editar uma colônia montada não altera a base de referência.

**Origem dos valores.** Os comentários de `dados.py` mantêm a marca do documento de apoio:
**R** (referência publicada, ex.: O₂ 0,895 kg/pessoa/24 h, R2), **P** (parâmetro de
projeto, ex.: 120 kW solares, limiares de cobertura) e **M** (dado modelado, ex.: pares
vento/potência da seção 8).

## Cálculos energéticos

Relação dimensional: **energia (kWh) = potência (kW) × tempo (h)**.

1. **Geração solar** — `geracao_solar_kwh(pot_solar_kw, horas_solares, fator_solar)`

   `E_solar = pot_solar_kw × horas_solares × fator_solar`

   As horas solares são horas equivalentes à potência de referência (não a duração do
   dia). O fator solar (0 a 1) já inclui a perda adotada pelo cenário — poeira inclusive —
   e é aplicado **uma única vez**; τ não é convertido em fator.

2. **Consumo** — `consumo_carga_kwh(carga, modo)` e `consumos_por_carga(cargas, modo)`

   `E_carga = potência × periodo_h`, com potência normal (`modo="normal"`) ou mínimo
   protegido (`modo="minimo"`). No cadastro, a potência normal não pode ser menor que o
   mínimo protegido.

3. **Balanço** — `balanco_energetico(geracoes, consumos)`

   Recebe gerações e consumos como entradas, ambos no formato `{rótulo: kWh}`:

   - `saldo = geração total − consumo total` (EXCEDENTE, DEFICIT ou EQUILIBRIO)
   - `cobertura = geração total ÷ consumo total`
   - classificação: **VERDE** se cobertura ≥ 1,10; **AMARELO** se 1,00 ≤ cobertura < 1,10;
     **VERMELHO** se cobertura < 1,00
   - consumo total igual a zero → cobertura `None`, classificação `NAO_APLICAVEL` e motivo
     registrado, sem divisão por zero

   O saldo é sempre exibido junto da classificação, porque excedente e margem pequena
   podem coexistir (ex.: 900 kWh gerados para 864 consumidos → saldo +36, AMARELO). Para a
   comparação com os limiares, a cobertura é arredondada a 9 casas: sem isso,
   950,4 ÷ 864 (exatamente 1,10) dá 1,0999999999999999 em ponto flutuante e cairia em
   AMARELO.

**Valores conferidos com o documento de apoio** (testes automatizados):

| Cenário | Solar (kWh) | Consumo normal (kWh) | Saldo (kWh) | Cobertura | Classe |
|---|---:|---:|---:|---:|---|
| NORMAL | 120×8×1,00 = 960 | 36 kW×24 = 864 | +96 | 1,1111 | VERDE |
| BAIXA_GERACAO | 120×8×0,80 = 768 | 864 | −96 | 0,8889 | VERMELHO |
| TEMPESTADE | 120×8×0,10 = 96 | 864 | −768 | 0,1111 | VERMELHO |

Cargas mínimas protegidas: 28,5 kW × 24 h = 684 kWh. Valores apenas com geração solar; a
eólica será somada quando o módulo for conectado.

**Validação das entradas.** Números precisam ser finitos (recusa texto, `None`, `bool`,
NaN e infinito); potências, horas e parcelas de energia não podem ser negativas; fator
solar entre 0 e 1; horas dentro da janela de 24 h; disponibilidade eólica somente 0 ou 1;
população inteira positiva. Entradas inválidas levantam `ValueError` com mensagem em
português.

**Simplificações declaradas.** O balanço é agregado em 24 h: saldo positivo não garante
energia à noite nem oferta contínua em cada instante (R4). Reserva elétrica (baterias) não
faz parte do escopo. Estoques, potências e limiares são parâmetros de projeto (P), não
medições de uma colônia real.
