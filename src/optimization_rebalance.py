"""Rebalance optimization algorithm with given efficient frontier"""

# Author: Zheng Zhu <zheng.zhu@alkanza.us>
# License: BSD 3 clause

import numpy
import pandas
import sys 
import argparse
from gurobipy import *
from math import sqrt

def get_args():
    """This function parses and return arguments passed in"""

    #assign description to the help doc
    parser = argparse.ArgumentParser()

    #add arguments
    parser.add_argument("-r", "--fund_return", type = str, help = ("The return"
                        " of funds"), required = True)

    parser.add_argument("-c", "--covariance", type = str, help = ("The covariance"
                        " of funds"), required = True)
   
    parser.add_argument("-p",  "--price", type = str, help = ("The price"
                        " of funds"), required = True)
   
    parser.add_argument("-f", "--frontier", type = str, help =
                        "The frontier of funds", required = True)

    parser.add_argument("-w", "--weights", type = str, help = ("The weights"
                        " of funds"), required = True)

    parser.add_argument("-l1", "--lower1", type = str, help = ("The lower"
                        " limit of funds"), required = True)

    parser.add_argument("-u1", "--upper1", type = str, help = ("The upper"
                        " limit of funds"), required = True)
   
    parser.add_argument("-l2",  "--lower2", type = str, help = ("The lower"
                        " limit of trading"), required = True)
   
    parser.add_argument("-u2", "--upper2", type = str, help =
                        "The upper limit of trading", required = True)

    parser.add_argument("-o", "--original", type = str, help = ("The original"
                        " weights of funds"), required = True)

    parser.add_argument("-q",  "--quantity", type = str, help = ("The quantity"
                        " limit of funds"), required = True)
   
    parser.add_argument("-tp", "--percent", type = str, help =
                        "The percent of trading cost", required = True)

    parser.add_argument("-tf", "--fixed", type = str, help = ("The fixed"
                        " trading cost"), required = True)

    parser.add_argument("-a",  "--aum", type = float, help = ("The AUM"
                        " of accounts"), required = True)

    parser.add_argument("-fr", "--fund_frontier_return", type = float, help =
                        "The return of fund frontier", required = True)

    parser.add_argument("-fv", "--fund_frontier_volatility", type = float, help = ("The volatility"
                        " of fund frontier"), required = True)


    #array for all arguments passed to script
    args = parser.parse_args()
   
    #assign args to variables

    fund_return = args.fund_return

    fund_covariance = args.covariance

    fund_price = args.price

    fund_frontier = args.frontier

    fund_weights = args.weights

    lower1 = args.lower1

    upper1 = args.upper1

    lower2 = args.lower2

    upper2 = args.upper2

    original = args.original

    quantity = args.quantity

    trading_cost_per = args.percent

    trading_fixed_cost = args.fixed
 
    aum = args.aum

    fund_frontier_return = args.fund_frontier_return

    fund_frontier_volatility = args.fund_frontier_volatility


    #print all variable values
    print ("##############################################################"
            "\nHere are input parameters:")

    print ("The AUM for the account: {}".format(aum))

    print ("The return of fund frontier: {}".format(fund_frontier_return))

    print ("The volatility of fund frontier: {}\n####################"
           "##########################################".format(fund_frontier_volatility))

    #return all variable values
    return fund_return, fund_covariance, fund_price, fund_frontier, fund_weights, lower1, upper1, lower2, upper2, original, quantity, trading_cost_per, trading_fixed_cost, aum, fund_frontier_return, fund_frontier_volatility 

