from typing import Tuple, List
import camelot
from camelot.core import TableList
import pandas as pd
from pdfminer.layout import LTRect, LTPage
import PyPDF2
import re
import functools
import pdfminer.high_level

import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.nota import NotaCorretagem

# import convert_gs

def getLTRectFromAllPages(pdf_file_path) -> List[pd.DataFrame]:
    return list(map(getLTRectFromPage, pdfminer.high_level.extract_pages(pdf_file_path)))

def getLTRectFromPage(page: LTPage) -> pd.DataFrame:
    lt_rect_objects = filter(lambda x: isinstance(x, LTRect), page)
    
    df_values = [{
         'x0': object.x0, 
         'y0': object.y0, 
         'x1': object.x1, 
         'y1': object.y1, 
         'height': object.height, 
         'width': object.width}
          for object in lt_rect_objects]
    
    return pd.DataFrame(df_values)

def toStringList(columns : pd.Series | list) -> str:
    if isinstance(columns, pd.Series):
        columns = columns.to_list()

    return str(columns).replace('[', '').replace(']', '')

def transformarColunas(colunas_transformar : list, largura : float) -> list:
    return list(map(lambda x: x * largura / 100.0, colunas_transformar))

def transformarAreas(area_transformar : List[float], largura : float, altura : float):
    area_transformar[0] *=  largura / 100.0
    area_transformar[1] *=  altura / 100.0
    area_transformar[2] *=  largura / 100.0
    area_transformar[3] *=  altura / 100.0

    return area_transformar

# Typical PT-BR number format is 1.000,00
# Convert it to 1000.00, so can be parsed as float or Decimal
def convertPTBRToNormalizedString(input_string : str) -> str:
    input_string = input_string.replace('.', '')
    input_string = input_string.replace(',', '.')
    return input_string

def preencheInformacoesNota(nota_corretagem : NotaCorretagem, tabela : TableList) -> NotaCorretagem:
    nota_corretagem.informacoes_nota.loc['Nr. nota'] = tabela[0].df.iloc[1, 0]
    nota_corretagem.informacoes_nota.loc['Data Pregão'] = tabela[0].df.iloc[1, 2]

    return nota_corretagem

def preencheInformacoesIdentificacao(nota_corretagem : NotaCorretagem, tabela : TableList) -> NotaCorretagem:
    nota_corretagem.informacoes_identificacao.loc['Nome Corretora'] = tabela[1].df.iloc[0, 0]
    nota_corretagem.informacoes_identificacao.loc['CNPJ Corretora'] = tabela[1].df.iloc[4, 0].replace('C.N.P.J: ', '')
    nota_corretagem.informacoes_identificacao.loc['Nome Cliente'] = tabela[2].df.iloc[1, 1]
    nota_corretagem.informacoes_identificacao.loc['Número Cliente'] = tabela[2].df.iloc[1, 0]
    nota_corretagem.informacoes_identificacao.loc['CPF Cliente'] = tabela[3].df.iloc[1, 0]
    nota_corretagem.informacoes_identificacao.loc['Código Cliente'] = tabela[3].df.replace('[ ]+', ' ', regex=True).iloc[3, 0]
    
    # Verifica se foram lidas as informações de banco
    if len(tabela[8].df.index) > 1:
        nota_corretagem.informacoes_identificacao.loc['Banco'] = tabela[8].df.iloc[1, 0]
        nota_corretagem.informacoes_identificacao.loc['Agência'] = tabela[8].df.iloc[1, 1]
        nota_corretagem.informacoes_identificacao.loc['Conta'] = tabela[8].df.iloc[1, 2]
    else:
        nota_corretagem.informacoes_identificacao.loc['Banco'] = 0
        nota_corretagem.informacoes_identificacao.loc['Agência'] = 0
        nota_corretagem.informacoes_identificacao.loc['Conta'] = 0

    return nota_corretagem

def preencheNegociosRealizados(nota_corretagem : NotaCorretagem, tabela : TableList) -> NotaCorretagem:
    tabela[12].df.columns = nota_corretagem.negocios_realizados.columns
    nota_corretagem.negocios_realizados = pd.concat([nota_corretagem.negocios_realizados, tabela[12].df], ignore_index=True)

    # Remove espaços repetidos
    nota_corretagem.negocios_realizados = nota_corretagem.negocios_realizados.replace('[ ]+', ' ', regex=True)
    
    # Converte para float os valores numéricos
    nota_corretagem.negocios_realizados = nota_corretagem.negocios_realizados.map(convertPTBRToNormalizedString)

    nota_corretagem.negocios_realizados = nota_corretagem.negocios_realizados.astype(
        {
            "Q" : str,
            "Negociação": str,
            "C/V" : str,
            "Tipo mercado" : str,
            "Prazo" : str, 
            "Especificação do título" : str,
            "Obs. (*)" : str,
            "Quantidade" : int,
            "Preço / Ajuste" : float,
            "Valor Operação / Ajuste" : float,
            "D/C" : str,
        }
    )

    return nota_corretagem

