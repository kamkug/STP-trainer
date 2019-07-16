#!/usr/python/env python

from distutils.core import setup


setup (
        name='STP Trainer',
        version='0.99',
        description='Software to practice STP',
        author='Kamil Kugler',
        author_email='kamilkugler@gmail.com',
        url='https://github.com/kamkug/STP-trainer',
        packages=[
                  '',
                  'classes',
                  'unittests',
                  ],
        package_data={
                        '': ['stp_domains/*.json', 'stp_domains/test/*.json', 'results/*.json' ]
                     },
        scripts=['run.py'],
      
        )
