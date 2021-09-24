import setuptools

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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
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
    ],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'Melodie=Melodie.scripts.scripts:cli'
        ]
    },
    include_package_data=True
)
