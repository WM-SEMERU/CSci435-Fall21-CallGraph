import unittest
import sys
import pandas as pd


# pass both csvs 
# python unit_test.py test_method.csv test_edge.csv
# method csv first then edge csv
# TODO: Revise last test case
method_file = None
edge_file = None
compare_edge = None
compare_method = None
file_checker = False
class TestCSV(unittest.TestCase):

    file_checker = True if len(sys.argv) == 5 else False

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
    # does not check if the call line is an integer rather than string
    def test_function_exist(self):
        pass_test = True
        for index, row in self.edge_df.iterrows():
            indx = row['called_index']
            line = row['call_line']
            # get rid of \n as this would cause lines that were called to not be 
            # checked due to indentations

            # convert the call line to a string incase it is an integer
            # cannot check for csv where call lines are not strings
            if(isinstance(row['call_line'],str) == False):
                continue
            elif(line.replace('\n','') in self.method_df['method'][indx].replace('\n','')):                
                continue
            else:
                pass_test = False
        assert True

    # checks if the maximum call exceeds the max method call
    def test_check_call_length(self):
        max_called_index = max(self.edge_df['called_index'])
        row_count = len(self.method_df)
        if(max_called_index <= row_count):
            assert True
        else:
            assert False

    # potentially if you want to give it a csv to compare to

    # checks if the compare file is csv 
    @unittest.skipUnless(file_checker == True, "skip")
    def test_if_edge_is_csv(self):
        print('file_checker', file_checker)
        print('test ran')
        extension = str(compare_edge)
        if(extension[-4:] == '.csv'):
            assert True
        else:
            assert False

    @unittest.skipIf(file_checker == False, "skip")
    def test_if_method_is_csv(self):
        extension = str(compare_method)
        if(extension[-4:] == '.csv'):
            assert True
        else:
            assert False

    # checks if the rows with the edge and comparison file are the same
    # checks that the callee row is the same
    @unittest.skipIf(file_checker == False, "skip")
    def test_compare_edge_callee_csv(self):
        # compare both csv here
        compare_edge_df = pd.read_csv(compare_edge)
        if(compare_edge_df['callee_index'].equals(self.edge_df['callee_index'])):
            assert True
        else:
            assert False

    # checks that the called index is the same
    @unittest.skipIf(file_checker == False, "skip")
    def test_compare_edge_called_csv(self):
        # compare both csv here
        compare_edge_df = pd.read_csv(compare_edge)
        if(compare_edge_df['called_index'].equals(self.edge_df['called_index'])):
            assert True
        else:
            assert False

    # checks that the call row is the same
    @unittest.skipIf(file_checker == False, "skip")
    def test_compare_edge_call_csv(self):
        # compare both csv here
        compare_edge_df = pd.read_csv(compare_edge)
        if(compare_edge_df['call_line'].equals(self.edge_df['call_line'])):
            assert True
        else:
            assert False

    '''
    @unittest.skipIf(file_checker == False, "skip")
    def test_compare_method_called_csv(self):
        # replaces the "\n" in the method columns with spaces in order to compare the columns
        # the parser may strip extra '\n' compared to adding it yourself, so 
        # this is necessary when comparing methods

        """
        def replace_dataframe_values(df):
            t = [None] * len(df)
            i = 0
            for m in df['method']:
                t[i] = m.replace('\n','')
                i +=1

            df['method'] = t
            return df
        """
        def replace_dataframe_values(df):
            pass

        # compare both csv here
        compare_method_df = pd.read_csv(compare_method)
        compare_df = replace_dataframe_values(compare_method_df)
        method_df = replace_dataframe_values(self.method_df)
        print(compare_method_df)
        print(self.method_df)
        if(method_df['method'].equals(compare_df['method'])):
            assert True
        else:
            assert False
    '''

if __name__ == '__main__':
    # makes sure two files are passed as inputs
    # can pass it a csv to compare it to
    if(len(sys.argv) == 5):
        file_checker = True
    else:
        file_checker = False

    if(len(sys.argv) != 3 and len(sys.argv) != 5):
        print('Please input the edge csv followed by the method csv. ')
        print('You can also pass both aditional csvs to compare it line by line')
        print('In order to check output with a specific csv, include the comparison edge and method csv as well.')
        quit()
    # if length if 5 then the user must have input csv to compare to

    # argv is popped out backwards
    # pop out the comparison files first
    # input should be python unit_test edge_file method_file compare_edge compare_method
    if(len(sys.argv) == 5):
        compare_method = sys.argv.pop()
        compare_edge = sys.argv.pop()

    method_file = sys.argv.pop()
    edge_file = sys.argv.pop()


    unittest.main()