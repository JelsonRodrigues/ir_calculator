import pandas as pd
import numpy as np
from decimal import *
from common.taxas import Taxas
from typing import Literal, Tuple

# Define a precisao dos decimais
getcontext().prec = 32

def contabiliza(
        linha : pd.Series,
        ativos : pd.DataFrame, 
        taxas_cobradas_nesta_operacao : Decimal,
    ) -> Tuple[pd.DataFrame, Decimal]:
    nome_ativo = linha.loc['Especificação do título'].upper()
    eh_compra = 'C' in linha.loc['C/V'].upper()
    lucro = Decimal('0.0')

    linha.loc['Taxas Operação'] = taxas_cobradas_nesta_operacao

    # Compra de um ativo
    if eh_compra:
        # Já está no dataframe de ativos
        if nome_ativo in ativos.loc[:, 'Especificação do título']:
            # Fechando uma posição vendida, ou invertendo a posição
            if ativos.at[nome_ativo, 'Quantidade'] < 0.0:
                # Foi invertida a posição - a compra atual é maior que o que estava vendido
                taxa_media_por_quantidade_ativo = ativos.at[nome_ativo, 'Taxas Operação'] / ativos.at[nome_ativo, 'Quantidade']
                preco_medio_ativo = ativos.at[nome_ativo, 'Preço / Ajuste'] - taxa_media_por_quantidade_ativo
                taxa_media_por_quantidade_linha = linha.loc['Taxas Operação'] / linha.loc['Quantidade']
                preco_medio_linha = linha.loc['Preço / Ajuste'] + taxa_media_por_quantidade_linha
                if (linha.loc['Quantidade'] > abs(ativos.at[nome_ativo, 'Quantidade'])):
                    lucro = abs(ativos.at[nome_ativo, 'Quantidade']) * (preco_medio_ativo - preco_medio_linha)

                    ativos.at[nome_ativo, 'Taxas Operação'] = abs((abs(ativos.at[nome_ativo, 'Quantidade']) - abs(linha.loc['Quantidade'])) * taxa_media_por_quantidade_linha)
                    ativos.at[nome_ativo, 'Preço / Ajuste'] = linha.loc['Preço / Ajuste']
                    ativos.at[nome_ativo, 'C/V'] = linha.loc['C/V']
                    ativos.at[nome_ativo, 'D/C'] = linha.loc['D/C']
                    ativos.at[nome_ativo, 'Nr. nota'] = linha.loc['Nr. nota']
                    ativos.at[nome_ativo, 'Data Pregão'] = linha.loc['Data Pregão']
                else:
                    lucro = linha.loc['Quantidade'] * (preco_medio_ativo - preco_medio_linha)

                    ativos.at[nome_ativo, 'Taxas Operação'] = abs((abs(ativos.at[nome_ativo, 'Quantidade']) - abs(linha.loc['Quantidade'])) * taxa_media_por_quantidade_ativo)

                ativos.at[nome_ativo, 'Quantidade'] += linha['Quantidade']
                ativos.at[nome_ativo, 'Valor Operação / Ajuste'] = ativos.at[nome_ativo, 'Quantidade'] * ativos.at[nome_ativo, 'Preço / Ajuste']
            # Aumentando uma posição já comprada
            else:
                ativos.at[nome_ativo, 'Quantidade'] += linha['Quantidade']
                ativos.at[nome_ativo, 'Valor Operação / Ajuste'] += linha['Valor Operação / Ajuste']
                ativos.at[nome_ativo, 'Taxas Operação'] += linha['Taxas Operação']
                # Recalcula o preço médio
                if ativos.at[nome_ativo, 'Quantidade'] != 0: # Previne divisão por zero
                    ativos.at[nome_ativo, 'Preço / Ajuste'] = abs(ativos.at[nome_ativo, 'Valor Operação / Ajuste'] / ativos.at[nome_ativo, 'Quantidade'])
        
        # Ainda não está no dataframe ativos, adiciona
        else:
            ativos = pd.concat([ativos, linha.to_frame().T])
            ativos.set_index(ativos['Especificação do título'], inplace=True)
    else:
        # Já está no dataframe de ativos
        if nome_ativo in ativos.loc[:, 'Especificação do título']:
            # Fechando uma posição comprada, ou invertendo a posição
            if ativos.at[nome_ativo, 'Quantidade'] > 0.0:
                # Foi invertida a posição - a venda atual é maior que o que estava comprado
                taxa_media_por_quantidade_ativo = ativos.at[nome_ativo, 'Taxas Operação'] / ativos.at[nome_ativo, 'Quantidade']
                preco_medio_ativo = ativos.at[nome_ativo, 'Preço / Ajuste'] + taxa_media_por_quantidade_ativo
                taxa_media_por_quantidade_linha = linha.loc['Taxas Operação'] / linha.loc['Quantidade']
                preco_medio_linha = linha.loc['Preço / Ajuste'] - taxa_media_por_quantidade_linha
                if (linha.loc['Quantidade'] > abs(ativos.at[nome_ativo, 'Quantidade'])):
                    lucro = abs(ativos.at[nome_ativo, 'Quantidade']) * (preco_medio_linha - preco_medio_ativo)
                    
                    ativos.at[nome_ativo, 'Taxas Operação'] = abs((abs(ativos.at[nome_ativo, 'Quantidade']) - abs(linha.loc['Quantidade'])) * taxa_media_por_quantidade_linha)
                    ativos.at[nome_ativo, 'Preço / Ajuste'] = linha.loc['Preço / Ajuste']
                    ativos.at[nome_ativo, 'C/V'] = linha.loc['C/V']
                    ativos.at[nome_ativo, 'D/C'] = linha.loc['D/C']
                    ativos.at[nome_ativo, 'Nr. nota'] = linha.loc['Nr. nota']
                    ativos.at[nome_ativo, 'Data Pregão'] = linha.loc['Data Pregão']
                else:
                    lucro = linha.loc['Quantidade'] * (preco_medio_linha - preco_medio_ativo)

                    ativos.at[nome_ativo, 'Taxas Operação'] = abs((abs(ativos.at[nome_ativo, 'Quantidade']) - abs(linha.loc['Quantidade'])) * taxa_media_por_quantidade_ativo)

                ativos.at[nome_ativo, 'Quantidade'] -= linha['Quantidade']
                ativos.at[nome_ativo, 'Valor Operação / Ajuste'] = ativos.at[nome_ativo, 'Quantidade'] * ativos.at[nome_ativo, 'Preço / Ajuste']
            # Aumentando uma posição já vendida
            else:
                ativos.at[nome_ativo, 'Quantidade'] -= linha['Quantidade']
                ativos.at[nome_ativo, 'Valor Operação / Ajuste'] += linha['Valor Operação / Ajuste']
                ativos.at[nome_ativo, 'Taxas Operação'] += linha.loc['Taxas Operação']
                # Recalcula o preço médio
                if ativos.at[nome_ativo, 'Quantidade'] != 0: # Previne divisão por zero
                    ativos.at[nome_ativo, 'Preço / Ajuste'] = abs(ativos.at[nome_ativo, 'Valor Operação / Ajuste'] / ativos.at[nome_ativo, 'Quantidade'])
        
        # Ainda não está no dataframe ativos, adiciona
        else:
            linha.loc['Quantidade'] *= -1
            ativos = pd.concat([ativos, linha.to_frame().T])
            ativos.set_index(ativos['Especificação do título'], inplace=True)
        
    # Quando a quantidade fica zero, a linha é excluída do dataframe dos ativos
    if ativos.at[nome_ativo, 'Quantidade'] == 0:
        ativos.drop(nome_ativo, inplace=True)

    return (ativos, lucro)

