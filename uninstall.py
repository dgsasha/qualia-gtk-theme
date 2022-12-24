#!/usr/bin/env python3
'''This module is for uninstalling the themes.'''

import os
import sys
import shutil
import subprocess

from install import Config, Enable, VARIANTS
from paths import installed, CONFIG, OLD_CONFIG

NC = '\033[0m'
BOLD = '\033[1m'
BRED = '\033[1;31m'

HELP = f'''Usage:
    {sys.argv[0]} <option> <theme> ...

Themes:
    gtk3            gtk4-libadwaita  gnome-shell
    cinnamon-shell  metacity         ubuntu-unity
    xfwm4           firefox          icons
    cursors         sounds           gtksourceview
    snap            vscode           gtk4-config

Options:
    -v, --verbose      Verbose mode.
    -d, --dry-run      Similar to verbose mode, except nothing is actually deleted.
    -h, --help         Show this screen.

Run '{sys.argv[0]}' followed by any number of the above themes to choose what to uninstall.
Or run '{sys.argv[0]}' with no arguments to uninstall the entire theme.'''

verbose = False
dry_run = False

available_themes = {}
for theme in VARIANTS['enableable']:
    for part in VARIANTS['enableable'][theme]:
        if part not in ('default_syntax', 'settings_theme'):
            available_themes[part] = VARIANTS['enableable'][theme][part]

def remove_config(name, version = False):
    '''
    Removes themes from config file after they are uninstalled.

    Parameters:
    name (str) : The name of the theme or line to remove.
    version (bool) : True if the line that stores the git version for the theme is being removed.
    '''
    if os.path.isfile(CONFIG) and not dry_run:
        with open(CONFIG, 'r', encoding='UTF-8') as f:
            filedata = f.read()
        for line in filedata.split('\n'):
            if version and line.startswith(name):
                filedata = filedata.replace(line + '\n', '')
            elif line.startswith("enabled"):
                newline = line.replace(f' {name}', '')
                if name == 'firefox':
                    newline = newline.replace(f' settings_theme', '')
                elif name == 'vscode':
                    newline = newline.replace(f' default_syntax', '')
                filedata = filedata.replace(line, newline)
        with open(CONFIG, 'w', encoding='UTF-8') as f:
            f.write(filedata)

def delete(path):
    '''
    Deletes a file or directory using rm.

    Parameters:
    path (str) : The path to remove.
    '''
    if verbose:
        print('Deleting ' + path)
    if not dry_run:
        subprocess.run(['sudo', 'rm', '-rf', path], check=True)

def remove_empty():
    '''
    Removes empty theme directories.
    '''
    theme_dirs = installed(just_theme_dirs = True)
    try:
        for i in theme_dirs:
            if isinstance(i, list):
                for folder in i:
                    folders = next(os.walk(folder))[1]
                    files = next(os.walk(folder))[2]
                    if len(folders) == 0:
                        contains_symlink = False
                        for file in files:
                            if os.path.islink(f'{folder}/{file}') and os.path.isdir(os.readlink(f'{folder}/{file}')):
                                contains_symlink = True # Symlinks that point to directories should stay
                                break
                        if not contains_symlink:
                            delete(folder)
    except StopIteration:
        pass

