# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['musicbot', 'musicbot.cli', 'musicbot.commands', 'musicbot.music']

package_data = \
{'': ['*'], 'musicbot': ['schema/*']}

install_requires = \
['attrs>=21.2.0,<22.0.0',
 'click-skeleton>=0.15,<0.16',
 'colorlog>=5.0.1,<6.0.0',
 'fuzzywuzzy>=0.18.0,<0.19.0',
 'graphql-py>=0.8.1,<0.9.0',
 'humanize>=3.0.1,<4.0.0',
 'logging-tree>=1.8,<2.0',
 'mutagen>=1.44.0,<2.0.0',
 'prettytable>=2.1.0,<3.0.0',
 'progressbar2>=3.53.1,<4.0.0',
 'prompt_toolkit>=3.0.2,<4.0.0',
 'pyacoustid>=1.1,<2.0',
 'pydub>=0.25.1,<0.26.0',
 'python-Levenshtein>=0.12.2,<0.13.0',
 'python-slugify>=5.0.0,<6.0.0',
 'python-vlc>=3.0,<4.0',
 'requests>=2.24.0,<3.0.0',
 'spotipy>=2.16.0,<3.0.0',
 'types-python-slugify>=0.1.1,<0.2.0',
 'types-requests>=2.25.0,<3.0.0',
 'watchdog>=2.0.2,<3.0.0',
 'youtube_dl>=2021.3.3,<2022.0.0']

entry_points = \
{'console_scripts': ['musicbot = musicbot.main:main',
                     'musicbot-fire = musicbot.main:main_fire']}

setup_kwargs = {
    'name': 'musicbot',
    'version': '0.7.5',
    'description': 'Music swiss army knife',
    'long_description': None,
    'author': 'Adrien Pensart',
    'author_email': 'crunchengine@gmail.com',
    'maintainer': 'Adrien Pensart',
    'maintainer_email': 'crunchengine@gmail.com',
    'url': 'https://github.com/AdrienPensart/musicbot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)

