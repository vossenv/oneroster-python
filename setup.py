from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps = ['mock', 'pytest', 'pytest-cov']

setup(name='oneroster',
      version='0.0.15',
      description='Simple Oneroster client for user management',
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
      url='https://github.com/vossenv/oneroster-python',
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
          'pytest',
          'pyyaml',
          'vcrpy',
          'pytest-vcr'
      ],
)

# twine upload --repository testpypi dist/*.tar.gz dist/*.whl
# twine upload dist/*.tar.gz dist/*.whl

# Github: https://github.com/vossenv/oneroster-python
# PyPI: https://pypi.org/project/oneroster
