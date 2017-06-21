# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import codecs
import os
import re
from hashlib import sha256
from collections import OrderedDict
from logging import getLogger

from django.conf.urls import url
from django.shortcuts import render
from django.template.loader import render_to_string

import yaml
from markdown import markdown


FILENAME_RE = re.compile('mfsa(\d{4}-\d{2,3})\.(md|yml)$')
log = getLogger(__name__)


def mfsa_id_from_filename(filename):
    match = FILENAME_RE.search(filename)
    if match:
        return match.group(1)

    return None


def parse_md_front_matter(lines):
    """Return the YAML and MD sections.

    :param: lines iterator
    :return: str YAML, str Markdown
    """
    # fm_count: 0: init, 1: in YAML, 2: in Markdown
    fm_count = 0
    yaml_lines = []
    md_lines = []
    for line in lines:
        # first line we care about is FM start
        if fm_count < 2 and line.strip() == '---':
            fm_count += 1
            continue

        if fm_count == 1:
            yaml_lines.append(line)

        if fm_count == 2:
            md_lines.append(line)

    if fm_count < 2:
        raise ValueError('Front Matter not found.')

    return ''.join(yaml_lines), ''.join(md_lines)


def get_file_checksum(filename):
    with open(filename) as fh:
        checksum = sha256(fh.read()).hexdigest()

    return checksum


def parse_md_file(file_name, checksum):
    """Return the YAML and MD sections for file_name."""
    with codecs.open(file_name, encoding='utf8') as fh:
        yamltext, mdtext = parse_md_front_matter(fh)

    data = yaml_ordered_safe_load(yamltext)
    if 'mfsa_id' not in data:
        mfsa_id = mfsa_id_from_filename(file_name)
        if mfsa_id:
            data['mfsa_id'] = mfsa_id

    data['filename'] = file_name
    data['checksum'] = checksum
    return data, markdown(mdtext)


def parse_yml_file(file_name, checksum):
    with codecs.open(file_name, encoding='utf8') as fh:
        data = yaml_ordered_safe_load(fh)

    if 'mfsa_id' not in data:
        mfsa_id = mfsa_id_from_filename(file_name)
        if mfsa_id:
            data['mfsa_id'] = mfsa_id

    data['filename'] = file_name
    data['checksum'] = checksum
    return data, generate_yml_advisories_html(data)


def generate_yml_advisories_html(data):
    html = []
    if data.get('description', None):
        html.append(markdown(data['description']))

    for cve, advisory in data['advisories'].items():
        advisory['id'] = cve
        advisory['impact_class'] = advisory['impact'].lower().split(None, 1)[0]
        if advisory.get('bugs', None):
            for bug in advisory['bugs']:
                if not bug.get('desc', None):
                    bug['desc'] = 'Bug %s' % bug['url']
                bug['url'] = parse_bug_url(bug['url'])
        html.append(render_to_string('security/partials/cve.html', advisory))

    return '\n\n'.join(html)


def parse_bug_url(url):
    """
    Take a bug number, list of bug numbers, or a URL and output a URL.

    url could be a bug number, a comma separated list of bug numbers, or a URL.
    """
    # could be an int
    url = str(url).strip()
    if re.match(r'^\d+$', url):
        url = 'https://bugzilla.mozilla.org/show_bug.cgi?id=%s' % url
    elif re.match(r'^[\d\s,]+$', url):
        url = re.sub(r'\s', '', url).replace(',', '%2C')
        url = 'https://bugzilla.mozilla.org/buglist.cgi?bug_id=%s' % url

    return url


def yaml_ordered_safe_load(stream, object_pairs_hook=OrderedDict):
    """
    Load YAML mappings as OrderedDicts

    from http://stackoverflow.com/a/21912744
    """
    class OrderedLoader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                                  construct_mapping)
    return yaml.load(stream, OrderedLoader)


def page(name, tmpl, url_name=None, **kwargs):
    """
    Define a bedrock page.

    The URL name is the template name, with the extension stripped and the
    slashes changed to dots. So if tmpl="path/to/template.html", then the
    page's URL name will be "path.to.template". Set the `url_name` parameter
    to override this name.

    @param name: The URL regex pattern.  If not empty, a trailing slash is
        added automatically, so it shouldn't be included in the parameter
        value.
    @param tmpl: The template name.  Also used to come up with the URL name.
    @param decorators: A decorator or an iterable of decorators that should
        be applied to the view.
    @param url_name: The value to use as the URL name, default is to coerce
        the template path into a name as described above.
    @param kwargs: Any additional arguments are passed to render
        after the request and the template name.
    """
    pattern = r'^%s/$' % name if name else r'^$'

    if url_name is None:
        # Set the name of the view to the template path replaced with dots
        (base, ext) = os.path.splitext(tmpl)
        url_name = base.replace('/', '.')

    def _view(request):
        kwargs.setdefault('urlname', url_name)
        return render(request, tmpl, kwargs)

    return url(pattern, _view, name=url_name)
