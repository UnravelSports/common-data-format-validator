## Release:
0. run `act` to test github workflows locally
1. up status in cdf/__init__.py
1b. if the schema VERSION in cdf/validators/__init__.py changed: run `python generate_docs.py` and commit docs/ (CI fails the PR if you skip this)
2. remove current version in dist/
3. python setup.py sdist bdist_wheel
4. twine upload dist/*
5. api key from .env
6. in github create new release

