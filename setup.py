from setuptools import setup
import os

requirements_dir = os.getcwd() + "/requirements.txt"
with open(requirements_dir, "r") as f:
    file = f.readlines()
    requirements = [line.rstrip() for line in file]

setup(
    name='product',
    version='0.1.0',
    description='attribute crud',
    author='Aasood',
    author_email='meisam2236@gmail.com',
    packages=['app'],
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False
)
