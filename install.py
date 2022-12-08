#!/usr/bin/env python3
'''This module is for installing the themes.'''

import os
import sys
import argparse
import subprocess
import shutil
import time
import threading
from re import sub
from urllib.request import urlopen

from paths import HOME, REPO_DIR, CONFIG_FILE, OLD_CONFIG, SRC, FIREFOX_DIR, installed_paths

NC = '\033[0m'
BOLD = '\033[1m'
BRED = '\033[1;31m'
BGREEN = '\033[1;32m'
BYELLOW = '\033[1;33m'
BLRED = '\033[1;91m'
BLYELLOW = '\033[1;93m'
BLBLUE = '\033[1;94m'
BLCYAN = '\033[1;96m'

VARIANTS = { # all of the possible configurations, name: pretty-name
    'color': {
        'orange': 'Orange',
        'bark': 'Bark',
        'sage': 'Sage',
        'olive': 'Olive',
        'viridian': 'Viridian',
        'prussiangreen': 'Prussian Green',
        'lightblue': 'Light Blue',
        'blue': 'Blue',
        'purple': 'Purple',
        'magenta': 'Magenta',
        'pink': 'Pink',
        'red': 'Red'
    },
    'theme': {
        'light': 'Light',
        'dark': 'Dark',
        'auto': 'Auto'
    },
    'enableable': {
        'dg-adw-gtk3': {
            'gtk3': 'GTK3',
            'gtk4-libadwaita': 'Libadwaita'
        },
        'dg-libadwaita': {
            'gtk4': 'GTK4'
        },
        'dg-yaru': {
            'gnome-shell': 'GNOME Shell',
            'cinnamon-shell': 'Cinnamon Shell',
            'metacity': 'Marco (Metacity)',
            'ubuntu-unity': 'Unity',
            'xfwm4': 'Xfwm4',
            'icons': 'Icon',
            'cursors': 'Cursor',
            'sounds': 'Sound',
            'gtksourceview': 'GtkSourceView'
        },
        'dg-firefox-theme': {
            'firefox-standard': 'Standard Firefox',
            'firefox-snap': 'Snap Firefox',
            'firefox-flatpak': 'Flatpak Firefox',
        },
        'dg-vscode-adwaita': {
            'vscode': 'VS Code',
            'default_syntax': 'default syntax highlighting'
        },
        'qualia-gtk-theme-snap': {
            'snap': 'Snap'
        }
    }
}

# Supported DE versions
VERSIONS = {
    'gnome': (42, 43),
    'cinnamon': (4, 5),
    'unity': (7,),
    'xfce': (4,),
    'mate': (1,),
    'budgie': (10.6,)
}

update_color = update_theme = update_syntax = reconfigure = verbose = force = configured = updated =False

#################
##  Functions  ##
#################

def cd(dir):
    '''
    Change directory.

    Parameters:
        dir (str) : The path of the directory to change to.
    '''
    if verbose:
        print(f"Changing directory to {dir}")
    os.chdir(dir)

def run_command(command, meson = False, override_verbose = None, show_ouput = False):
    '''
    Run an external command and handle errors.

    Parameters:
        command (list) : A list containing the command and each argument.
        meson (bool) : If the option to clean build dir should be printed.
        override_verbose (bool) : Override the global verbose value.
        show_ouput (bool) : Show output of command.
    '''
    if override_verbose is None:
        global verbose
    else:
        verbose = override_verbose
    if verbose:
        print('Running ' + ' '.join(command))
    try:
        subprocess.run(command, capture_output=False if verbose or show_ouput else True, check=True)
    except subprocess.CalledProcessError as error:
        if not (verbose or show_ouput):
            print('\n' + error.output.decode("utf-8"))
            print(f"{BRED}Something went wrong, run {BLRED}'{sys.argv[0]} --verbose'{BRED} for more info.{NC}")
        else:
            print(f'{BRED}Something went wrong. Check the log above.{NC}')
        if meson:
            print(f"{BRED}Also, running {BLRED}'{sys.argv[0]} --clean'{BRED} might fix the issue.{NC}")
        raise error

def check_output(command):
    '''
    Check output of command.

    Parameters:
        command (list) : A list of the command and arguments to run.

    Returns:
        output (str) : The ouput of the command
    '''
    output = subprocess.run(command, stdout=subprocess.PIPE, check=True).stdout.decode('utf-8').strip('\'\n')
    return output

