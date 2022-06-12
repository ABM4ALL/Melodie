cd ..
python3 setup.py build_ext -i

cd docs/
sphinx-build source build/html -E -a
