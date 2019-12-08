from setuptools import setup, find_packages
import src.gomoku # pytype:disable=import-error

with open('README.md') as f:
  readme = f.read()

TESTS_REQUIRE = [
    'codespell',
    'pytest',
]

setup(
  name='gomoku',
  version='0.1',
  description=readme,
  author='mtrazzi & kcosta',
  url='https://github.com/mtrazzi/gomoku',
  package_dir={'': 'src'},
  packages=find_packages('src', exclude=('tests', 'docs', './gomoku.py')),
  tests_require=TESTS_REQUIRE,
  install_requires=['numpy>=1.16.2'],
  extras_require={
    # recommended packages for development
    'dev': [
        'autopep8',
        'flake8',
        'flake8-blind-except',
        'flake8-builtins',
        'flake8-commas',
        'flake8-debugger',
        'flake8-isort',
        'sphinx',
        'sphinxcontrib-napoleon',
        # for convenience
        *TESTS_REQUIRE,
  ],}
)