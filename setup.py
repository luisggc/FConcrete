#!/usr/bin/ENV python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['pint==0.11',
                'numpy==1.18.2',
                'matplotlib==3.2.1',
                'pandas==1.0.3',
                'ezdxf==0.11.1'
                ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Luis Gabriel Gonçalves Coimbra",
    author_email='luiscoimbraeng@outlook.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Concrete beams according to NBR:6118:2014",
    entry_points={
        'console_scripts': [
            'fconcrete=fconcrete.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fconcrete',
    name='fconcrete',
    packages=find_packages(include=['fconcrete', 'fconcrete.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/luisggc/fconcrete',
    version='0.1.1.5',
    zip_safe=False,
    exclude_package_data = {'': ['docs/*', 'tests/*', 'examples/*', 'ENV/*', '.git/*', '.github/*']}
)
