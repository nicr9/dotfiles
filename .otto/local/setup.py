import otto.utils as otto
import os
import os.path

PRE = {
        None: '',
        'Ubuntu': """sudo echo "deb http://repository.spotify.com stable non-free" >> /etc/apt/sources.list
                     wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
                     sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
                     sudo echo "deb http://debian.sur5r.net/i3/ $(lsb_release -c -s) universe" >> /etc/apt/sources.list
                     sudo apt-get update
                     sudo apt-get --allow-unauthenticated install sur5r-keyring
                     sudo apt-get update""",
        'CentOS': '',
        }

SUPPORTED_PLATFORMS = PRE.keys()
SUPPORTED_PLATFORMS.remove(None)

PPAS = [
        'ppa:ubuntu-x-swat/x-updates',
        ]

PACKAGES = {
        'Ubuntu': [
            'git',
            'vim',
            'screen',
            'exuberant-ctags',
            'terminator',
            'pandoc',
            'i3',
            'feh',
            ],
        'CentOS': [],
        'python': [
            #'https://github.com/Lokaltog/powerline/tarball/develop',
            ],
        }

PACKAGE_INSTALL_CMD = {
        'Ubuntu': "sudo apt-get install -y %s",
        'CentOS': "sudo yum install -y %s",
        'python': "sudo pip install %s",
        }

SYMLINKS = {
        None: [
            ('dotvimrc', '.vimrc'),
            ('dotvim/', '.vim'),
            ('dotinputrc', '.inputrc'),
            ],
        'Ubuntu': [
            ('doti3/', '.inputrc'),
            ],
        'CentOS': [],
        }

CP_FILES = {
        None: [
            ('dotgitconfig', '.gitconfig'),
            ],
        'Ubuntu': [
            ('monofur.otf', '/usr/share/fonts/truetype/'),
            ],
        'CentOS': [],
        }

CRONS = {
        None: [],
        'Ubuntu': [
            "* * * * * find ~/.wallpaper -type f \( -name '*.jpg' -o -name '*.png' \) -print0 | shuf -n1 -z | xargs -0 feh --bg-scale",
            ],
        'CentOS': [],
        }

POST = {
        None: """git submodule init
                 git submodule update
                 git config --global user.name "%(username)s"
                 git config --global user.email "%(email)s" """,
        'Ubuntu': "sudo fc-cache -f -v",
        'CentOS': "",
    }

def _run_script(script, details={}):
    res = ''
    if script:
        lines = script.splitlines()
        for cmd in lines:
            res += otto.shell(cmd.strip() % details)

    return res

def _packages(platform):
    """Install user packages"""
    if PACKAGES[platform]:
        otto.info("Installing %s packages..." % platform)
        to_install = ' '.join(PACKAGES[platform])
        otto.shell(PACKAGE_INSTALL_CMD[platform] % to_install)

def _run_crons(platform):
    if CRONS[platform]:
        otto.info("Adding %s crons..." % platform if platform else 'default')
    for cron in CRONS[platform]:
        otto.shell("""(crontab -l; echo "%s" ) | crontab -""" % cron)

def _install_symlinks(dotfiles_path, platform):
    if SYMLINKS[platform]:
        otto.info("Creating %s symlinks..." % (platform if platform else 'default'))
    for link_from, link_to in SYMLINKS[platform]:
        relative_from = os.path.join(dotfiles_path, link_from)
        otto.shell("ln -s %s %s" % (relative_from, link_to))

def _cp_files(dotfiles_path, platform):
    if CP_FILES[platform]:
        otto.info("Copying %s files..." % (platform if platform else 'misc'))
    for cp_from, cp_to in CP_FILES[platform]:
        relative_from = os.path.join(dotfiles_path, cp_from)
        otto.shell("cp %s %s" % (relative_from, cp_to))

class Setup(otto.OttoCmd):
    def run(self, gui=True):
        otto.debug_on()

        # Ask for user details first
        platform = otto.Dialog("Which platform is this?")
        platform.choose(SUPPORTED_PLATFORMS)

        username = otto.Dialog("What's your name?")
        username.input('Nic Roland')

        email = otto.Dialog("What's your email?")
        email.input('nicroland9@gmail.com')

        # Figure out some important details
        dotfiles_path = os.path.relpath(os.getcwd(), os.path.expanduser('~'))

        print

        # General setup
        _run_script(PRE[None])
        _run_script(PRE[platform.result])

        # Get all PPAs setup
        if platform.result == 'Ubuntu' and PPAS:
            otto.info("Adding regular PPAs...")
            for ppa in PPAS:
                otto.shell("sudo add-apt-repository %s" % ppa)
            otto.shell("sudo apt-get update")

        _packages(platform.result)
        _packages('python')

        # Configure everything
        with otto.ChangePath():
            _install_symlinks(dotfiles_path, None)
            _install_symlinks(dotfiles_path, platform.result)

            _cp_files(dotfiles_path, None)
            _cp_files(dotfiles_path, platform.result)

        # Setup crons
        _run_crons(None)
        _run_crons(platform.result)

        # More config
        details = {
                'username': username.result,
                'email': email.result,
                }
        otto.info("Some last minute config...")
        _run_script(POST[None], details)
        _run_script(POST[platform.result])
