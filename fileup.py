#!/usr/bin/env python
# -*-Python-*-

import argparse
import base64
import datetime
import ftplib
import os
import subprocess
import tempfile

# Get arguments
parser = argparse.ArgumentParser(description='Publish a file.')
parser.add_argument('fname', type=str)
parser.add_argument('-t', '--time', type=int, default=90)
parser.add_argument('-d', '--direct', action='store_true')
parser.add_argument('-i', '--img', action='store_true')
args = parser.parse_args()


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub('[-\s]+', '-', value))


fname = os.path.abspath(os.path.expanduser(args.fname))
fname_base = os.path.basename(fname)
today = datetime.datetime.now().date()

# Read the config
with open(os.path.expanduser('~/.config/fileup/config'), 'r') as f:
    """Create a config file at ~/.config/fileup/config with the
    following information and structure:
        example.com
        file_up_folder
        my_user_name
        my_difficult_password
    """
    base_url, folder, user, pw = [s.replace('\n', '') for s in f.readlines()]


# Connect to server
ftp = ftplib.FTP(base_url, user, pw)
ftp.cwd('/public_html/' + folder)


# Remove all files that are past the limit
files = [f for f in ftp.nlst() if '_delete_on_' in f]
file_dates = [f.rsplit('_delete_on_', 1) for f in files]
for file_name, date in file_dates:
    rm_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    if rm_date < today:
        try:
            ftp.delete(file_name)
        except:
            # File didn't exist anymore for some reason...
            pass
        ftp.delete(file_name + "_delete_on_" + date)


# Fix the filename to avoid filename character issues
fname_base = slugify(fname_base)


# Delete first if file already exists, it could happen that there is already
# a file with a specified deletion date, these should be removed.
for f in ftp.nlst():
    if f.startswith(fname_base) and '_delete_on_' in f:
        ftp.delete(f)


if args.time != 0:  # could be negative (used for debugging).
    remove_on = today + datetime.timedelta(days=args.time)
    fname_date = fname_base + '_delete_on_' + str(remove_on)
    with tempfile.TemporaryFile() as f:
        print('upload ' + fname_date)
        ftp.storbinary('STOR {0}'.format(fname_date), f)


# Upload and open the actuall file
with open(fname, 'rb') as f:
    ftp.storbinary('STOR {0}'.format(fname_base), f)
    print('upload ' + fname_base)
    ftp.quit()


# Create URL
url = '{}/{}/{}'.format(base_url, folder, fname_base)


if args.direct:
    # Returns the url as is.
    url = 'http://' + url
elif args.img:
    url = '![](http://{})'.format(url)
elif fname.endswith('ipynb'):
    # Return the url in the nbviewer
    url = 'http://nbviewer.jupyter.org/url/' + url


# Put a URL into clipboard
process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'},
                           stdin=subprocess.PIPE)

process.communicate(url.encode('utf-8'))