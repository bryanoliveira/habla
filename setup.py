from setuptools import setup, find_packages

setup(
    name='habla',
    version='0.1.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'habla = habla.chat:main',
            'habla-scan = habla.scanner:main',
        ],
    },
)
