#!/usr/bin/ENV python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0',
                'pint==0.11',
                'numpy==1.18.2',
                'scipy==1.4.1',
                'matplotlib==3.2.1',
                'ipython==7.13.0',
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
    version='0.1.1.4',
    zip_safe=False,
)
