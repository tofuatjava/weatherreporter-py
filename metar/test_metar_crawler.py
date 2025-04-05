import unittest
import metar_crawler as mc

class TestMetarCrawler(unittest.TestCase):

    def testFetchLOWW(self):
        metar = mc.fetchMetar("LOWW")
        self.assertTrue(metar.startswith("LOWW"))