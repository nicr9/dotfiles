import otto.utils as otto
import os
import os.path

SETUP_CODE = {
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

SUPPORTED_PLATFORMS = SETUP_CODE.keys()
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

SYMLINKS = [
        ('dotvimrc', '.vimrc'),
        ('dotvim/', '.vim'),
        ('dotinputrc', '.inputrc'),
        ('doti3/', '.inputrc'),
        ]
CP_FILES = [
        ('dotgitconfig', '.gitconfig'),
        ('monofur.otf', '/usr/share/fonts/truetype/'),
        ]

def _run_script(script):
    res = ''
    if script:
        lines = script.splitlines()
        for cmd in lines:
            res += otto.shell(cmd.strip())

    return res

def _packages(platform):
    """Install user packages"""
    if PACKAGES[platform]:
        otto.info("Installing %s packages..." % platform)
        to_install = ' '.join(PACKAGES[platform])
        otto.shell(PACKAGE_INSTALL_CMD[platform] % to_install)

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
        _run_script(SETUP_CODE[None])
        _run_script(SETUP_CODE[platform.result])

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
            otto.info("Creating config symlinks...")
            for link_from, link_to in SYMLINKS:
                relative_from = os.path.join(dotfiles_path, link_from)
                otto.shell("ln -s %s %s" % (relative_from, link_to))

            otto.info("Copying other config files...")
            for cp_from, cp_to in CP_FILES:
                relative_from = os.path.join(dotfiles_path, cp_from)
                otto.shell("cp %s %s" % (relative_from, cp_to))

        # More config
        otto.info("Some last minute config...")
        otto.shell("git submodule init")
        otto.shell("git submodule update")
        otto.shell("sudo fc-cache -f -v")
        otto.shell('git config --global user.name "%s"' % username.result)
        otto.shell('git config --global user.email "%s"' % email.result)
