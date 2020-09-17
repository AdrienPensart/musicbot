import logging
import threading
import re
from html.parser import HTMLParser
import click
import requests
import semver


logger = logging.getLogger(__name__)


class MyParser(HTMLParser):
    def __init__(self, output_list=None):
        HTMLParser.__init__(self)
        if output_list is None:
            self.output_list = []
        else:
            self.output_list = output_list

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.output_list.append(dict(attrs).get('href'))


class VersionCheckerThread(threading.Thread):
    def __init__(self, prog_name, current_version, domain='pypi.org', autostart=True, **kwargs):
        super().__init__(**kwargs)
        self.prog_name = prog_name
        self.new_version_warning = None
        self.domain = domain
        self.current_version = current_version
        self.url = f'https://{domain}/simple/{prog_name}'
        if autostart:
            self.start()

    def run(self):
        try:
            resp = requests.get(self.url)
            p = MyParser()
            p.feed(resp.text)
            last_link = p.output_list[-1]
            last_version = re.search(r'(?:(\d+\.[.\d]*\d+))', last_link).group(1)
            if semver.compare(self.current_version, last_version) < 0:
                self.new_version_warning = click.style(
                    f'''
{self.prog_name} : new version {last_version} available (current version: {self.current_version})
upgrade command : pip3 install -U --extra-index-url=https://{self.domain} {self.prog_name}''',
                    fg='bright_blue',
                )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(e)
