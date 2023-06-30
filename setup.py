from setuptools import setup, find_packages

setup(
    name="veda-utils",
    version="0.1",
    packages=find_packages(),
    install_requires=['boto3'],
    extras_require={
        's3_discovery': ['awslambdaric', 'smart_open'],
        'cmr_query': ['python-cmr', 'awslambdaric'],
        'cogify': ['awslambdaric', 'rasterio', 'netCDF4', 'rio-cogeo', 'h5py', 'cdsapi'],
        'submit_stac': ['awslambdaric', 'aws-lambda-powertools', 'requests'],
        'proxy': ['aws-lambda-powertools'],
    }
)
