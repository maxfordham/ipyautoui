
from setuptools import setup, find_packages
import versioneer

with open('README.md') as readme_file:
    README = readme_file.read()

with open('requirements.txt') as requirements_file:
    reqs = requirements_file.readlines()
REQUIREMENTS = [r.split('==')[0] for r in reqs] # lets the mamba solver solve versions

setup(
    name='ipyautoui',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="wrapper that sits on top of ipywidgets and other ipy widget libraries to template / automate the creation of widget forms. Uses pydantic to create defined data-container and serialisation to JSON. Includes example patterns for adding new custom widgets.",
    license="BSD",
    author="John Gunstone",
    author_email='gunstone.john@gmail.com',
    url='https://github.com/gunstonej/ipyautoui',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=REQUIREMENTS,
    keywords='ipyautoui',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
