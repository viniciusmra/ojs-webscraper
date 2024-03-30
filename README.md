# OJS Web Scraper
Ferramenta para extrair metadados e baixar os arquivos em pdf das publicações das revistas da plataforma OJS da UFPI.

O objetivo é permitir o backup da plataforma antiga (revistas.ufpi.br) para facilitar a migração desses dados para a plataforma nova (periodicos.ufpi.br), ambas OJS, porém com versões diferentes.

O script foi construído em python.

## Como rodar?
Para rodar o script, um ambiente virtual deve ser configurado com as bibliotecadas e módulos necessários:

~~~ bash
python -m venv venv                 # instala o venv
.\venv\Scripts\activate             # ativa o venv
pip install -r requirements.txt     # instala as bilbiotecas necessários no ambiente virtual
~~~

Depois, é preciso entrar no arquivo ```main.py``` e inserir a URL da revista desejada e o nome da mesma (em ```journalArchiveURL``` e ```journalName``` respectivamente).

ATENÇÃO, a URL deve ser do arquivo da revista, por exemplo ```https://revistas.ufpi.br/index.php/NOME-DA-REVISTA/issue/archive```, que geralmente pode ser acessado clicando em "edições anteriores" na página incial da revista.

## Como funciona?
O presente script funciona usando o conceito de web scraper, ou seja, ele extrai os dados da internet de forma automatizada.
Para isso, são feitas requisições para a página da revista e a resposta (o código html da página) é então tratada usando a biblioteca ```beautifulsoup4```. 

Nessa etapa são extraidas informações relacionadas ao nome, ano, quantidade de artigos publicados de cada edição (ou issue) e os dados de cada artigo. Isso tudo é salvo em um dicionário que posteriormente é transformado em um json. Enquanto extrai os dados, o script exibe no console algumas informações sobre as publicações e a quantidade de artigos.

Depois, o dicionário com todas as informações da revista é convertido em um arquivo .json, que eventualment pode ser carregado e transformado em dicionário novamente, para que o usuário não precise extrair todas as informações da revista.

Para organizar e catalogar os dados, uma planilha do tipo XLS é criada. Ela guarda todas essas informações de uma forma mais amigável, sem a necessidade do usuário final precisar consultar o arquvio .json.

Por fim, o script percorre o dicionário e baixa todos os arquivos da revista e os organiza em pastas.

## Autor
<a href="https://github.com/viniciusmra"><img src="https://badgen.net/badge/icon/Vinícius%20Alves/blue?icon=github&label" alt="Creator badge" /></a>