def unificaNegociosNaData(negocios_na_data : pd.DataFrame) -> pd.DataFrame:
    # Separa os negócios daytrade e swingtrade
    negocios_daytrade = negocios_na_data.where(negocios_na_data.loc[:, 'Obs. (*)'] == 'DAYTRADE').dropna()
    negocios_daytrade = negocios_daytrade.astype(negocios_na_data.dtypes)
    negocios_swingtrade = negocios_na_data.where(negocios_na_data.loc[:, 'Obs. (*)'] == 'SWINGTRADE').dropna()
    negocios_swingtrade = negocios_swingtrade.astype(negocios_na_data.dtypes)

    df_final = unificaNegociosPorPreco(negocios_daytrade)
    df_final = pd.concat([df_final, unificaNegociosPorPreco(negocios_swingtrade)], ignore_index=True)

    return df_final

def unificaNegociosPorPreco(negocios : pd.DataFrame) -> pd.DataFrame:
    # Cria o dataframe final
    df_final = pd.DataFrame(columns=negocios.columns)

    if not negocios.empty:
        # Filtra os diferentes ativos negociados
        ativos = negocios.loc[:, 'Especificação do título'].drop_duplicates(keep='first')

        for ativo in ativos:
            # Filtra as operações com o ativo
            negocios_ativo = negocios.where(negocios.loc[:, 'Especificação do título'] == ativo).dropna()

            compras_ativo = negocios_ativo.where(negocios.loc[:, 'C/V'] == 'C').dropna()
            compras_ativo = compras_ativo.astype(negocios.dtypes)
            precos_compras = compras_ativo.loc[:, 'Preço / Ajuste'].drop_duplicates(keep='first')

            for preco in precos_compras:
                linha_unificada = unificaOperacoes(compras_ativo, preco)
                df_final = pd.concat([df_final, linha_unificada.to_frame().T], ignore_index=True)
                
            vendas_ativo = negocios_ativo.where(negocios.loc[:, 'C/V'] == 'V').dropna()
            vendas_ativo = vendas_ativo.astype(negocios.dtypes)
            precos_vendas = vendas_ativo.loc[:, 'Preço / Ajuste'].drop_duplicates(keep='first')
            
            for preco in precos_vendas:
                linha_unificada = unificaOperacoes(vendas_ativo, preco)
                df_final = pd.concat([df_final, linha_unificada.to_frame().T], ignore_index=True)

    # Arruma o tipo dos dados antes de retornar      
    df_final = df_final.astype(negocios.dtypes)
    return df_final

