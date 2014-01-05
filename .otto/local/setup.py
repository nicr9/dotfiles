import otto.utils as otto
import os
import os.path

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
            'python',
            'pandoc',
            'i3',
            'feh',
            ],
        'CentOS5': [],
        }
SUPPORTED_PLATFORMS = PACKAGES.keys()

PIP_PACKAGES = [
        #'https://github.com/Lokaltog/powerline/tarball/develop',
        ]

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

        # Get all PPAs setup
        if platform.result == 'Ubuntu':
            otto.info("Adding various non-Ubuntu PPAs the hardway...")
            otto.shell('sudo echo "deb http://repository.spotify.com stable non-free" >> /etc/apt/sources.list')
            otto.shell('wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -')
            otto.shell("""sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'""")
            otto.shell('sudo echo "deb http://debian.sur5r.net/i3/ $(lsb_release -c -s) universe" >> /etc/apt/sources.list')
            otto.shell("sudo apt-get update")
            otto.shell("sudo apt-get --allow-unauthenticated install sur5r-keyring")
            otto.shell("sudo apt-get update")

            if PPAS:
                otto.info("Adding regular PPAs...")
                for ppa in PPAS:
                    otto.shell("sudo add-apt-repository %s" % ppa)
                otto.shell("sudo apt-get update")

        # Install user packages
        if PACKAGES[platform.result]:
            otto.info("Installing packages for %s..." % platform.result)
            to_install = ' '.join(PACKAGES[platform.result])
            otto.shell("sudo apt-get install -y %s" % to_install)

        # Install pip packages
        if PIP_PACKAGES:
            otto.info("Installing packages from pip..." % platform.result)
            to_install = ' '.join(PIP_PACKAGES)
            otto.shell("sudo pip install %s" % to_install)

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