def remove_theme(name, pretty, paths, old = False, disconnect = True, override_verbose = None):
    '''
    Removes a part of the theme.

    Parameters:
    name (str) : The name of the part of the theme.
    pretty (str) : The name of the part of the theme that should be printed.
    paths (dict) : The dictionary returned by the paths.installed function.
    old (bool): Whether or not it should be printed that it is the old theme being removed.
    disconnect (bool): Whether or not the associated snap theme should be disconnected.
    override_verbose (bool) : Override the global verbose value.
    '''
    if override_verbose is not None:
        global verbose
        verbose = override_verbose

    shown = False
    if old:
        message = f'{BRED}Removing{NC} the {BOLD}old '
    else:
        message = f'{BRED}Removing{NC} the {BOLD}'

    if name == 'gtk4-libadwaita':
        message += f'{pretty} GTK4 theme{NC}.'
    elif name == 'gtk4':
        message += f'{pretty} configuration{NC}.'
    else:
        message += f'{pretty} theme{NC}.'

    snap = ('dg-adw-gtk3-theme',) if old else ('qualia-gtk-theme', 'dg-adw-gtk3-theme')

    if not dry_run:
        if name == 'snap' and shutil.which('snap') is not None:
            for i in snap:
                snap_list = subprocess.run(['sudo', 'snap', 'list'], stdout=subprocess.PIPE, check=True).stdout.decode('utf-8').split('\n')
                for line in snap_list:
                    line = line.split()
                    if i in line:
                        print(message)
                        subprocess.run(['sudo', 'snap', 'remove', i], check=True)
                        return

    if name != 'snap':
        if isinstance(paths[name], list):
            for i in paths[name]:
                if isinstance(i, list):
                    for path in i:
                        if name == 'icons' and path in paths['cursors']:
                            pass # Since cursors and icons are in same dir, don't remove cursors unless user wants to
                        else:
                            if not shown:
                                print(message)
                            shown = True
                            delete(path)
                elif os.path.exists(i):
                    if not shown:
                        print(message)
                    shown = True
                    delete(i)

    if disconnect and not dry_run:
        for i in snap:
            if name in ('gtk3', 'icons', 'sounds') and shutil.which('snap') is not None:
                connections = subprocess.run(['sudo', 'snap', 'connections'], stdout=subprocess.PIPE, check=True).stdout.decode('utf-8').strip().split('\n')
                for line in connections:
                    line = line.split()
                    for key, value in {'gtk3': 'gtk-3', 'icons': 'icon', 'sounds': 'sound'}.items():
                        if key == name:
                            if line[2] == f'{i}:{value}-themes':
                                subprocess.run(['sudo', 'snap', 'disconnect', line[1], f'{i}:{value}-themes'], check=True)

def enable_old(config, themes):
    '''
    Re-enable the previously enabled themes

    Parameters:
    config (dict) : The dictionary that stores the configuration.
    themes (list): The list of the themes being uninstalled.
    '''
    kwargs = {}

    for theme in config['old']:
        if theme in themes:
            for de in config['old'][theme]:
                name = config['old'][theme][de]
                try:
                    kwargs[de][theme] = name
                except KeyError:
                    kwargs[de] = {}
                    kwargs[de][theme] = name

    for de, kwargs in kwargs.items():
        enable = Enable(config, verbose, **kwargs)
        enable.enable_theme(de, True)

def main():
    '''The main function.'''
    if os.getuid() == 0:
        print(f"{BRED}Don't run this script as root, exiting.")
        sys.exit()

    uninstalling = []

    global verbose
    global dry_run

    paths = installed()

    for i in sys.argv:
        if i == 'unity':
            i = 'ubuntu-unity'
        if i == 'gtk4-config':
            i = 'gtk4'
        if i != sys.argv[0]:
            if i.startswith('-'):
                if i in ('-h', '--help'):
                    print(HELP)
                    sys.exit()
                elif i in ('-v', '--verbose'):
                    verbose = True
                elif i in ('-d', '--dry-run'):
                    verbose = True
                    dry_run = True
                else:
                    print(f"Unrecognized option '{i}'.")
                    sys.exit()
            else:
                if i in available_themes:
                    uninstalling.append(i)
                else:
                    print(f"Unrecognized theme '{i}'.")
                    sys.exit()

    args = []
    for i in sys.argv:
        if not i.startswith('-'):
            args.append(i)

    if len(args) <= 1:
        uninstalling = available_themes

    # Enable old themes
    if os.path.isfile(CONFIG) and not dry_run:
        conf = Config()

        conf.read()

        config = conf.ret_config()

        if 'enabled' in config:
            enable_old(config, uninstalling)

    # Remove theme
    for i in uninstalling:
        remove_theme(i, available_themes[i], paths)
        remove_config(i)

    # Cleanup config file
    if os.path.isfile(CONFIG) and not dry_run:
        new_conf = Config()
        new_conf.read()
        config = new_conf.ret_config()

        # Remove version of theme from config file if it is fully uninstalled
        if 'enabled' in config and len(config['enabled']) > 0:
            for theme in VARIANTS['enableable']:
                found = False
                for part in config['enabled']:
                    if part in VARIANTS['enableable'][theme]:
                        found = True
                if not found:
                    remove_config(theme, True)
        else:
            os.remove(CONFIG) # Remove config file if nothing is enabled

    remove_empty()
if __name__ == "__main__":
    main()
