from setuptools import setup, find_packages

setup(
name="bheem-sales",
version="1.0.0",
packages=find_packages(include=["app*"]),
include_package_data=True,
install_requires=["fastapi", "uvicorn"],
)