import setuptools
import numpy as np
from distutils.extension import Extension

try:
    from Cython.Distutils import build_ext
    ext_modules = [
        Extension("Melodie.boost._vectorize",  # location of the resulting .so
                  ["Melodie/boost/_vectorize.pyx"], ),
        Extension("Melodie.boost._vectorize2d",  # location of the resulting .so
                  ["Melodie/boost/_vectorize2d.pyx"], )
    ]
except:
    import traceback

    traceback.print_exc()
    ext_modules = None
    build_ext = lambda _: print('Cython was not installed. With cython you may get better peformance boost!')
with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='Melodie',
    version='0.1',
    description='A general framework that can be used to establish agent-based models for specific uses.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SongminYu/Melodie',
    author='Songmin Yu',
    author_email='songmin.yu@isi.fraunhofer.de',
    license='BSD 3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows'
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 3.8',
        # 'Programming Language :: Python :: 3.9',
        # 'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    project_urls={
        'Documentation': 'https://Melodie.readthedocs.io/en/latest/index.html',
    },
    packages=setuptools.find_namespace_packages(
        include=['Melodie', 'Melodie.*']
    ),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'networkx',
        'openpyxl'
    ],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'Melodie=Melodie.scripts.scripts:cli'
        ]
    },
    include_package_data=True,
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext},
    include_dirs=[np.get_include()]
)
