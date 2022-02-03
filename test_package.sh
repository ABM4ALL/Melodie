python3.8 setup.py bdist_wheel
conda create -n testmelodie python==3.8.5 -y
cd dist
source ~/.bash_profile
conda activate testmelodie
pip install Melodie-1.0.0-cp38-cp38-macosx_10_9_x86_64.whl
pip install pytest
cd ../tests
pytest
#conda remove -n testmelodie --all -y