def unificaOperacoes(ativos : pd.DataFrame, preco : Decimal) -> pd.Series:
    operacoes_mesmo_preco = ativos.where(ativos.loc[:, 'Preço / Ajuste'] == preco).dropna()
    operacoes_mesmo_preco = operacoes_mesmo_preco.astype(ativos.dtypes)

    if len(operacoes_mesmo_preco.index) > 0:
        linha_unificada = operacoes_mesmo_preco.iloc[0, :].copy(deep=True)
        # Caso exista mais de uma entrada com o mesmo preço, será tudo unificado
        # Alterando a quantidade total comprada e o preço total. O resto fica inalterado
        if len(operacoes_mesmo_preco.index) > 1:
            linha_unificada.loc['Quantidade'] = operacoes_mesmo_preco.loc[:, 'Quantidade'].sum()
            linha_unificada.loc['Valor Operação / Ajuste'] = operacoes_mesmo_preco.loc[:, 'Valor Operação / Ajuste'].sum()
        return linha_unificada
    else:
        return pd.Series(index=ativos.columns)

def criaDataFrameImpostos() -> pd.DataFrame:
    colunas_impostos = [
        'Data', 
        'Compras DAYTRADE',
        'Vendas DAYTRADE',
        'Emolumentos DAYTRADE',
        'Liquidação DAYTRADE',
        'IRRF DAYTRADE',
        'Lucro DAYTRADE',
        'Compras SWINGTRADE',
        'Vendas SWINGTRADE',
        'Emolumentos SWINGTRADE',
        'Liquidação SWINGTRADE',
        'IRRF SWINGTRADE',
        'Lucro SWINGTRADE', 
        'Total Emolumentos', 
        'Total Liquidação',
        'Resultado',
    ]
    dataframe = pd.DataFrame(columns=colunas_impostos)

    dataframe.set_index(dataframe.loc[:, 'Data'], inplace=True)
    dataframe.fillna(value=Decimal('0.0'), inplace=True)

    return dataframe

def criaDataFrameAtivos() -> pd.DataFrame:
    colunas = [
        'Q',
        'Negociação',
        'C/V',
        'Tipo mercado',
        'Prazo',
        'Especificação do título',
        'Obs. (*)',
        'Classe',
        'Quantidade',
        'Preço / Ajuste',
        'Valor Operação / Ajuste',
        'Taxas Operação',
        'D/C',
        'Nr. nota',
        'Data Pregão',
    ]
    dataframe = pd.DataFrame(columns=colunas)
    dataframe.set_index(dataframe['Especificação do título'], inplace=True)

    return dataframe

