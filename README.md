📦 Smart Station

Smart Station é um sistema de monitoramento de processos operacionais utilizando visão computacional.
O objetivo do projeto é medir e analisar o tempo de execução de um processo produtivo, especificamente o tempo que um operador leva para inserir itens em uma caixa até que ela saia da área monitorada pela câmera.

Além disso, o sistema também identifica períodos de ociosidade da bancada, ou seja, quando não há movimentação ou presença de caixas no local de trabalho.

O projeto busca aplicar conceitos de Lean Digital, permitindo identificar gargalos, medir produtividade e analisar eficiência do processo.

🎯 Objetivo do Projeto

O objetivo principal da Smart Station é coletar e disponibilizar dados sobre o tempo de execução de um processo operacional, permitindo visualizar:
- Tempo total de processamento de uma caixa
- Tempo médio de operação
- Períodos de ociosidade da estação
- Registro de eventos do processo
Essas informações são exibidas em um dashboard interativo, permitindo acompanhar o desempenho da estação em tempo real ou através de registros históricos.

⚙️ Como o sistema funciona
O funcionamento do sistema ocorre em três etapas principais:

1️⃣ Captura do Processo
Uma câmera monitora a bancada de trabalho e utiliza visão computacional para identificar a presença de uma caixa.
Quando uma caixa entra no campo de visão da câmera:
- O sistema inicia a contagem do tempo.
Quando a caixa sai da área monitorada:
- O sistema encerra a contagem e registra o tempo total do processo.
2️⃣ Processamento dos Dados
Os dados capturados são enviados para o backend, onde são processados e armazenados para análise posterior.
O backend é responsável por:
- Receber os tempos registrados
- Processar as informações
- Disponibilizar os dados para o dashboard
3️⃣ Visualização no Dashboard
O dashboard exibe as informações do processo, permitindo acompanhar:
- Tempo de cada operação
- Tempo médio do processo
- Períodos de ociosidade
- Histórico de registros

🧠 Tecnologias Utilizadas

O projeto utiliza uma arquitetura simples dividida em três camadas:

🐍 Python

Responsável pela visão computacional e captura de dados da câmera, identificando a presença de caixas e registrando os tempos do processo.

☕ Java

Responsável pelo backend da aplicação, que recebe os dados do sistema de visão computacional e disponibiliza as informações para o frontend.
Funções principais:

- API para recebimento dos dados
- Processamento das métricas
- Integração com o dashboard

⚛️ React

Responsável pelo frontend da aplicação, onde será exibido um dashboard com os dados coletados.

O dashboard apresenta:
- Tempo de processamento das caixa
- Estatísticas do processo
- Informações de ociosidade da estação

👨‍💻 Equipe

Projeto desenvolvido como parte de atividade acadêmica do curso de Engenharia de Software – UNAERP.

Henrique Falasco de Souza
Rafael Golçalves Guerino
Miguel Mendes Sant'ana
Joao Filipe Betin
Leonardo Elias








