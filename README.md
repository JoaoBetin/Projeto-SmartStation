<div align="center">
  <img src="https://img.shields.io/badge/Smart_Station-Project-blue?style=for-the-badge&logo=iot" alt="Smart Station Logo">
  <h1>Station Smart Station - Monitoramento de Processos</h1>
  <p><i>Otimizando a logística e o tempo de operação com Inteligência e Visão Computacional.</i></p>
</div>

<hr>

## 📌 Sobre o Projeto

O **Smart Station** é uma solução completa para gestão de tempo em linhas de produção. O sistema monitora, através de uma câmera, o tempo que um operador leva para completar o envase de itens em uma caixa até a sua saída da estação. 

Além do cronômetro de processo, o sistema detecta o **tempo de ociosidade** da bancada, identificando períodos sem movimento ou sem chegada de novas caixas, gerando dados valiosos para a eficiência operacional.



---

## 🚀 Funcionalidades Chave

* **Monitoramento em Tempo Real:** Captura do início e fim do processo de empacotamento.
* **Detecção de Ociosidade:** Cálculo exato de quanto tempo a bancada fica parada.
* **Dashboard Interativo:** Visualização clara das métricas de performance.
* **Arquitetura Escalável:** Divisão clara entre captura de dados, processamento e interface.

---

## 🛠️ Tecnologias Utilizadas

<table>
  <tr>
    <td align="center"><b>Camada</b></td>
    <td align="center"><b>Tecnologia</b></td>
    <td align="center"><b>Função</b></td>
  </tr>
  <tr>
    <td><b>Visão Computacional</b></td>
    <td>Python + YOLOv8</td>
    <td>Processamento da imagem da câmera e lógica de detecção de movimento/objetos.</td>
  </tr>
  <tr>
    <td><b>Backend</b></td>
    <td>Java</td>
    <td>Processamento de regras de negócio, persistência de dados e API.</td>
  </tr>
  <tr>
    <td><b>Frontend</b></td>
    <td>React</td>
    <td>Dashboard para visualização dos indicadores (KPIs) de tempo.</td>
  </tr>
</table>

---

## 🏗️ Como o sistema funciona?

1.  **Captura (Python):** A câmera monitora a área da caixa. Ao detectar a entrada e saída, o Python envia os timestamps para o backend.
2.  **Processamento (Java):** O backend recebe os dados, calcula a diferença de tempo e armazena o histórico, gerenciando também o status da bancada.
3.  **Visualização (React):** O dashboard consome a API Java e exibe em tempo real se a estação está ativa ou ociosa.

---

## 📂 Como rodar o repositório

> [!IMPORTANT]
> Certifique-se de ter o Python 3.x, JDK 17+ e Node.js instalados.

```bash
# Clone o repositório
git clone [https://github.com/seu-usuario/smart-station.git](https://github.com/seu-usuario/smart-station.git)

# Acesse a pasta do projeto
cd smart-station
```
---

### 📦 Download do Modelo

O modelo treinado para detecção de caixas de papelão está disponível para download no link abaixo:

> 🔗 **[Baixar modelo (Google Drive)](https://drive.google.com/file/d/1ORDBkFxF88z4NUGfg5hum9xog4akT32U/view?usp=sharing)**

Após o download, **coloque o arquivo do modelo na pasta `boxDetection/`** dentro do repositório:

```
Projeto-SmartStation/
└── boxDetection/
    └── best.pt    ← coloque o arquivo aqui
```

---

### ⚙️ Configuração e Execução do Módulo Python

#### Pré-requisitos

- Python 3.10 ou superior
- `pip` atualizado
- Câmera conectada ou arquivo de vídeo para teste

#### 1. Instale as dependências

```bash
pip install -r requirements.txt
```

> As principais bibliotecas utilizadas são `ultralytics` (YOLOv8), `opencv-python` e `requests`.

#### 2. Posicione o modelo

Certifique-se de que o arquivo `best.pt` (baixado no link acima) está em `boxDetection/best.pt`.
