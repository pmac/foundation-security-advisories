# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import codecs
import glob
import os
import re
import sys
from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import NoArgsCommand, BaseCommand, CommandError

from dateutil.parser import parse as parsedate

from generator.security.models import Product, SecurityAdvisory
from generator.security.utils import (
    FILENAME_RE,
    get_file_checksum,
    mfsa_id_from_filename,
    parse_md_file,
    parse_yml_file,
)


ADVISORIES_PATH = settings.ADVISORIES_PATH

SM_RE = re.compile('seamonkey', flags=re.IGNORECASE)
FNULL = open(os.devnull, 'w')


def fix_product_name(name):
    if 'seamonkey' in name.lower():
        name = SM_RE.sub('SeaMonkey', name, 1)

    if name.endswith('.0'):
        name = name[:-2]

    return name


def filter_advisory_filenames(filenames):
    return [os.path.join(ADVISORIES_PATH, fn) for fn in filenames
            if FILENAME_RE.search(fn)]


def add_or_update_advisory(data, html):
    """
    Add or update an advisory in the database.

    :param data: dict of metadata about the advisory
    :param html: HTML content of the advisory
    :return: SecurityAdvisory
    """
    mfsa_id = data.pop('mfsa_id')
    year, order = [int(x) for x in mfsa_id.split('-')]
    kwargs = {
        'id': mfsa_id,
        'title': data.pop('title'),
        'impact': data.pop('impact', None) or '',
        'reporter': data.pop('reporter', None) or '',
        'filename': data.pop('filename'),
        'checksum': data.pop('checksum'),
        'year': year,
        'order': order,
        'html': html,
    }
    datestr = data.pop('announced', None)
    if datestr:
        dateobj = parsedate(datestr).date()
        kwargs['announced'] = dateobj
    prodver_objs = []

    fixed_in = data.pop('fixed_in')
    if isinstance(fixed_in, basestring):
        fixed_in = [fixed_in]

    for productname in fixed_in:
        productname = fix_product_name(productname)
        productobj, created = Product.objects.get_or_create(name=productname)
        prodver_objs.append(productobj)

    # discard products. we rely on fixed_in.
    data.pop('products', None)

    if data:
        kwargs['extra_data'] = data

    advisory = SecurityAdvisory(**kwargs)
    advisory.save()
    advisory.fixed_in.add(*prodver_objs)
    return advisory


def file_needs_update(filename, checksum):
    try:
        advisory = SecurityAdvisory.objects.get(filename=filename)
    except SecurityAdvisory.DoesNotExist:
        return True

    return advisory.checksum != checksum


def update_db_from_file(filename):
    """
    Parse file for YAML and Markdown and update database.

    :raises: KeyError or ValueError
    :param filename: path to markdown file.
    :return: SecurityAdvisory instance
    """
    checksum = get_file_checksum(filename)
    if not file_needs_update(filename, checksum):
        return None

    if filename.endswith('.md'):
        parser = parse_md_file
    elif filename.endswith('.yml'):
        parser = parse_yml_file
    else:
        raise RuntimeError('Unknown file type %s' % filename)

    return add_or_update_advisory(*parser(filename, checksum))


def get_all_mfsa_files():
    return glob.glob(os.path.join(ADVISORIES_PATH, 'announce', '*', 'mfsa*.*'))


def get_ids_from_files(filenames):
    ids = [mfsa_id_from_filename(fn) for fn in filenames]
    # filter any Nones
    return [mfsa_id for mfsa_id in ids if mfsa_id]


class Command(NoArgsCommand):
    help = 'Refresh database of MoFo Security Advisories.'
    option_list = BaseCommand.option_list + (
        make_option('--quiet',
                    action='store_true',
                    dest='quiet',
                    default=False,
                    help='Do not print output to stdout.'),
    )

    def handle_noargs(self, **options):
        call_command('migrate', noinput=False)
        quiet = options['quiet']

        def printout(msg, ending=None):
            if not quiet:
                self.stdout.write(msg, ending=ending)

        errors = []
        updates = 0
        all_files = get_all_mfsa_files()
        for mf in all_files:
            mf = os.path.join(ADVISORIES_PATH, mf)
            try:
                advisory = update_db_from_file(mf)
            except Exception as e:
                errors.append('ERROR parsing %s: %s' % (mf, e))
                if not quiet:
                    sys.stdout.write('E')
                    sys.stdout.flush()
                continue
            if advisory is not None:
                if not quiet:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                updates += 1
        printout('\nUpdated {0} files.'.format(updates))

        if errors:
            raise CommandError('Encountered {0} errors:\n\n'.format(len(errors)) +
                               '\n==========\n'.join(errors))
