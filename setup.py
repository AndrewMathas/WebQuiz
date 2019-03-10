# -*- encoding: utf-8 -*-

r'''
-----------------------------------------------------------------------------------------
    setup | webquiz setuptools configuration
-----------------------------------------------------------------------------------------
    Copyright (C) Andrew Mathas, University of Sydney

    Distributed under the terms of the GNU General Public License (GPL)
                  http://www.gnu.org/licenses/

    This file is part of the WebQuiz system.

    <Andrew.Mathas@sydney.edu.au>
-----------------------------------------------------------------------------------------
'''

# python setup.py ctan    --> create zip file for upload to ctan
# python setup.py develop --> set up links etc for code development

import glob
import os
import subprocess
import shutil
import sys
import time
import zipfile

from setuptools import setup, find_packages, Command
from webquiz.webquiz_util import kpsewhich, MetaData

if sys.version_info.major<3:
    print('Aborting! Setup requires python3')
    sys.exit(1)

class MetaData(dict):
    r"""
    A dummy class for reading and storing key-value pairs that are read from a file
    """
    def __init__(self, filename):
        with open(filename,'r') as meta:
            for line in meta:
                key, val = line.split('=')
                if len(key.strip())>0:
                    setattr(self, key.strip().lower(), val.strip())

settings = MetaData('latex/webquiz.ini')

class WebQuizDevelop(Command):
    r"""
    Custom develop command to install development version of WebQuiz.
    """

    description = 'Setup links for latex files and web files for code development'
    user_options = []

    def run(self):
        r'''
        Install links for the latex files, executable and web files
        '''
        texmfdist = kpsewhich('-var TEXMFDIST')
        tex_dir = os.path.join(texmfdist,'tex', 'latex', 'webquiz')
        doc_dir = os.path.join(texmfdist,'doc', 'latex', 'webquiz')
        cwd = os.path.dirname(os.path.realpath(__file__))

        try:
            # add a link to the latex files
            tex_dir = self.ask('Install links to latex files in directory', tex_dir)
            if os.path.exists(tex_dir):
                print('Tex files not installed as directory already exists'.format(tex_dir))
            else:
                os.symlink(os.path.join(cwd,'latex'), tex_dir)

                # update the tex search paths if not installed in home directory
                subprocess.call('mktexlsr {}/'.format(tex_dir), shell=True)

            # add a link to the doc files
            doc_dir = self.ask('Install links to doc files in directory', doc_dir)
            if os.path.exists(doc_dir):
                print('doc files not installed as directory already exists'.format(doc_dir))
            else:
                os.symlink(os.path.join(cwd,'doc'), doc_dir)


            # add a link to webquiz.py
            texbin = os.path.dirname(subprocess.check_output('which pdflatex', shell=True).decode().split()[-1])
            bindir = self.ask('Directory for executable', texbin)
            webquiz = os.path.join(bindir, 'webquiz')

            if os.path.exists(webquiz):
                print('Not installing executable as {} already exists'.format(webquiz))
            else:
                os.symlink(os.path.join(cwd,'webquiz','webquiz.py'), webquiz)

            # now add links for web files
            subprocess.call('{} --developer'.format(webquiz), shell=True)

            print('To build the WebQuiz css files run the bash script doc/makedoc -t')
            print('To build the WebQuiz documentation run the bash script doc/makedoc --all')

        except PermissionError as err:
            print('Insufficient permissions. Try running using sudo')
            raise err

        except OSError as err:
            print('There was a problem copying files or adding links')
            raise err

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

# "Magic" bitmasks for adding symlinks to zip files
SYMLINK_TYPE  = 0xA
SYMLINK_PERM  = 0o755
SYMLINK_ISDIR = 0x10
SYMLINK_MAGIC = (SYMLINK_TYPE << 28) | (SYMLINK_PERM << 16)

assert SYMLINK_MAGIC == 0xA1ED0000, 'Bit math is askew'

