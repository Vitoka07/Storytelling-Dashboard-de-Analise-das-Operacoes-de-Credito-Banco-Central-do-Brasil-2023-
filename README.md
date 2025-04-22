# 📊 Dashboard de Análise das Operações de Crédito – Banco Central do Brasil (2023)

![credito](https://github.com/user-attachments/assets/f1a8bec2-9d06-424f-b6c1-31ced8622d10)

# Sobre o projeto

Este projeto é um dashboard interativo desenvolvido com Streamlit para explorar os dados históricos das operações de crédito disponibilizados pelo Banco Central do Brasil em 2023. O objetivo é fornecer uma visão clara e acessível das principais estatísticas relacionadas a concessões, modalidades, inadimplência e tipos de cliente (PF ou PJ).

## Descrição
A aplicação foi construída utilizando Streamlit como framework para a interface interativa, permitindo a visualização de gráficos e informações em tempo real. 

O dashboard explora dados de 2023, oferecendo análise detalhada sobre as operações de crédito, com agrupamento por regiões, identificação de inadimplência e distribuição por tipo de cliente.

O usuário pode interagir com o painel para visualizar os dados de diferentes perspectivas e tomar decisões informadas sobre as operações de crédito no Brasil.

#  Funcionalidades 🔍
 - 📈 Concessões: Volume de operações por modalidade e tempo.
 - 💳 Modalidades: Quais modalidades concentram mais operações.
 - ⚠️ Inadimplência: Perfil de inadimplência por região e valor.
 - 🌎 Regiões: Agrupamento das informações por região do Brasil.

![grafico 2](https://github.com/user-attachments/assets/12a25a8a-a12e-4ce6-9857-c5f95e4c25d8)

![image](https://github.com/user-attachments/assets/161b4102-b347-46fc-8479-0840ce066d76)

## Tecnologias Utilizadas 👨‍💻:
 - Python
 - Streamlit
 - Pandas
 - Plotly / Matplotlib / Seaborn
 - NumPy

## Instalação apos Download do projeto
No terminal (recomenda-se o uso do VSCode), execute:

Lembre-se de baixar a base e alterar o caminho de leitura do .Csv
Base: https://www.bcb.gov.br/pda/desig/planilha_2023.zip

```bash
# development
$ pip install -r requirements.txt

## Executando o projeto

$ streamlit run app.py

## License

[MIT licensed](LICENSE).
