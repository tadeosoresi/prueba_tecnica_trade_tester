import sys
import os
import glob
import argparse
from scripts.bot import Bot
import pandas as pd
from datetime import datetime

"""
Para ejecutar programa: python main.py --funds --tickers --start --end --csv --xlsx
--funds: OBLIGATORIO, fondos totales que se dispone.
--tickers: OBLIGATORIO, tickers de las acciones a operar, ingresar de forma accion1 accion2 accionN
--start: NO OBLIGATORIO, toma fecha default (date start), si ingresamos archivo con cotizaciones toma la primera fecha
en el indice.
--end: NO OBLIGATORIO, toma fecha default (date end), si ingresamos archivo con cotizaciones toma la ultima fecha
en el indice.
--csv: NO OBLIGATORIO SALVO QUE SE DESEE INGRESAR COTIZACIONES DESDE CSV, por defecto FALSE.
--xlsx: NO OBLIGATORIO SALVO QUE SE DESEE INGRESAR COTIZACIONES DESDE XLSX, por defecto FALSE.
SI INGRESAMOS COTIZACIONES DESDE ARCHIVO, LA COLUMNA DATE DEBE SER LA PRIMERA Y 
LOS TICKERS CONTENIDOS EN EL ARCHIVO DEBEN SER LOS MISMOS QUE ESPECIFICAMOS VIA CONSOLA (HACE UN MATCH)
"""
class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, '%s: error: %s\n' % (self.prog, message))

if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--funds', help = 'Fondos a invertir', type=int)
    parser.add_argument('--tickers', help='Tickers de acciones', type=str, nargs='*')
    parser.add_argument('--start', help='Start day', type=str, default='2021-10-01')
    parser.add_argument('--end', help='End day', type=str, default='2021-12-31')
    parser.add_argument('--csv', help='¿Cotizaciones desde csv?', type=bool, default=False)
    parser.add_argument('--xlsx', help='¿Cotizaciones desde excel?', type=bool, default=False)
    args = parser.parse_args()
    if not args.funds:
        raise Exception('--- ESPECIFICAR FONDOS VIA ARGUMENTO --funds ---')
    if not args.tickers:
        raise Exception('--- ESPECIFICAR TICKERS DE ACCIONES VIA ARGUMENTO --tickers ---')
    file = False
    funds = args.funds
    tickers = args.tickers
    start_date = args.start
    end_date = args.end
    if not args.csv and not args.xlsx:
        format = '%Y-%m-%d'
        try:
            datetime.strptime(args.start, format)
            datetime.strptime(args.end, format)
        except ValueError:
            print('--- INCORRECT DATE STRING FORMAT, IT SHOULD BE YYYY-MM-DD')
            sys.exit(0)
    else:
        if args.csv and args.xlsx:
            print('--- ESPECIFICAR SOLAMENTE UN TIPO DE ARCHIVO (.csv o .xlsx) ---')
            sys.exit(0)
        elif args.csv and not args.xlsx:
            path = os.getcwd()
            csv_files = glob.glob(os.path.join(path, '*.csv'))
            if not csv_files:
                print('--- GUARDAR csv EN CARPETA DEL SCRIPT ---')
                sys.exit(0)
            for index, csv in enumerate(csv_files):
                print(f'N°: {index}\n File Name:', csv.split('\\')[-1])
            try:
                choice = int(input('Ingrese numero de archivo que desea analizar: '))
            except ValueError:
                print('Respuesta incorrecta (debe ser numero).')
                sys.exit(0)
            try:
                pre_file = csv_files[choice]
            except IndexError:
                print('Eligio un numero fuera de rango.')
                sys.exit(0)
            file = pd.read_csv(pre_file, index_col=0)
        else:
            path = os.getcwd()
            xlsx_files = glob.glob(os.path.join(path, '*.xlsx'))
            if not xlsx_files:
                print('--- GUARDAR xlsx EN CARPETA DEL SCRIPT ---')
                sys.exit(0)
            for index, xlsx in enumerate(xlsx_files):
                print(f'N°: {index}\n File Name:', xlsx.split('\\')[-1])
            try:
                choice = int(input('Ingrese numero de archivo que desea analizar: '))
            except ValueError:
                print('Respuesta incorrecta (debe ser numero).')
                sys.exit(0)
            try:
                pre_file = xlsx_files[choice]
            except IndexError:
                print('Eligio un numero fuera de rango.')
                sys.exit(0)
            file = pd.read_excel(pre_file, index_col=0)
        file.sort_index(axis=0, ascending=True, inplace=True)
        file.index.names = ['date']
        print(file)
        if sorted(args.tickers) != sorted(list(file.columns)):
            print('El archivo contiene columnas distintas a los tickers especificados, revisar.')
            sys.exit(0)
        else:
            start_date = file.index[0]
            end_date = file.index[-1]
    Bot(funds, tickers, start_date, end_date, file=file)