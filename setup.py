# setup for package tools
# python3 setup.py sdist bdist_wheel
from setuptools import setup, find_packages

setup(
    name='tcvectordb',
    version='1.4.1',
    description='Tencent VectorDB Python SDK',
    author='tencent vdb team',
    url='',
    packages=find_packages(),
    install_requires=[
        'requests',
        'cos-python-sdk-v5',
        'grpcio',
        'grpcio-tools',
        'cachetools',
        'urllib3',
        'tcvdb-text'
    ],
    python_requires='>=3'
)
