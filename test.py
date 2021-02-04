import unittest
from pandas._testing import assert_frame_equal
from saturn_routes.methods import load_data
import pandas as pd

class TestLoadData(unittest.TestCase):

     def setUp(self):
     # Method results
          self.test_strategic_data, self.test_qgis_data = load_data('tests/strategic_data_test.xlsx', 'tests/qgis_data_test.xlsx')

          # Expected results
          self.expected_strategic_data = pd.DataFrame({'&ROUTES': [pd.NA,'route']*2,
                                                  'O':[74045.0, 74491.0, 74045.0, 74491.0],
                                                  'D': [74054.0, 74490.0, 99001.0, 74490.0],
                                                  'UC': [1.0, 74077.0, 1.0, 74076.0],
                                                  'Flow': [0.020769, 74801.000000, 0.762151, 746.400000]})

          self.expected_qgis_data = pd.DataFrame({'AssBNode':['74811>74810', '74810>74811'],
  												'ID':[221, 219]})
          print(self.expected_qgis_data)

     def test_strategic_data(self):
         assert_frame_equal(self.test_strategic_data.iloc[0:4, 0:5], self.expected_strategic_data)

    def test_gis_data(self):
         assert_frame_equal(test_qgis_data[0:4], expected_qgis_data)



if __name__ == "__main__":
	unittest.main()