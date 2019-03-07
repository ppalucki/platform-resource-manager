from setuptools import setup, find_packages

setup(
    name='prm',
    install_requires=[
        'setuptools',
        'scikit-learn==0.20.0',
        'sklearn==0.0',
        'scipy==1.1.0',
        'pandas==0.23.4',
    ],
    tests_require=[
        'flake8==3.6.0',
        'pytest==4.3.0',
        'requests==2.21.0',
        'pex==1.5.1',
        'tox==3.5.2',
        'pytest-cov==2.6.1'
    ],
    packages=find_packages(),
)
