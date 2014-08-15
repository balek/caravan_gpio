#!/usr/bin/env python

from setuptools import setup

setup(name='caravan_gpio',
    version='0.0.1',
    description='GPIO module for Caravan',
    author='Alexey Balekhov',
    author_email='a@balek.ru',
    py_modules = ['caravan_gpio'],
    entry_points = {
        'autobahn.twisted.wamplet': [ 'gpio = caravan_gpio:AppSession' ]
    })