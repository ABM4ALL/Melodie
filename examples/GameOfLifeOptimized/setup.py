import setuptools
import numpy as np
from distutils.extension import Extension

from Cython.Distutils import build_ext
from Cython.Compiler import Options
import sys
sys.path.append("/Users/hzy/Documents/Projects/MelodieABM/Melodie")

Options.annotate = True
ext_modules = [
    Extension("model.environment",
              ["model/environment.py"], ),
]

setuptools.setup(
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext},
    include_dirs=[np.get_include()]
)
