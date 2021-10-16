import os
import sqlite3
import pandas as pd

class DB:

    def create_Connection(self, db_path):
        conn = sqlite3.connect(db_path)
        return conn

    def read_DataFrame(self, table_name, conn, **kwargs):
        if len(kwargs) > 0:
            condition_temp = " where "
            for key, value in kwargs.items():
                condition_temp = condition_temp + key + " == '" + str(value) + "' and "
            condition = condition_temp[0:-5]
            DataFrame = pd.read_sql('select * from ' + table_name + condition, con=conn)
        else:
            DataFrame = pd.read_sql('select * from ' + table_name, con=conn)
        return DataFrame

    def write_DataFrame(self, table, table_name, column_names, conn, **kwargs):
        table_DataFrame = pd.DataFrame(table, columns=column_names)
        if "dtype" in kwargs:
            table_DataFrame.to_sql(table_name, conn, index=False,
                                   if_exists='replace', chunksize=1000, dtype=kwargs["dtype"])
        else:
            table_DataFrame.to_sql(table_name, conn, index=False, if_exists='replace', chunksize=1000)
        return None

    def revise_DataType(self, table_name, data_type, conn):
        table_DataFrame = self.read_DataFrame(table_name, conn)
        table_DataFrame.to_sql(table_name, conn, index=False, if_exists='replace', chunksize=1000,
                               dtype=data_type)



db_path = "C:\\Users\yus\Dropbox\ABM4ALL\Melodie\examples\TertiaryModel\_data\Tertiary.sqlite"
conn = DB().create_Connection(db_path)
table_1 = DB().read_DataFrame("SharedEndUse", conn)
table_2 = DB().read_DataFrame("Sheet1", conn)
list_to_save_column = ["ID_Company", "NACE_CODE", "NACE_CODE_2",
                       "SURVEY_GROUP", "SURVEY_BRANCH_CODE", "SURVEY_SECTOR_CODE"]
list_to_save = []

for row in range(0, len(table_2)):
    firm_row = list(table_2.iloc[row])
    firm_id = firm_row[0]
    value_list = list(table_1.loc[table_1["SEU1"] == firm_id][["SEU2", "SEU3", "SEU4", "SEU5"]].values[0])
    firm_row += value_list
    list_to_save.append(firm_row)

DB().write_DataFrame(list_to_save, "Save", list_to_save_column, conn)



