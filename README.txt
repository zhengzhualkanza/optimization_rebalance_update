------------------------------------------------------------------------------- 
Cluster algorithm:         v1.0                                                  
Creation:                  12/05/2017                    
Author:                    Zheng Zhu, Alkanza, Inc                     
-------------------------------------------------------------------------------

DESCRIPTION
-------------------------------------------------------------------------------
We present bagging hierachy cluster algorithm for financial time series.
-------------------------------------------------------------------------------

REQUIREMENTS
-------------------------------------------------------------------------------
Python3
NumPy
Pandas
gurobipy
-------------------------------------------------------------------------------

USAGE
-------------------------------------------------------------------------------
To generate output(return, volatilaty, weights):
python3 ./optimization_rebalance.py 
    -r  ./relative/path/to/return.csv
    -c  ./relative/path/to/covariance.csv
    -p  ./relative/path/to/price.csv
    -f  ./relative/path/to/frontier.csv
    -w  ./relative/path/to/weights.csv
    -l1 ./relative/path/to/lower1.csv
    -u1 ./relative/path/to/upper1.csv
    -l2 ./relative/path/to/lower2.csv
    -u2 ./relative/path/to/upper2.csv
    -o  ./relative/path/to/original.csv
    -q  ./relative/path/to/quantity.csv
    -tp ./relative/path/to/trading_cost_per.csv
    -tf ./relative/path/to/trading_fixed_cost.csv
    -q  aum
    -fr frontier_return
    -fv frontier_volatility


optimization_rebalance.py     --- python file for rebalance analysis
return.csv                    --- csv file for return of funds 
covariance.csv                --- csv file for covariance of funds 
price.csv                     --- csv file for price of funds
frontier.csv                  --- csv file for frontier of funds 
weights.csv                   --- csv file for weights of funds
lower1.csv                    --- csv file for lower limit of funds
upper1.csv                    --- csv file for upper limit of funds
lower2.csv                    --- csv file for lower limit of trading
upper2.csv                    --- csv file for upper limit of trading
original.csv                  --- csv file for original weights of funds
quantity.csv                  --- csv file for quantity limit of funds
trading_cost_per.csv          --- csv file for percent of trading cost
trading_fixed_cost.csv        --- csv file for fixedtrading cost
aum                           --- AUM of the account
frontier_return               --- return of fund frontier
frontier_volatility           --- volatility of fund frontier


The cost function J(W) of rebalance optimization problem is defined as follows:

J(W) = |R^T*W- r_p| + |W^T*\Sigma*W -  \sigma_p^2| + \sum_ia_i

W         -- weight vector
R         -- return vector
\Sigma    -- covariance matrix
r_p       -- return on the original frontier
\sigma_p  -- volatility on the original frontier
a_i       -- trading cost for fund i


-------------------------------------------------------------------------------

EXAMPLES
-------------------------------------------------------------------------------
cd src

python3 ./optimization_rebalance.py
    -r  ../data/rico_return.csv
    -c  ../data/rico_covariance.csv
    -p  ../data/rico_price.csv
    -f  ../data/rico_frontier.csv
    -w  ../data/rico_weights.csv
    -l1 ../data/rico_lower1.csv
    -u1 ../data/rico_upper1.csv
    -l2 ../data/rico_lower2.csv
    -u2 ../data/rico_upper2.csv
    -o  ../data/rico_original.csv
    -q  ../data/rico_quantity.csv
    -tp ../data/rico_trading_cost_per.csv
    -tf ../data/rico_trading_fixed_cost.csv
    -q  50000
    -fr 0.10
    -fv 0.04

[WARNINGS]: - There are a numberof precision warnings gernerated with this program,
to supress the warnings include "-W ignore" in your CLI arguments.
------------------------------------------------------------------------------------


UNIT TEST
------------------------------------------------------------------------------------
To do unit test of codes:

cd test
python3 -W ignore ./test_optimization_rebalance.py
