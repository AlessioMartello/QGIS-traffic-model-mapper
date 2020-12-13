from pandas._testing import assert_frame_equal
from saturn_routes.methods import load_data
import pandas as pd

# Method results
test_strategic_data, test_qgis_data = load_data('tests/strategic_data_test.xlsx', 'tests/qgis_data_test.xlsx')

# Expected results
expected_strategic_data = pd.DataFrame({'&ROUTES': [pd.NA,'route']*2,
                                        'O':[74045.0, 74491.0, 74045.0, 74491.0],
                                        'D': [74054.0, 74490.0, 99001.0, 74490.0],
                                        'UC': [1.0, 74077.0, 1.0, 74076.0],
                                        'Flow': [0.020769, 74801.000000, 0.762151, 746.400000]})

# expected_qgis_data = pd.DataFrame()
# Test
assert_frame_equal(test_strategic_data.iloc[0:4, 0:5], expected_strategic_data)
# assert_frame_equal(test_qgis_data[:4], expected_qgis_data)
#todo: add qgis test