def main():
    '''The main function.'''
    ##############################
    ##   Command Line Options   ##
    ##############################

    parser = argparse.ArgumentParser(
        description='This script is used to install, update, and reconfigure the theme'
    )

    parser.add_argument(
        '-c', '--clean',
        action = 'store_true',
        help = 'clean build directories and exit'
    )
    parser.add_argument(
        '-r', '--reconfigure',
        action='store_true',
        help='reconfigure the theme'
    )
    parser.add_argument(
        '-t', '--theme',
        action = 'store_true',
        help = 'change theme variant'
    )
    parser.add_argument(
        '-s', '--syntax',
        action = 'store_true',
        help = 'change VS Code syntax highlighting'
    )
    parser.add_argument(
        '-a', '--accent',
        action = 'store_true',
        help = 'change accent color'
    )
    parser.add_argument(
        '-f', '--force',
        action = 'store_true',
        help = 'force install the theme'
    )
    parser.add_argument(
        '-v', '--verbose',
        action = 'store_true',
        help = 'verbose mode'
    )

    args = parser.parse_args()

    global update_color
    update_color = args.accent

    global update_theme
    update_theme = args.theme

    global update_syntax
    update_syntax = args.syntax

    global reconfigure
    reconfigure = args.reconfigure

    global verbose
    verbose = args.verbose

    global force
    force = args.force

    global configure_all
    configure_all = False

    if args.clean:
        if os.getuid() != 0:
            args = ['sudo', sys.executable] + sys.argv + [os.environ]
            os.execlpe('sudo', *args)

        for i in [SRC['yaru'], SRC['gtk3']]:
            try:
                shutil.rmtree(f'{i}/build')
            except NotADirectoryError:
                os.remove(f'{i}/build')
            except FileNotFoundError:
                pass
        sys.exit()

    if not args.clean and os.getuid() == 0:
        print(f"{BRED}Don't run this script as root, exiting.")
        sys.exit()

    #####################
    ##  Configuration  ##
    #####################

    if shutil.which('sassc') is None:
        print(f"{BLRED}'sassc'{BRED} not found, exiting.{NC}")
        sys.exit()

    if shutil.which('git') is None:
        print(f"{BLRED}'git'{BRED} not found, exiting.{NC}")
        sys.exit()

    conf = Config()

    # Move old config file
    if os.path.isfile(OLD_CONFIG) and not os.path.isfile(CONFIG_FILE):
        shutil.move(OLD_CONFIG, CONFIG_FILE)

    # Whether or not to configure
    if not os.path.isfile(CONFIG_FILE) or reconfigure:
        configure_all = True
        conf.configure()
        if os.path.isfile(CONFIG_FILE):
            os.remove(CONFIG_FILE)

    conf.read()

    config = conf.ret_config()

    # Reconfigure if config file has issues
    try:
        color_scheme = conf.theme_variants(config['theme'])
        if not (isinstance(config['color'], str) or isinstance(config['theme'], str) or isinstance(config['enabled'], list)) or color_scheme is None:
            configure_all = True
            conf.configure()
    except KeyError:
        configure_all = True
        conf.configure()

    # Reconfigure color, theme variant, or syntax highlighting if user wants to
    if update_color or update_theme or update_syntax:
        conf.configure()

    if configured:
        config = conf.ret_config()

    conf.write(config)

    ######################
    ##  Install Themes  ##
    ######################

    if not configured:
        print(f'{BYELLOW}Updating themes using previous configuration.{NC}')
        print(f"{BYELLOW}Use {BLYELLOW}'{sys.argv[0]} --reconfigure'{BYELLOW} if you want to change anything.{NC}")

    theme_names = {}
    for i in ['dg-yaru', 'dg-adw-gtk3', 'dg-firefox-theme']:
        theme_names[i]=['qualia'] # For detecting the old version of the theme

    paths = installed_paths(theme_names)

    config['suffix']='-dark' if config['color_scheme'] == 'prefer-dark' else ''
    config['variant']='dark' if config['color_scheme'] == 'prefer-dark' else 'light'

    def check_path(name, paths, should_print = True):
        '''
        Check if the path to a theme exists, used for when a theme was previously installed but is disabled.

        Parameters:
            name (str) : The name of the part of the theme to check.
            paths (dict) : The dict containing all of the paths.
            should_print (bool) : If we should print that the path exists

        Returns:
            exists (bool) : If ret is true, whether or not the path exists
        '''
        exists = False

        for i in paths[name]:
            if isinstance(i, list):
                for path in i:
                    if name == 'icons' and path in paths['cursors']:
                        pass
                    else:
                        exists = os.path.exists(path)
            else:
                if name == 'icons' and i in paths['cursors']:
                    pass
                else:
                    exists = os.path.exists(i)
        if should_print and exists:
            for theme in VARIANTS['enableable']:
                if name in VARIANTS['enableable'][theme]:
                    pretty = VARIANTS['enableable'][theme][name]
                    if name == 'gtk4-libadwaita':
                        message += f'{pretty} GTK4 theme{NC}.'
                    elif name == 'gtk4':
                        message += f'{pretty} configuration{NC}.'
                    else:
                        message += f'{pretty} theme{NC}.'
                    print(f"The {message} was installed previously, use './uninstall.py {name}' to remove it.")
        
        return exists

    # Install dg-adw-gtk3
    if 'gtk3' in config['enabled'] or 'gtk4-libadwaita' in config['enabled']:
        gtk3 = InstallDgAdwGtk3(config)
        config['dg-adw-gtk3_version'] = gtk3.get_version()
        conf.write(config)
    else:
        check_path('gtk3', paths)
        check_path('gtk4', paths)

    # Symlink to /usr dir if using mate
    targets = []
    if config['desktop_versions']['mate'] is not None:
        for path in paths['themes']:
            if isinstance(path, list):
                for i in path:
                    targets.append(i)
            else:
                targets.append(path)
        for target in targets:
            if target.startswith(f'{HOME}/.local'):
                dest = '/usr' + target.split(f'{HOME}/.local')[1]
                run_command(['sudo', 'mkdir', '-p', dest])
                for i in ['gtk-3.0', 'gtk-4.0', 'index.theme']:
                    if not os.path.exists(f'{dest}/{i}'):
                        run_command(['sudo', 'ln', '-sf', f'{target}/{i}', f'{dest}/{i}'])

    # Install dg-yaru
    yaru_parts_pretty = []
    yaru_parts = []
    yaru_disabled = []

    for i in VARIANTS['enableable']['dg-yaru']:
        pretty_name = VARIANTS['enableable']['dg-yaru'][i]
        if i in config['enabled']:
            yaru_parts_pretty.append(pretty_name)
            yaru_parts.append(i)
        else:
            yaru_disabled.append(i)

    if len(yaru_parts) > 0:
        yaru = InstallDgYaru(config, yaru_parts, yaru_parts_pretty)
        config['dg-yaru_version'] = yaru.get_version()
        conf.write(config)
    for i in yaru_disabled:
        check_path(i, paths)

    # Install dg-libadwaita
    if 'gtk4' in config['enabled']:
        gtk4 = InstallDgLibadwaita(config)
        config['dg-libadwaita_version'] = gtk4.get_version()
        conf.write(config)
    else:
        check_path('gtk4', paths)

    # Install dg-firefox-theme
    for key, value in FIREFOX_DIR.items():
        if f'firefox-{key}' in config['enabled']:
            firefox = InstallDgFirefoxTheme(config, value)
            config['dg-firefox-theme_version'] = firefox.get_version()
            conf.write(config)
        else:
            check_path(f'firefox-{key}', paths)

    # Install dg-vscode-adwiata
    if 'vscode' in config['enabled']:
        vscode = InstallDgVscodeAdwaita(config)
        config['dg-vscode-adwaita_version'] = vscode.get_version()
        conf.write(config)
    else:
        check_path('vscode', paths)

    # Install snap theme
    if 'snap' in config['enabled']:
        try:
            # Check that there is an internet connection
            urlopen('https://www.google.com/', timeout=3)
            InstallQualiaGtkThemeSnap(config)
        except OSError:
            pass
    elif shutil.which('snap'):
        snap_list = check_output(['snap', 'list'])
        for line in snap_list:
            line = line.split()
            if 'qualia-gtk-theme' in line:
                print("Snap theme was installed previously, use './uninstall.py snap' to remove it.")

    #####################
    ##  Enable Themes  ##
    #####################

    theme_name = f"qualia{config['suffix']}" if config['color'] == 'orange' else f"qualia-{config['color']}{config['suffix']}"
    icon_name = 'qualia-dark' if config['color'] == 'orange' else f"qualia-{config['color']}-dark"
    cursor_name = 'qualia'
    xfwm4_name = f"qualia{config['suffix']}"

    cd(REPO_DIR)

    kwargs = {
        'gtk3': theme_name,
        'icons': icon_name,
        'cursors': cursor_name,
        'sounds': cursor_name,
        'gnome-shell': theme_name,
        'cinnamon-shell': theme_name,
        'metacity': xfwm4_name,
        'xfwm4': xfwm4_name
    }

    enable = Enable(config, verbose, **kwargs)

    config = enable.enable_theme()

    # Update config file one last time
    conf.write(config)

    # Set color scheme
    if config['color_scheme'] is not None and shutil.which('gsettings') is not None:
        run_command(['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', config['color_scheme']])

    ########################
    #   Remove old theme   #
    ########################

    old_paths = installed_paths(OLD_NAMES, True)

    for i in old_paths:
        old_exists = check_path(i, old_paths, False)
        if old_exists:
            print("Removing old theme.")
            run_command(['sudo', './uninstall.py', '--old'])
            break

    if updated:
        print(f"{BYELLOW}Log out and log back in for everything to be updated.{NC}")

