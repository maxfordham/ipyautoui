from setuptools import setup
import versioneer

requirements = [
    # package requirements go here
]

setup(
    name='ipyautoui',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="wrapper that sits on top of ipywidgets and other ipy widget libraries to template / automate the creation of widget forms. Uses pydantic to create defined data-container and serialisation to JSON. Includes example patterns for adding new custom widgets.",
    license="BSD",
    author="John Gunstone",
    author_email='gunstone.john@gmail.com',
    url='https://github.com/gunstonej/ipyautoui',
    packages=['ipyautoui'],
    
    install_requires=requirements,
    keywords='ipyautoui',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
