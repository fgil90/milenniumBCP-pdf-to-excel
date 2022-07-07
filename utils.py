import json
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tabula
import re

class Parser():

    @staticmethod
    def parse_pdf(file: str) -> pd.DataFrame:

        keywords = json.load(open('keywords.json'))
        columns = ['data_lanc', 'data_valor','descritivo', 'debito', 'credito', 'saldo']
        try:
            df = tabula.read_pdf(file, pages='all', output_format='dataframe', pandas_options={'header': None}) 
        except:
            print('Could not read file ' + file)
            return

        df = df[0]
        df = Parser.fix_dates(df)
        try:
            df.columns = columns
        except:
            print('Number of columns is not matching. Expected ' + str(len(df.columns)) + ', found ' + str(len(columns)))

        df['categoria'] = df.apply(Parser.parse_category, axis=1, filter=keywords)
           
        Parser.fix_numeric(df,'data_lanc')
        Parser.fix_numeric(df,'data_valor')
        Parser.fix_numeric(df,'debito')
        Parser.fix_numeric(df,'credito')
        Parser.fix_numeric(df,'saldo')
      
        return df

    @classmethod
    def parse_category(self, row, filter={}):
        for key in filter:
            if any(re.search(keyword, row['descritivo'], re.IGNORECASE) for keyword in filter[key]):
                return key
        return 'Other'

    @classmethod
    def fix_numeric(self, df:pd.DataFrame, cat:str):
        df[cat] = df[cat].astype(str)
        df[cat] = df[cat].str.replace(' ', '')
        df[cat] = df[cat].astype(float)

    @staticmethod
    def parse_xlsl(file:str) -> pd.DataFrame:
        return pd.read_excel(file)
    
    @classmethod
    def fix_dates(self, df) -> pd.DataFrame:
        drop_i = []
        for i, row in df.iterrows():
            value = (str(row[0]).strip().split())
            if len(value)>1:
                df.iloc[i,1:-1] = df.iloc[i,0:-2]
                df.iloc[i,0] = value[0]
                df.iloc[i,1] = value[1]
            try:
                float(df.iloc[i,0])
                float(df.iloc[i,1])
            except:
                # print('Indexes to be dropped: '+ str(i))
                drop_i.append(i)
        
        try:
            df.drop(df.index[drop_i], axis=0, inplace=True)
        except:
            print('Could not drop indexes', drop_i)

        return df.reset_index(drop=True)

class Cruncher:
    
    def graph_month_total(df:pd.DataFrame, path:str):
        default_graphs_path = 'Graphs/'

        first_value = df.loc[0, 'saldo']
        temp_df = df.copy(deep=False)
        temp_df['delta'] = df['saldo']-first_value
        temp_df['debito'].fillna(0,inplace=True)
        temp_df['credito'].fillna(0,inplace=True)

        temp_df['amount'] = temp_df['debito'] + temp_df['credito']
        sns.relplot(data=temp_df, x='data_valor', y='delta', size='amount', sizes=(5, 400), color='#344febaa')
        plt.xlabel(xlabel='Mes/Dia')
        plt.ylabel(ylabel='Variacao')
        plt.title('TÍTULO',pad=20)
        sns.lineplot(data=temp_df.groupby('data_valor').mean(), x='data_valor', y='delta', size=1, legend=None, color='#444444cc')
        plt.yticks(list(plt.yticks()[0]) + [temp_df.iloc[-1]['delta']])
        plt.axhline(y=temp_df.iloc[-1]['delta'], color='red', linestyle='dotted')
        plt.savefig(os.path.join(default_graphs_path, path)+"monthly_totals.png",dpi=300)

    def calc_total_exp_and_rev(path:str, dataframes:list[pd.DataFrame]):
        total_df = pd.DataFrame(columns=['expenses', 'revenue', 'balance'])
        for i, df in enumerate(dataframes):
            try:
                total_expenses = df['debito'].sum()
                total_revenue = df['credito'].sum()
                balance = total_revenue - total_expenses
                total_df.loc[i] = [total_expenses, total_revenue, balance]
            except:
                continue
                   
        print(total_df.reset_index(drop=True))
