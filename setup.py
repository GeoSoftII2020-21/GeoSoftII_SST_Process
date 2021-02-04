import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geosoft2-sst-process", 
    version="0.0.1",
    author="digilog11",
    author_email="66838684+digilog11@users.noreply.github.com",
    description="A script for calculating the arithmatic mean of sst data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GeoSoftII2020-21",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='3.8.6',
)
