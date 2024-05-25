from decimal import Decimal

class Taxas: 
    # Taxas da B3 disponível em: 
    # http://www.b3.com.br/pt_br/produtos-e-servicos/tarifas/listados-a-vista-e-derivativos/renda-variavel/tarifas-de-acoes-e-fundos-de-investimento/a-vista/
    taxa_liquidacao_swing_trade             = Decimal('0.000250')  # 0,025%    sobre valor total das operações ST
    taxa_negociacao_swing_trade             = Decimal('0.000050')  # 0,005%    sobre valor total das operações ST
    taxa_liquidacao_day_trade               = Decimal('0.000180')  # 0,018%    sobre valor total das operações DT
    taxa_negociacao_day_trade               = Decimal('0.000050')  # 0,005%    sobre valor total das operações DT
    porcentagem_irrf_retido_day_trade       = Decimal('0.010000')  # 1%        sobre lucro diário
    porcentagem_irrf_retido_swing_trade     = Decimal('0.000050')  # 0,005%    sobre lucro diário
    porcentagem_imposto_day_trade           = Decimal('0.200000')  # 20%       sobre lucro mensal
    porcentagem_imposto_swing_trade         = Decimal('0.150000')  # 15%       sobre lucro mensal
    valor_isencao_swing_trade               = Decimal('20000.00')  # Vendas menores que 20 mil no mês são isentas se for na ordem Compra -> Vende
    porcentagem_imposto_fundos_imobiliarios = Decimal('0.200000')  # 20%       sobre lucro mensal, independente de SwingTrade ou DayTrade