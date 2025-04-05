import unittest
import metar_parser as mp

class TestMetarParser(unittest.TestCase):
    def test_parse_metar(self):
        metar = "KJFK 202300Z 24004KT 10SM CLR 28/22 A2992"
        result = mp.parseMETAR(metar)
        self.assertEqual(result["wind"], {'direction': 240, 'speed': 4, 'unit': 'KT', 'gust': None})
        self.assertEqual(result["visibility"], 16093)
        self.assertEqual(result["clouds"], ["clear of clouds below 12000ft"])
        self.assertEqual(result["temperatures"]["temperature"], 28)
        self.assertEqual(result["temperatures"]["dew_point"], 22)
        self.assertEqual(result["QNH"], 1013)

    def test_parse_metar2(self):
        metar = "LOWW 191820Z 15010KT CAVOK 06/M05 Q1029 NOSIG"
        result = mp.parseMETAR(metar)
        self.assertEqual(result["temperatures"]["temperature"], 6)
        self.assertEqual(result["temperatures"]["dew_point"], -5)
        self.assertEqual(result["visibility"], 10000)

    def test_gustWinds(self):
        metar = "LOWW 051420Z 35018G29KT 9999 FEW050 17/05 Q1007 NOSIG"
        result = mp.parseMETAR(metar)
        self.assertEqual(result["wind"]["gust"], 29)

if __name__ == '__main__':
    unittest.main()