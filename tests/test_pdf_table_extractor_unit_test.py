import unittest

# Add the src folder to the path, so the tests can import the modules
import sys, os; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.extraction.extrator_tabela_pdf

class TestStringMethods(unittest.TestCase):
    def test_string_list(self):
        test_value = [1, 4, 2]
        result = src.extraction.extrator_tabela_pdf.toStringList(test_value)
        self.assertEqual(result, "1, 4, 2")
    
    def test_string_list_empty(self):
        test_value = []
        result = src.extraction.extrator_tabela_pdf.toStringList(test_value)
        self.assertEqual(result, "")

class TestConversionMethods(unittest.TestCase):
    def test_convert_list(self):
        original_list = [1, 2, 3]
        converting_widht = 3
        self.assertEqual(src.extraction.extrator_tabela_pdf.transformarColunas(original_list, converting_widht), [0.03, 0.06, 0.09])

    def test_convert_PTBR_format_currency_to_normalized_string(self):
        func = src.extraction.extrator_tabela_pdf.convertPTBRToNormalizedString
        self.assertEqual(func("1.234,56"), "1234.56")
        self.assertEqual(func("1.000.234,56"), "1000234.56")
        self.assertEqual(float(func("1.000.234")), 1000234.0)

class TestIRRFExtractionMethods(unittest.TestCase):
    def test_extract_base_IRRF(self):
        func = src.extraction.extrator_tabela_pdf.extractBaseValueFromIRRFString
        self.assertEqual(func("I.R.R.F. s/ operações, base R$194,00"), 194.0)
        self.assertEqual(func("I.R.R.F. s/ operações, base R$0,00"), 0.0)
        self.assertEqual(func("I.R.R.F. s/ operações, base R$ 0,00"), 0.0)
        self.assertEqual(func("I.R.R.F. s/ operações, base R$1.822,30"), 1822.30)

if __name__ == '__main__':
    unittest.main()