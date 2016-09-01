#!/usr/bin/env python
import os

from setuptools import setup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

PACKAGES = [
    'django_sofortueberweisung',
]

REQUIREMENTS = [
    'Django>=1.5',
    'xmltodict>=0.9.2',
]


setup(
    name='django-sofortueberweisung',
    author='Particulate Solutions GmbH',
    author_email='tech@particulate.me',
    description=u'Django integration of Sofort.com',
    version='0.1.1',
    url='https://github.com/ParticulateSolutions/django-sofortueberweisung',
    packages=PACKAGES,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires=REQUIREMENTS,
    zip_safe=False)
