import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='abm-framework',
    version='0.1',
    description='A general framework that can be used to establish agent-based models for specific uses.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SongminYu/ABM_Framework',
    author='Songmin Yu',
    author_email='songmin.yu@isi.fraunhofer.de',
    license='BSD 3',
    classifiers=[
        'Development Status :: Just started',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    project_urls={
        'Documentation': 'https://abm-framework.readthedocs.io/en/latest/index.html',
    },
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
    ],
    python_requires='>=3.7, <3.9',
    entry_points={
        'console_scripts': [
            'abm-framework=abm-framework.scripts.scripts:cli'
        ]
    },
)
