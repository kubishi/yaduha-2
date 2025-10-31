from setuptools import setup, find_packages

setup(
    name='yaduha',
    version='0.3',
    packages=['yaduha'],
    install_requires=[
        'openai',
        'pydantic',
        'python-dotenv',
    ]
)
