#encoding: utf-8

import unittest
from main import CompareApp
 
class TestCompareApp(unittest.TestCase):

    def test_case1(self):
        app = CompareApp('WatchGuard Firebox® M440','WatchGuard Firebox® M5600')
        result = app.get_csv_result()
        self.assertNotEqual(result,None)

    def test_case2(self):
        app = CompareApp('WatchGuard Firebox® M440','WatchGuard Firebox® M5600','WatchGuard® Firebox T70')
        csv = app.get_csv_result()
        self.assertNotEqual(csv,None)

    def test_case3(self):
        with self.assertRaises(Exception):
            app = CompareApp('WatchGuard Firebox® M440')
            csv = app.get_csv_result()

if __name__ == '__main__':
    unittest.main()