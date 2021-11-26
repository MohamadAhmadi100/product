from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    version='1.0.0',
    name='product',
    license='none',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=['product/product*', 'tests*']),
    install_requires=required,
    author='aasood',
)
