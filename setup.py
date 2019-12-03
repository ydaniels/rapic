import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

def readme():
    with open('README.md') as f:
        return f.read()

about = {}
with open(os.path.join(here, 'rapic', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(name=about['__title__'],
      version=about['__version__'],
      description=about['__description__'],

      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[

          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='rapic web network internet reverse engineering sdk library api client apiclient',
      url=about['__url__'],
      author=about['__author__'],
      author_email=about['__author_email__'],
      license=about['__license__'],
      packages=  find_packages(),
      include_package_data=True,
      install_requires=[
          'requests',
            'xmltodict'
      ],
      scripts=['bin/rapic-client-generator'],
      zip_safe=False)
