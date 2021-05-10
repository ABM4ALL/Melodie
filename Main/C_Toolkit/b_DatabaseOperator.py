# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main._Config.ExPackages import *

class DatabaseOperator:

    def read_DataFrame(self, table_name, conn):
        DataFrame = pd.read_sql('select * from ' + table_name, con=conn)
        return DataFrame

    def write_DataFrame(self, table, table_name, column_names, conn):
        table_DataFrame = pd.DataFrame(table, columns=column_names)
        table_DataFrame.to_sql(table_name, conn, index=False, if_exists='replace', chunksize=1000)
        return None

    def copy_DataFrame(self, table_name_from, conn_from, table_name_to, conn_to):
        table = self.read_DataFrame(table_name_from, conn_from)
        table.to_sql(table_name_to, conn_to, index=False, if_exists='replace', chunksize=1000)
        return None



