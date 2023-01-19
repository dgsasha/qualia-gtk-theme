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
from glob import glob

from paths import HOME, REPO_DIR, CONFIG, OLD_CONFIG, SRC, FIREFOX_DIR, VSCODE_DIR, installed

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
    'dir': {
        'default': f'Default  {BGREEN}(Recommended for most distros){NC}',
        'home': f'{HOME}/.local/share  {BYELLOW}(Only recommended for immutable distros){NC}',
        'root': f'/usr/share  {BYELLOW}(Do not choose if you use Flatpaks){NC}'
    },
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
        'auto': f'Auto  {BYELLOW}(Only recommended for GNOME or Budgie){NC}'
    },
    'window-controls': {
        'macos': 'macOS',
        'symbolic': 'Libadwaita',
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
            'firefox': 'Firefox',
            'settings_theme': ''
        },
        'dg-vscode-adwaita': {
            'vscode': 'VS Code',
            'default_syntax': ''
        },
        'qualia-gtk-theme-snap': {
            'snap': 'Snap'
        },
        'extra': {
            'flatpak': 'Flatpak'
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

DIR_MSG = f'{BLBLUE}Where do you want to {NC}{BLCYAN}install the theme{NC}{BLBLUE}?{NC}'
SETTINGS_MSG = f'{BLBLUE}Do you want to theme the {NC}{BLCYAN}settings pages{NC}{BLBLUE} in {BLCYAN}Firefox{BLBLUE}?{NC}{BOLD}'
SYNTAX_MSG = f'{BLBLUE}Do you want to keep the {NC}{BLCYAN}default syntax highlighting{NC}{BLBLUE} in {BLCYAN}VS Code{BLBLUE}?{NC}{BOLD}'
LIBADWAITA_MSG = f'{BLBLUE}Do you want to install {BLCYAN}Libadwaita{BLBLUE} as a {NC}{BLCYAN}GTK4 theme{NC}{BLBLUE}?{NC}{BOLD}'
GTK4_MSG = f'{BLBLUE}Do you want to install the {NC}{BLCYAN}custom GTK4 configuration{NC}{BLBLUE}?{NC}{BOLD}'
FLATPAK_MSG = f'{BLBLUE}Do you want to give {NC}{BLCYAN}Flatpak apps{NC}{BLBLUE} access to the {NC}{BLCYAN}GTK themes{NC}{BLBLUE}?{NC}{BOLD}'

# dg-gnome-theme
OLD_THEMES = [
    'gtk3',
    'gnome-shell',
    'icons',
    'cursors',
    'gtksourceview',
    'sounds',
    'firefox',
    'snap'
]

# anything in dg-yaru or dg-adw-gtk3
MESON_THEMES = list(VARIANTS['enableable']['dg-yaru'].keys()) + list(VARIANTS['enableable']['dg-adw-gtk3'].keys())

# Set some things to false
reinstall = no_update = update_color = update_theme = update_settings = update_syntax = reconfigure = verbose = force = configured = updated = False

#################
##  Functions  ##
#################

def cd(directory):
    '''
    Change directory.

    Parameters:
        dir (str) : The path of the directory to change to.
    '''
    if verbose:
        print(f"Changing directory to '{directory}'")
    os.chdir(directory)

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
        print("Running command '" + ' '.join(command) + "'")
    try:
        subprocess.run(command, stdout=None if verbose or show_ouput else subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    except subprocess.CalledProcessError as error:
        if not (verbose or show_ouput):
            print('\n' + error.output.decode("utf-8"))
            print(f"{BRED}Something went wrong, run {BLRED}'{sys.argv[0]} --verbose'{BRED} for more info.{NC}")
        else:
            print(f'{BRED}Something went wrong. Check the log above.{NC}')
        if meson:
            print(f"{BRED}Also, running {BLRED}'{sys.argv[0]} --clean'{BRED} might fix the issue.{NC}")
        print('\033[?25h') # bring back cursor
        os._exit(1)

def check_output(command):
    '''
    Check output of command.

    Parameters:
        command (list) : A list of the command and arguments to run.

    Returns:
        output (str) : The ouput of the command.
    '''
    output = subprocess.run(command, stdout=subprocess.PIPE, check=True).stdout.decode('utf-8').strip('\'\n')
    return output

def main():
    '''The main function.'''
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
    conf.read()

    global configure_all
    global reinstall

    # Move old config file
    if os.path.isfile(OLD_CONFIG) and not os.path.isfile(CONFIG):
        shutil.move(OLD_CONFIG, CONFIG)

    # Whether or not to configure
    if not os.path.isfile(CONFIG) or reconfigure:
        configure_all = True
        conf.configure()
        if os.path.isfile(CONFIG):
            os.remove(CONFIG)

    config = conf.ret_config()

    # Reconfigure if config file has issues
    try:
        color_scheme = conf.theme_variants(config['theme'])
        if not isinstance(config['enabled'], list) or color_scheme is None or len(config['enabled']) == 0:
            configure_all = True
            conf.configure()
    except KeyError:
        configure_all = True
        conf.configure()

    # Reconfigure color, theme variant, or syntax highlighting if user wants to
    if ( update_color or update_theme or update_syntax or update_settings or update_dir or update_window_controls ) and not configure_all:
        conf.configure()

    if configured:
        config = conf.ret_config()

    conf.write(config)

    if configure_all or force or update_color:
        reinstall = True

    ######################
    ##  Install Themes  ##
    ######################

    if not configured:
        print(f'{BYELLOW}Updating themes using previous configuration.{NC}')
        print(f"{BYELLOW}Use {BLYELLOW}'{sys.argv[0]} --reconfigure'{BYELLOW} if you want to change anything.{NC}")

    paths = installed(new_only = True)

    config['suffix']='-dark' if config['color_scheme'] == 'prefer-dark' else ''
    config['variant']='dark' if config['color_scheme'] == 'prefer-dark' else 'light'

    def check_path(name, paths, should_print = True):
        '''
        Check if the path to a theme exists, used for when a theme was previously installed but is disabled.

        Parameters:
            name (str) : The name of the part of the theme to check.
            paths (dict) : The dict containing all of the paths.
            should_print (bool) : If we should print that the path exists.

        Returns:
            exists (bool) : Whether or not the path exists.
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
            message = ''
            for theme in VARIANTS['enableable']:
                if name in VARIANTS['enableable'][theme]:
                    pretty = VARIANTS['enableable'][theme][name]
                    if name == 'gtk4-libadwaita':
                        message += f'{pretty} GTK4 theme{NC}'
                    elif name == 'gtk4':
                        message += f'{pretty} configuration{NC}'
                    else:
                        message += f'{pretty} theme{NC}'
                    print(f"The {message} was installed previously, use './uninstall.py {name}' to remove it.")

        return exists

    # Install dg-adw-gtk3
    if 'gtk3' in config['enabled'] or 'gtk4-libadwaita' in config['enabled']:
        # If user is installing in root dir, remove old symlinks if they exist
        if config['dir'] == 'root':
            dirs = paths['gtk3'] + paths['gtk4-libadwaita']
            if isinstance(dirs, list):
                for directory in dirs:
                    if os.path.islink(directory):
                        run_command(['sudo', 'rm', '-rf', directory])

        gtk3 = InstallDgAdwGtk3(config)
        config['dg-adw-gtk3_version'] = gtk3.get_version()
        conf.write(config)
    else:
        check_path('gtk3', paths)
        check_path('gtk4', paths)

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
    if 'firefox' in config['enabled']:
        firefox = InstallDgFirefoxTheme(config)
        config['dg-firefox-theme_version'] = firefox.get_version()
        conf.write(config)
    else:
        check_path('firefox', paths)

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

    gtk3_name = f"qualia{config['suffix']}-{config['window-controls']}" if config['color'] == 'orange' else f"qualia-{config['color']}{config['suffix']}-{config['window-controls']}"
    theme_name = f"qualia{config['suffix']}" if config['color'] == 'orange' else f"qualia-{config['color']}{config['suffix']}"
    icon_name = 'qualia-dark' if config['color'] == 'orange' else f"qualia-{config['color']}-dark"
    cursor_name = 'qualia'
    sourceview_name = f"qualia{config['suffix']}"
    xfwm4_name = f"qualia{config['suffix']}-{config['window-controls']}"
    if shutil.which('xfconf-query') is not None:
        if 'xsettings' in check_output(['xfconf-query', '-l']) and check_output(['xfconf-query', '-c', 'xsettings', '-p', '/Gdk/WindowScalingFactor']) == '2':
            xfwm4_name += '-xhdpi'

    cd(REPO_DIR)

    kwargs = {
        'gtk3': gtk3_name,
        'icons': icon_name,
        'cursors': cursor_name,
        'sounds': cursor_name,
        'gnome-shell': theme_name,
        'cinnamon-shell': theme_name,
        'metacity': xfwm4_name,
        'xfwm4': xfwm4_name,
        'gtksourceview': sourceview_name
    }

    enable = Enable(config, verbose, **kwargs)

    config = enable.enable_theme()

    # Update config file one last time
    conf.write(config)

    # Set color scheme
    try:
        if config['color_scheme'] is not None and shutil.which('gsettings') is not None:
            subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', config['color_scheme']], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
            if config['desktop_versions']['budgie'] is not None:
                dark = 'true' if config['color_scheme'] == 'prefer-dark' else 'false'
                subprocess.run(['gsettings', 'set', 'com.solus-project.budgie-panel', 'dark-theme', dark ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
    except subprocess.CalledProcessError:
        pass

    if 'flatpak' in config['enabled']:
        print('Giving Flatpak apps access to the GTK themes.')
        run_command(['flatpak', 'override', '--user', '--filesystem=xdg-config/gtk-4.0', '--filesystem=xdg-data/themes'])

    # Remove old variants of the theme
    from uninstall import remove_theme, available_themes, remove_empty, delete

    print('Cleaning up...')

    old_paths = installed(old_only=True)
    for theme in OLD_THEMES:
        remove_theme(theme, available_themes[theme], old_paths, True, False, verbose)

    if config['dir'] == 'root':
        home_paths = installed(directory='home')
        for theme in MESON_THEMES:
            remove_theme(theme, available_themes[theme], home_paths, True, False, verbose)
    elif config['dir'] == 'home':
        root_paths = installed(directory='root')
        for theme in MESON_THEMES:
            remove_theme(theme, available_themes[theme], root_paths, True, False, verbose)
    elif config['dir'] == 'default':
        non_default_paths = installed(directory='not_default')
        for theme in MESON_THEMES:
            remove_theme(theme, available_themes[theme], non_default_paths, True, False, verbose, True)

    theme_dirs = installed(new_only = True, just_theme_dirs = True)

    for i in theme_dirs:
        if 'share/themes' in i:
            paths = glob(f'{i}/*')
        else:
            paths = [i]
        for path in paths:
            for variant in VARIANTS['window-controls']:
                if variant != config['window-controls'] and variant in path:
                    delete(path)
                for subdir in ('gtk-2.0', 'gtk-3.0', 'gtk-4.0', 'xfwm4', 'metacity', 'unity'):
                    if path.endswith(subdir) and config['window-controls'] not in path:
                        delete(path)
            for color in VARIANTS['color']:
                if color != config['color'] and color in path:
                    delete(path)
                    break

    remove_empty()

    theme_dirs = installed(new_only = True, just_theme_dirs = True, directory = 'home')

    # Symlink themes to /usr dir if using mate
    if config['desktop_versions']['mate'] is not None and config['dir'] == 'default':
        if isinstance(theme_dirs, list):
            for directory in theme_dirs:
                paths = glob(f'{directory}/*')
                for target in paths:
                    dest = '/usr' + target.split(f'{HOME}/.local')[1]
                    directory = os.path.dirname(dest)
                    if not os.path.isdir(directory):
                        run_command(['sudo', 'mkdir', '-p', directory])
                    if not os.path.exists(dest) and os.path.exists(target):
                        run_command(['sudo', 'ln', '-rsf', target, dest])

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
            ver = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')
            ver = sub(regex, '', ver)

            if '.' in ver and float(ver) in VERSIONS[name]:
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
            desktop_versions (dict): dictionary containing the desktop versions.

        Returns:
            enableable (dict) : {name: pretty_name}, themes that can be enabled.
        '''
        enableable = {}

        config = self.config

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

        config['firefox'] = []

        for variant, path in FIREFOX_DIR.items():
            if os.path.isdir(path):
                config['firefox'].append(variant)

        if len(config['firefox']) == 0:
            del enableable['firefox']

        config['vscode'] = []

        for variant, path in VSCODE_DIR.items():
            if os.path.isdir(path):
                config['vscode'].append(variant)

        if len(config['vscode']) == 0:
            del enableable['vscode']

        if shutil.which('snap') is None:
            del enableable['snap']

        if shutil.which('flatpak') is None:
            del enableable['flatpak']

        return enableable

    def configure(self):
        '''Prompts user to configure the theme.'''
        global configured
        config = self.config

        if configure_all or update_dir:
            config['dir'] = self.config_menu('', VARIANTS['dir'], custom_msg=DIR_MSG, no_columns=True)

        if configure_all or update_color:
            config['color'] = self.config_menu('accent color', VARIANTS['color'])

        if configure_all or update_theme:
            config['theme'] = self.config_menu('theme variant', VARIANTS['theme'])

        if configure_all or update_window_controls:
            config['window-controls'] = self.config_menu('window controls variant', VARIANTS['window-controls'])

        if configure_all:
            config['enabled'] = []

        for key, value in config['enableable'].items():
            if key == 'settings_theme' and (update_settings or configure_all):
                if 'firefox' in config['enabled']:
                    if self.config_yn(key, value, custom_msg=SETTINGS_MSG):
                        if key not in config['enabled']:
                            config['enabled'].append(key)
                    else:
                        if key in config['enabled']:
                            config['enabled'].remove(key)
                elif update_settings:
                    print('Firefox theme is not enabled, exiting.')
                    sys.exit()
                continue
            if key == 'default_syntax' and (update_syntax or configure_all):
                if 'vscode' in config['enabled']:
                    if self.config_yn(key, value, 'n', custom_msg=SYNTAX_MSG):
                        if key not in config['enabled']:
                            config['enabled'].append(key)
                    else:
                        if key in config['enabled']:
                            config['enabled'].remove(key)
                elif update_syntax:
                    print('VS Code theme is not enabled, exiting.')
                    sys.exit()
                continue
            if configure_all:
                if key == 'gtk4':
                    if self.config_yn(key, value, custom_msg=GTK4_MSG):
                        config['enabled'].append(key)
                    continue
                if key == 'gtk4-libadwaita':
                    if self.config_yn(key, value, custom_msg=LIBADWAITA_MSG):
                        config['enabled'].append(key)
                    continue
                if key == 'flatpak':
                    if self.config_yn(key, value, custom_msg=FLATPAK_MSG):
                        config['enabled'].append(key)
                    continue
                if self.config_yn(key, value):
                    config['enabled'].append(key)

        print() # blank line
        configured = True

    def config_menu(self, message, options, default=1, custom_msg=None, no_columns=False):
        '''
        Prompts user with a menu of options.

        Parameters:
            message (str) : Which {message} do you want?
            options (dict) : {name: pretty_name} dictionary that contains options.
            default (int) : Default option.
            custom_msg (str) : Provide a custom message to print. Defaults to None.
            no_colums (bool) : Each option takes up a full line.
        '''
        if custom_msg is not None:
            question = custom_msg
        else:
            question = f'{BLBLUE}Which {NC}{BLCYAN}{message}{NC}{BLBLUE} do you want?{NC}'

        print (question)

        for i in range(len(options)):
            array = list(options.keys())
            pretty_name = list(options.values())[i]
            num = f'{i+1}:'

            if not no_columns and (i % 2) == 0 and i != len(array) - 1:
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
            try:
                if not self.theme_variants(ret): # If auto and cant detect theme
                    continue
            except UnboundLocalError:
                continue
            break

        return ret

    def config_yn(self, name, pretty, default = 'y', custom_msg = None):
        '''
        Prompts user with a yes or no question.

        Parameters:
            name (str) : Name of part of themye.
            pretty (str) : Name of part of theme to print.
            default (str) : Default option, either 'y' or 'n'. Defaults to 'y'
            custom_msg (str) : Provide a custom message to print. Defaults to None.
        '''
        while True:
            if custom_msg is not None:
                question = custom_msg
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
        config['old_vscode'] = []
        config['old_firefox'] = []
        config['dir'] = 'default'
        config['color'] = 'orange'
        config['theme'] = 'light'
        config['window-controls'] = 'macos'

        for theme in VARIANTS['enableable']:
            if theme != 'qualia-gtk-theme-snap' and theme != 'extra':
                config[theme + '_version'] = ''

        try:
            for line in open(CONFIG, encoding='UTF-8').readlines():
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

                if not configured and key in ('enabled', 'firefox', 'vscode'):
                    prefix = 'old_' if key in ('firefox', 'vscode') else ''
                    config[prefix + key] = []
                    if isinstance(value, list):
                        for theme in value:
                            if theme.startswith('firefox'):
                                theme = 'firefox'
                            if (theme in config['enableable'] or key != 'enabled') not in config[prefix + key]:
                                config[prefix + key].append(theme)
                    elif isinstance(value, str):
                        if value.startswith('firefox'):
                            value = 'firefox'
                        if (value in config['enableable'] or prefix + key != 'enabled') and value not in config[prefix + key]:
                            config[prefix + key].append(value)

                elif key.startswith('old'): # Themes that were enabled before qualia
                    old = key.split('_')
                    theme = old[1]
                    desktop = old[2]
                    if desktop in VERSIONS:
                        config['old'][theme] = {}
                        config['old'][theme][desktop] = value
                elif key == 'gnome':
                    try:
                        config['old_gnome'] = int(value)
                    except ValueError:
                        config['old_gnome'] = None
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
        if os.path.isfile(CONFIG):
            os.remove(CONFIG)
        elif os.path.isdir(CONFIG):
            shutil.rmtree(CONFIG)

        f = open(CONFIG, 'x', encoding='UTF-8')
        f.write("This file is generated and used by the install script.\n")
        f.write("You probably shouldn't edit it.\n\n")

        f.write('color: ' + config['color'] + '\n')
        f.write('theme: ' + config['theme'] + '\n')
        f.write('window-controls: ' + config['window-controls'] + '\n')
        f.write('dir: ' + config['dir'] + '\n')
        f.write('enabled: ' + ' '.join(config['enabled']) + '\n\n')
        f.write('gnome: ' + str(config['desktop_versions']['gnome']) + '\n')
        f.write('firefox: ' + ' '.join(config['firefox']) + '\n')
        f.write('vscode: ' + ' '.join(config['vscode']) + '\n\n')

        for theme in VARIANTS['enableable']:
            if theme == 'extra':
                continue
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
            pref (str) : 'light' 'dark' or 'auto'.
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
        process (Thread) : The thread of the install process we are waiting on.
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
                    sys.stdout.write(f'\r\033[?25l' + message + '   ' + f'\033[J\033[{columns}G' + cursor + '\n')
                    sys.stdout.write(f'\033[{(message_len + 2) // (columns) + 1}A')
                    sys.stdout.flush()
                    time.sleep(0.1)
            sys.stdout.write('\r' + message + '\033[J\n\033[?25h')
            sys.stdout.flush()

class InstallThread(threading.Thread):
    '''
    A thread for installing a part of the theme.

    Attributes:
        process (object) : Callable object to run in a thread.
    '''
    def __init__(self, process):
        cd(REPO_DIR)
        self.spinner = None
        super().__init__(target=process)
        self.start()
        self.join()
        while self.spinner is not None and self.spinner.is_alive(): # Wait for spinner thread to close
            pass

    def get_version(self):
        '''
        Return current version of the submodule.

        Returns:
            version (str) : 40 character commit hash
        '''
        version = check_output(['git', 'rev-parse', 'HEAD'])
        return version

    def updated(self):
        '''
        Sets the global variable 'updated' to true.
        '''
        global updated
        updated = True

class InstallDgAdwGtk3(InstallThread):
    '''
    Installs the dg-adw-gtk3 theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        self.config = config
        super().__init__(process=self._install)

    def _install(self):
        config = self.config
        if not no_update:
            run_command(['git', 'submodule', 'update', '--init', 'src/dg-adw-gtk3'])
        cd(SRC['gtk3'])

        install_dir = f'{HOME}/.local' if config['dir'] in ('default', 'home') else '/usr'

        options = [f'-Dprefix={install_dir}']
        if 'gtk4-libadwaita' in config['enabled'] and 'gtk3' in config['enabled']:
            pretty_string = 'qualia GTK3 and Libadwaita GTK4 themes'
            up_to_date = 'qualia GTK3 and Libadwaita GTK4 themes are'
            options += ['-Dgtk4=true', '-Dgtk3=true']
        elif 'gtk3' in self.config['enabled']:
            pretty_string = 'qualia GTK3 theme'
            up_to_date = 'qualia GTK3 theme is'
            options += ['-Dgtk4=false', '-Dgtk3=true']
        else:
            pretty_string = 'Libadwaita GTK4 theme'
            up_to_date = 'Libadwaita GTK4 theme is'
            options += ['-Dgtk4=true', '-Dgtk3=false']

        options += [f"-Dwindow-controls={config['window-controls']}"]

        options += [f"-Daccent-colors={'' if config['color'] == 'orange' else config['color']}"]

        if self.get_version() != self.config['dg-adw-gtk3_version'] or reinstall or update_dir or update_window_controls:
            self.spinner = Spinner(f"{config['color']} {pretty_string}", f'{install_dir}/share/themes', self)
            if not os.path.isdir('build'):
                run_command(['meson', 'build'] + options, meson=True)
            else:
                run_command(['meson', 'configure', 'build'] + options, meson=True)
            run_command(['meson', 'configure', 'build'] + options, meson=True)
            run_command(['ninja', '-C', 'build', 'install'], meson=True)
            self.updated()
        else:
            print(f'The {up_to_date} up to date.')

class InstallDgYaru(InstallThread):
    '''
    Installs the dg-yaru theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
        parts (list) : Parts of the theme that should be installed.
        parts_pretty (list) : Names of parts of theme to be printed.
    '''
    def __init__(self, config, parts, parts_pretty):
        self.config = config
        self.parts = parts
        self.parts_pretty = parts_pretty
        super().__init__(process=self._install)

    def _install(self):
        config = self.config
        if not no_update:
            run_command(['git', 'submodule', 'update', '--init', 'src/dg-yaru'])

        cd(SRC['yaru'])

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

        install_dir = f'{HOME}/.local' if config['dir'] == 'home' else '/usr'

        if self.get_version() != config['dg-yaru_version'] or reinstall or update_dir or \
        (update_window_controls and ('metacity' in config['enabled'] or 'xfwm4' in config['enabled'] or 'ubuntu-unity' in config['enabled'])) or \
        config['old_gnome'] != config['desktop_versions']['gnome']:
            self.spinner = Spinner(f"{config['color']} {pretty_string}", f'{install_dir}/share', self)

            options = [f'-Dprefix={install_dir}']

            options += [f"-Daccent-colors={'' if config['color'] == 'orange' else config['color']}"]

            options += [f"-Dwindow-controls={config['window-controls']}"]

            for p in self.parts:
                options.append('-D' + p + '=true')

            for i in VARIANTS['enableable']['dg-yaru']:
                if i not in self.parts:
                    options.append('-D' + i + '=false')

            if 'unity' in config['desktop_versions'] or 'mate' in config['desktop_versions']:
                options.append('-Dpanel-icons=true')
            else:
                options.append('-Dpanel-icons=false')

            gnome_version = self.config['desktop_versions']['gnome']
            if gnome_version is not None:
                options.append('-Dgnome-shell-version=' + str(gnome_version))

            if not os.path.isdir('build'):
                run_command(['meson', 'build'] + options, meson=True)
            else:
                run_command(['meson', 'configure', 'build'] + options, meson=True)
            run_command(['ninja', '-C', 'build', 'install'], meson=True)
            self.updated()
        else:
            if len(self.parts) > 1:
                print(f'The {pretty_string} are up to date.')
            else:
                print(f'The {pretty_string} is up to date.')

class InstallDgLibadwaita(InstallThread):
    '''
    Installs the dg-libadwaita theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        self.config = config
        super().__init__(process=self._install)

    def _install(self):
        config = self.config
        if not no_update:
            run_command(['git', 'submodule', 'update', '--init', 'src/dg-libadwaita'])
        cd(SRC['gtk4'])

        if self.get_version() != config['dg-libadwaita_version'] or reinstall or update_theme or update_window_controls:
            command = ['./install.sh', '-c', config['color'], '-t', config['variant']]
            if config['window-controls'] == 'symbolic':
                command.append('-s')
            run_command(command, show_ouput=True)
            self.updated()
        else:
            print('The qualia GTK4 configuration is up to date.')

class InstallDgFirefoxTheme(InstallThread):
    '''
    Installs the dg-firefox-theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        self.config = config
        super().__init__(process=self._install)

    def _install(self):
        config = self.config
        if not no_update:
            run_command(['git', 'submodule', 'update', '--init', 'src/dg-firefox-theme'])
        cd(SRC['firefox'])

        firefox_changed = False
        for variant in config['firefox']:
            if variant not in config['old_firefox']:
                firefox_changed = True

        if self.get_version() != config['dg-firefox-theme_version'] or reinstall or update_settings or firefox_changed or update_window_controls:
            command = ['./install.sh', '-c', self.config['color']]
            if 'settings_theme' not in self.config['enabled']:
                command.append('-n')
            if config['window-controls'] == 'symbolic':
                command.append('-s')
            run_command(command, show_ouput=True)
        else:
            print('The qualia Firefox theme is up to date.')

class InstallDgVscodeAdwaita(InstallThread):
    '''
    Installs the dg-vscode-adwaita theme if it was updated or if being forced.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        self.config = config
        super().__init__(process=self._install)

    def _install(self):
        config = self.config
        if not no_update:
            run_command(['git', 'submodule', 'update', '--init', 'src/dg-vscode-adwaita'])
        cd(SRC['vscode'])

        vscode_changed = False
        for variant in config['vscode']:
            if variant not in config['old_vscode']:
                vscode_changed = True

        if self.get_version() != self.config['dg-vscode-adwaita_version'] or configure_all or update_syntax or vscode_changed or update_color:
            if 'default_syntax' in self.config['enabled']:
                run_command(['./install.py', '-c', self.config['color'], '-t', self.config['variant'], '-d'], show_ouput = True)
            else:
                run_command(['./install.py', '-c', self.config['color'], '-t', self.config['variant']], show_ouput = True)
            self.updated()
        else:
            print('The qualia VSCode theme is up to date.')

class InstallQualiaGtkThemeSnap(InstallThread):
    '''
    Installs the qualia-gtk-theme snap if it was updated.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
    '''
    def __init__(self, config):
        self.config = config
        super().__init__(process=self._install)

    def _install(self):
        snap_list = check_output(['snap', 'list']).split('\n')
        for name in ('gtk-common-themes', 'qualia-gtk-theme'):
            installed = False
            for line in snap_list:
                line = line.split()
                if name in line:
                    installed = True
                    print(f'Checking if {BOLD}{name}{NC} Snap can be updated.')
                    run_command(['sudo', 'snap', 'refresh', name], show_ouput = True)
            if not installed:
                print(f'{BGREEN}Installing{NC} the {BOLD}{name}{NC} Snap.')
                run_command(['sudo', 'snap', 'install', name], show_ouput = True)

        connections = check_output(['snap', 'connections']).split('\n')
        for line in connections:
            line = line.split()
            for key, value in {'gtk3': 'gtk-3', 'icons': 'icon', 'sounds': 'sound'}.items():
                try:
                    if key in self.config["enabled"]:
                        if line[2] == f'gtk-common-themes:{value}-themes':
                            run_command(['sudo', 'snap', 'connect', line[1], f'qualia-gtk-theme:{value}-themes'], show_ouput = True)
                    else:
                        if line[2] == f'qualia-gtk-theme:{value}-themes':
                            run_command(['sudo', 'snap', 'disconnect', line[1], f'qualia-gtk-theme:{value}-themes'], show_ouput = True)
                except IndexError:
                    pass

class Enable:
    '''
    Enables themes in supported desktops.

    Attributes:
        config (dict) : Dictionary that contains the configuration.
        do_verbose (bool): Verbose output.
        kwargs (dict) : {theme: name} Dictionary of the themes to enable.
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

        gtksourceview_schemas = {
            'Text Editor': 'org.gnome.TextEditor',
            'Gedit': 'org.gnome.gedit.preferences.editor',
            'Builder': 'org.gnome.builder.editor',
            'mousepad': 'org.xfce.mousepad.preferences.view',
            'pluma': 'org.mate.pluma'
        }

        gtksourceview_keys = {
            'Text Editor': 'style-scheme',
            'Gedit': 'scheme',
            'Builder': 'style-scheme-name',
            'mousepad': 'color-scheme',
            'pluma': 'color-scheme'
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
        try:
            data['gtksourceview'] = {
                'schemas': gtksourceview_schemas,
                'key': gtksourceview_keys,
                'property': None,
                'channel': None,
                'theme_name': self.names['gtksourceview']
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
        schema_list = check_output(['gsettings', 'list-schemas'])
        for theme, value in data.items():
            if theme in config['enabled'] or uninstalling:
                if value['theme_name'] is None:
                    continue

                if theme == 'gnome-shell':
                    if shutil.which('gnome-extensions') is not None:
                        try:
                            if 'user-theme@gnome-shell-extensions.gcampax.github.com' in check_output(['gnome-extensions', 'list']):
                                    run_command(['gnome-extensions', 'enable', 'user-theme@gnome-shell-extensions.gcampax.github.com'], override_verbose = self.verbose)
                            else:
                                print(f"{BLYELLOW}'User Themes'{BYELLOW} GNOME Shell Extension not found, not enabling GNOME Shell theme.{NC}")
                                continue
                        except subprocess.CalledProcessError:
                            print(f"{BLYELLOW}'User Themes'{BYELLOW} GNOME Shell Extension not found, not enabling GNOME Shell theme.{NC}")
                            continue
                    else:
                        print(f"{BLYELLOW}'gnome-extensions'{BYELLOW} not found, not enabling GNOME Shell theme.{NC}")
                        continue

                for de, schema in value['schemas'].items():
                    if desktop != 'all' and desktop != de:
                        continue
                    if theme == 'icons' and de == 'unity' and not uninstalling:
                        # because the panel isn't always dark in the unity theme, use light icons in light theme
                        name = f"qualia{config['suffix']}"
                    else:
                        name = value['theme_name']
                    if isinstance(value['key'], dict):
                        key = value['key'][de]
                    else:
                        key = value['key']
                    if shutil.which('gsettings') is not None:
                        if schema in schema_list:
                            if not (de in config['desktop_versions'] and config['desktop_versions'][de] is None):
                                de_pretty = 'GNOME' if de == 'gnome' else de.capitalize()
                                old = check_output(['gsettings', 'get', schema, key])
                                if theme not in config['old']:
                                    config['old'][theme] = {}
                                    config['old'][theme][de] = old
                                elif de in config['old'][theme] and config['old'][theme][de].startswith('qualia'):
                                    config['old'][theme][de] = old
                                if old != name:
                                    print(f'Changing {config["enableable"][theme]} theme in {de_pretty} to {BOLD}{name}{NC}.')
                                    run_command(['gsettings', 'set', schema, key, name], override_verbose = self.verbose)
                    else:
                        print(f"{BLYELLOW}'gsettings'{BYELLOW} not found, not enabling {theme} theme.{NC}")
                        break

                prop = data[theme]['property']
                if shutil.which('xfconf-query') is not None:
                    name = value['theme_name']
                    channel = data[theme]['channel']
                    if prop is not None and config['desktop_versions']['xfce'] is not None:
                        old = check_output(['xfconf-query', '-c', channel, '-p', prop])
                        if theme not in config['old']:
                            config['old'][theme] = {}
                            config['old'][theme]['xfce'] = old
                        elif 'xfce' in config['old'][theme] and config['old'][theme]['xfce'].startswith('qualia'):
                            config['old'][theme]['xfce'] = old
                        if old != name:
                            print(f'Changing {config["enableable"][theme]} theme in XFCE to {BOLD}{name}{NC}.')
                            run_command(['xfconf-query', '-c', channel, '-p', prop, '-s', name], override_verbose = self.verbose)
                elif prop is not None and config['desktop_versions']['xfce'] is not None:
                    print(f"{BLYELLOW}'xfconf-query'{BYELLOW} not found, not enabling {theme} theme.{NC}")

        return config

if __name__ == "__main__":
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
        '-d', '--install-dir',
        action = 'store_true',
        help = 'change install dir'
    )
    parser.add_argument(
        '-t', '--theme',
        action = 'store_true',
        help = 'change theme variant'
    )
    parser.add_argument(
        '-w', '--window',
        action = 'store_true',
        help = 'change window controls variant'
    )
    parser.add_argument(
        '-s', '--syntax',
        action = 'store_true',
        help = 'change VS Code syntax highlighting'
    )
    parser.add_argument(
        '-F', '--firefox',
        action = 'store_true',
        help = 'change Firefox settings theming'
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
        '-n', '--no-update',
        action = 'store_true',
        help = "don't update the submodules, useful if you made local changes"
    )
    parser.add_argument(
        '-v', '--verbose',
        action = 'store_true',
        help = 'verbose mode'
    )

    args = parser.parse_args()

    update_color = args.accent

    update_dir = args.install_dir

    update_theme = args.theme

    update_window_controls = args.window

    update_syntax = args.syntax

    reconfigure = args.reconfigure

    no_update = args.no_update

    verbose = args.verbose

    force = args.force

    update_settings = args.firefox

    configure_all = False

    if args.clean:
        if os.getuid() != 0:
            args = ['sudo', sys.executable] + sys.argv + [os.environ]
            os.execlpe('sudo', *args)

        for i in (SRC['yaru'], SRC['gtk3']):
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

    main()
