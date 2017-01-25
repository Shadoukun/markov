try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A markov chain bot.',
    'author': 'shadoukun',
    'url': 'https://github.com/shadoukun/markov',
    'author_email': 'shadoukun@gmail.com',
    'version': '0.2',
    'install_requires': ['markovify', 'twisted', 'walrus'],
    'packages': ['markov'],
    'scripts': [],
    'name': 'markov'
}

setup(**config)
