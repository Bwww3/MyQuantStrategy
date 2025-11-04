from jqdata import *
from jqlib.optimizer import *


def initialize(context):
    set_strategy_params(context)
    set_variables(context)
    set_backtest_params(context)
    set_cost_params(context)
    
    run_monthly(before_market_open, monthday=1, time='before_open') 
    run_monthly(market_open, monthday=1, time='14:30')
    run_monthly(after_market_close, monthday=1, time='after_close')


'''
================================================================================
Setting Params
================================================================================
'''

def set_strategy_params(context):
    g.rebalance_period = 3    # quarterly rebalancing
    g.invest_stock_pool = [
        '513300.XSHG',        # Nasdaq100 ETF, starting from 2020/11/30
        '159937.XSHE',        # Gold ETF, starting from 2014/9/30
        '511260.XSHG',        # 10Y CGB ETF, starting from 2017/8/31
        '515100.XSHG',        # Low-vol Dividend ETF, starting from 2020/7/31
        '511360.XSHG',        # Money Market ETF, starting from 2020/9/31
    ]
    g.weights_optimizer_type = 2
    

def set_variables(context):
    g.current_t = 0
    g.if_rebalance = False
    g.rf = 0.02
    
    
def set_backtest_params(context):
    set_option('use_real_price', True)
    set_option("avoid_future_data", True)
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

def do_rebalancing(context, weights):
    if weights is None:
        pass
    else:
        total_value = context.portfolio.total_value
        for stock in weights.keys():
            value = total_value * weights[stock]
            order_target_value(stock, value)


def get_optimized_weights(context):
    
    # Equal weights
    if g.weights_optimizer_type == 1:
        equal_weights = [1.0 / len(g.invest_stock_pool)] * len(g.invest_stock_pool)
        optimized_weights = pd.Series(data=equal_weights, index=g.invest_stock_pool)
    
    # Risk Parity Optimizer
    if g.weights_optimizer_type == 2:
        optimized_weights = portfolio_optimizer(
            date=context.previous_date,
            securities=g.invest_stock_pool,
            target=RiskParity(count=250, risk_budget=None),
            constraints=[MarketConstraint('etf', low=0.0, high=1.0)],
            bounds=[Bound(0, 0.5)],
            default_port_weight_range=[0., 1.0],
            ftol=1e-09,
            return_none_if_fail=True,
        )
    
    # Maximum Sharpe Optimizer
    if g.weights_optimizer_type == 3:
        optimized_weights = portfolio_optimizer(
            date=context.previous_date,
            securities=g.invest_stock_pool,
            target=MaxSharpeRatio(rf=g.rf, weight_sum_equal=0.5, count=250),
            constraints=[],
            bounds=[Bound(0, 0.1)],
            default_port_weight_range=[0., 1.0],
            ftol=1e-09,
            return_none_if_fail=True,
        )
    
    if optimized_weights is None:
        print('Warning：failed to get portfolio weights!')
    else:
        print('Portfolio weights updated！')
        print(optimized_weights)
    
    return optimized_weights
        


def before_market_open(context):
    if g.current_t % g.rebalance_period == 0:
        g.if_rebalance = True
    g.current_t += 1
    
    
def market_open(context):
    if g.if_rebalance:
        optimized_weights = get_optimized_weights(context)
        do_rebalancing(context, weights=optimized_weights)
        
        
def after_market_close(context):
    pass









