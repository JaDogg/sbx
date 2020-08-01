from codecs import open
from inspect import getsource
from os.path import abspath, dirname, join

from setuptools import find_packages, setup

here = abspath(dirname(getsource(lambda: 0)))

with open(join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sbx",
    version="0.1.0",
    description="StudyBox (SBX) - Terminal Flashcards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JaDogg/sbx",
    author="Bhathiya Perera",
    author_email="JaDogg@users.noreply.github.com",
    python_requires=">=3.6",
    license="MIT",
    package_data={"": ["*.md"]},
    install_requires=[
        "prompt-toolkit>=3.0.5",
        "Pygments>=2.6.1",
        "pytz>=2020.1",
        "tzlocal>=2.1",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="study flashcard terminal",
    packages=find_packages(exclude=["tests", "docs"]),
    entry_points={"console_scripts": ["sbx = sbx.__main__:main"]},
    setup_requires=["wheel"],
)
