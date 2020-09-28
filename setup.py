import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tcpsockets",
    version="1.0.0",
    author="Ayan Datta",
    author_email="advin4603@gmail.com",
    description="A package to easily create TCP servers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/advin4603/tcpsockets",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)