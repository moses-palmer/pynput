#!/usr/bin/env python

import os
import re
import subprocess
import sys

DESCRIPTION='''Makes a full release.

This script will update the version number of the package and perform all steps
necessary to make a full release.
'''

ROOT = os.path.join(
    os.path.dirname(__file__),
    os.pardir)

LIB_DIR = os.path.join(ROOT, 'lib')

PACKAGE_NAME = next(
    name
    for name in os.listdir(LIB_DIR)
    if name[0] != '_')

PACKAGE_DIR = os.path.join(LIB_DIR, PACKAGE_NAME)


def main(version):
    assert_current_branch_is_clean()
    update_info(version)
    check_readme()
    check_release_notes(version)
    commit_changes(version)
    try:
        tag_release(version)
    except:
        commit_changes.undo()
        raise
    push_to_origin()
    upload_to_pypi()


def assert_current_branch_is_clean():
    """Asserts that the current branch contains no local changes.

    :raises RuntimeError: if the repository contains local changes
    """
    try:
        git('diff-index', '--quiet', 'HEAD', '--')
    except RuntimeError as e:
        print(e.args[0] % e.args[1:])
        raise RuntimeError('Your repository contains local changes')


def update_info(version):
    """Updates the version information in ``._info.``

    :param tuple version: The version to set.
    """
    gsub(
        os.path.join(PACKAGE_DIR, '_info.py'),
        re.compile(r'__version__\s*=\s*(\([0-9]+(\s*,\s*[0-9]+)*\))'),
        1,
        repr(version))


def check_readme():
    """Verifies that the ``README`` is *reStructuredText* compliant.
    """
    python('setup.py', 'check', '--restructuredtext', '--strict')


def check_release_notes(version):
    """Displays the release notes and allows the user to cancel the release
    process.

    :param tuple version: The version that is being released.
    """
    CHANGES = os.path.join(ROOT, 'CHANGES.rst')
    header = 'v%s' % '.'.join(str(v) for v in version)

    # Read the release notes
    found = False
    release_notes = []
    with open(CHANGES) as f:
        for line in (l.strip() for l in f):
            if found:
                if not line:
                    # Break on the first empty line after release notes
                    break
                elif set(line) == {'-'}:
                    # Ignore underline lines
                    continue
                release_notes.append(line)

            elif line.startswith(header):
                # The release notes begin after the header
                found = True

    while True:
        # Display the release notes
        sys.stdout.write('Release notes for %s:\n' % header)
        sys.stdout.write(
            '\n'.join(
                '  %s' % release_note
                for release_note in release_notes) + '\n')
        sys.stdout.write('Is this correct [yes/no]? ')
        sys.stdout.flush()
        response = sys.stdin.readline().strip()
        if response in ('yes', 'y'):
            break
        elif response in ('no', 'n'):
            raise RuntimeError('Release notes are not up to date')


def commit_changes(version):
    """Commits all local changes.

    :param tuple version: The version that is being released.
    """
    git('commit',
        '-a',
        '-m', 'Release %s' % '.'.join(str(v) for v in version))


def _commit_changes_undo():
    git('reset',
        '--hard',
        'HEAD^')
commit_changes.undo = _commit_changes_undo


def tag_release(version):
    """Tags the current commit as a release.

    :param version: The version that is being released.
    :type version: tuple of version parts
    """
    git('tag',
        '-a',
        '-m', 'Release %s' % '.'.join(str(v) for v in version),
        'v' + '.'.join(str(v) for v in version))


def push_to_origin():
    """Pushes master to origin.
    """
    print('Pushing to origin...')

    git('push', 'origin', 'HEAD:master')
    git('push', '--tags')


def upload_to_pypi():
    """Uploads this project to PyPi.
    """
    print('Uploading to PyPi...')

    python(
        os.path.join(ROOT, 'setup.py'),
        'sdist',
        'bdist_egg',
        'bdist_wheel',
        'upload')


def git(*args):
    """Executes ``git`` with the command line arguments given.

    :param args: The arguments to ``git``.

    :return: stdout of ``git``

    :raises RuntimeError: if ``git`` returns non-zero
    """
    return command('git', *args)


def python(*args):
    """Executes *Python* with the command line arguments given.

    The *Python* used is the one executing the current script.

    :param args: The arguments to *Python*.

    :return: stdout of *Python*

    :raises RuntimeError: if *Python* returns non-zero
    """
    return command(sys.executable, *args)


def gsub(path, regex, group, replacement):
    """Runs a regular expression on the contents of a file and replaces a
    group.

    :param str path: The path to the file.

    :param regex: The regular expression to use.

    :param int group: The group of the regular expression to replace.

    :param str replacement: The replacement string.
    """
    with open(path) as f:
        data = f.read()

    def sub(match):
        full = match.group(0)
        o = match.start(0)
        return full[:match.start(group) - o] \
            + replacement \
            + full[match.end(group) - o:]

    with open(path, 'w') as f:
        f.write(regex.sub(sub, data))


def command(*args):
    """Executes a command.

    :param args: The command and arguments.

    :return: stdout of the command

    :raises RuntimeError: if the command returns non-zero
    """
    g = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = g.communicate()
    if g.returncode != 0:
        raise RuntimeError(
            'Failed to execute <%s> (%d): %s',
            ' '.join(args),
            g.returncode, stderr)
    else:
        return stdout.decode('utf-8')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument(
        'version',
        type=lambda s: tuple(int(v) for v in s.split('.')))

    try:
        main(**vars(parser.parse_args()))
    except Exception as e:
        try:
            sys.stderr.write(e.args[0] % e.args[1:] + '\n')
        except:
            sys.stderr.write('%s\n' % str(e))
        sys.exit(1)
