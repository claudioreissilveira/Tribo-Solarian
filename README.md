# 🚀 MISSÃO SLR-33 🚀

## Relatório Pré-Decolagem

Projeto em desenvolvimento para Fase I do curso de Ciências da Computação, consiste em um sistema automatizado em Python para simulação de telemetria, validação de restrições de segurança, cálculos de autonomia energética e emissão de diagnósticos inteligentes baseados em regras para missões aeroespaciais.
 
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