def rebalance(fund_return, fund_covariance, fund_weights, fund_price, lower1, upper1, lower2, upper2, original, quantity, trading_cost_per, trading_fixed_cost, fund_AUM, fund_frontier_return, fund_frontier_volatility):

    #get data from input files
    fund_names = fund_return.columns

    fund_return = fund_return.values[0]

    funds = range(len(fund_return))

    fund_covariance = fund_covariance.values

    fund_price = fund_price.values[0]

    fund_weights = fund_weights.values[0]
    
    lower1 = lower1.values[0]

    upper1 = upper1.values[0]

    lower2 = lower2.values[0]
 
    upper2 = upper2.values[0]

    original = original.values[0]

    quantity = quantity.values[0]

    trading_cost_per = trading_cost_per.values[0]

    trading_fixed_cost = trading_fixed_cost.values[0]

    #define variables
    m = Model('rebalance')

    vars =  m.addVars(funds, vtype = GRB.CONTINUOUS, lb = 0)

    portfolio_return_diff = m.addVar(vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)

    portfolio_risk_diff = m.addVar(vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)

    first_cost = m.addVar(vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)

    second_cost = m.addVar(vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)

    trading_abs = m.addVars(funds, vtype = GRB.CONTINUOUS, lb=0)

    trading_vars = m.addVars(funds, vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)

    booleans1 = m.addVars(funds, vtype = GRB.BINARY)

    booleans2 = m.addVars(funds, vtype = GRB.BINARY)

    integers = m.addVars(funds, vtype = GRB.INTEGER)

    weight_diff = m.addVars(funds, vtype = GRB.CONTINUOUS, lb=-GRB.INFINITY)

    weight_diff_abs = m.addVars(funds, vtype = GRB.CONTINUOUS, lb=0)
        
    quantity_constraints = [fund_price[index]*quantity[index]/fund_AUM for index in funds]

    #update model
    m.update()

    #compute return and risk
    portfolio_risk =  numpy.dot(numpy.dot(vars.select(), fund_covariance), vars.select())

    portfolio_return = numpy.dot(fund_return, vars.select())

    #define cost function
    portfolio_risk_diff = (portfolio_risk - fund_frontier_volatility*fund_frontier_volatility)

    trading_cost = quicksum([(trading_abs[index]*trading_cost_per[index] + booleans2[index]*trading_fixed_cost[index]/fund_AUM) for index in funds])

    cost_function = portfolio_return_diff + portfolio_risk_diff + trading_cost

    m.setObjective(cost_function , GRB.MINIMIZE)

    #define constraints
    m.addConstr(vars.sum() == 1)

    m.addConstr (first_cost == portfolio_return - fund_frontier_return)

    m.addGenConstrAbs(portfolio_return_diff, first_cost)

    m.addConstr(portfolio_return - fund_frontier_return >= 0)

    m.addConstrs((vars[index] - upper1[index]*booleans1[index] <= 0)  for index in funds)

    m.addConstrs((vars[index] - lower1[index]*booleans1[index] >= 0)  for index in funds)

    for index in funds:

        m.addConstr(trading_vars[index] == vars[index] - original[index] )

        m.addGenConstrAbs(trading_abs[index], trading_vars[index])

    m.addConstrs((trading_abs[index] <= upper2[index]*booleans2[index])  for index in funds)

    m.addConstrs((trading_abs[index] >= lower2[index]*booleans2[index])  for index in funds)

    m.addConstrs((vars[index] == quantity_constraints[index]*integers[index]) for index in funds)

    m.setParam('OutputFlag', 0)

    m.optimize()

    #print results
    if sqrt(portfolio_risk.getValue()) != fund_frontier_volatility:

            print ("%.6f" %portfolio_return.getValue()+", "+"%.6f" %sqrt(portfolio_risk.getValue()), end = ', ')

            for v in m.getVars()[:len(funds)]:

                  print("%.6f" %v.x, end = ',')
            print ('')

    return portfolio_return.getValue(), sqrt(portfolio_risk.getValue())



if __name__ == '__main__':

   #read data
   fund_return, fund_covariance, fund_price, fund_frontier, fund_weights, lower1, upper1, lower2, upper2, original, quantity, trading_cost_per, trading_fixed_cost, aum, fund_frontier_return, fund_frontier_volatility = get_args()

   fund_return = pandas.read_csv(fund_return)

   fund_covariance = pandas.read_csv(fund_covariance)

   fund_price = pandas.read_csv(fund_price)

   fund_frontier = pandas.read_csv(fund_frontier)

   fund_weights = pandas.read_csv(fund_weights)

   lower1 = pandas.read_csv(lower1)

   upper1 = pandas.read_csv(upper1)

   lower2 = pandas.read_csv(lower2)

   upper2 = pandas.read_csv(upper2)
 
   original = pandas.read_csv(original)

   quantity = pandas.read_csv(quantity)

   trading_cost_per = pandas.read_csv(trading_cost_per)

   trading_fixed_cost = pandas.read_csv(trading_fixed_cost)

   #run the rebalance function and get results
   x, y = rebalance(fund_return, fund_covariance, fund_price, fund_weights, lower1, upper1, lower2, upper2, original, quantity, trading_cost_per, trading_fixed_cost, aum, fund_frontier_return, fund_frontier_volatility)
