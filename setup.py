from setuptools import setup

setup(
    name='avahi-recorder',
    version='0.1.0',
    description='Dynamic Zero Config DNS Server powered by Avahi.',
    long_description=open('README.md').read(),
    classifiers=[
        'Programming Language :: Python',
    ],
    keywords=['avahi', 'dns', 'beer'],
    author='Jonathan Sanchez Pando',
    author_email='me@jsan.me',
    url='https://github.com/j-san/avahi-recorder',
    license='Beer-Ware',
    install_requires=('dnslib', ),
    extras_require={
        'dev': ('flake8',)
    },
    scripts=['avahi-recorder.py'],
)
