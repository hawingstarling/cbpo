""" Parsing test cases for PythonEDI """

import unittest
import pprint
from app.edi import pythonedi
import pathlib, os


class TestParse810(unittest.TestCase):
    """ Tests the Parser module """

    def setUp(self):
        self.parser = pythonedi.EDIParser(edi_format="810")

    def test_parse(self):
        self.parser = pythonedi.EDIParser(edi_format="810", element_delimiter="*")
        path_folder = pathlib.Path(__file__).parent.absolute()
        path_file = os.path.join(path_folder, 'fixtures', 'Sample810.4010.txt')
        print(path_file)
        with open(path_file, "r") as test_edi_file:
            test_edi = test_edi_file.read()
            found_segments, edi_data = self.parser.parse(test_edi)
            print("\n\n{}".format(found_segments))
            print("\n\n")
            pprint.pprint(edi_data)