def preencheResumoDosNegocios(nota_corretagem : NotaCorretagem, tabela : TableList) -> NotaCorretagem:
    # Converte os valores da tabela para float
    tabela[15].df.iloc[:, 1] = tabela[15].df.iloc[:, 1].apply(convertPTBRToNormalizedString)
    tabela[15].df = tabela[15].df.astype({0:str, 1:float})
    
    nota_corretagem.resumo_dos_negocios.loc['Debêntures'] = tabela[15].df.iloc[0,1]
    nota_corretagem.resumo_dos_negocios.loc['Vendas à vista'] = tabela[15].df.iloc[1, 1]
    nota_corretagem.resumo_dos_negocios.loc['Compras à vista'] = tabela[15].df.iloc[2, 1]
    nota_corretagem.resumo_dos_negocios.loc['Opções - compras'] = tabela[15].df.iloc[3, 1]
    nota_corretagem.resumo_dos_negocios.loc['Opções - vendas'] = tabela[15].df.iloc[4, 1]
    nota_corretagem.resumo_dos_negocios.loc['Operações à termo'] = tabela[15].df.iloc[5, 1]
    nota_corretagem.resumo_dos_negocios.loc['Valor das oper. c/ títulos públ. (v. nom.)'] = tabela[15].df.iloc[6, 1]
    nota_corretagem.resumo_dos_negocios.loc['Valor das operações'] = tabela[15].df.iloc[7, 1]
    
    base, projecao = (0.0, 0.0)
    if tabela[16].df.shape == (3, 1):
        base, projecao = extractIRRFDayTradeBaseAndProjectionFromString(tabela[16].df.iloc[2,0])
    nota_corretagem.resumo_dos_negocios.loc['IRRF DayTrade base'] = base
    nota_corretagem.resumo_dos_negocios.loc['IRRF DayTrade retido'] = projecao

    return nota_corretagem

def extractIRRFDayTradeBaseAndProjectionFromString(base_string:str) -> Tuple[float, float]:
    regex = re.compile(r"(Base\s+R\$\s?(\d+,\d+))\s?(Projeção\s+R\$\s?(\d+,\d+))")
    search_groups = regex.search(base_string)
    base = convertPTBRToNormalizedString(search_groups.group(2))
    projection = convertPTBRToNormalizedString(search_groups.group(4))
    return (float(base), float(projection))

