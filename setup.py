
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='musicbot',
    version='0.7.5',
    description='Music swiss army knife',
    python_requires='<3.9,>=3.8',
    author='Adrien Pensart',
    author_email='crunchengine@gmail.com',
    license='MIT',
    entry_points={"console_scripts": ["musicbot = musicbot.main:main", "musicbot-fire = musicbot.main:main_fire"]},
    packages=['musicbot', 'musicbot.cli', 'musicbot.commands', 'musicbot.music'],
    package_dir={"": "."},
    package_data={"musicbot": ["schema/*.sql"]},
    install_requires=['attrs==20.*,>=20.1.0', 'click-skeleton==0.*,>=0.13.0', 'colorlog==5.*,>=5.0.1', 'fuzzywuzzy==0.*,>=0.18.0', 'graphql-py==0.*,>=0.8.1', 'humanize==3.*,>=3.0.1', 'logging-tree==1.*,>=1.8.0', 'mutagen==1.*,>=1.44.0', 'prettytable==2.*,>=2.1.0', 'progressbar2==3.*,>=3.53.1', 'prompt-toolkit==3.*,>=3.0.2', 'pyacoustid==1.*,>=1.1.0', 'pydub==0.*,>=0.25.1', 'python-levenshtein==0.*,>=0.12.2', 'python-slugify==4.*,>=4.0.0', 'python-vlc==3.*,>=3.0.0', 'requests==2.*,>=2.24.0', 'spotipy==2.*,>=2.16.0', 'watchdog==2.*,>=2.0.2', 'youtube-dl==2021.*,>=2021.3.3'],
    extras_require={"dev": ["bump2version==1.*,>=1.0.0", "coverage-badge==1.*,>=1.0.0", "dephell==0.*,>=0.8.3", "flake8==3.*,>=3.8.3", "mypy==0.*,>=0.812.0", "pygments==2.*,>=2.7.0", "pylint==2.*,>=2.6.0", "pytest-cov==2.*,>=2.6.0", "pytest-docker-compose==3.*,>=3.1.2", "pytest-timeout==1.*,>=1.4.2", "pytype==2021.*,>=2021.2.23", "restructuredtext-lint==1.*,>=1.3.0"]},
)
