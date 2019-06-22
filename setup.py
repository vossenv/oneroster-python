from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps = ['mock', 'pytest', 'pytest-cov']

setup(name='classlink-oneroster',
      version='0.0.1rc3',
      description='Simple API integration with Classlink\'s Oneroster implementation',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
      ],
      url='https://github.com/vossen-adobe/classlink',
      maintainer='Danimae Vossen',
      maintainer_email='vossen.dm@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'six',
          'requests'
      ],
      tests_require=[
          'mock',
          'pytest'
      ],
)

# twine upload --repository testpypi dist/*.tar.gz dist/*.whl
# twine upload dist/*.tar.gz dist/*.whl

# Github: https://github.com/vossen-adobe/classlink
# PyPI: https://pypi.org/project/classlink-oneroster/
