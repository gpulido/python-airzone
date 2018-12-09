#!/bin/sh
rm dist/*
python setup.py sdist
python setup.py bdist_wheel
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pip uninstall python-airzone
pip install --index-url https://test.pypi.org/simple/ python-airzone