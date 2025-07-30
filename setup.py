from setuptools import setup, find_packages

setup(
    name='bheem-sales',
    version='1.0.0',
    packages=find_packages(include=["sales", "sales.*"]),
    install_requires=[],
    include_package_data=True,
    description='Bheem Sales ERP module',
    author='Bheem Core Team',
    url='https://github.com/bheemverse/Bheem_Sales'
)

