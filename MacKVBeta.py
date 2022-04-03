#!/usr/bin/python
'''
Copyright <2022> <cfile6066@outlook.com>

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, I
NCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
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
