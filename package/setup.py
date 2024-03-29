import re
import setuptools
from pathlib import Path

with open("../README.md") as f:
    long_description = f.read()

with open("../requirements.txt") as f:
    reqs = f.read().splitlines()

with open("wuphf/__init__.py") as f:
    content = f.read()
    match = re.findall(r"__([a-z0-9_]+)__\s*=\s*\"([^\"]+)\"", content)
    print(match)
    metadata = dict(match)

setuptools.setup(
    name=metadata.get("name"),
    version=metadata.get("version"),
    author=metadata.get("author"),
    author_email=metadata.get("author_email"),
    description=metadata.get("desc"),
    url=metadata.get("url"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license='MIT',
    install_requires=reqs
)