# IR Calculator

Este reposisitório contém uma calculadora de imposto de renda automatizado. Seu desenvolvimento se deu para automatizar o processo de calcular o lucro/prejuízo e imposto sobre operações, tendo como base as notas de corretagem.

# Features

* Extração de notas de corretagem PDF para CSV, XLSX e ODS
* Cálculo de lucro sobre operações 
* Cálculo de imposto
* Operações separadas automaticamente entre DayTrade e SwingTrade
* Leitura de notas das corretoras Clear, RICO e XP Investimentos

# TODO

[] Geração automática de DARF <br>
[] GUI <br>
[] Suporte a mais corretoras <br>

# Requirements

É necessário possuir o [GhostScript](https://www.ghostscript.com/releases/index.html) e o binário deve estar no PATH.

As bibliotecas do Python estão listadas no arquivo ` src\requirements.txt ` e podem ser instaladas com o seguinte comando

```bash
# Linux
pip3 instal -r src\requirements.txt

# Windows
pip install -r src\requirements.txt
```

# Contributing

Você pode contribuir criado issues, ou seguindo o padrão do [github de contribuições](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project?platform=linux).

Este projeto iniciou-se de uma necessidade e não foi pensado para ser aberto, portanto neste momento não segue as melhores práticas de desenvolvimento e você irá encontrar funções com 50+ linhas, arquivos com 200+ linhas, ainda é necessário adicionar testes, refatorar várias partes do código, empregar padrões de projeto adequados. Sinta-se livre para contribuir nestes aspectos. Mesmo que seja com a simples refatoração de uma função. :)

Se você gostou do projeto ou achou útil de alguma forma deixe sua estrelinha no GitHub.

# Known issues and limitations

* Não existe suporte para notas de corretagem de DayTrade da BMF <br>

# Disclaimer

Este projeto foi feito para uso pessoal, não me resposabilizo por qualquer cálculo errado e eventuais problemas com a RFB.

*USE POR SUA CONTA E RISCO*
