cd ..
python setup.py build_ext -i

cd docs/
python -m sphinx -E -a source html
