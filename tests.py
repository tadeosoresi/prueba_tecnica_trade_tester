import unittest
from scripts.api import Api
from scripts.bot import Bot

class Tests(unittest.TestCase):
    ''' Casos de prueba '''

    def test_api(self):
        api = Api()
        tickers = ['AAPL', 'GGAL']
    
    def test_strategies(self):
        bot = Bot()

if __name__ == '__main__':
    unittest.main()