def separaDayTrade(negocios : pd.DataFrame) -> pd.DataFrame:
    df_final = pd.DataFrame(columns=negocios.columns)
    negocios_day_trade = negocios.where(negocios.loc[:, 'Obs. (*)'] == 'DAYTRADE').dropna()
    negocios_day_trade = negocios_day_trade.astype(negocios.dtypes)

    ativos_dt = pd.DataFrame(columns=negocios.columns)

    for indice, linha in negocios_day_trade.iterrows():
        ativos_dt, lucro = contabiliza(linha, ativos_dt, Decimal('0.0'))
    
    if ativos_dt.empty:
        df_final = negocios
    else:
        ativos_dt.drop('Taxas Operação', axis=1, inplace=True)
        for indice, linha in negocios.iterrows():
            nome_ativo = linha.loc['Especificação do título']
            preco = linha.loc['Preço / Ajuste']
            quantidade = linha.loc['Quantidade']
            tipo = linha.loc['Obs. (*)']

            # Verificar se a linha está nas sobras do daytrade, se estiver, dividir em duas linhas novas, senão, só adicionar mesmo
            if nome_ativo in ativos_dt.loc[:, 'Especificação do título']:
                if preco == ativos_dt.at[nome_ativo, 'Preço / Ajuste']:
                    if tipo == ativos_dt.at[nome_ativo, 'Obs. (*)']:
                        eh_compra = linha.loc['C/V'] == 'C'
                        if (ativos_dt.at[nome_ativo, 'Quantidade'] > 0 and eh_compra) or (ativos_dt.at[nome_ativo, 'Quantidade'] < 0 and not eh_compra):
                            # Esta é a linha de daytrade que será editada
                            linha.loc['Quantidade'] -= abs(ativos_dt.at[nome_ativo, 'Quantidade'])
                            linha.loc['Valor Operação / Ajuste'] -= abs(ativos_dt.at[nome_ativo, 'Quantidade']) * preco

                            # Esta é a linha que será criada como swingtrade
                            ativos_dt.at[nome_ativo, 'Quantidade'] = abs(ativos_dt.at[nome_ativo, 'Quantidade'])
                            ativos_dt.at[nome_ativo, 'Valor Operação / Ajuste'] = abs(ativos_dt.at[nome_ativo, 'Quantidade']) * preco
                            ativos_dt.at[nome_ativo, 'C/V'] = linha.loc['C/V']
                            ativos_dt.at[nome_ativo, 'D/C'] = linha.loc['D/C']
                            ativos_dt.at[nome_ativo, 'Obs. (*)'] = 'SWINGTRADE'

                            # Adiciona as duas linhas no dataframe final
                            df_final = pd.concat([df_final, linha.to_frame().T], ignore_index=True)
                            df_final = pd.concat([df_final, ativos_dt.loc[nome_ativo, :].to_frame().T], ignore_index=True)

                            # Exclui a linha que foi adicionada do ativos_dt
                            ativos_dt.drop(nome_ativo, inplace=True)

                            continue
                
            df_final = pd.concat([df_final, linha.to_frame().T], ignore_index=True)
            
    return df_final

