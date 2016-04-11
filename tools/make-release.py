#!/usr/bin/env python

import os
import re
import subprocess
import sys

PACKAGE_NAME = 'pynput'


def git(*args):
    """Executes ``git`` with the command line arguments given.

    :param args: The arguments to ``git``.

    :return: stdout of ``git``

    :raises RuntimeError: if ``git`` returns non-zero
    """
    g = subprocess.Popen(
        ['git'] + list(args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = g.communicate()
    if g.returncode != 0:
        raise RuntimeError(
            'Failed to call git %s (%d): %s',
            ' '.join(args),
            g.returncode, stderr)
    else:
        return stdout


def get_version():
    """Returns the version to set, read from the command line.

    :return: the tuple (v1, v2,...)
    """
    try:
        return tuple(int(p) for p in sys.argv[1].split('.'))
    except IndexError:
        raise RuntimeError('You must pass the version as the first argument')
    except:
        raise RuntimeError('Invalid version: %s', sys.argv[1])


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


def assert_current_branch_is_master_and_clean():
    """Asserts that the current branch is *master* and contains no local
    changes.

    :raises AssertionError: if the current branch is not master

    :raises RuntimeError: if the repository contains local changes
    """
    assert git('rev-parse', '--abbrev-ref', 'HEAD').strip() == 'master', \
        'The current branch is not master'
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
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'lib', PACKAGE_NAME, '_info.py'),
        re.compile(r'__version__\s*=\s*(\([0-9]+(\s*,\s*[0-9]+)*\))'),
        1,
        repr(version))


def check_readme():
    """Verifies that the ``README`` is *reStructuredText* compliant.
    """
    subprocess.check_call([
        'python', 'setup.py', 'check', '--restructuredtext', '--strict'])


def check_release_notes(version):
    """Displays the release notes and allows the user to cancel the release
    process.

    :param tuple version: The version that is being released.
    """
    CHANGES = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        'CHANGES.rst')
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

    g = subprocess.Popen(
        [
            'python',
            os.path.join(os.path.dirname(__file__), os.pardir, 'setup.py'),
            'build_sphinx',
            'upload_docs',
            'bdist_egg',
            'bdist_wheel',
            'upload'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = g.communicate()
    if g.returncode != 0:
        raise RuntimeError(
            'Failed to upload to PyPi (%d): %s',
            g.returncode, stderr)


def main():
    version = get_version()

    assert_current_branch_is_master_and_clean()
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


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        try:
            sys.stderr.write(e.args[0] % e.args[1:] + '\n')
        except:
            sys.stderr.write('%s\n' % str(e))
        sys.exit(1)
