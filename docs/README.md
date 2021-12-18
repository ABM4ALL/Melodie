sphinx-build -b gettext ./source build/gettext
sphinx-intl update -p ./build/gettext -l zh_CN
sphinx-build -b html -D language=zh_CN ./source/ build/html/zh_CN

sphinx-autobuild -b html source build/html

set SPHINXOPTS=-D language=zh_CN
make.bat html