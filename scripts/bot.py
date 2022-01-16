import math
import numpy as np
import pandas as pd
from scripts.api import Api
from collections import Counter

class Bot():
    ''' Clase que setea y testea las distintas estrategias
    y luego imprime un reporte 
    '''

    def __init__(self, funds, tickers, start_date, end_date, file=False):
        if isinstance(file, pd.DataFrame):
            self.data = file   
        else:
            self.data = Api().get_dataframe(tickers, start_date, end_date)
        self.tickers = list(self.data.columns)
        self.count_stocks = dict.fromkeys(self.tickers, 0)
        self.count_money = dict.fromkeys(self.tickers, 0)
        self.total_results = {'1': 0, '2': 0, '3': 0}
        self.funds = funds
        self.test_strategy_one(self.data, self.tickers, self.funds)
        self.test_strategy_two(self.data, self.tickers, self.funds)
        self.test_strategy_three(self.data, self.tickers, self.funds)
        self.report(start_date, end_date)
    
    def report(self, start_date, end_date):
        print(f'\n\n--- REPORTE ESTRATEGIAS {start_date} a {end_date} ---\n')
        c_strategy = Counter(self.total_results)
        best_strategy = c_strategy.most_common(1)
        c_stocks = Counter(self.count_stocks)
        stocks_common = c_stocks.most_common(3)
        c_money = Counter(self.count_money)
        top_money = c_money.most_common(3)
        for strategy, result in best_strategy:
            print(f'MEJOR ESTRATEGIA: NUMERO {strategy} RESULTADO {round(result, 2)}$.\n')
        print('ACCIONES CON MÁS GANANCIA/MENOR PERDIDA:')
        for index, tuple in enumerate(top_money):
            stock = tuple[0]
            result = round(tuple[1], 2)
            print(f'{index+1}. {stock} ---> {result}$')
        print('\nACCIONES MÁS COMPRADAS:')
        for index, tuple in enumerate(stocks_common):
            stock = tuple[0]
            buys = tuple[1]
            print(f'{index+1}. {stock} ---> {buys} veces.')

    def test_strategy_one(self, df_merged, tickers, funds):
        print('\n--- INICIANDO ESTRATEGIA 1 ---\n')
        try:
            down_percentage = int(input(
                'INGRESE PORCENTAJE DE BAJA PARA COMPRAR ACCIÓN (NUMERO NEGATIVO UNICAMENTE): '))
            if down_percentage > 0: self.test_strategy_one()
        except ValueError:
            self.test_strategy_one()
        try:
            up_percentage = int(input(
                'INGRESE PORCENTAJE AL ALZA PARA VENDER ACCIÓN (NUMERO POSITIVO UNICAMENTE): '))
        except ValueError:
            self.test_strategy_one()
        for ticker in tickers:
            df_merged[f'% {ticker}'] = round(df_merged[ticker].pct_change() * 100, 2)
            df_merged[f'result {ticker}'] = None
        positive_trades = 0
        buys = 0
        result_total = 0
        funds = funds
        for ticker in tickers:
            blocked = False
            stocks = None
            broke = False
            for index, row in df_merged.iterrows():
                if index == df_merged.index[-1] and blocked == True:
                    df_merged.at[index, f'result {ticker}'] = 'SOLD LAST TRADE'
                    money_earn = stocks * row[ticker]
                    result = round(money_earn - 1000, 2)
                    if result > 0: positive_trades += 1
                    self.count_money[ticker] += result
                    result_total += result
                    funds += result
                elif row[f'% {ticker}'] < down_percentage and blocked == False and funds > 1000:
                    self.count_stocks[ticker] += 1
                    df_merged.at[index, f'result {ticker}'] = 'BUYED'
                    buys += 1
                    total_stocks = math.floor(1000/row[ticker])
                    stocks = total_stocks
                    blocked = True
                elif row[f'% {ticker}'] > up_percentage and blocked == True:
                    df_merged.at[index, f'result {ticker}'] = 'SOLD'
                    money_earn = stocks * row[ticker]
                    result = round(money_earn - 1000, 2)
                    if result > 0: positive_trades += 1
                    self.count_money[ticker] += result
                    result_total += result
                    funds += result
                    blocked = False
                elif funds < 1000:
                    print(f'BROKE ACCOUNT {funds} :(')
                    broke = True
                    break
                else:
                    continue
            if broke:
                break
        print(f'\nFINALISED STRATEGY ONE RESULT TOTAL {result_total}$, '
                f'TOTAL BUYS {buys}, POSITIVE TRADES {positive_trades}.')
        self.total_results['1'] = result_total
        df_merged.to_excel('strategy_one_results.xlsx')
        print('EXCEL OF TRADES DETAILS GENERATED')
    
    def test_strategy_two(self, df_merged, tickers, funds):
        print('\n--- INICIANDO ESTRATEGIA 2 ---\n')
        try:
            days = int(input(
                'INGRESE LIMITE DE DÍAS DE TENENCIA DE ACCIÓN (NUMERO UNICAMENTE): '))
        except ValueError:
            self.test_strategy_two()
        try:
            percentage_mean = int(input(
                'INGRESE PORCENTAJE QUE DEBE SUPERAR LA COTIZACIÓN SOBRE LA MEDIA PARA COMPRAR (NUMERO ENTERO): '))
            percentage_mean = percentage_mean / 100
        except ValueError:
            self.test_strategy_two()
        df_merged.reset_index(inplace=True)
        for ticker in tickers:
            df_merged[f'mean {ticker}'] = None
            df_merged[f'result {ticker}'] = None
            for index, row in df_merged.iterrows():
                partial_mean = round(df_merged[ticker].iloc[0:index].mean(), 2)
                df_merged.at[index, f'mean {ticker}'] = partial_mean
        buys = 0
        positive_trades = 0
        result_total = 0
        funds = funds
        broke = False
        for ticker in tickers:
            blocked = False
            stocks = None
            entry_date = None
            for index, row in df_merged.iterrows():
                price = float(row[{ticker}])
                try:
                    mean = float(row[f'mean {ticker}'])
                except TypeError:
                    mean = 0
                if index == df_merged.index[-1] and blocked == True:
                    df_merged.at[index, f'result {ticker}'] = 'SOLD LAST TRADE'
                    money_earn = stocks * row[ticker]
                    result = round(money_earn - 1000, 2)
                    if result > 0: positive_trades += 1
                    self.count_money[ticker] += result
                    result_total += result
                    funds += result
                elif price > mean * (1+percentage_mean) and blocked == False and funds > 1000:
                    self.count_stocks[ticker] += 1
                    df_merged.at[index, f'result {ticker}'] = 'BUYED'
                    buys += 1
                    total_stocks = math.floor(1000/row[ticker])
                    stocks = total_stocks
                    entry_date = index
                    blocked = True
                elif entry_date and (index - entry_date) == days and blocked == True:
                    df_merged.at[index, f'result {ticker}'] = f'SOLD ({days} DAYS)'
                    money_earn = stocks * row[ticker]
                    result = round(money_earn - 1000, 2)
                    if result > 0: positive_trades += 1
                    self.count_money[ticker] += result
                    result_total += result
                    funds += result
                    entry_date = None
                    blocked = False
                elif funds < 1000:
                    print(f'BROKE ACCOUNT {funds} :(')
                    df_merged.at[index, f'result {ticker}'] = 'BROKE ACCOUNT'
                    broke = True
                    break
                else:
                    continue
            if broke:
                break
        print(f'\nFINALISED STRATEGY TWO RESULT TOTAL {result_total}$, '
                f'TOTAL BUYS {buys}, POSITIVE TRADES {positive_trades}.')
        self.total_results['2'] = result_total
        df_merged.to_excel('strategy_two_results.xlsx')
        print('EXCEL OF TRADES DETAILS GENERATED')

    def test_strategy_three(self, df_merged, tickers, funds):
        print('\n--- INICIANDO ESTRATEGIA 3 ---\n')
        try:
            down_percentage = int(input(
                'INGRESE PORCENTAJE DE BAJA PARA COMPRAR ACCIÓN (NUMERO NEGATIVO UNICAMENTE): '))
            if down_percentage > 0: self.test_strategy_three()
        except ValueError:
            self.test_strategy_three()
        try:
            percentage_mean = int(input(
                'INGRESE PORCENTAJE QUE DEBE SUPERAR LA COTIZACIÓN SOBRE LA MEDIA PARA COMPRAR (NUMERO ENTERO): '))
            percentage_mean = percentage_mean / 100
        except ValueError:
            self.test_strategy_three()
        try:
            up_percentage = int(input(
                'INGRESE PORCENTAJE AL ALZA PARA VENDER ACCIÓN (NUMERO POSITIVO UNICAMENTE): '))
        except ValueError:
            self.test_strategy_three()
        try:
            days = int(input(
                'INGRESE LIMITE DE DÍAS DE TENENCIA DE ACCIÓN (NUMERO UNICAMENTE): '))
        except ValueError:
            self.test_strategy_three()
        df_merged.reset_index(inplace=True)
        for ticker in tickers:
            df_merged[f'% {ticker}'] = round(df_merged[ticker].pct_change() * 100, 2)
            df_merged[f'mean {ticker}'] = None
            df_merged[f'result {ticker}'] = None
            for index, row in df_merged.iterrows():
                partial_mean = round(df_merged[ticker].iloc[0:index].mean(), 2)
                df_merged.at[index, f'mean {ticker}'] = partial_mean
        buys = 0
        positive_trades = 0
        result_total = 0
        funds = funds
        broke = False
        for ticker in tickers:
            blocked = False
            stocks = None
            entry_date = None
            for index, row in df_merged.iterrows():
                price = float(row[{ticker}])
                try:
                    mean = float(row[f'mean {ticker}'])
                except TypeError:
                    mean = 0
                if index == df_merged.index[-1] and blocked == True:
                    df_merged.at[index, f'result {ticker}'] = 'SOLD LAST TRADE'
                    money_earn = stocks * row[ticker]
                    result = round(money_earn - 1000, 2)
                    if result > 0: positive_trades += 1
                    self.count_money[ticker] += result
                    result_total += result
                    funds += result
                elif price > mean * (1+percentage_mean) and row[f'% {ticker}'] < down_percentage \
                    and blocked == False and funds > 1000:
                    self.count_stocks[ticker] += 1
                    df_merged.at[index, f'result {ticker}'] = 'BUYED'
                    buys += 1
                    total_stocks = math.floor(1000/row[ticker])
                    stocks = total_stocks
                    entry_date = index
                    blocked = True
                elif entry_date and (index - entry_date) == days or row[f'% {ticker}'] > up_percentage \
                    and blocked == True:
                    df_merged.at[index, f'result {ticker}'] = f'SOLD ({days} DAYS)'
                    money_earn = stocks * row[ticker]
                    result = round(money_earn - 1000, 2)
                    if result > 0: positive_trades += 1
                    self.count_money[ticker] += result
                    result_total += result
                    funds += result
                    entry_date = None
                    blocked = False
                elif funds < 1000:
                    print(f'BROKE ACCOUNT {funds} :(')
                    df_merged.at[index, f'result {ticker}'] = 'BROKE ACCOUNT'
                    broke = True
                    break
                else:
                    continue
            if broke:
                break
        print(f'\nFINALISED STRATEGY THREE RESULT TOTAL {result_total}$, '
                f'TOTAL BUYS {buys}, POSITIVE TRADES {positive_trades}.')
        self.total_results['3'] = result_total
        df_merged.to_excel('strategy_three_results.xlsx')
        print('EXCEL OF TRADES DETAILS GENERATED')