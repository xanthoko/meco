from os import path
from setuptools import setup, find_packages

__version__ = '0.0.1'

here = path.abspath(path.dirname(__file__))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().split('\n')
    requirements = [x.strip() for x in requirements]

setup(
    author="Konstantinos Xanthopoulos",
    author_email="konxantho@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    description="A packages for modeling asynchronous message-driven systems",
    install_requires=requirements,
    license='BSD',
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="meco",
    packages=find_packages(exclude=['docs', 'tests*']),
    python_requires='>=3.6',
    url="https://github.com/xanthoko/thesis",
    version=__version__,
)
