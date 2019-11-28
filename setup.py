from setuptools import setup, find_packages

with open('README.md') as f:
  readme = f.read()

setup(
  name='gomoku',
  version='0.1',
  description=readme,
  author='mtrazzi & kcosta',
  url='https://github.com/mtrazzi/gomoku',
  packages=find_packages(exclude=('tests', 'docs'))
)