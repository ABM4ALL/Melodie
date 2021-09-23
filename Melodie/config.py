import os


class Config:
    def __init__(self,
                 project_name: str,
                 project_root: str = '',
                 db_folder: str = '_database',
                 output_folder: str = '_output',
                 with_db: bool = True
                 ):
        self.project_name = project_name
        assert self.project_name.isidentifier(), 'project_name should be a valid identifier'
        self.project_root = project_root
        if self.project_root != '':
            assert os.path.exists(project_root)
        self.with_db = with_db
        if with_db:
            self.db_folder = os.path.join(self.project_root, db_folder)
            if not os.path.exists(self.db_folder):
                os.mkdir(self.db_folder)
            self.output_folder = os.path.join(self.project_root, output_folder)
            if not os.path.exists(self.output_folder):
                os.mkdir(self.output_folder)
