# 🚀 MISSÃO SLR-33 🚀

## Relatório Pré-Decolagem

A Missão SLR-33 foi desenvolvida como uma simulação de um sistema de apoio à decisão para uma missão aeroespacial. A proposta do projeto surgiu da necessidade de representar, em um ambiente computacional, uma situação na qual diferentes informações de telemetria precisam ser analisadas simultaneamente antes de uma operação crítica.

Em uma missão real, a decisão de realizar uma decolagem depende da condição de diversos subsistemas. Temperatura, pressão, energia disponível e integridade estrutural são exemplos de parâmetros que precisam ser constantemente monitorados. Um único parâmetro fora dos limites estabelecidos pode representar um risco para a missão.

A partir desse conceito, o projeto foi pensado para transformar dados simulados de sensores em uma decisão operacional, utilizando regras previamente estabelecidas. Dessa forma, o sistema recebe os valores de telemetria, verifica cada parâmetro individualmente, classifica sua condição e, ao final, determina se a missão está PRONTA PARA DECOLAR ou se a DECOLAGEM DEVE SER ABORTADA.
 
---

## :dart: Objetivo do Projeto

O principal objetivo da SLR-33 é desenvolver um sistema em Python capaz de realizar uma verificação automatizada das condições de uma missão antes da decolagem.

O sistema foi projetado para:

- receber dados simulados de telemetria;
- analisar diferentes parâmetros simultaneamente;
- comparar os valores recebidos com limites previamente definidos;
- classificar cada parâmetro como Nominal, Atenção ou Aborta;
- identificar situações que possam comprometer a segurança da missão;
- consolidar os resultados individuais em uma decisão final;
- apresentar um diagnóstico de fácil interpretação;
- utilizar Inteligência Artificial como ferramenta auxiliar na interpretação dos resultados.

---

## :brain: Como o projeto foi pensado

O desenvolvimento da SLR-33 foi estruturado a partir de uma lógica de monitoramento → validação → classificação → decisão.

Primeiramente, foram definidos os principais parâmetros que poderiam representar condições relevantes para uma missão: temperatura interna e externa, integridade estrutural, nível de energia e pressão dos tanques.

Em seguida, foram estabelecidas faixas de operação para cada parâmetro. Essas faixas dividem os valores possíveis em três estados:

🟢 Nominal: condição considerada adequada para a missão;
🟡 Atenção: condição que ainda não representa uma reprovação imediata, mas exige monitoramento;
🔴 Aborta: condição que ultrapassa o limite estabelecido e impede a liberação da missão.

Essa estrutura permite que o sistema não apenas indique se um valor está correto ou incorreto, mas também forneça uma interpretação intermediária para situações que exigem atenção.

A etapa seguinte consiste na aplicação das regras de decisão. Cada grupo de telemetria é analisado individualmente e seu resultado é armazenado para que, posteriormente, o sistema possa consolidar todas as informações.

---

## :gear: Processo de funcionamento

O funcionamento da aplicação pode ser representado pelo seguinte fluxo:

Dados de telemetria → Validação dos valores → Aplicação das regras → Classificação → Consolidação → Diagnóstico final

#### 1. Entrada dos dados

O sistema recebe valores simulados referentes aos sensores e subsistemas da missão.

Esses valores representam informações como:

temperatura da cabine;
temperatura externa;
integridade estrutural;
nível de energia;
pressão do tanque de hélio;
pressão do tanque de propelente.

#### 2. Validação

Cada valor recebido é comparado com os limites definidos para seu respectivo parâmetro.

Essa etapa evita que a decisão seja baseada apenas na interpretação visual dos dados. O algoritmo realiza as comparações de maneira sistemática e padronizada.

#### 3. Classificação

Após a comparação, cada parâmetro recebe uma classificação.

Por exemplo, uma temperatura interna dentro da faixa nominal é classificada como Nominal. Caso esteja próxima dos limites estabelecidos, recebe Atenção. Se ultrapassar uma condição considerada crítica, recebe Aborta.

#### 4. Consolidação dos resultados

Depois da análise individual, os resultados são reunidos para produzir uma visão geral da missão.

Essa etapa é importante porque uma missão pode apresentar diversos parâmetros normais e, ainda assim, possuir uma única condição crítica capaz de impedir a decolagem.

#### 5. Diagnóstico final

Por fim, o sistema apresenta o diagnóstico geral da missão.

Existem dois resultados principais:

#### PRONTO PARA DECOLAR

Indica que os requisitos definidos para a simulação foram atendidos.

#### DECOLAGEM ABORTADA

Indica que pelo menos uma condição crítica não foi atendida.

---

## Telemetria analisada

O sistema verifica os seguintes grupos de dados:

- Temperaturas;

#### Temperatura interna °C:

