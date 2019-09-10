import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="wuphf_cli",
    version="1.0.0",
    author="Derek Merck",
    author_email="derek.merck@ufl.edu",
    description="Command line interface for WUPHF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/derekmerck/python-wuphf",
    packages=setuptools.find_packages(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license='MIT',
    install_requires=["click"],

    entry_points='''
        [console_scripts]
        wuphf-cli=wuphf_cli.cli:main
    ''',
)