def preencheResumoFinanceiro(nota_corretagem : NotaCorretagem, tabela : TableList) -> NotaCorretagem:
    # Quando é débito, o valor é salvo como negativo, quando é crédito é salvo como positivo        
    tabela[13].df.iloc[:, 1] = tabela[13].df.iloc[:, 1].apply(convertPTBRToNormalizedString)
    tabela[13].df = tabela[13].df.astype({0:str, 1:float, 2:str})
    tabela[13].df.iloc[:, 1] = tabela[13].df.iloc[:, 1].mask(tabela[13].df.iloc[:, 2] == 'D', -tabela[13].df.iloc[:, 1])

    nota_corretagem.resumo_financeiro.loc['Valor líquido das operações'] = tabela[13].df.iloc[0, 1]
    nota_corretagem.resumo_financeiro.loc['Taxa de liquidação'] = tabela[13].df.iloc[1, 1]
    nota_corretagem.resumo_financeiro.loc['Taxa de Registo'] = tabela[13].df.iloc[2, 1]
    nota_corretagem.resumo_financeiro.loc['Total CLBC'] = tabela[13].df.iloc[3, 1]

    # Quando é débito, o valor é salvo como negativo, quando é crédito é salvo como positivo        
    tabela[14].df.iloc[:, 1] = tabela[14].df.iloc[:, 1].apply(convertPTBRToNormalizedString)
    tabela[14].df = tabela[14].df.astype({0:str, 1:float, 2:str})
    tabela[14].df.iloc[:, 1] = tabela[14].df.iloc[:, 1].mask(tabela[14].df.iloc[:, 2] == 'D', -tabela[14].df.iloc[:, 1])

    nota_corretagem.resumo_financeiro.loc['Taxa de termo/opções'] = tabela[14].df.iloc[0, 1]
    nota_corretagem.resumo_financeiro.loc['Taxa A.N.A.'] = tabela[14].df.iloc[1, 1]
    nota_corretagem.resumo_financeiro.loc['Emolumentos'] = tabela[14].df.iloc[2, 1]
    nota_corretagem.resumo_financeiro.loc['Total Bovespa / Soma'] = tabela[14].df.iloc[3, 1]

    # Quando é débito, o valor é salvo como negativo, quando é crédito é salvo como positivo        
    tabela[17].df.iloc[:, 1] = tabela[17].df.iloc[:, 1].apply(convertPTBRToNormalizedString)
    tabela[17].df = tabela[17].df.astype({0:str, 1:float, 2:str})
    tabela[17].df.iloc[:, 1] = tabela[17].df.iloc[:, 1].mask(tabela[17].df.iloc[:, 2] == 'D', -tabela[17].df.iloc[:, 1])

    nota_corretagem.resumo_financeiro.loc['Taxa Operacional'] = tabela[17].df.iloc[0, 1]
    nota_corretagem.resumo_financeiro.loc['Execução'] = tabela[17].df.iloc[1, 1]
    nota_corretagem.resumo_financeiro.loc['Taxa de Custódia'] = tabela[17].df.iloc[2, 1]
    nota_corretagem.resumo_financeiro.loc['Impostos'] = tabela[17].df.iloc[3, 1]
    
    nota_corretagem.resumo_financeiro.loc['IRRF SwingTrade base'] = extractBaseValueFromIRRFString(tabela[17].df.iloc[4, 0])
    nota_corretagem.resumo_financeiro.loc['IRRF SwingTrade retido'] = tabela[17].df.iloc[4, 1]
    nota_corretagem.resumo_financeiro.loc['Outros'] = tabela[17].df.iloc[5, 1]
    nota_corretagem.resumo_financeiro.loc['Total Custos / Despesas'] = tabela[17].df.iloc[6, 1]
    nota_corretagem.resumo_financeiro.loc['Líquido'] = tabela[17].df.iloc[7, 1]

    return nota_corretagem

def extractBaseValueFromIRRFString(irrf_string:str) -> float:
    regex = re.compile(r"(base\s+R\$\s?)(\d+(\.\d+)?,\d+)")
    result = regex.search(irrf_string).group(2)
    value = convertPTBRToNormalizedString(result)
    return float(value)

def getNumeroPaginas(caminho_pdf) -> int:
    leitor = PyPDF2.PdfReader(caminho_pdf)
    numero_paginas = len(leitor.pages)

    return numero_paginas 

def getDimensoesPagina(caminho_pdf) -> Tuple[float, float]:
    leitor = PyPDF2.PdfReader(caminho_pdf)
    dimesoes = leitor.pages[0].mediabox.upper_right

    return dimesoes

def getAreasConvertidas(areas_original : pd.Series, largura : float = 595, altura : float = 842):
    return areas_original.copy().apply(lambda x: toStringList(transformarAreas(x, largura, altura)))

def getColunasConvertidas(colunas_original : pd.Series, largura : float = 595) -> pd.Series:
    return colunas_original.copy().apply(lambda x: toStringList(transformarColunas(x, largura)))

