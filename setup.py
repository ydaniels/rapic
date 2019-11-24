from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='rapic',
      version='0.1.0',
      description='Automatically generate api client libraries/sdk for websites, online services and 3rd party private api.',

      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[

          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='rapic web network internet reverse engineering sdk library api client apiclient',
      url='https://github.com/ydaniels/rapic',
      author='Yomi D',
      author_email='yomid4all@gmail.com',
      license='MIT',
      packages=  find_packages(),
      include_package_data=True,
      install_requires=[
          'requests',
            'xmltodict'
      ],
      scripts=['bin/rapic-client-generator'],
      zip_safe=False)
