from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent

setup(
      name='claydates',
      version='1.0.4',
      description='Package used for cleaning, restructuring, logging, and plotting of financial data retrieved from the Twelve Data API.',
      long_description=(this_directory / 'README.md').read_text(),
      long_description_content_type='text/markdown',
      url='https://github.com/ClaytonDuffin/claydates',
      readme='README.md',
      author='Clayton Duffin',
      author_email='clayduffin@gmail.com',
      license_files=('LICENSE'),
      packages=find_packages(exclude=['tests']),
      package_data={'claydates': [str(this_directory) + '/claydates/datasets/currencyPairs.txt',
                                  str(this_directory) + '/claydates/datasets/key.txt',
                                  str(this_directory) + '/claydates/datasets/missingDataLog.csv',
                                  str(this_directory) + '/claydates/datasets/exampleSet.csv']},
      install_requires=[['matplotlib',
                         'numpy',
                         'pandas',
                         'pandas_market_calendars',
                         'python_dateutil',
                         'requests',
                         'twelvedata']
                        ],
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.9',
                   ],
      keywords=['twelvedata API',
                'restructuring',
                'cleaning',
                'plotting',
                'financial data',
                ]
      )
