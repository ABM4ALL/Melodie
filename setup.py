import setuptools
import numpy as np
from distutils.extension import Extension

try:
    from Cython.Distutils import build_ext
    from Cython.Compiler import Options
    import Cython
    import numpy
    import sys

    print(
        "cython version is",
        Cython.__version__,
        Cython.__file__,
        sys.executable,
        numpy.__version__,
    )

    Options.annotate = True
    ext_modules = [
        Extension(
            "Melodie.boost._vectorize",
            ["Melodie/boost/_vectorize.pyx"],
            language="c++",
            # extra_compile_args=["-std=c++11"]
        ),
        Extension(
            "Melodie.boost._vectorize2d",
            ["Melodie/boost/_vectorize2d.pyx"],
            language="c++",
            # extra_compile_args=["-std=c++11"]
        ),
        Extension(
            "Melodie.boost.agent_list",
            ["Melodie/boost/agent_list.pyx"],
            language="c++",
            # extra_compile_args=["-std=c++11"]
        ),
        Extension(
            "Melodie.boost.grid",
            ["Melodie/boost/grid.pyx"],
            language="c++",
            # extra_compile_args=["-std=c++11"],
        ),
        # define_macros=[('CYTHON_TRACE', '1')]),
        Extension("Melodie.boost.fastrand", ["Melodie/boost/fastrand.pyx"]),
        Extension(
            "Melodie.boost.basics",
            ["Melodie/boost/basics.pyx"],
            language="c++",
            # extra_compile_args=["-std=c++11"]
        ),
        # Extension("Melodie.boost.containers.container",
        #           ["Melodie/boost/containers/container.pyx"],
        #           language="c++",
        #           # extra_compile_args=["-std=c++11"]
        #           ),
    ]
except:
    import traceback

    traceback.print_exc()
    ext_modules = None

    def build_ext(_):
        return print(
            "Cython was not installed. With cython you may get better peformance boost!"
        )


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Melodie",
    version="0.1.0",
    description="A general framework that can be used to establish agent-based models for specific uses.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SongminYu/Melodie",
    author="Songmin Yu",
    author_email="songmin.yu@isi.fraunhofer.de",
    license="BSD 3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows"
        "Programming Language :: Python :: 3",
        # 'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 3.8',
        # 'Programming Language :: Python :: 3.9',
        # 'Programming Language :: Python :: 3.10',
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    project_urls={
        "Documentation": "https://Melodie.readthedocs.io/en/latest/index.html",
    },
    packages=setuptools.find_namespace_packages(include=["Melodie", "Melodie.*"]),
    install_requires=[
        "chardet",
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "networkx",
        "openpyxl",
        "websockets",
        "sqlalchemy",
        "astunparse",
        "pprintast",
        "cython==3.0.0a10",
    ],
    python_requires=">=3.5",
    entry_points={"console_scripts": ["Melodie=Melodie.scripts.scripts:cli"]},
    include_package_data=True,
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    include_dirs=[np.get_include()],
)
