from setuptools import setup

setup(name='fileup',
      version=0.1,
      description='Easily upload files to an FTP-server and get back the url.',
      url='https://github.com/basnijholt/fileup',
      author='Bas Nijholt',
      license='BSD 3-clause',
      py_modules=["fileup"],
      entry_points={'console_scripts': ['fu=fileup:main']}
      )