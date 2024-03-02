# import os
import sys
import setuptools
import platform
from distutils.extension import Extension


with open("Melodie/version.txt", "r", encoding="utf8") as fv:
    version = fv.read()

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()


def scientific_toolchain_versions():
    python_distribution_bits = 32 if "32" in platform.architecture()[0] else 64
    version = (sys.version_info.major, sys.version_info.minor)
    if python_distribution_bits == 32:
        assert version <= (
            3,
            9,
        ), "Melodie does not support 32 bit cpython interpreter > 3.9"
    numpy_requirement = "numpy"
    matplotlib_requirement = "matplotlib"
    scipy_requirement = "scipy"
    if version == (3, 7):
        matplotlib_requirement = "matplotlib <= 3.5.3"
        scipy_requirement = "scipy <= 1.7.3"
    elif version == (3, 8):
        if python_distribution_bits == 32:
            scipy_requirement = "scipy <= 1.9.1"
    elif version == (3, 9):
        if python_distribution_bits == 32:
            scipy_requirement = "scipy <= 1.9.1"

    return [numpy_requirement, matplotlib_requirement, scipy_requirement]


def db_tools_versions():
    pandas_req = "pandas"
    sqlalchemy_req = "sqlalchemy"
    return []


setuptools.setup(
    name="Melodie",
    version=version,
    description="A general framework that can be used to establish agent-based models for specific uses.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ABM4ALL/Melodie",
    author="Songmin Yu, Zhanyi Hou",
    author_email="abm4all@outlook.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    project_urls={
        "Documentation": "http://docs.abm4all.com",
    },
    packages=setuptools.find_namespace_packages(
        include=["Melodie", "Melodie.*", "MelodieInfra", "MelodieInfra.*"]
    ),
    install_requires=scientific_toolchain_versions()
    + [
        "chardet",
        "pandas",
        "seaborn",
        "networkx",
        "openpyxl",
        "sqlalchemy>=2.0",
        "sqlalchemy_utils",
        "astunparse",
        "pprintast",
        "cloudpickle",
        "scikit-opt~=0.6",
        "rpyc",
        "flask",
        "flask-cors",
        "flask_sock",
    ],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["Melodie=Melodie.scripts.scripts:cli"]},
    include_package_data=True,
)
