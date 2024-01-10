# setup for package tools
# python3 setup.py sdist bdist_wheel
from setuptools import setup, find_packages

setup(
    name='tcvectordb',
    version='1.2.0',
    description='Tencent VectorDB Python SDK',
    author='tencent vdb team',
    url='',
    packages=find_packages(),
    install_requires=[
        'requests',
        'cos-python-sdk-v5==1.9.26',
    ],
    python_requires='>=3'
)
