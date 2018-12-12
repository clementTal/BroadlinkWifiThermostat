import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BroadlinkWifiThermostat",
    version='2.4.0',
    author="Clément talvard",
    author_email="c.talvard@gmail.com",
    description="Python mmodule to controle broadlink wifi thermostat",
    long_description="Python mmodule to controle broadlink wifi thermostat",
    long_description_content_type="text/markdown",
    url="https://github.com/clementTal/BroadlinkWifiThermostat",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
