import unittest
import sys
import pandas as pd


# pass both csvs 
# python unit_test.py test_method.csv test_edge.csv
# method csv first then edge csv
method_file = None
edge_file = None
has_compare = False
compare_edge_file = None
compare_method_file = None
class TestCSV(unittest.TestCase):


    def setUp(self):
        self.method_df = pd.read_csv(method_file)
        self.edge_df = pd.read_csv(edge_file)
        #print(self.method_df)
    
    # checks that the method file passed in has the file extension csv
    def test_method_is_a_csv(self):
        extension = str(method_file)
        if(extension[-3:] == 'csv'):
            assert True
        else:
            assert False

    # checks that the edge file passed has the file extension csv
    def test_edge_is_a_csv(self):
        extension = str(edge_file)
        if(extension[-4:] == '.csv'):
            assert True
        else:
            assert False

    # checks that the csv output has the correct columns
    def test_method_structure(self):
        numberColumns = len(self.method_df.columns)
        self.assertEqual(numberColumns, 2)
        #print(self.method_df)

    # checks that the structure of the edge csv is correct 
    def test_edge_structure(self):
        numberColumns = len(self.edge_df.columns)
        self.assertEqual(numberColumns, 4)
        #print(self.method_df)

    # compares the calls and makes sure they exist within the method csv
    def test_function_exist(self):
        pass_test = True
        for index, row in self.edge_df.iterrows():
            indx = row['called_index']
            line = row['call_line']
            # get rid of \n as this would cause lines that were called to not be 
            # checked due to indentations
            if(line.replace('\n','') in self.method_df['method'][indx].replace('\n','')):
                continue
            else:
                pass_test = False
        self.assertEqual(pass_test, True)

    # checks if the maximum call exceeds the max method call
    def test_check_call_length(self):
        max_called_index = max(self.edge_df['called_index'])
        row_count = len(self.method_df)
        if(max_called_index <= row_count):
            assert True
        else:
            assert False

    # potentially if you want to give it a csv to compare to

    # # checks if the compare file is csv 
    # @unittest.skipIF(has_compare == False)
    # def test_if_compare_is_csv(self):
    #     extension = str(compare_file)
    #     if(extension[-4:] == '.csv'):
    #         assert True
    #     else:
    #         assert False

    # @unittest.skipIF(has_compare == False)
    # def test_compare_method_csv(self):
    #     pass
    #         # run the compare test


if __name__ == '__main__':
    # makes sure two files are passed as inputs
    # can pass it a csv to compare it to
    if(len(sys.argv) != 3):
        print('Please input the edge csv followed by the method csv. ')
        print('You can also pass both aditional csvs to compare it line by line')
        quit()

    edge_file = sys.argv.pop()
    method_file = sys.argv.pop()

    unittest.main()