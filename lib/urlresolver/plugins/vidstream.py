"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import urllib2
from urlresolver import common

# Custom imports
import re


class VidstreamResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "vidstream"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()
        #e.g. http://vidstream.in/xdfaay6ccwqj
        self.pattern = 'http://((?:www.)?vidstream.in)/(.*)'


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        try:
            resp = self.net.http_GET(web_url)
        except urllib2.URLError, e:
            common.addon.log_error(self.name + ': got http error %d fetching %s' %
                                    (e.code, web_url))
            return False
        html = resp.content
        post_url = resp.get_url()

        # get post vars
        form_values = {}
        for i in re.finditer('<input.*?name="(.*?)".*?value="(.*?)">', html):
            form_values[i.group(1)] = i.group(2)
        try:
            html = self.net.http_POST(post_url, form_data=form_values).content
        except urllib2.URLError, e:
            common.addon.log_error(self.name + ': got http error %d fetching %s' %
                                    (e.code, settings_url))
            return False
        # get stream url
        pattern = 'file:\s*"([^"]+)",'
        r = re.search(pattern, html)
        if r:
            return r.group(1)

        return False

    def get_url(self, host, media_id):
            return 'http://vidstream.in/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        return re.match(self.pattern, url) or self.name in host