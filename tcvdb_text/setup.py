# setup for package tools
# python3 setup.py sdist bdist_wheel
from setuptools import setup, find_packages

setup(
    name='tcvdb_text',
    version='1.1.1',
    description='Tencent VectorDB Sparse Vector SDK',
    author='tencent vdb team',
    url='',
    packages=find_packages(),
    package_data={
        'tcvdb_text': ['data/*.txt', 'data/*.json'],
    },
    install_requires=[
        'numpy',
        'tqdm',
        'mmh3',
        'jieba>=0.42.1',
    ],
    python_requires='>=3'
)
