import pandas as pd

class NotaCorretagem:
    def __init__(self):
        self.informacoes_nota = pd.Series(
            index = [
                "Nr. nota",
                "Data Pregão"
            ],
            dtype=object
        )

        self.informacoes_identificacao = pd.Series(
            index = [
                "Nome Corretora",
                "CNPJ Corretora",
                "Nome Cliente",
                "CPF Cliente",
                "Número Cliente",
                "Código Cliente",
                "Banco",
                "Agência",
                "Conta",
            ],
            dtype=object
        )

        self.negocios_realizados = pd.DataFrame(
            columns = [
                'Q',
                'Negociação',
                'C/V',
                'Tipo mercado', 
                'Prazo', 
                'Especificação do título', 
                'Obs. (*)', 
                'Quantidade', 
                'Preço / Ajuste', 
                'Valor Operação / Ajuste', 
                'D/C', 
            ]
        )

        self.resumo_dos_negocios = pd.Series(
            index = [
                "Debêntures",
                "Vendas à vista",
                "Compras à vista",
                "Opções - compras",
                "Opções - vendas",
                "Operações à termo",
                "Valor das oper. c/ títulos públ. (v. nom.)",
                "Valor das operações",
                "IRRF DayTrade base",
                "IRRF DayTrade retido",
            ],
            dtype=float
        )

        self.resumo_financeiro = pd.Series(
            index = [
                "Valor líquido das operações",
                "Taxa de liquidação",
                "Taxa de Registo",
                "Total CLBC",
                "Taxa de termo/opções",
                "Taxa A.N.A.",
                "Emolumentos",
                "Total Bovespa / Soma",
                "Taxa Operacional",
                "Execução",
                "Taxa de Custódia",
                "Impostos",
                "IRRF SwingTrade base",
                "IRRF SwingTrade retido",
                "Outros",
                "Total Custos / Despesas",
                "Líquido",
            ],
            dtype=float
        )
    
    def salvar(self, nome_arquivo):
        self.getNegociosNaData().to_csv(nome_arquivo, index=False)
    
    def getNegociosEData(self) -> pd.DataFrame:
        resultado = self.negocios_realizados.dropna().copy(deep=True)

        if resultado.empty:
            resultado = resultado.reindex(columns = resultado.columns.tolist() + ['Nr. nota', 'Data Pregão'])

        else:
            resultado.loc[:, "Nr. nota"] = self.informacoes_nota.loc["Nr. nota"]
            resultado.loc[:, "Data Pregão"] = self.informacoes_nota.loc["Data Pregão"]
            resultado["Data Pregão"] = pd.to_datetime(resultado.loc[:, "Data Pregão"], dayfirst=True, format='%d/%m/%Y')

            resultado = resultado.astype(
                {
                    'Q' : str,
                    'Negociação' : str,
                    'C/V' : str,
                    'Tipo mercado' : str, 
                    'Prazo' : str, 
                    'Especificação do título' : str, 
                    'Obs. (*)' : str, 
                    'Quantidade' : int, 
                    'Preço / Ajuste' : float, 
                    'Valor Operação / Ajuste' : float, 
                    'D/C' : str,
                    'Nr. nota' : int,
                    'Data Pregão' : 'datetime64[ns]'
                }
            )

        return resultado
    
    def getResumosEData(self) -> pd.DataFrame:
        resumo_dos_negocios = self.resumo_dos_negocios.to_frame().T.dropna().copy(deep=True)
        resumo_financeiro = self.resumo_financeiro.to_frame().T.dropna().copy(deep=True)
        data = self.informacoes_nota.to_frame().T.dropna().copy(deep=True)

        resultado = pd.concat([resumo_dos_negocios, resumo_financeiro], axis='columns')
        
        if resultado.empty:
            # Adiciona as colunas Nr. nota e Data Pregão vazias ao resultado
            resultado = resultado.reindex(columns = resultado.columns.tolist() + ['Nr. nota', 'Data Pregão'])
        
        else:
            resultado = pd.concat([resultado, data], axis='columns')
            resultado["Data Pregão"] = pd.to_datetime(resultado.loc[:, "Data Pregão"], dayfirst=True, format='%d/%m/%Y')

            resultado = resultado.astype(
                {
                    "Debêntures" : float,
                    "Vendas à vista" : float,
                    "Compras à vista" : float,
                    "Opções - compras" : float,
                    "Opções - vendas" : float,
                    "Operações à termo" : float,
                    "Valor das oper. c/ títulos públ. (v. nom.)" : float,
                    "Valor das operações" : float,
                    "IRRF DayTrade base" : float,
                    "IRRF DayTrade retido" : float,
                    "Valor líquido das operações" : float,
                    "Taxa de liquidação" : float,
                    "Taxa de Registo" : float,
                    "Total CLBC" : float,
                    "Taxa de termo/opções" : float,
                    "Taxa A.N.A." : float,
                    "Emolumentos" : float,
                    "Total Bovespa / Soma" : float,
                    "Taxa Operacional" : float,
                    "Execução" : float,
                    "Taxa de Custódia" : float,
                    "Impostos" : float,
                    "IRRF SwingTrade base" : float,
                    "IRRF SwingTrade retido" : float,
                    "Outros" : float,
                    "Total Custos / Despesas" : float,
                    "Líquido" : float,
                    "Nr. nota" : int,
                    "Data Pregão" : 'datetime64[ns]'
                }
            )

        return resultado

    def getInformacoes(self) -> pd.DataFrame:
        resultado = self.informacoes_identificacao.to_frame().T.dropna().copy(deep=True)
        data = self.informacoes_nota.to_frame().T.dropna().copy(deep=True)

        if resultado.empty:
            resultado = resultado.reindex(columns = resultado.columns.tolist() + ['Nr. nota', 'Data Pregão'])
        else:
            resultado = pd.concat([resultado, data], axis='columns')
            resultado["Data Pregão"] = pd.to_datetime(resultado.loc[:, "Data Pregão"], dayfirst=True, format='%d/%m/%Y')

            resultado = resultado.astype(
                {
                    'Nome Corretora' : str,
                    'CNPJ Corretora' : str,
                    'Nome Cliente' : str,
                    'CPF Cliente' : str,
                    'Número Cliente' : int,
                    'Código Cliente' : str,
                    'Banco' : int,
                    'Agência' : int,
                    'Conta' : int,
                    'Nr. nota' : int,
                    'Data Pregão' : 'datetime64[ns]'
                }
            )

        return resultado
