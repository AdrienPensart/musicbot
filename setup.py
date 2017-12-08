#!/usr/bin/python3

import pip
from setuptools import setup, find_packages

requirements = pip.req.parse_requirements('requirements.txt', session=pip.download.PipSession())
requires = []
links = []
for item in requirements:
    if getattr(item, 'url', None):  # older pip has url
        links.append(str(item.url))
    if getattr(item, 'link', None):  # newer pip has link
        links.append(str(item.link))
    if item.req:
        requires.append(str(item.req))

print(find_packages())
print(requires)

setup(
    name='musicbot',
    author='Adrien Pensart',
    author_email='crunchengine@gmail.com',
    description='Music swiss army knife',
    version_format='{tag}.dev{commitcount}+{gitsha}',
    setup_requires=['setuptools-git-version'],
    install_requires=requires,
    # packages=find_packages('musicbot'),
    packages=['musicbot'],
    entry_points={
        'console_scripts': [
            'musicbot = musicbot.__main__:cli',
        ]
    }
)