def extractPDF(
    caminho_pdf,
    extrair_negocios : bool = True,
    extrair_resumos : bool = True,
    extrair_informacoes_corretora : bool = True,
) -> List[NotaCorretagem]:
    """
        Extrai uma nota de corretagem e retorna uma lista com as notas
        
        IMPORTANTE: O PDF PASSADO DEVE TER SIDO CONVERTIDO COM O GHOSTSCRIPT PRIMEIRO

        caminho_pdf: Caminho para o arquivo que será extraído
        extrair_negocios: boolean extrair a tabela negócios realizados do PDF, default True
        extrair_resumos: boolean extrair a tabela de resumos do PDF, default True
        extrair_informacoes_corretora: boolean extrair as informações de cliente e corretora do cabeçalho do PDF, default True
    """

    notas = []

    if not (extrair_negocios or extrair_resumos or extrair_informacoes_corretora):
        return notas
    
    largura, altura = getDimensoesPagina(caminho_pdf)

    areas = getAreasConvertidas(AREAS, largura=float(largura), altura=float(altura))
    colunas = getColunasConvertidas(COLUNAS, largura=float(largura))
    
    for index, page_layout in enumerate(pdfminer.high_level.extract_pages(caminho_pdf)):
        page_ltrects = getLTRectFromPage(page_layout)
        page_ltrects = page_ltrects.where(page_ltrects.loc[:, "height"].between(ALTURA_LTRECT_NEGOCIOS_INFERIOR * altura, ALTURA_LTRECT_NEGOCIOS_SUPERIOR * altura)).dropna()
        page_ltrects = page_ltrects.drop_duplicates(subset=['x0'], keep='first')
        
        colunas["negociacoes"] = toStringList(page_ltrects.loc[2:, 'x0'])

        tabela = camelot.read_pdf(
            filepath=caminho_pdf, 
            table_areas=areas.values, 
            columns=colunas.values, 
            pages=str(index + 1), 
            split_text=True, 
            strip_text='\n', 
            suppress_stdout=True, 
            flavor='stream'
        )
        
        nota_atual = NotaCorretagem()

        nota_atual = preencheInformacoesNota(nota_atual, tabela)
        
        if extrair_informacoes_corretora:
            nota_atual = preencheInformacoesIdentificacao(nota_atual, tabela)
        
        if extrair_negocios:
            nota_atual = preencheNegociosRealizados(nota_atual, tabela)
        
        if extrair_resumos:
            extracao_resumos_bem_sucedida = tabela[14].df.iloc[2,1].upper() != 'CONTINUA...'
            
            if extracao_resumos_bem_sucedida:
                preencheResumoDosNegocios(nota_atual, tabela)
                preencheResumoFinanceiro(nota_atual, tabela)

        notas.append(nota_atual)

    return notas

def concatenationFunction(x: pd.DataFrame, y : pd.DataFrame) -> pd.DataFrame:
    if x.empty:
        return y
    if y.empty:
        return x
    return pd.concat([x,y], axis='index', ignore_index=True)