def realizarBatimento(df_negocios : pd.DataFrame, df_resumos : pd.DataFrame, sobras_swing_trade : pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
        A divisão entre DayTrade e SwigTrade, é para calcular percentualmente as taxas,
        por exemplo, na nota de corretagem está descrito R$ 0.10 de emolumentos,
        tem que calcular quanto destes emolumentos são referentes às operações DayTrade
        e quanto destes emolumentos são do SwingTrade, para que seja possível calcular o lucro
    """
    ativos_dt = criaDataFrameAtivos()

    ativos_st = criaDataFrameAtivos()
    # Carrega os valores de sobras no dataframe dos ativos de SwingTrade
    if not sobras_swing_trade.empty:
        ativos_st = sobras_swing_trade.copy(deep=True)
    ativos_st.set_index(ativos_st['Especificação do título'], inplace=True)

    # Converte os valores dos resumos para Decimal, menos as colunas com o número da nota e a data
    df_resumos.iloc[:, 0:-2] = df_resumos.iloc[:, 0:-2].apply(lambda x: pd.Series(x).apply(lambda y : Decimal(str(y))))
    df_resumos.set_index(df_resumos.loc[:, 'Data Pregão'], inplace=True)

    # Seleciona as datas de negociação
    datas = df_negocios.loc[:, 'Data Pregão'].drop_duplicates(keep='first')
    
    # Cria os dataframes com os impostos
    impostos_acoes = criaDataFrameImpostos()
    impostos_fii = criaDataFrameImpostos()

    impostos_acoes['Data'] = datas
    impostos_acoes.set_index(impostos_acoes.loc[:, 'Data'], inplace=True)
    impostos_acoes.fillna(value=Decimal('0.0'), inplace=True)
    impostos_acoes.sort_index(axis='index', ascending=True, inplace=True)

    impostos_fii['Data'] = datas
    impostos_fii.set_index(impostos_fii.loc[:, 'Data'], inplace=True)
    impostos_fii.fillna(value=Decimal('0.0'), inplace=True)
    impostos_fii.sort_index(axis='index', ascending=True, inplace=True)

    for data in datas:
        # Filtra apenas os negócios na data
        negociacoes_na_data = df_negocios.where(df_negocios.loc[:, 'Data Pregão'] == data).dropna(how='all')
        
        # Define os tipos dos dados das colunas
        negociacoes_na_data =  negociacoes_na_data.astype(
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
                "Nr. nota" : int,
                "Data Pregão" : 'datetime64[ns]',
                "Classe" : str,
            }
        )
        # Converte os valores float para Decimal
        negociacoes_na_data['Preço / Ajuste'] = negociacoes_na_data.loc[:, 'Preço / Ajuste'].apply(lambda x: Decimal(str(x)))
        negociacoes_na_data['Valor Operação / Ajuste'] = negociacoes_na_data.loc[:, 'Valor Operação / Ajuste'].apply(lambda x: Decimal(str(x)))

        negociacoes_na_data = unificaNegociosNaData(negociacoes_na_data)

        negociacoes_na_data = separaDayTrade(negociacoes_na_data)

        valor_operacoes_daytrade = negociacoes_na_data.where(negociacoes_na_data['Obs. (*)'] == 'DAYTRADE').dropna().loc[:, 'Valor Operação / Ajuste'].sum()
        valor_operacoes_swingtrade = negociacoes_na_data.where(negociacoes_na_data['Obs. (*)'] == 'SWINGTRADE').dropna().loc[:, 'Valor Operação / Ajuste'].sum()

        valor_operacoes_daytrade = Decimal(str(valor_operacoes_daytrade))
        valor_operacoes_swingtrade = Decimal(str(valor_operacoes_swingtrade))

        """
        liquidacao_swingtrade = Decimal(Taxas.taxa_liquidacao_swing_trade * valor_operacoes_swingtrade).quantize(Decimal('0.01'), ROUND_DOWN)
        liquidacao_daytrade = Decimal(str(df_resumos.at[data, 'Taxa de liquidação'])).copy_abs() - liquidacao_swingtrade

        emolumentos_swingtrade = Decimal(Taxas.taxa_negociacao_swing_trade * valor_operacoes_swingtrade).quantize(Decimal('0.01'), ROUND_DOWN)
        emolumentos_daytrade = Decimal(str(df_resumos.at[data, 'Emolumentos'])).copy_abs() - emolumentos_swingtrade
        """
        if valor_operacoes_daytrade == Decimal('0.0'):
            liquidacao_daytrade = Decimal('0.0')
            liquidacao_swingtrade = Decimal(str(df_resumos.at[data, 'Taxa de liquidação'])).copy_abs()

            emolumentos_daytrade = Decimal('0.0')
            emolumentos_swingtrade = Decimal(str(df_resumos.at[data, 'Emolumentos'])).copy_abs()
        elif valor_operacoes_swingtrade == Decimal('0.0'):
            liquidacao_daytrade = Decimal(str(df_resumos.at[data, 'Taxa de liquidação'])).copy_abs()
            liquidacao_swingtrade = Decimal('0.0')

            emolumentos_daytrade = Decimal(str(df_resumos.at[data, 'Emolumentos'])).copy_abs()
            emolumentos_swingtrade = Decimal('0.0')
        else:
            liquidacao_daytrade = Decimal(Taxas.taxa_liquidacao_day_trade * valor_operacoes_daytrade).quantize(Decimal('0.01'), ROUND_DOWN)
            liquidacao_swingtrade = Decimal(str(df_resumos.at[data, 'Taxa de liquidação'])).copy_abs() - liquidacao_daytrade

            emolumentos_daytrade = Decimal(Taxas.taxa_negociacao_day_trade * valor_operacoes_daytrade).quantize(Decimal('0.01'), ROUND_DOWN)
            emolumentos_swingtrade = Decimal(str(df_resumos.at[data, 'Emolumentos'])).copy_abs() - emolumentos_daytrade
        
        for indice, linha in negociacoes_na_data.iterrows():
            # Informações pertinentes são salvas em variáveis
            data = linha.loc['Data Pregão']
            nome_ativo = linha.loc['Especificação do título']
            classe = linha.loc['Classe'].upper()
            tipo_operacao = linha.loc['Obs. (*)'].upper()

            if tipo_operacao == 'DAYTRADE':
                percentual_operacao_representa = (Decimal(str(linha.loc['Valor Operação / Ajuste'])) / valor_operacoes_daytrade)
                emolumentos = percentual_operacao_representa * emolumentos_daytrade.copy_abs()
                liquidacao = percentual_operacao_representa * liquidacao_daytrade.copy_abs()
                
                taxas_cobradas_nesta_operacao = emolumentos + liquidacao
                
                ativos_dt, lucro = contabiliza(linha, ativos_dt, taxas_cobradas_nesta_operacao)
                
            elif tipo_operacao == 'SWINGTRADE':
                percentual_operacao_representa = (Decimal(str(linha.loc['Valor Operação / Ajuste'])) / valor_operacoes_swingtrade)
                emolumentos = percentual_operacao_representa * emolumentos_swingtrade.copy_abs()
                liquidacao = percentual_operacao_representa * liquidacao_swingtrade.copy_abs()
                
                taxas_cobradas_nesta_operacao = emolumentos + liquidacao
                
                ativos_st, lucro = contabiliza(linha, ativos_st, taxas_cobradas_nesta_operacao)
                
            if classe == 'FII':
                impostos_fii = preencheImpostos(
                                impostos_fii,
                                linha,
                                emolumentos,
                                liquidacao,
                                tipo_operacao,
                                lucro
                            )   
            else:
                impostos_acoes = preencheImpostos(
                                impostos_acoes,
                                linha,
                                emolumentos,
                                liquidacao,
                                tipo_operacao,
                                lucro
                            )   
        
        if ativos_dt.empty == False:
            for indice, linha in ativos_dt.iterrows():
                data = linha.loc['Data Pregão']
                classe = linha.loc['Classe'].upper()
                tipo_operacao = linha.loc['Obs. (*)'].upper()
                
                ativos_st, lucro = contabiliza(linha, ativos_st, Decimal('0.0'))
                
                linha.loc['Valor Operação / Ajuste'] = Decimal('0.0')

                if classe == 'FII':
                    impostos_fii = preencheImpostos(
                                    impostos_fii,
                                    linha,
                                    Decimal('0.0'),
                                    Decimal('0.0'),
                                    'SWINGTRADE',
                                    lucro
                                )   
                else:
                    impostos_acoes = preencheImpostos(
                                    impostos_acoes,
                                    linha,
                                    Decimal('0.0'),
                                    Decimal('0.0'),
                                    'SWINGTRADE',
                                    lucro
                                )   
                
            ativos_dt = criaDataFrameAtivos()
        
        total_movimentacao_acoes_daytrade = impostos_acoes.at[data, 'Compras DAYTRADE'] + impostos_acoes.at[data, 'Vendas DAYTRADE']
        total_movimentacao_fii_daytrade = impostos_fii.at[data, 'Compras DAYTRADE'] + impostos_fii.at[data, 'Vendas DAYTRADE']

        if (total_movimentacao_acoes_daytrade + total_movimentacao_fii_daytrade) != 0:
            percentual_fii_daytrade = total_movimentacao_fii_daytrade / (total_movimentacao_acoes_daytrade + total_movimentacao_fii_daytrade)

            irrf_daytrade_retido_fii = Decimal(df_resumos.at[data, 'IRRF DayTrade retido'] * percentual_fii_daytrade).quantize(Decimal('0.01'), ROUND_DOWN)
            irrf_daytrade_retido_acoes = df_resumos.at[data, 'IRRF DayTrade retido'] - irrf_daytrade_retido_fii

            impostos_acoes.at[data, 'Resultado'] -= irrf_daytrade_retido_acoes
            impostos_fii.at[data, 'Resultado'] -= irrf_daytrade_retido_fii

            impostos_acoes.at[data, 'IRRF DAYTRADE'] += irrf_daytrade_retido_acoes
            impostos_fii.at[data, 'IRRF DAYTRADE'] += irrf_daytrade_retido_fii

    # Junta os valores em um único dataframe
    impostos_acoes['IRRF SWINGTRADE'] = impostos_acoes.loc[:, 'Vendas SWINGTRADE'] * Taxas.porcentagem_irrf_retido_swing_trade
    impostos_fii['IRRF SWINGTRADE'] = impostos_fii.loc[:, 'Vendas SWINGTRADE'] * Taxas.porcentagem_irrf_retido_swing_trade

    impostos_resultado = impostos_acoes.copy()
    impostos_resultado['Resultado'] += impostos_fii.loc[:, 'Resultado']
    impostos_resultado['Compras FII DAYTRADE'] = impostos_fii.loc[:, 'Compras DAYTRADE']
    impostos_resultado['Vendas FII DAYTRADE'] = impostos_fii.loc[:, 'Vendas DAYTRADE']
    impostos_resultado['Compras FII SWINGTRADE'] = impostos_fii.loc[:, 'Compras SWINGTRADE']
    impostos_resultado['Vendas FII SWINGTRADE'] = impostos_fii.loc[:, 'Vendas SWINGTRADE']
    impostos_resultado['Emolumentos FII DAYTRADE'] = impostos_fii.loc[:, 'Emolumentos DAYTRADE']
    impostos_resultado['Liquidação FII DAYTRADE'] = impostos_fii.loc[:, 'Liquidação DAYTRADE']
    impostos_resultado['Emolumentos FII SWINGTRADE'] = impostos_fii.loc[:, 'Emolumentos SWINGTRADE']
    impostos_resultado['Liquidação FII SWINGTRADE'] = impostos_fii.loc[:, 'Liquidação SWINGTRADE']
    impostos_resultado['IRRF FII DAYTRADE'] = impostos_fii.loc[:, 'IRRF DAYTRADE']
    impostos_resultado['IRRF FII SWINGTRADE'] = impostos_fii.loc[:, 'IRRF SWINGTRADE']
    impostos_resultado['Lucro FII DAYTRADE'] = impostos_fii.loc[:, 'Lucro DAYTRADE']
    impostos_resultado['Lucro FII SWINGTRADE'] = impostos_fii.loc[:, 'Lucro SWINGTRADE']

    impostos_resultado['Total Emolumentos'] = impostos_resultado.loc[:, 'Emolumentos FII DAYTRADE'] + impostos_resultado.loc[:, 'Emolumentos FII SWINGTRADE'] + impostos_resultado.loc[:, 'Emolumentos DAYTRADE'] + impostos_resultado.loc[:, 'Emolumentos SWINGTRADE']
    impostos_resultado['Total Liquidação'] = impostos_resultado.loc[:, 'Liquidação FII DAYTRADE'] + impostos_resultado.loc[:, 'Liquidação FII SWINGTRADE'] + impostos_resultado.loc[:, 'Liquidação DAYTRADE'] + impostos_resultado.loc[:, 'Liquidação SWINGTRADE']
    
    return (impostos_resultado, ativos_st, ativos_dt)

def preencheImpostos(
        impostos : pd.DataFrame,
        linha : pd.Series,
        emolumentos : Decimal,
        liquidacao : Decimal,
        tipo : Literal['DAYTRADE', 'SWINGTRADE'],
        lucro : Decimal,
    ) -> pd.DataFrame:
    data = linha.loc['Data Pregão']
    eh_compra = linha.loc['C/V'].upper() == 'C'

    impostos.at[data, f'Emolumentos {tipo}'] += emolumentos
    impostos.at[data, f'Liquidação {tipo}'] += liquidacao
    impostos.at[data, f'Lucro {tipo}'] += lucro

    impostos.at[data, f'Compras {tipo}' if eh_compra else f'Vendas {tipo}'] += linha['Valor Operação / Ajuste']

    if 'C' == linha['D/C'].upper():
        impostos.at[data, 'Resultado'] += linha['Valor Operação / Ajuste']
    elif 'D' == linha['D/C'].upper():
        impostos.at[data, 'Resultado'] -= linha['Valor Operação / Ajuste']
    
    impostos.at[data, 'Resultado'] -= (emolumentos + liquidacao)

    return impostos

def padronizaColunaOBS(df_negocios : pd.DataFrame):
    """
        Esta função padroniza a coluna Obs. (*) do dataframe
        Colocando DayTrade e SwingTrade, ao invés do que tem lá
    """
    copia_coluna = df_negocios.loc[:, 'Obs. (*)'].copy(deep=True)

    copia_coluna = copia_coluna.replace(r'[\s\S]*D[\s\S]*', 'DAYTRADE', regex=True)
    copia_coluna = copia_coluna.mask(
        copia_coluna != 'DAYTRADE',
        other='SWINGTRADE'
    )
    copia_coluna.fillna('SWINGTRADE', inplace=True)
    
    df_negocios['Obs. (*)'] = copia_coluna

def padronizaFinalNomeAtivo(df_negocios : pd.DataFrame):
    """
        Padroniza os nomes dos ativos, realizando as modificações INPLACE, deixa o final como:
        ON -> classe de ações ordinárias (final 3)
        PN, PNA, PNB, PNC, PND -> classe de ações preferenciais (final 4, 5, 6, 7, 8)
        UNT -> classe de units (final 11)
        XXXX11 -> fundos imobiliários, onde XXXX são as letras do ticker (final também 11)
        DRN, DRE, DR1, DR2, DR3 -> classe de BDR's (final 34)
    """
    """
    O ReGex abaixo captura o seguinte, tendo a seguinte string como exemplo: RANDON PART ON EJ N1 
    O primeiro grupo é o nome da empresa: RANDON PART
    O segundo grupo é o tipo do ativo: ON
    O terceiro é o que será jogado fora (indica ex-juros, ex-dividendos, etc.): EJ
    O quarto grupo é o nível de governança da empresa: N1
    Sendo que os dois primeiros grupos são obrigatórios, os dois últimos são opcionais
    """
    df_negocios.loc[:, 'Especificação do título'].replace(
        r'(.+\b\s)(ON|PN[A-D]?|UNT|CI|DIR|FIDC|TPR|BNS|DR[NE1-3])\b(\sE\S+\b)?(\s(?:N[M12]|M[AB2]|[A-C])\b)?',
        r'\g<1>\g<2>',
        regex=True,
        inplace=True
    )

def classificaAtivos(df_negocios : pd.DataFrame):
    """
        Esta função cria uma coluna extra no DataFrame que classifica:

        FII, AÇÃO ou BDR 

        As alterações são realizadas INPLACE e por isso não é retornado nada
    """
    df_negocios['Classe'] = df_negocios.loc[:, 'Especificação do título']
    df_negocios['Classe'] = df_negocios.loc[:, 'Classe'].mask(
            df_negocios.loc[:, 'Especificação do título'].str.endswith('ON') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('PN') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('PNA') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('PNB') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('PNC') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('PND') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('UNT'),
            other = 'AÇÃO'
        )
    df_negocios['Classe'] = df_negocios.loc[:, 'Classe'].mask(
            df_negocios.loc[:, 'Especificação do título'].str.endswith('DRN') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('DRE') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('DR1') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('DR2') |
            df_negocios.loc[:, 'Especificação do título'].str.endswith('DR3'),
            other = 'BDR'
        )
    df_negocios['Classe'] = df_negocios.loc[:, 'Classe'].mask(
            df_negocios.loc[:, 'Especificação do título'].str.startswith('FII'), 
            other = 'FII'
        )

def salvarODS(impostos : pd.DataFrame, sobras_st : pd.DataFrame, sobras_dt : pd.DataFrame, caminho : str):
    if not impostos.empty:
        impostos.iloc[:, 1:] = impostos.iloc[:, 1:].astype(np.float64)
        impostos.to_excel(caminho + '_Impostos.ods', index=False)
    if not sobras_st.empty:
        sobras_st.loc[:, ['Preço / Ajuste', 'Valor Operação / Ajuste', 'Taxas Operação']] = sobras_st.loc[:, ['Preço / Ajuste', 'Valor Operação / Ajuste', 'Taxas Operação']].astype(np.float64)
        sobras_st.to_excel(caminho + '_SobrasSwingTrade.ods', index=False)
    if not sobras_dt.empty:
        sobras_dt.loc[:, ['Preço / Ajuste', 'Valor Operação / Ajuste', 'Taxas Operação']].astype(np.float64, copy=False)
        sobras_dt.to_excel(caminho + '_SobrasDayTrade.ods', index=False)

def salvarXLSX(impostos : pd.DataFrame, sobras_st : pd.DataFrame, sobras_dt : pd.DataFrame, caminho : str):
    if not impostos.empty:
        impostos.iloc[:, 1:] = impostos.iloc[:, 1:].astype(np.float64)
        impostos.to_excel(caminho + '_Impostos.xlsx', index=False)
    if not sobras_st.empty:
        sobras_st.loc[:, ['Preço / Ajuste', 'Valor Operação / Ajuste', 'Taxas Operação']] = sobras_st.loc[:, ['Preço / Ajuste', 'Valor Operação / Ajuste', 'Taxas Operação']].astype(np.float64)
        sobras_st.to_excel(caminho + '_SobrasSwingTrade.xlsx', index=False)
    if not sobras_dt.empty:
        sobras_dt.loc[:, ['Preço / Ajuste', 'Valor Operação / Ajuste', 'Taxas Operação']] = sobras_dt.loc[:, ['Preço / Ajuste', 'Valor Operação / Ajuste', 'Taxas Operação']].astype(np.float64)
        sobras_dt.to_excel(caminho + '_SobrasDayTrade.xlsx', index=False)

if __name__ == '__main__':

    caminho_arquivo = "C:/Users/jelso/Desktop/Investimentos/Notas/Clear/2021/2204318_NotaCorretagem_03.ods"
    # caminho_arquivo = "C:/Users/jelso/Desktop/Investimentos/Notas/Rico/2022/6648793_NotaCorretagem_02.ods"

    df_negocios = pd.read_excel(caminho_arquivo, sheet_name='Negócios', header=0)
    df_resumos = pd.read_excel(caminho_arquivo, sheet_name='Resumos', header=0)

    # Formatação inicial dos dados
    padronizaFinalNomeAtivo(df_negocios)
    classificaAtivos(df_negocios)
    padronizaColunaOBS(df_negocios)

    """
    sobras = pd.read_excel("C:/Users/jelso/Desktop/Investimentos/Notas/Rico/2022/6648793_NotaCorretagem_04_SobrasSwingTrade.ods", header=0)
    sobras =  sobras.astype(
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
            "Taxas Operação" : float,
            "D/C" : str,
            "Nr. nota" : int,
            "Data Pregão" : np.datetime64,
            "Classe" : str,
        }
    )
    sobras.loc[:, "Preço / Ajuste"] = sobras.loc[:, "Preço / Ajuste"].apply(lambda x: Decimal(str(x)))
    sobras.loc[:, "Valor Operação / Ajuste"] = sobras.loc[:, "Valor Operação / Ajuste"].apply(lambda x: Decimal(str(x)))
    sobras.loc[:, "Taxas Operação"] = sobras.loc[:, "Taxas Operação"].apply(lambda x: Decimal(str(x)))
    """

    sobras = pd.DataFrame()
    impostos, sobras_swingtrade, sobras_daytrade = realizarBatimento(df_negocios, df_resumos, sobras)

    salvarODS(impostos, sobras_swingtrade, sobras_daytrade, caminho_arquivo.removesuffix('.ods'))

    print(df_negocios)
    print(impostos)