class WebQuizCtan(Command):
    r"""
    Create zip file for submission to ctan/texlive.
    """

    description = 'Build and publish the package.'
    user_options = []

    ctan_data = {
        'contribution' : settings.program,
             'version' : settings.version,
                'name' : settings.authors,
               'email' : settings.author_email,
             'summary' : settings.description,
           'directory' : '/macros/latex/contrib/webquiz',
            'announce' : settings.description,
               'notes' : 'See README file in webquiz',
             'license' : 'free',
         'freeversion' : 'gpl',
    }

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def ask(self, message, default):
        r'''
        Prompt the user for input using the message `message` and with default
        `default` and return the result.
        '''
        value = input('\n{}{}[{}] '.format(message, '\n' if len(message+default)>50 else ' ',
                                           default)
        ).strip()
        return default if value=='' else value

    def run(self):
        # write the zip file for uploading to ctan
        self.zipfile = 'webquiz-{}.zip'.format(settings.version)
        self.ctan_data['file'] = self.zipfile
        self.write_zip_file()

        # upload the zip file to ctan using ctanupload
        subprocess.call('ctanupload -v {options}'.format(
                options = ' '.join('--{}="{}"'.format(key, val) for key,val in self.ctan_data.items())
            ),
            shell=True
        )

    def shell_command(self, cmd, quiet=False):
        r'''
        Run the system command `cmd` and print any output to stdout indented
        by two spaces.
        '''
        if not quiet:
            print('Executing {}'.format(cmd))
        subprocess.call(cmd, shell=True)

    def update_copyright(self):
        r'''
        Make sure that the end dates on the copyright notices are correct as
        given by the copyright line in webquiz.ini
        '''
        copy = 'Copyright (C) '+settings.copyright[:9]
        print('Updating the copyright dates')
        for file in [ 'latex/webquiz-doc.code.tex',
                      'latex/webquiz.ini',
                      'doc/credits.tex',
                      'doc/webquiz-online-manual.tex',
                      'doc/webquiz.tex',
                      'doc/README-bottom',
                      'README.rst'
                    ]:
            self.shell_command(
                "sed -i.bak 's@Copyright (C) 2004-20[0-9][0-9]@{}@' {}".format(copy, file),
                quiet=True,
            )

    def build_distribution(self):
        r'''
        Rebuilds the documentation files and css for inclusion in the zip file:
            - doc/webquiz-manual.tex
            - doc/webquiz.tex
            - css/webquiz-*.css
        to ensure that they are correct for the ctan upload. We need to make
        webquiz-manual.pdf first because it is included in webquiz.pdf.
        '''
        # update the copyright notices in list of known files
        self.update_copyright()

        # auto generate all of the data used in the manual and build the manuals
        makedoc = input('Run makedoc [N/yes]? ')
        if makedoc.lower() == 'yes':
            self.shell_command('doc/makedoc --all --fast')

        try:
            os.remove('javasript/webquiz-min.js')

        except FileNotFoundError:
            pass

        except OSError as err:
            print('Something went wrong: {}'.format(err))
            pass

        # minify the javascript code
        print('Minifying webquiz.js')
        self.shell_command('uglifyjs --output javascript/webquiz-min.js --compress sequences=true,conditionals=true,booleans=true  javascript/webquiz.js ', quiet=True)

    def write_zip_file(self):
        r'''
        Create a zip file for webquiz that can be uploaded to ctan. To do
        this we use the zipfile module to write the zopfile with all files in
        their expected places.
        '''
        # if the zip file for ctan already exists then delete it
        try:
            os.remove(self.zipfile)
            os.remove('doc/README')
            shutil.rmtree('doc/www', ignore_errors=True)

        except OSError:
            pass

        self.build_distribution()

        # save the files as a TDS (Tex directory standard) zip file
        with zipfile.ZipFile(self.zipfile, 'w', zipfile.ZIP_DEFLATED) as zip_file:

            # now add the files: the target is assume to be a directory
            # unless it contains a '.', in which case we change the filename
            for (src, target) in [
                ('doc/README.rst',                './README.rst'),
                ('latex/webquiz.c*',              'latex'),
                ('latex/webquiz-*.code.tex',      'latex'),
                ('latex/webquiz.ini',             'latex'),
                ('latex/webquiz-*.lang',          'latex'),
                ('latex/pgfsys-dvisvgm4ht.def',   'latex'),
                ('CHANGES.rst',                   'scripts'),
                ('LICENCE',                       'scripts'),
                ('webquiz/README-scripts',        'scripts'),
                ('webquiz/webquiz*.py',           'scripts'),
                ('webquiz/webquiz.bat',           'scripts'),
                ('doc/README-doc',                'doc'),
                ('doc/webquiz.tex',               'doc'),
                ('doc/webquiz.pdf',               'doc'),
                ('doc/webquiz.1',                 'doc'),
                ('doc/webquiz-online-manual.pdf', 'doc'),
                ('doc/webquiz-online-manual.tex', 'doc'),
                ('doc/webquiz.languages',         'doc'),
                ('doc/webquiz.settings',          'doc'),
                ('doc/webquiz.themes',            'doc'),
                ('doc/webquiz.usage',             'doc'),
                ('javascript/webquiz-min.js',     'doc/www/js/webquiz.js'),
                ('css/webquiz-*.css',             'doc/www/css'),
                ('doc/examples/README-examples',  'doc/examples'),
                ('doc/examples/*.tex',            'doc/examples'),
                ('doc/examples/ctanLion.jpg',     'doc/examples'),
                ('doc/examples/*.png',            'doc/examples'),
            ]:
                for file in glob.glob(src):
                    if '.' in target:
                        # take filename from target
                        zip_file.write(file, os.path.join('webquiz', target))
                    else:
                        # copy file to the directory specified by target
                        zip_file.write(file, os.path.join('webquiz', target, file.split('/')[-1]))

            # this very much a hack...is there a more elegant way to construct
            # these links in the zip file?
            if os.path.isdir('symlinks'):
                shutil.rmtree('symlinks')
            os.mkdir('symlinks')
            os.chdir('symlinks')
            try:
                for (src, target, link) in [
                        ('doc/README.rst', 'README', 'README.rst'),
                        ('webquiz/webquiz.py', 'scripts/webquiz', 'webquiz.py'),
                        ('doc/examples', 'doc/www/doc/examples', '../../examples'),
                        ('doc/webquiz-online-manual.tex', 'doc/www/doc/webquiz-online-manual.tex', '../../webquiz-online-manual.tex')
                    ]:
                    if '/' in target:
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                    target_file = os.path.abspath(os.path.join(
                                    os.path.dirname(target),
                                    os.path.dirname(link),
                                    os.path.basename(link)
                                )
                    )
                    if '/' in target_file:
                        os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    if os.path.isdir(os.path.join('..',src)):
                        os.makedirs(os.path.join('..',src), exist_ok=True)
                    else:
                        shutil.copyfile(os.path.join('..',src), target_file)
                    os.symlink(link, target)
                    self.add_sym_link_to_zipfile(target, os.path.join('webquiz',target), zip_file)
            except:
                raise
            os.chdir('..')
            shutil.rmtree('symlinks')

    def add_sym_link_to_zipfile(self, link, zippath, zip_file):
        r'''
            Code from
                https://learning-python.com/cgi/showcode.py?name=ziptools/ziptools/ziptools/zipsymlinks.py
            to add a sym-link `link` to the file `file` in the zip file `zipfile`.

            'filepath' is the (possibly-prefixed and absolute) path to the link file.
            'zippath'  is the (relative or absolute) path to record in the zip itself.
            'zipfile'  is the ZipFile object used to format the created zip file.
        '''
        assert os.path.islink(link)
        linkpath = os.readlink(link)                # str of link itself

        # 0 is windows, 3 is unix (e.g., mac, linux) [and 1 is Amiga!]
        createsystem = 0 if sys.platform.startswith('win') else 3

        # else time defaults in zip_file to Jan 1, 1980
        linkstat = os.lstat(link)                   # stat of link itself
        origtime = linkstat.st_mtime                # mtime of link itself
        ziptime  = time.localtime(origtime)[0:6]    # first 6 tuple items

        # zip mandates '/' separators in the zip_file
        if not zippath:                             # pass None to equate
            zippath = link
        zippath = os.path.splitdrive(zippath)[1]    # drop Windows drive, unc
        zippath = os.path.normpath(zippath)         # drop '.', double slash...
        zippath = zippath.lstrip(os.sep)            # drop leading slash(es)
        zippath = zippath.replace(os.sep, '/')      # no-op if unix or simple

        newinfo = zipfile.ZipInfo()                 # new zip entry's info
        newinfo.filename      = zippath
        newinfo.date_time     = ziptime
        newinfo.create_system = createsystem        # woefully undocumented
        newinfo.compress_type = zip_file.compression# use the file's default
        newinfo.external_attr = SYMLINK_MAGIC       # type plus permissions

        if os.path.isdir(link):                     # symlink to dir?
            newinfo.external_attr |= SYMLINK_ISDIR  # DOS directory-link flag

        zip_file.writestr(newinfo, linkpath)         # add to the new zip_file



#----------------------------------------------------------------------------------------
setup(name             = settings.program,
      version          = settings.version,
      description      = settings.description,
      long_description = open('README.rst').read(),
      long_description_content_type='text/rst',
      url              = settings.url,
      author           = settings.authors,
      author_email     = settings.author_email,

      keywords         = 'web quizzes, latex, mathematics',

      packages=find_packages(),
      include_package_data=True,
      package_data     = {'webfiles' : '/'},

      cmdclass         = {'ctan': WebQuizCtan, 'develop': WebQuizDevelop},

      provides         = 'webquiz',
      entry_points     = { 'console_scripts': [ 'webquiz=webquiz.webquiz:main' ], },

      license          = settings.licence,

      classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Education :: Testing',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Markup :: XML',
      ]
)
