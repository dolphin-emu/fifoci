#! /usr/bin/env python

# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

# Runs a system specific script to generate frame dumps, and exports the test
# results to a Zip file that can then be imported back by the central system.
#
# The Zip needs to contain the following files:
#  * fifoci-result/meta.json
#  * fifoci-result/*.png
#
# meta.json example:
# {
#   "type": "opengl",
#   "rev": {
#     "base": "HASH",
#     "hash": "HASH",
#     "name": "name"
#   },
#   "results": {
#     "fifotest1": {
#       "failure": false,
#       "hashes": [ ... ]
#     },
#     ...
#   }
# }
#
# Assumes this is running in a directory that's part of the Dolphin Git
# repository.
#
# REQUIRES:
#  * Pillow
#  * requests
#  * (CLI) git, until our Buildbot config gets better

from PIL import Image

import argparse
import hashlib
import json
import os
import os.path
import requests
import shutil
import subprocess
import sys
import tempfile
import zipfile


def recent_enough():
    """A bit ugly, but checks that the version being ran is more recent than
    the one introducing features we need for fifoci to not hang.

    20e82ec08c9ab811b04664a6a4f9859924f712f0 adds the configuration option to
    stop a FIFO log playback after the last frame was rendered (instead of
    looping back to the first frame).

    b7916f965530b0369bf08ed6bc9ec3ef20f7cd2f fixes a WX assert error that
    causes freezes on Windows FifoCI (and is a close descendent of another
    commits that adds DumpFramesSilent to remove more interactivity).
    """
    return os.system('git merge-base --is-ancestor '
                     'b7916f965530b0369bf08ed6bc9ec3ef20f7cd2f HEAD') == 0


def find_parents(rev_hash):
    """List a given number of parents commits from a Git hash. Required until
    the Buildbot starts getting this information from Github.
    """
    out = []
    ref = rev_hash
    for i in range(50):
        ref += "^"
        hash = subprocess.check_output('git rev-parse ' + ref, shell=True).strip()
        out.append(hash.decode('ascii'))
    return out


def download_dff(url, path):
    """Downloads a missing DFF from the specified URL to a given FS path."""
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        print('DFF %s not found' % url)
        return False
    with open(path, 'wb') as fp:
        for chunk in resp.iter_content(chunk_size=4096):
            if chunk:
                fp.write(chunk)
    return True


def generate_targets_list(dff_dir, url_base):
    """Generates a list of targets and their respective output directory from a
    given spec URL. If the required input files are missing, they are
    downloaded from the URL given in the spec.
    """
    url_base = url_base.rstrip('/')
    out = []
    spec = requests.get(url_base + '/dff/').json()
    for target in spec:
        path = os.path.join(dff_dir, target['filename'])
        success = True
        if not os.path.exists(path):
            print('DFF %s does not exist, downloading...' % path)
            success = download_dff(url_base + target['url'], path)
        if success:
            out.append((target['shortname'], path,
                        tempfile.mkdtemp(suffix='.fifoci-out')))
    return out


def get_existing_images(url_base):
    """Downloads the list of images already present on the server to reduce
    upload footprint. Only new images will be present in the result zip.
    """
    return requests.get(url_base.rstrip('/') + '/existing-images/').json()


def spawn_tests(args, targets):
    """Spawn the test runner, which will run each log and write output images
    to a given path.
    """
    base_path = os.path.dirname(__file__)
    backend, system, driver = args.type.split('-', 2)

    # HACK: Since we use : as field separator, C:\ paths on windows break.
    # Assume that we are only ever going to run fifoci on the system drive and
    # strip the drive.
    def strip_drive(p):
        return p[2:] if p[1] == ':' else p
    if system == 'win':
        targets = [(t[0], strip_drive(t[1]), strip_drive(t[2]))
                   for t in targets]

    target_descr = ' '.join(':'.join(target[1:]) for target in targets)
    if system == 'lin':
        ret = os.system('%s/linux/run_fifo_test.sh %s %s %s %s'
                        % (base_path, backend, driver, args.dolphin,
                           target_descr))
    elif system == 'win':
        ret = subprocess.call('powershell %s/windows/run_fifo_test.ps1 %s %s %s %s'
                        % (base_path, backend, driver, args.dolphin,
                           target_descr))
    else:
        raise RuntimeError('unsupported system: %r' % system)

    if ret:
        raise RuntimeError('run_fifo_test.sh returned %d' % ret)


def compute_image_hash(fn):
    """From a given image file, generate a hash of the pixel data of that
    image.
    """
    im = Image.open(fn)
    data = im.convert('RGB').tobytes('raw', 'RGB')
    return hashlib.sha1(data).hexdigest()


def generate_results_data(args, targets):
    """Writes the results to a ZIP file. Metadata is contained in a JSON
    object, and images are stored as individual files.
    """
    parents = find_parents(args.rev_base_hash)
    if args.rev_base_hash != args.rev_hash:
        parents = [args.rev_base_hash] + parents
    meta = {
        'type': args.type,
        'rev': {
            'parents': parents,
            'hash': args.rev_hash,
            'name': args.rev_name,
            'submitted': args.rev_submitted.lower() in ['true', 'yes', '1'],
        },
        'results': {}
    }
    zf = zipfile.ZipFile(args.output, 'w')

    already_existing = get_existing_images(args.url_base)

    for dff_short_name, dff_path, out_path in targets:
        result = {'hashes': []}
        meta['results'][dff_short_name] = result
        if os.path.exists(os.path.join(out_path, 'failure')):
            result['failure'] = True
        else:
            result['failure'] = False
            for i in range(1, 1001):
                fn = os.path.join(out_path, 'frame-%03d.png' % i)
                if not os.path.exists(fn):
                    break
                hash = compute_image_hash(fn)

                # HACK: Currently D3D on Windows inserts a black frame as the
                # first frame of all recordings.
                if i == 1 and hash in ('f971f36357cc45414090cecece55a91ee19aab29',
                                       '44bba96a45cf665df718f81ea48f867e174999da'):
                    continue

                result['hashes'].append(hash)
                if hash not in already_existing:
                    zf.writestr('fifoci-result/%s.png' % hash,
                                open(fn, 'rb').read())

    zf.writestr('fifoci-result/meta.json', json.dumps(meta).encode('utf-8'))
    zf.close()


def remove_output_directories(targets):
    """Deletes the temporary directory created to store image data."""
    for dff_short_name, dff_path, out_path in targets:
        shutil.rmtree(out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run fifoCI tests on a given Dolphin build')
    parser.add_argument('--type', required=True)
    parser.add_argument('--dolphin', required=True)
    parser.add_argument('--rev_base_hash', required=True)
    parser.add_argument('--rev_hash', required=True)
    parser.add_argument('--rev_name', required=True)
    parser.add_argument('--rev_submitted', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--url_base', required=True)
    parser.add_argument('--dff_dir', required=True)
    args = parser.parse_args()

    if not recent_enough():
        print('The requested version is lacking features required for fifoci.')
        print('Exiting early without providing results.')
        sys.exit(1)

    targets = generate_targets_list(args.dff_dir, args.url_base)
    spawn_tests(args, targets)

    generate_results_data(args, targets)
    remove_output_directories(targets)
