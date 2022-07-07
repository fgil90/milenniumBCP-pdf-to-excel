import os
import pandas as pd
from utils import Cruncher, Parser

__author__ = "Your Name"
__version__ = "0.1.0"
__license__ = "MIT"

default_input_path = 'Data/'
default_output_path = 'Output/'

def main():

    print('You can add categories to your expenses and revenue manually after you parse the .pdf into a .xlsl if you want or configure some keywords in the keywords file before (STILL NOT IMPLEMENTED)')
    dataframes = [pd.DataFrame]

    print("Attempting to read .xlsl files in Output folder...")
    if (has_empty_output_folder()):
        print("No files in Output folder")

    try:
        dataframes = read_xlsls()
        print("Files read Sucessfully")
    except:
        print("Could not read files sucessfully.")
            
  
    options = [
        'Exit',
        'Save data from .pdfs to .xlsl (Note: Could have some errors, be sure to check manually afterwards',
        'Load data from .xlsl files',
        'Monthly graphs',
        'Show monthly totals table'
    ]

    choice = -1

    while choice!=0:
        for i, option in enumerate(options):
            print(i, " - ", option)

        choice = int(input('Choose your option:'))

        match choice:
            case 0:
                return
            case 1:
                read_pdfs()
            case 2:
                dataframes = read_xlsls()
            case 3:
                if (len(dataframes) == 0):
                    print('There are no loaded dataframes in memory')
                    continue
                for i, df in enumerate(dataframes):
                    try:
                        Cruncher.graph_month_total(df,str(i+1) + "_")
                    except:
                        continue
            case 4:
                if (len(dataframes) == 0):
                    print('There are no loaded dataframes in memory')
                    continue            
                Cruncher.calc_total_exp_and_rev('', dataframes)
            case _:
                pass

def has_empty_output_folder()->bool:
    return (len(os.listdir(default_output_path)) == 0)

def read_xlsls():
    output_files = [f for f in os.listdir(default_output_path)]
    dataframes = [pd.DataFrame]
    for file in output_files:
        path = os.path.join(default_output_path, file)
        try:
            df = Parser.parse_xlsl(path)
            dataframes.append(df)
        except Exception as e:
            print('Could not parse dataframe ' + file)
            print('Exception: ' + e)
            return
    return dataframes

def read_pdfs():
    input_files = [f for f in os.listdir(default_input_path)]
    output_files = [f for f in os.listdir(default_output_path)]
    for file in input_files:
        output_file = file.replace('.pdf', '.xlsx')
        if (output_file in output_files):
            print(".xlsl file with the same name already exists. " + output_file)
            continue
        path = os.path.join(default_input_path, file)
        try:
            df = Parser.parse_pdf(path)
            save_xlsl(df, file.replace('.pdf', '.xlsx'))
        except Exception as e:
            print('Could not parse dataframe ' + file)
            print('Exception: ' + e)


def save_xlsl(df:pd.DataFrame, file_name:str):
    try:
        excel_file_path = os.path.join(default_output_path, file_name)
        df.to_excel(excel_file_path)
    except Exception as e:
        print('Could not save file as .xlsl')
        print('Exception: ' + e)


if __name__ == "__main__":
    main()

# load excel save with data
# create dashboards and save them
# show options
