# setup for package tools
# python3 setup.py sdist bdist_wheel
from setuptools import setup, find_packages

setup(
    name='tcvectordb',
    version='0.0.2',
    description='Tencent VectorDB Python SDK',
    author='tencent vectordb team',
    url='https://github.com/Tencent/vectordatabase-sdk-python',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    python_requires='>=3'
)