def getNotasAgrupadas(notas : List[NotaCorretagem]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_negocios = functools.reduce(concatenationFunction, map(lambda x: x.getNegociosEData(), notas))
    df_resumos = functools.reduce(concatenationFunction, map(lambda x: x.getResumosEData(), notas))
    df_informacoes = functools.reduce(concatenationFunction, map(lambda x: x.getInformacoes(), notas))

    return (df_informacoes, df_negocios, df_resumos)

def salvarCSV(notas : List[NotaCorretagem], caminho):
    df_informacoes, df_negocios, df_resumos = getNotasAgrupadas(notas)
    
    if not df_informacoes.empty:
        df_informacoes.to_csv(caminho+'_informacoes.csv', index=False)
    if not df_negocios.empty:
        df_negocios.to_csv(caminho+'_negocios.csv', index=False, decimal=',')
    if not df_resumos.empty:
        df_resumos.to_csv(caminho+'_resumos.csv', index=False, decimal=',')

def salvarODS(notas : List[NotaCorretagem], caminho, agrupar : bool = True):
    df_informacoes, df_negocios, df_resumos = getNotasAgrupadas(notas)
    
    if agrupar:
        with pd.ExcelWriter(
            path=caminho+'.ods',
        ) as writer:
            if not df_negocios.empty:
                df_negocios.to_excel(writer, sheet_name='Negócios', index=False)
            if not df_resumos.empty:
                df_resumos.to_excel(writer, sheet_name='Resumos', index=False)
            if not df_informacoes.empty:
                df_informacoes.to_excel(writer, sheet_name='Informações', index=False)
    else:
        if not df_informacoes.empty:
            df_informacoes.to_excel(caminho+'_informacoes.ods', sheet_name='Informações', index=False)
        if not df_negocios.empty:
            df_negocios.to_excel(caminho+'_negocios.ods', sheet_name='Negócios', index=False)
        if not df_resumos.empty:
            df_resumos.to_excel(caminho+'_resumos.ods', sheet_name='Resumos', index=False)

def salvarXLSX(notas : List[NotaCorretagem], caminho, agrupar : bool = True):
    df_informacoes, df_negocios, df_resumos = getNotasAgrupadas(notas)
    
    if agrupar:
        with pd.ExcelWriter(
            path=caminho+'.xlsx',
        ) as writer:
            if not df_negocios.empty:
                df_negocios.to_excel(writer, sheet_name='Negócios', index=False)
            if not df_resumos.empty:
                df_resumos.to_excel(writer, sheet_name='Resumos', index=False)
            if not df_informacoes.empty:
                df_informacoes.to_excel(writer, sheet_name='Informações', index=False)
    else:
        if not df_informacoes.empty:
            df_informacoes.to_excel(caminho+'_informacoes.xlsx', sheet_name='Informações', index=False)
        if not df_negocios.empty:
            df_negocios.to_excel(caminho+'_negocios.xlsx', sheet_name='Negócios', index=False)
        if not df_resumos.empty:
            df_resumos.to_excel(caminho+'_resumos.xlsx', sheet_name='Resumos', index=False)

####################################################################################################

# Estes valores estão representados como porcentagem da folha
# é necessário ler a resolução do pdf e converter para coordenadas no pdf
# se nada for mudado a resolução é altura = 842, largura = 595, isso com a resolução de 300ppi padrão

## Esta ordem é muito importante, não pode ser alterada, deve estar ordenado de acordo com o valor do y1
# lembrando que os valores estão [x0, y0, x1, y1]
AREAS = pd.Series({
    "data" :                                        [72.18, 93.70, 94.37, 91.51],
    "informacoes_corretora" :                       [ 5.53, 91.30, 94.37, 83.15],
    "informacoes_cliente" :                         [ 5.53, 82.95, 71.12, 78.70],
    "cpf" :                                         [71.51, 82.95, 94.37, 78.70],
    "informacoes_participante_destino_repasse" :    [ 5.53, 78.50, 38.57, 76.58],
    "campo_cliente" :                               [38.86, 78.50, 54.07, 76.58],
    "informacoes_valor" :                           [54.36, 78.50, 71.12, 76.58],
    "informacoes_custodiante" :                     [71.51, 78.50, 94.37, 76.58],
    "informacoes_conta_corrente" :                  [ 5.53, 76.38, 38.57, 74.53],
    "informacoes_acionista" :                       [38.86, 76.38, 54.07, 74.53],
    "informacoes_administrador" :                   [54.36, 76.38, 71.12, 74.53],
    "informacoes_complemento_nome" :                [71.51, 76.38, 94.37, 74.53],
    "negociacoes" :                                 [ 5.53, 70.25, 94.37, 47.50],
    "resumo_financeiro_clearing" :                  [50.39, 44.13, 94.08, 39.81],
    "resumo_financeiro_bolsa" :                     [50.39, 38.72, 94.08, 34.47],
    "resumo_dos_negocios" :                         [ 5.53, 45.29, 50.10, 34.20],
    "day_trade" :                                   [ 5.53, 34.20, 50.10, 24.02],
    "resumo_financeiro_custos_operacionais" :       [50.39, 33.31, 94.08, 23.04],
})

COLUNAS = pd.Series({
    "data" : [79.65, 86.43],
    "informacoes_corretora" : [65.54],
    "informacoes_cliente" : [22.68, 56.47],
    "cpf" : [],
    "informacoes_participante_destino_repasse" : [],
    "campo_cliente" : [],
    "informacoes_valor" : [],
    "informacoes_custodiante" : [],
    "informacoes_conta_corrente" : [],
    "informacoes_acionista" : [],
    "informacoes_administrador" : [],
    "informacoes_complemento_nome" : [],
    "negociacoes" : [],
    "resumo_financeiro_clearing" : [73.44, 91.76],
    "resumo_financeiro_bolsa" : [73.44, 91.76],
    "resumo_dos_negocios" : [33.61],
    "day_trade" : [],
    "resumo_financeiro_custos_operacionais" : [73.44, 91.76],
})

ALTURA_LTRECT_NEGOCIOS_INFERIOR = 0.0109263657957
ALTURA_LTRECT_NEGOCIOS_SUPERIOR = 0.0109857482185

if __name__ == '__main__':
    # caminho_pdf = "C:/Users/jelso/Desktop/Investimentos/Notas/Rico/2022/6648793_NotaCorretagem_04.pdf"

    # convert_gs.convert_file_with_ghostscript(caminho_pdf)

    # caminho_pdf = "C:/Users/jelso/Documents/Scripts/ir_calculator/2204318_NotaCorretagem.pdf"
    caminho_pdf = "C:/Users/jelso/Documents/Scripts/ir_calculator/NOTA_CORRETAGEM_2021_02.pdf"
    notas = extractPDF(caminho_pdf)
    #salvarXLSX(notas, caminho_pdf)

    salvarODS(notas, caminho=caminho_pdf.removesuffix('.pdf'))

"""
Permitir a leitura das coordenadas apartir de um arquivo externo, 
isso possibilitaria a adaptação para leitura de outras
notas de corretagem de outras corretoras
No futuro, fazer uma Inteligência Artificial que ache as coordenadas
das notas, para que seja possível ler de qualquer corretora
"""