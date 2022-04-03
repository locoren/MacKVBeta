#!/usr/bin/python
from sys import version_info

from requests import get

if version_info.major == 2:
    from HTMLParser import HTMLParser
elif version_info.major == 3:
    from html.parser import HTMLParser
else:
    raise Exception('unsupported interpreter {version}'.format(version=version_info.major))
from os import environ, link, unlink
from os.path import exists

config = "{home}/Library/MakeMKV/settings.conf".format(home=environ['HOME'])
url = 'https://forum.makemkv.com/forum/viewtopic.php?f=5&t=1053'


class RParser(HTMLParser):
    def __init__(self):
        self.reset()
        self.depth = 0
        self.code = None

    def handle_starttag(self, tag, attrs):
        if tag == 'code':
            self.depth = self.depth + 1

    def handle_endtag(self, tag):
        if tag == 'code':
            self.depth = self.depth - 1

    def handle_data(self, data):
        if self.depth == 1:
            self.code = data


def update_config(code):
    lines = []
    with open(config, 'rt') as fd:
        for line in fd:
            if not line.startswith('app_Key = '):
                lines.append(line)
            else:
                new_key = 'app_Key = "{code}"\n'.format(code=code)
                if new_key == line:
                    print('key {key} has not changed, no update needed'.format(key=code))
                    return  # no change needed
                else:
                    lines.append(new_key)
    bak = "{config}.bak".format(config=config)
    if exists(bak):
        unlink(bak)
    link(config, bak)
    unlink(config)
    with open(config, 'wt') as fd:
        fd.write("".join(lines))
    print('updated {config}, old config saved as {old}'.format(config=config, old=bak))


if not exists(config):
    raise Exception("Need an existing config file first")

response = get(url)
if response.ok:
    content = response.content.decode('utf-8')
    rp = RParser()
    rp.feed(content)
    if rp.code is not None:
        update_config(rp.code)
