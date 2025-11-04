from jqdata import *


def initialize(context):
    set_strategy_params(context)
    set_variables(context)
    set_backtest_params(context)
    set_cost_params(context)
    
    run_daily(before_market_open, time='before_open') 
    run_daily(market_open, time='every_bar')
    run_daily(after_market_close, time='after_close')


'''
================================================================================
Setting Params
================================================================================
'''

def set_strategy_params(context):
    g.invest_period = 5
    g.invest_amount = 10000
    g.invest_stock_pool = [
        '513300.XSHG',     # Nasdaq100 ETF, starting from 2020/11/30
        # '513650.XSHG',     # SP500 ETF
    ]


def set_variables(context):
    g.current_t = 0
    g.if_trade = False
    
    
def set_backtest_params(context):
    set_option('use_real_price', True)
    log.set_level('order', 'error')
    
    
def set_cost_params(context):
    set_slippage(FixedSlippage(0))
    set_order_cost(
        OrderCost(
            close_tax=0.001,
            open_commission=0.0008, 
            close_commission=0.0008, 
            min_commission=0,
            ), 
        type='etf',
    )


'''
================================================================================
Functions to run
================================================================================
'''

def before_market_open(context):
    if g.current_t % g.invest_period == 0:
        g.if_trade = True
    g.current_t += 1
    
    
def market_open(context):
    if g.if_trade:
        for stock in g.invest_stock_pool:
            order_value(stock, g.invest_amount)
        
        
def after_market_close(context):
    pass









