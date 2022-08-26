
from __future__ import absolute_import, division, print_function

from setuptools import setup

__version__ = '0.1.0'


URL = 'https://commonfate.io'

setup_requires = [
]

install_requires = [
    'Flask>=0.12.2',
    'click>=6.7',
]

docs_require = []

extras_require = {
    'docs': docs_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    extras_require['all'].extend(reqs)

setup(
    version = __version__,
    name='granted_flask',
    autosemver={
        'bugtracker_url': URL + '/issues',
    },
    url=URL,
    license='MIT',
    author='Common Fate',
    author_email='hello@commonfate.io',
    py_modules=['flask_shell_bpython'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    description=__doc__,
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require=extras_require,
    packages=['flask_shell_granted']
    entry_points={
        'flask.commands': [
            'shell=flask_shell_granted:shell_command',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python',
    ],
)