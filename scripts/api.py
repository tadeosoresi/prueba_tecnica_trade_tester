import sys
import time
import requests
import pandas as pd
from scripts.keys import Key
from functools import reduce
from json.decoder import JSONDecodeError 

class Api():
    ''' Clase que se encarga de hacer los requests a la API
    de AlphaVantage
    Metodos: match_tickers() se encarga de validar los tickers
    asignados en consola en la API.
    get_dataframe(): una vez matcheados los tickers se descarga la data
    y se parsea a dataframe.
    DETALLES: Solamente 5 requests por minuto, maximo 500 por dia.
    DATA: Antiguedad de 3 meses.'''
    def __init__(self):
        self.key = Key.return_key()
        self.url = 'https://www.alphavantage.co/query?'
    
    def get_dataframe(self, tickers, start_date, end_date):
        ''' Requests to AlphaVantage API and parse to dataframe'''
        tickers = self.match_tickers(tickers)
        params = {'function': 'TIME_SERIES_DAILY', 'symbol': None, 
                    'outputsize': 'compact', 'apikey': self.key}
        all_data = []
        for ticker in tickers:
            params['symbol'] = ticker
            response = self.get_response(self.url, params)
            if not response:
                print('--- ERROR DE CONEXIÓN ---') 
                sys.exit(0)
            try:
                content = response['Time Series (Daily)']
            except KeyError:
                print('--- Standard API call frequency is 5 calls per minute and 500'
                        ' calls per day, limit reached ---')
                sys.exit(0)
            dataframe = pd.DataFrame.from_dict(content, orient='index')
            dataframe = dataframe.astype('float')
            dataframe.index.name = 'date'
            dataframe.drop(['1. open', '2. high', '3. low', '5. volume'], axis=1, inplace=True)
            dataframe.rename(columns={'4. close': ticker}, inplace=True)
            all_data.append(dataframe)

        df_merged = reduce(lambda left,right: pd.merge(left, right, on=['date'],
                                            how='inner'), all_data)
        df_merged.sort_values('date', ascending=True, inplace=True)
        df_merged = df_merged[start_date:end_date]
        return df_merged

    def match_tickers(self, tickers):
        ''' PROCEDIMIENTO: API requests to find and match tickers '''
        
        params = {'function': 'SYMBOL_SEARCH', 'keywords': None, 'apikey': self.key}
        new_tickers = []
        for index, ticker in enumerate(tickers):
            params['keywords'] = ticker
            response = self.get_response(self.url, params=params)
            if not response:
                print('--- ERROR DE CONEXIÓN ---') 
                sys.exit(0)
            print(f'\n--- ENCONTRANDO MATCH EN API ALPHAVANTAGE {ticker} ---')
            content = response.get('bestMatches', None)
            if not content:
                print(f'--- NO SE PUDO ENCONTRAR TICKER {ticker}, ELIMINANDOLO DE LISTA ---\n')
            else:
                for number, active in enumerate(content):
                    ticker_active = active['1. symbol']
                    name = active['2. name']
                    region = active['4. region']
                    print(f'ENCONTRADO TICKER NUMERO {number}\nDATA:\n'
                            f' TICKER: {ticker_active}\n NAME: {name}\n REGIÓN: {region}')
                selection = input('--- INGRESE EL NUMERO DE TICKER SI HUBO MATCH, NONE'
                                    ' SI NO HUBO NINGUN MATCH: ').split()
                try:
                    number = int(selection[0])
                    new_tickers.append(content[number]['1. symbol'])
                except ValueError:
                    if selection[0].lower() == 'none':
                        print(f'--- ELIMINANDO {ticker} ---')
                    else:
                        print('RESPUESTA NULE')
                        self.match_tickers(tickers)
                except IndexError:
                    print('RESPUESTA NULA')
                    self.match_tickers(tickers)
        if not new_tickers:
            print('--- SE ELIMINARON TODOS LOS TICKERS INGRESADOS VIA CONSOLA (0 MATCHES) ---')
            sys.exit(0)
        print('\n--- WAITING 120 SECONDS TO CALL API AGAIN ---\n')
        time.sleep(120)
        return new_tickers

    def get_response(self, url, params):
        ''' Metodo para hacer las requests y
        tratar excepciones'''
        request_timeout = 5
        tries = 0
        while True:
            if tries > 5:
                return None
            try:
                response = requests.get(
                    url,
                    timeout=request_timeout,
                    params = params
                ).json()
                return response
            except JSONDecodeError:
                print(f'--- JSON DECODE ERROR IN {url} ---')
                sys.exit(0)
            except requests.exceptions.ConnectionError:
                print("Connection Error, Retrying")
                time.sleep(request_timeout)
                tries += 1
                continue
            except requests.exceptions.RequestException:
                print('Waiting...')
                time.sleep(request_timeout)
                tries += 1
                continue