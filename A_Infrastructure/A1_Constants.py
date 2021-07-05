
import os
from pathlib import Path

class CONS:

    def __init__(self):
        self.ProjectPath = Path(os.path.dirname(__file__)).parent
        self.DatabasePath = os.path.join(str(self.ProjectPath) ,"_Database")
        self.FiguresPath = os.path.join(str(self.ProjectPath) , "_Figures")
        self.RootDB = "WealthDistribution"


        

