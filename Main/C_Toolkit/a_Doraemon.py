# -*- coding: utf-8 -*-
__author__ = 'Songmin'

from Main._Config.ExPackages import *
from Main._Config.ExParameters import *

class Doraemon:

    def conn_create(self, DatabaseName):
        conn = sqlite3.connect(DatabaseFolder + DatabaseName + ".sqlite")
        return conn