| Classificação | Intervalo | Ação | Base real |
| -------- | -------- | -------- | -------- |
| :green_circle: | 21 a 25 | Nominal | Cabine da ISS mantida em 22–24°C |
| :yellow_circle:| 18 a 21 ou 25 a 27 | Atenção | Ainda dentro do limite operacional real |
| :red_circle: | abaixo de 18 ou acima de 27 | Aborta | Fora da faixa operacional segura  |



#### Temperatura externa °C:

| Classificação | Intervalo | Ação | Base real |
| -------- | -------- | -------- | -------- |
| :green_circle: | 5 a 35 | Nominal | Condição térmica segura para materiais/vedações |
| :yellow_circle:| -5 a 5 ou 35 a 45 | Atenção | Fora do ideal, monitorar de perto |
| :red_circle: | abaixo de -5 ou acima de 45 | Aborta | Challenger (1986) lançou a ~2°C, abaixo do testado com segurança  |


- Integridade estrutural (0 ou 1):

| Classificação | Intervalo | Ação | Base real |
| -------- | -------- | -------- | -------- |
| :green_circle: | Nenhum sensor excedeu o limiar | Nominal | ISS opera 81 acelerômetros + extensômetros em sua estrutura |
| :red_circle: | Ao menos um sensor excedeu o limiar  | Aborta | Sinal contínuo de vibração/deformação vira alerta binário ao cruzar o limiar de projeto  |


 
- Níveis de energia (% da carga total)

| Classificação | Intervalo | Ação | Base real |
| -------- | -------- | -------- | -------- |
| :green_circle: | 85 a 100 | Nominal | Carga plena, margem ampla |
| :yellow_circle:| 60 a 85 | Atenção | Adequada, sem folga confortável |
| :red_circle: | abaixo de 60 | Aborta | Baterias NiH2 da ISS operam com DOD máx. de 35%, sempre reservam margem  |


- Pressão dos tanques.

#### Pressão do tanque pressurizante de hélio (psi):

| Classificação | Intervalo | Ação | Base real |
| -------- | -------- | -------- | -------- |
| :green_circle: | 5500 a 6500 | Nominal | Tanques pressurizantes reais carregados perto de 6000 psi |
| :yellow_circle:| 4500 a 5500 ou 6500 a 7000 | Atenção | Fora do ideal, monitorar de perto |
| :red_circle: | abaixo de 4500 ou acima de 7000 | Aborta | Insuficiente para pressurizar, ou risco de ruptura  |

#### Pressão do tanque de propelente regulado (psi):

| Classificação | Intervalo | Ação | Base real |
| -------- | -------- | -------- | -------- |
| :green_circle: | 240 a 260 | Nominal | Pressão de alimentação típica de sistemas hipergólicos regulados |
| :yellow_circle:| 220 a 240 ou 260 a 280 | Atenção | Fora do ideal, monitorar de perto |
| :red_circle: | abaixo de 220 ou acima de 280 | Aborta | Alimentação de propelente comprometida  |


---

 ## Verificação

  O algoritmo verifica individualmente os grupos da telemetria.

  A missão recebe **PRONTO PARA DECOLAR** quando todas as condições são aprovadas.

  Caso uma condição seja reprovada, recebe **DECOLAGEM ABORTADA**.

  | Classificação | Intervalo | Ação | Base real |
| -------- | -------- | -------- | -------- |
| :green_circle: | Todos os testes internos aprovados | Liberado | Aviônica real certificada por Níveis A/B da norma SAE ARP 4761 |
| :yellow_circle:| Algum teste fora do ideal | Sob observação | Cada subsistema reporta a própria saúde ao sistema de decisão |
| :red_circle: | Algum teste reprovado | Aborta | Módulo não confiável para a decolagem  |


  ---

  ## Análise assistida por Inteligência Artificial

A Inteligência Artificial foi utilizada como ferramenta de apoio à interpretação dos dados simulados.

A análise auxilia na:

- classificação dos dados;
- identificação de possíveis anomalias;
- análise de riscos.

 ---

  ## Tecnologias utilizadas

- Python
- Jupyter Notebook
- PyCharm
- GitHub

 ---

 ## Como executar

### Jupyter Notebook

1. Faça o download ou clone deste repositório.
2. Abra o arquivo em um ambiente compatível com Jupyter Notebook.
3. Selecione um kernel Python.
4. Execute todas as células na ordem ou utilize **Run All**.
5. Consulte o relatório de verificação exibido no próprio Notebook.

 ---

 ## Evidências de execução

### Verificação da telemetria

<img width="1770" height="813" alt="Verificacao_telemetria" src="https://github.com/user-attachments/assets/10b3f1ce-eb3d-45da-bbb6-5e8bb5e44a80" />
