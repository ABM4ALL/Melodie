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

    def revise_DataType(self, table_name, data_types, conn):
        table_DataFrame = self.read_DataFrame(table_name, conn)
        table_DataFrame.to_sql(table_name, conn, index=False, if_exists='replace', chunksize=1000,
                               dtype=data_types)

