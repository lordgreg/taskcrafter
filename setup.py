from setuptools import setup, find_packages

setup(
    name="taskcrafter",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "pyyaml"],
    entry_points={"console_scripts": ["taskcrafter=taskcrafter.cli:cli"]},
)
