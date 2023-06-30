import pathlib
import configparser

# define the root directory of your project
root_dir = pathlib.Path('.')

# create a configparser object
config = configparser.ConfigParser()

# loop over all files in the directory, recursively
for filepath in root_dir.rglob('requirements.txt'):
    # get the parent directory of the file
    parent_dir = filepath.parent

    # get the relative path to the parent directory from the root directory
    rel_path = parent_dir.relative_to(root_dir)

    # read the requirements file
    with filepath.open() as f:
        requirements = f.read().splitlines()

    # add the requirements to the configparser object
    config[str(rel_path)] = {'requirements': requirements}

# write the setup.py file
with open('setup.py', 'w') as f:
    f.write("""\
from setuptools import setup, find_packages

setup(
    name="veda-pipeline-modules",
    version="0.1",
    packages=find_packages(),
    install_requires=[],
    extras_require={
""")
    
    # write each section of the configparser object to the setup.py file
    for section in config.sections():
        f.write(f"        '{section}': {config[section]['requirements']},\n")

    f.write("""\
    }
)
""")

print('setup.py file written')