import re
import setuptools

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
    description="PyCRUD messenger endpoints",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/derekmerck/python-wuphf",
    packages=setuptools.find_packages(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license='MIT',
    install_requires=["attrs >= 18.1.0",
                      "requests",
                      "pyyaml"],
    extras_require={
        'twilio': 'twilio'
    }
)