class Config:
    '''Handles configuration of theme.'''
    def __init__(self):
        self.config = {}
        self.config['desktop_versions'] = self.get_desktops()
        self.config['enableable'] = self.get_enableable(self.config['desktop_versions'])

    def ret_config(self):
        '''
        Returns the config dictionary.

        Returns:
            config (dict) : dictionary that stores the configuration.
        '''
        return self.config

    def get_desktops(self):
        '''
        Find out what desktops are installed.

        Returns:
            desktop_versions (dict) : dictionary that stores the versions of the installed desktops.
        '''
        desktop_versions = {}

        desktop_versions['gnome'] = self.check_de_version(['gnome-shell', '--version'], r'\.[0-9]?\n?$|\D', 'gnome')
        desktop_versions['cinnamon'] = self.check_de_version(['cinnamon', '--version'], r'\.[0-9]\.?[0-9]?[0-9]?\n?$|^Cinnamon ', 'cinnamon')
        desktop_versions['unity'] = self.check_de_version(['unity', '--version'], r'\.[0-9]\.[0-9]?\n?$|\D', 'unity')
        desktop_versions['mate'] = self.check_de_version(['mate-session', '--version'], r'\.[0-9][0-9]?\.[0-9][0-9]?\n?$|^mate-session ', 'mate')
        desktop_versions['budgie'] = self.check_de_version(['budgie-desktop', '--version'], r'Copyright.*\n|\.[0-9]\n|^budgie-desktop', 'budgie')

        if shutil.which('xfce4-session') is not None:
            desktop_versions['xfce'] = VERSIONS['xfce'][0]
        else:
            desktop_versions['xfce'] = None

        return desktop_versions

    def check_de_version(self, command, regex, name):
        '''
        Get the current version number of an installed desktop.

        Parameters:
            command (list) : list that contains command and arguments to run.
            regex (str) : regex of what to ignore in output.
            name (str) : name of part of theme.

        Returns:
            enableable (int or float) : version of desktop.
        '''
        try:
            ver = subprocess.run(command, stdout=subprocess.PIPE, check=True).stdout.decode('utf-8')
            ver = sub(regex, '', ver)

            if float(ver) in VERSIONS[name]:
                version = float(ver)
            elif int(ver) in VERSIONS[name]:
                version = int(ver)
            else:
                version = None
        except(FileNotFoundError, ValueError):
            version = None

        return version

    def get_enableable(self, desktop_versions):
        '''
        Find out what themes can be enabled.

        Parameters:
            desktop_versions (dict): dictionary containing the desktop versions

        Returns:
            enableable (dict) : {name: pretty_name}, themes that can be enabled
        '''
        enableable = {}

        for parts in VARIANTS["enableable"].values():
            for part, pretty_name in parts.items():
                enableable[part] = pretty_name

        for i in desktop_versions:
            if desktop_versions[i] is None:
                if i == 'gnome':
                    del enableable['gnome-shell']
                if i == 'cinnamon':
                    del enableable['cinnamon-shell']
                if i == 'unity':
                    del enableable['ubuntu-unity']
                if i == 'mate':
                    del enableable['metacity']
                if i == 'xfce':
                    del enableable['xfwm4']

        if not os.path.isdir(FIREFOX_DIR['standard']):
            del enableable['firefox-standard']

        if not os.path.isdir(FIREFOX_DIR['snap']):
            del enableable['firefox-snap']

        if not os.path.isdir(FIREFOX_DIR['flatpak']):
            del enableable['firefox-flatpak']

        if shutil.which('code') is None:
            del enableable['vscode']

        if shutil.which('snap') is None:
            del enableable['snap']

        return enableable

    def configure(self):
        '''Prompts user to configure the theme.'''
        global configured
        config = self.config

        if configure_all or update_color:
            config['color'] = self.config_menu('accent color', VARIANTS['color'])

        if configure_all or update_theme:
            config['theme'] = self.config_menu('theme variant', VARIANTS['theme'])

        if configure_all:
            config['enabled'] = []
            for key, value in config['enableable'].items():
                if key == 'default_syntax':
                    if 'vscode' in config['enabled']:
                        if self.config_yn(key, value, 'n'):
                            config['enabled'].append(key)
                    continue
                if self.config_yn(key, value):
                    config['enabled'].append(key)
        elif update_syntax and 'vscode' in config['enabled']:
            if self.config_yn('default_syntax', 'default syntax highlighting', 'n'):
                config['enabled'].append('default_syntax')
        elif update_syntax:
            print('VS Code theme is not enabled, exiting.')
            sys.exit()

        print() # blank line
        configured = True

    def config_menu(self, message, options, default=1):
        '''
        Prompts user with a menu of options.

        Parameters:
            message (str) : Which {message} do you want?
            options (dict) : {name: pretty_name} dictionary that contains options
            default (int) : Default option.
        '''
        print (f'{BLBLUE}Which {NC}{BLCYAN}{message}{NC}{BLBLUE} do you want?{NC}')

        for i in range(len(options)):
            array = list(options.keys())
            name = array[i]
            pretty_name = list(options.values())[i]
            num = f'{i+1}:'
            if name == 'auto':
                pretty_name += f'{BYELLOW} (Only recommended for GNOME or Budgie){NC}'

            if (i % 2) == 0 and i != len(array) - 1:
                print(f'  {num:<4}{pretty_name:<12}', end='')
            else:
                print(f'  {num:<4}{pretty_name:<12}')

        while True:
            val = input(f'{BOLD}Enter the number corresponding to your choice [Default: {default}]: {NC}')
            try:
                if 1 <= int(val) <= len(array):
                    ret = array[int(val) - 1]
            except(ValueError):
                if val == '':
                    ret = array[int(default) - 1]
                else:
                    continue
            if not self.theme_variants(ret): # If auto and cant detect theme
                continue
            break

        return ret

    def config_yn(self, name, pretty, default = 'y'):
        '''
        Prompts user with a yes or no question.

        Parameters:
            name (str) : Name of part of theme.
            pretty (str) : Name of part of theme to print.
            default (str) : Default option [y/n].
        '''
        while True:
            if name == 'default_syntax':
                question = f'{BLBLUE}Do you want to keep the {NC}{BLCYAN}{pretty}{NC}{BLBLUE}?{NC}{BOLD}'
            elif name == 'gtk4-libadwaita':
                question = f'{BLBLUE}Do you want to install {NC}{BLCYAN}{pretty}{NC}{BLBLUE} as a {NC}{BLCYAN}GTK4{NC}{BLBLUE} theme?{NC}{BOLD}'
            elif name == 'gtk4':
                question = f'{BLBLUE}Do you want to install the custom {NC}{BLCYAN}{pretty}{NC}{BLBLUE} configuration?{NC}{BOLD}'
            else:
                question = f'{BLBLUE}Do you want to install the {NC}{BLCYAN}{pretty}{NC}{BLBLUE} theme?{NC}{BOLD}'

            val = input(question + ' [y/n]'.replace(default, default.capitalize()) + f': {NC}')

            if val.casefold() == 'y'.casefold() or ( default == 'y' and val == '' ):
                if name in VARIANTS['enableable']['dg-yaru'] or name in VARIANTS['enableable']['dg-adw-gtk3']:
                    if shutil.which('meson') is None:
                        print(f"{BLRED}'meson'{BRED} not found, can't install {pretty} theme.{NC}")
                        continue
                    if shutil.which('ninja') is None:
                        print(f"{BLRED}'ninja'{BRED} not found, can't install {pretty} theme.{NC}")
                        continue
                return True
            if val.casefold() == 'n'.casefold() or ( default == 'n' and val == '' ):
                return False

    def read(self):
        '''Reads config file.'''
        config = self.config
        config['old'] = {}
        for theme in VARIANTS['enableable']:
            if theme != 'qualia-gtk-theme-snap':
                config[theme + '_version'] = ''

        try:
            for line in open(CONFIG_FILE, encoding='UTF-8').readlines():
                if ': ' in line:
                    line = line.strip().split(': ')
                else:
                    continue

                key = line[0]

                try:
                    value = line[1]
                except IndexError:
                    continue

                if ' ' in value:
                    value = value.split(' ')

                if not configured and key == 'firefox' or key == 'enabled':
                    config['enabled'] = []
                    prefix = 'firefox-' if key == 'firefox' else '' # old config file was a little different
                    if isinstance(value, list):
                        for i in value:
                            config['enabled'].append(prefix + i)
                    elif isinstance(value, str):
                        config['enabled'].append(prefix + value)
                elif key.startswith('old'): # Themes that were enabled before qualia
                    old = key.split('_')
                    theme = old[1]
                    desktop = old[2]
                    if desktop in VERSIONS:
                        config['old'][theme] = {}
                        config['old'][theme][desktop] = value
                elif isinstance(value, str):
                    try:
                        if not configured and key in VARIANTS and value in VARIANTS[key]:
                            config[key] = value
                        elif key.endswith('version') and len(value) == 40:
                            config[key] = value
                    except TypeError:
                        continue
        except FileNotFoundError:
            pass

    def write(self, config):
        '''
        Writes to config file.

        Parameters:
            config (dict) : Dictionary that contains the configuration.
        '''
        if os.path.isfile(CONFIG_FILE):
            os.remove(CONFIG_FILE)
        elif os.path.isdir(CONFIG_FILE):
            shutil.rmtree(CONFIG_FILE)

        f = open(CONFIG_FILE, 'x', encoding='UTF-8')
        f.write("This file is generated and used by the install script.\n")
        f.write('color: ' + config['color'] + '\n')
        f.write('theme: ' + config['theme'] + '\n')
        f.write('enabled: ' + ' '.join(config['enabled']) + '\n')
        f.write('\n')

        for theme in VARIANTS['enableable']:
            try:
                key = f'{theme}_version'
                version = config[key]
                f.write(f'{key}: {version}\n')
            except KeyError:
                pass

        f.write('\n')

        for theme in config['old']:
            for de in config['old'][theme]:
                if config['old'][theme][de] != '' and not config['old'][theme][de].startswith('qualia'):
                    f.write(f"old_{theme}_{de}: {config['old'][theme][de]}\n")

        f.close()

    def theme_variants(self, pref):
        '''
        Finds out what variant of the themes should be installed (light or dark).

        Parameters:
            pref (str) : 'light' 'dark' or 'auto'
        '''
        config = self.config
        if pref == 'auto':
            try:
                theme_setting = check_output(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'])
            except(FileNotFoundError):
                theme_setting=None
            if theme_setting == 'prefer-dark':
                config['color_scheme']='prefer-dark'
            elif theme_setting == 'default':
                config['color_scheme']='default'
            else:
                print(f"{BRED}Can't detect system light/dark theme preference.{NC}")
                return False # Failed
        elif pref == 'light':
            config['color_scheme']='default'
        elif pref == 'dark':
            config['color_scheme']='prefer-dark'
        return True

class Spinner(threading.Thread):
    '''
    Draws a spinner in terminal on long processes.

    Attributes:
        theme (str) : The theme name to be printed in the message.
        directory (str) : The directory to be printed in the message.
        process (Thread) : The thread of the install process we are waiting on
    '''
    def __init__(self, theme, directory, process):
        super().__init__(target=self._msg)
        self.theme = theme
        self.directory = directory
        self.process = process
        self.start()

    def _msg(self):
        '''Prints spinner with message'''
        message = f'{BGREEN}Installing{NC} the {BOLD}{self.theme}{NC} in {BOLD}{self.directory}{NC}'
        message_len = len(f'Installing the {self.theme} in {self.directory}') # without the color escape codes
        if verbose:
            print(message)
            while self.process.is_alive():
                pass
        else:
            while self.process.is_alive():
                for cursor in '|/-\\':
                    columns = int(os.popen('stty size', 'r').read().split()[1])
                    sys.stdout.write(f'\r\033[?25l' + message + f'\033[J\033[{columns - 1}G' + cursor + '\n')
                    sys.stdout.write(f'\033[{message_len // (columns - 1) + 1}A')
                    sys.stdout.flush()
                    time.sleep(0.1)
            sys.stdout.write('\r' + message + '\033[J\n\033[?25h')
            sys.stdout.flush()

class InstallDgAdwGtk3(threading.Thread):
    '''
    Installs the dg-adw-gtk3 theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        cd(SRC['gtk3'])
        super().__init__(target=self._install)
        self.spinner = None
        self.config = config
        self.start()
        self.join()
        while self.spinner != None and self.spinner.is_alive(): # Wait for spinner thread to close
            pass

    def get_version(self):
        '''
        Return current version of dg-adw-gtk3.

        Returns:
            version (str) : 40 character commit hash
        '''
        version = check_output(['git', 'rev-parse', 'HEAD'])
        return version

    def _install(self):
        run_command(['git', 'submodule', 'update', '--init', '.'])

        if 'gtk4-libadwaita' in self.config['enabled'] and 'gtk3' in self.config['enabled']:
            pretty_string = 'qualia GTK3 and Libadwaita GTK4 themes'
            up_to_date = 'qualia GTK3 and Libadwaita GTK4 themes are'
            options = ['-Dgtk4=true', '-Dgtk3=true']
        elif 'gtk3' in self.config['enabled']:
            pretty_string = 'qualia GTK3 theme'
            up_to_date = 'qualia GTK3 theme is'
            options = ['-Dgtk4=false', '-Dgtk3=true']
        else:
            pretty_string = 'Libadwaita GTK4 theme'
            up_to_date = 'Libadwaita GTK4 theme is'
            options = ['-Dgtk4=true', '-Dgtk3=false']

        if self.get_version() != self.config['dg-adw-gtk3_version'] or configure_all or force:
            global updated
            self.spinner = Spinner(pretty_string, f'{HOME}/.local/share/themes', self)
            if not os.path.isdir('build'):
                run_command(['meson', f'-Dprefix={HOME}/.local', 'build'], meson=True)
            run_command(['meson', 'configure', 'build'] + options, meson=True)
            run_command(['ninja', '-C', 'build', 'install'], meson=True)
            updated = True
        else:
            print(f'The {up_to_date} up to date.')

class InstallDgYaru(threading.Thread):
    '''
    Installs the dg-yaru theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
        parts (list) : Parts of the theme that should be installed.
        parts_pretty (list) : Names of parts of theme to be printed.
    '''
    def __init__(self, config, parts, parts_pretty):
        cd(SRC['yaru'])
        super().__init__(target=self._install)
        self.spinner = None
        self.config = config
        self.parts = parts
        self.parts_pretty = parts_pretty
        self.start()
        self.join()
        while self.spinner is not None and self.spinner.is_alive(): # Wait for spinner thread to close
            pass

    def get_version(self):
        '''
        Return current version of dg-yaru.

        Returns:
            version (str) : 40 character commit hash
        '''
        version = check_output(['git', 'rev-parse', 'HEAD'])
        return version

    def _install(self):
        run_command(['git', 'submodule', 'update', '--init', '.'])

        pretty_string = 'qualia '
        for i, pretty in enumerate(self.parts_pretty):
            if i == len(self.parts_pretty) - 1:
                sep = ', and '
            elif i == 0:
                sep = ''
            else:
                sep = ', '
            pretty_string += sep + pretty
        if len(self.parts_pretty) > 1:
            pretty_string += ' themes'
        else:
            pretty_string += ' theme'

        if self.get_version() != self.config['dg-yaru_version'] or configure_all or force:
            global updated
            self.spinner = Spinner(pretty_string, '/usr/share', self)

            if 'ubuntu-unity' in self.config['enabled'] or 'mate' in self.config['enabled']:
                panel_icons=True
            else:
                panel_icons=False

            options = []

            for p in self.parts:
                options.append('-D' + p + '=true')

            for i in VARIANTS['enableable']['dg-yaru']:
                if i not in self.parts:
                    options.append('-D' + i + '=false')

            if panel_icons:
                options.append('-Dpanel-icons=true')
            else:
                options.append('-Dpanel-icons=false')

            gnome_version = int(self.config['desktop_versions']['gnome'])
            if gnome_version is not None:
                options.append('-Dgnome-shell-version=' + str(gnome_version))

            if not os.path.isdir('build'):
                run_command(['meson', 'build'] + options, meson=True)
            else:
                run_command(['meson', 'configure', 'build'] + options, meson=True)
            run_command(['ninja', '-C', 'build', 'install'], meson=True)
            updated = True
        else:
            if len(self.parts) > 1:
                print(f'The {pretty_string} are up to date.')
            else:
                print(f'The {pretty_string} is up to date.')

class InstallDgLibadwaita(threading.Thread):
    '''
    Installs the dg-libadwaita theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        cd(SRC['gtk4'])
        super().__init__(target=self._install)
        self.config = config
        self.start()
        self.join()

    def get_version(self):
        '''
        Return current version of dg-libadwaita.

        Returns:
            version (str) : 40 character commit hash
        '''
        version = check_output(['git', 'rev-parse', 'HEAD'])
        return version

    def _install(self):
        run_command(['git', 'submodule', 'update', '--init', '.'])

        if self.get_version() != self.config['dg-libadwaita_version'] or configure_all or force or update_color or update_theme:
            global updated
            run_command(['./install.sh', '-c', self.config['color'], '-t', self.config['variant']], show_ouput=True)
            updated = True
        else:
            print('The qualia GTK4 configuration is up to date.')

class InstallDgFirefoxTheme(threading.Thread):
    '''
    Installs the dg-firefox-theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
        directory (str) : Directory to install to.
    '''
    def __init__(self, config, directory):
        cd(SRC['firefox'])
        super().__init__(target=self._install)
        self.config = config
        self.directory = directory
        self.start()
        self.join()

    def get_version(self):
        '''
        Return current version of dg-firefox-theme.

        Returns:
            version (str) : 40 character commit hash
        '''
        version = check_output(['git', 'rev-parse', 'HEAD'])
        return version

    def _install(self):
        run_command(['git', 'submodule', 'update', '--init', '.'])

        if self.get_version() != self.config[f'dg-firefox-theme_version'] or configure_all or force or update_color:
            run_command(['./install.sh', '-c', self.config['color'], '-f', self.directory], show_ouput=True)
        else:
            print('The qualia Firefox theme is up to date.')

class InstallDgVscodeAdwaita(threading.Thread):
    '''
    Installs the dg-vscode-adwaita theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        cd(SRC['vscode'])
        super().__init__(target=self._install)
        self.config = config
        self.start()
        self.join()

    def get_version(self):
        '''
        Return current version of dg-vscode-adwaita.

        Returns:
            version (str) : 40 character commit hash
        '''
        version = check_output(['git', 'rev-parse', 'HEAD'])
        return version

    def _install(self):
        global updated
        run_command(['git', 'submodule', 'update', '--init', '.'])
        if self.get_version() != self.config['dg-vscode-adwaita_version'] or configured or force:
            if 'default_syntax' in self.config['enabled']:
                run_command(['./install.py', '-c', self.config['color'], '-t', self.config['variant'], '-d'], show_ouput = True)
            else:
                run_command(['./install.py', '-c', self.config['color'], '-t', self.config['variant']], show_ouput = True)
            updated = True
        else:
            print('The qualia VSCode theme is up to date.')

class InstallQualiaGtkThemeSnap(threading.Thread):
    '''
    Installs the qualia-gtk-theme snap if it was updated.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        super().__init__(target=self._install)
        self.config = config
        self.start()
        self.join()

    def _install(self):
        snap_list = check_output(['snap', 'list']).split('\n')
        for i in ['gtk-common-themes', 'qualia-gtk-theme']:
            installed = False
            for line in snap_list:
                line = line.split()
                if i in line:
                    installed = True
                    print(f'Checking if {BOLD}{i}{NC} Snap can be updated.')
                    run_command(['sudo', 'snap', 'refresh', i])
            if not installed:
                print(f'{BGREEN}Installing{NC} the {BOLD}{i}{NC} Snap.')
                run_command(['sudo', 'snap', 'install', i])

        connections = check_output(['snap', 'connections']).split('\n')
        for line in connections:
            line = line.split()
            for key, value in {'gtk3': 'gtk-3', 'icons': 'icon', 'sounds': 'sound'}.items():
                if key in self.config["enabled"]:
                    if line[2] == f'gtk-common-themes:{value}-themes':
                        run_command(['sudo', 'snap', 'connect', line[1], f'qualia-gtk-theme:{value}-themes'])
                else:
                    if line[2] == f'qualia-gtk-theme:{value}-themes':
                        run_command(['sudo', 'snap', 'disconnect', line[1], f'qualia-gtk-theme:{value}-themes'])

class Enable:
    '''
    Enables themes in supported desktops.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
        do_verbose (bool): verbose output
        kwargs (dict) : {theme: name} dictionary of the themes to enable
    '''
    def __init__(self, config, do_verbose, **kwargs):
        self.names = {}
        for theme in VARIANTS['enableable']:
            for part in theme:
                self.names[part] = None # default all of them to none
        for key, value in kwargs.items():
            self.names[key] = value

        self.config = config
        self.data = self._data()
        self.verbose = do_verbose # pass verbose as an argument because uninstall.py also uses this class

    def _data(self):
        schemas = {
            'gnome': 'org.gnome.desktop.interface',
            'cinnamon': 'org.cinnamon.desktop.interface',
            'unity': 'org.gnome.desktop.interface',
            'mate': 'org.mate.interface',
            'budgie': 'org.gnome.desktop.interface'
        }

        cursor_scemas = schemas.copy()
        cursor_scemas['mate'] = 'org.mate.peripherals-mouse'

        sound_schemas = {
            'gnome': 'org.gnome.desktop.sound',
            'cinnamon': 'org.cinnamon.desktop.sound',
            'unity': 'org.gnome.desktop.sound',
            'mate': 'org.mate.sound',
            'budgie': 'org.gnome.desktop.sound'
        }

        data = {}
        try:
            data['gtk3'] = {
                'schemas': schemas,
                'key': 'gtk-theme',
                'property': '/Net/ThemeName',
                'theme_name': self.names['gtk3'],
                'channel': 'xsettings'
            }
        except KeyError:
            pass
        try:
            data['icons'] = {
                'schemas': schemas,
                'key': 'icon-theme',
                'property': '/Net/IconThemeName',
                'theme_name': self.names['icons'],
                'channel': 'xsettings'
            }
        except KeyError:
            pass
        try:
            data['cursors'] = {
                'schemas': cursor_scemas,
                'key': 'cursor-theme',
                'property': '/Gtk/CursorThemeName',
                'theme_name': self.names['cursors'],
                'channel': 'xsettings'
            }
        except KeyError:
            pass
        try:
            data['sounds'] = {
                'schemas': sound_schemas,
                'key': 'theme-name',
                'property': '/Net/SoundThemeName',
                'theme_name': self.names['sounds'],
                'channel': 'xsettings'
            }
        except KeyError:
            pass
        try:
            data['gnome-shell'] = {
                'schemas': {'gnome': 'org.gnome.shell.extensions.user-theme'},
                'key': 'name',
                'property': None,
                'channel': None,
                'theme_name': self.names['gnome-shell']
            }
        except KeyError:
            pass
        try:
            data['cinnamon-shell'] = {
                'schemas': {'cinnamon': 'org.cinnamon.theme'},
                'key': 'name',
                'property': None,
                'channel': None,
                'theme_name': self.names['cinnamon-shell']
            }
        except KeyError:
            pass
        try:
            data['metacity'] = {
                'schemas': {'mate': 'org.mate.Marco.general'},
                'key': 'theme',
                'property': None,
                'channel': None,
                'theme_name': self.names['metacity']
            }
        except KeyError:
            pass
        try:
            data['xfwm4'] = {
                'schemas': {},
                'key': None,
                'property': '/general/theme',
                'channel': 'xfwm4',
                'theme_name': self.names['xfwm4']
            }
        except KeyError:
            pass

        return data

    def enable_theme(self, desktop='all', uninstalling = False):
        '''
        Enables themes in installed desktops.

        Attributes:
            desktop (str) : Either 'all' or name of desktop to enable themes in.
            uninstalling (bool) : True if being ran by uninstall script, so it doesn't check that the theme is enabled in configuration.
        '''
        data = self.data
        config = self.config
        for theme, value in data.items():
            if theme in config['enabled'] or uninstalling:
                if value['theme_name'] is None:
                    continue
                else:
                    name = value['theme_name']

                if theme == 'gnome-shell':
                    if shutil.which('gnome-extensions') is not None:
                        if 'user-theme@gnome-shell-extensions.gcampax.github.com' in check_output(['gnome-extensions', 'list']):
                            run_command(['gnome-extensions', 'enable', 'user-theme@gnome-shell-extensions.gcampax.github.com'], override_verbose = self.verbose)
                        else:
                            print(f"{BLYELLOW}'User Themes'{BYELLOW} GNOME Shell Extension not found, not enabling GNOME Shell theme.{NC}")
                            continue
                    else:
                        print(f"{BLYELLOW}'gnome-extensions'{BYELLOW} not found, not enabling GNOME Shell theme.{NC}")
                        continue

                for de, schema in value['schemas'].items():
                    if desktop != 'all' and desktop != de:
                        continue
                    key = value['key']
                    if shutil.which('gsettings') is not None:
                        if config['desktop_versions'][de] is not None:
                            de_pretty = 'GNOME' if de == 'gnome' else de.capitalize()
                            old = check_output(['gsettings', 'get', schema, key])
                            if theme not in config['old']:
                                config['old'][theme] = {}
                                config['old'][theme][de] = old
                            elif de in config['old'][theme] and config['old'][theme][de].startswith('qualia'):
                                config['old'][theme][de] = old
                            if old != name:
                                print(f'Changing {theme} theme in {de_pretty} to {BOLD}{name}{NC}.')
                                run_command(['gsettings', 'set', schema, key, name], override_verbose = self.verbose)
                    else:
                        print(f"{BLYELLOW}'gsettings'{BYELLOW} not found, not enabling {theme} theme.{NC}")
                        break

                prop = data[theme]['property']
                if shutil.which('xfconf-query') is not None:
                    channel = data[theme]['channel']
                    if prop is not None and config['desktop_versions']['xfce'] is not None:
                        old = check_output(['xfconf-query', '-c', channel, '-p', prop])
                        if theme not in config['old']:
                            config['old'][theme] = {}
                            config['old'][theme]['xfce'] = old
                        elif 'xfce' in config['old'][theme] and config['old'][theme]['xfce'].startswith('qualia'):
                            config['old'][theme]['xfce'] = old
                        if old != name:
                            print(f'Changing {theme} theme in XFCE to {BOLD}{name}{NC}.')
                            run_command(['xfconf-query', '-c', channel, '-p', prop, '-s', name], override_verbose = self.verbose)
                elif prop is not None and config['desktop_versions']['xfce'] is not None:
                    print(f"{BLYELLOW}'xfconf-query'{BYELLOW} not found, not enabling {theme} theme.{NC}")

        return config

if __name__ == "__main__":
    from uninstall import OLD_NAMES
    main()
