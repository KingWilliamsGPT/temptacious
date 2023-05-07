
from distutils.core import setup
setup(
  name = 'temptacious',
  packages = ['temptacious'],
  version = '1.0',
  license='MIT',
  description = 'Lightweight template engine',
  author = 'Williams Samuel',
  author_email = 'williamusanga22@gmail.com',
  url = 'https://github.com/KingWilliamsGPT/temptacious',
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['template engine', 'template', 'engine', 'python', 'django', 'jinja'],
  install_requires=[            # I get to this in a second
          'validators',
          'beautifulsoup4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which python versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)