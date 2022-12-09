#!/usr/bin/env python3
'''This module is for uninstalling the themes.'''

import os
import sys
import shutil
import subprocess

from install import BRED, BOLD, VARIANTS, NC, Config, Enable
from paths import installed_paths, CONFIG_FILE, OLD_CONFIG, HOME

CODE_CONFIG_DIR = f'{HOME}/.config/Code/User'
CODE_CONFIG = f'{CODE_CONFIG_DIR}/settings.json'

OLD = [
    'gtk3',
    'gnome-shell',
    'icons',
    'cursors',
    'gtksourceview',
    'sounds',
    'firefox-standard',
    'firefox-snap',
    'firefox-flatpak',
    'snap'
]

OLD_NAMES = {
    'dg-yaru': ['dg-yaru'],
    'dg-adw-gtk3': ['dg-adw-gtk3'],
    'dg-firefox-theme': ['dg-firefox-theme'],
}

HELP = f'''Usage:
    {sys.argv[0]} <option> <theme> ...

Themes:
    gtk3            gtk4-libadwaita  gnome-shell
    cinnamon-shell  metacity         ubuntu-unity
    xfwm4           firefox          firefox-standard
    firefox-snap    firefox-flatpak  icons
    cursors         sounds           gtksourceview
    snap            vscode           gtk4-config

Options:
    -o, --old       Removes the old version of the theme (dg-gnome-theme).
    -v, --verbose   Verbose mode.
    -d, --dry-run   Similar to verbose mode, except nothing is actually deleted.
    -h, --help      Show this screen.

Run '{sys.argv[0]}' followed by any number of the above themes to choose what to uninstall.
Or run '{sys.argv[0]}' with no arguments to uninstall the entire theme.

Run '{sys.argv[0]} firefox' to remove the theme from all Firefox variants.'''

snap = ['qualia-gtk-theme', 'dg-adw-gtk3-theme']

verbose = False
dry_run = False

def remove_config(name, version = False):
    '''
    Removes themes from config file after they are uninstalled.

    Parameters:
    name (str) : The name of the theme or line to remove.
    version (bool) : True if the line that stores the git version for the theme is being removed.
    '''
    if os.path.isfile(CONFIG_FILE) and not dry_run:
        with open(CONFIG_FILE, 'r', encoding='UTF-8') as f:
            filedata = f.read()
        for line in filedata.split('\n'):
            if version and line.startswith(name):
                filedata = filedata.replace(line + '\n', '')
            elif line.startswith("enabled"):
                newline = line.replace(f' {name}', '')
                filedata = filedata.replace(line, newline)
        with open(CONFIG_FILE, 'w', encoding='UTF-8') as f:
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
            subprocess.run('sudo', 'rm', '-rf', path, check=True)

def remove_empty(themes):
    '''
    Removes empty theme directories.

    Parameters:
    themes (dict) : The possible names of the directories of the themes. theme: [name1, name2]
    '''
    paths = installed_paths(themes)
    for i in paths['themes']:
        if isinstance(i, list):
            for folder in i:
                if len(next(os.walk(folder))[1]) == 0:
                    delete(folder)
        elif os.path.isdir(i):
            if len(next(os.walk(i))[1]) == 0:
                delete(i)

def remove_theme(name, pretty, themes, old = False , disconnect = True):
    '''
    Removes a part of the theme.

    Parameters:
    name (str) : The name of the part of the theme.
    pretty (str) : The name of the part of the theme that should be printed.
    themes (dict) : The possible names of the directories of the theme. theme: [name1, name2]
    old (bool): Whether or not it should be printed that it is the old theme being removed.
    disconnect (bool): Whether or not the associated snap theme should be disconnected.
    '''
    shown = False
    if not old:
        message = f'{BRED}Removing{NC} the {BOLD}'
    else:
        message = f'{BRED}Removing{NC} the {BOLD}old '

    if name == 'gtk4-libadwaita':
        message += f'{pretty} GTK4 theme{NC}.'
    elif name == 'gtk4':
        message += f'{pretty} configuration{NC}.'
    else:
        message += f'{pretty} theme{NC}.'

    if not disconnect and not dry_run:
        if name == 'snap' and shutil.which('snap') is not None:
            for i in snap:
                snap_list = subprocess.run(['sudo', 'snap', 'list'], stdout=subprocess.PIPE, check=True).stdout.decode('utf-8').split('\n')
                for line in snap_list:
                    line = line.split()
                    if i in line:
                        print(message)
                        subprocess.run(['sudo', 'snap', 'remove', i], check=True)
                        return

    paths = installed_paths(themes, old)
    if name != 'snap':
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
            if name in ['gtk3', 'icons', 'sounds'] and shutil.which('snap') is not None:
                connections = subprocess.run(['sudo', 'snap', 'connections'], stdout=subprocess.PIPE, check=True).stdout.decode('utf-8').strip().split('\n')
                for line in connections:
                    line = line.split()
                    for key, value in {'gtk3': 'gtk-3', 'icons': 'icon', 'sounds': 'sound'}.items():
                        if key == name:
                            if line[2] == f'{i}:{value}-themes':
                                subprocess.run(['sudo', 'snap', 'disconnect', line[1], f'{i}:{value}-themes'], check=True)

def remove_old():
    '''Removes all of the parts of dg-gnome-theme (the old theme).'''
    for i in OLD:
        remove_theme(i, VARIANTS["enableable"][i], OLD_NAMES, True, False)


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

    themes = {
        'dg-yaru': ['dg-yaru', 'qualia'],
        'dg-adw-gtk3': ['dg-adw-gtk3', 'qualia'],
        'dg-firefox-theme': ['dg-firefox-theme', 'qualia'],
    }

    available_themes = {}
    for i in VARIANTS["enableable"]:
        for theme in VARIANTS["enableable"][i]:
            if theme != 'default_syntax':
                available_themes[theme] = VARIANTS["enableable"][i][theme]

    uninstalling = []

    global verbose
    global dry_run

    for i in sys.argv:
        if i == 'unity':
            i = 'ubuntu-unity'
        if i == 'gtk4-config':
            i = 'gtk4'
        if i == 'firefox':
            for f in VARIANTS["enableable"]['dg-firefox-theme']:
                uninstalling.append(f)
                remove_theme(f, VARIANTS["enableable"]['dg-firefox-theme'][f], themes)
                remove_config(f)
        if i != sys.argv[0]:
            if i.startswith('-'):
                if i in ['-h', '--help']:
                    print(HELP)
                    sys.exit()
                elif i in ['-v', '--verbose']:
                    verbose = True
                elif i in ['-d', '--dry-run']:
                    verbose = True
                    dry_run = True
                elif i in ['-o', '--old']:
                    global snap
                    snap = ['dg-adw-gtk3-theme']
                    remove_old()
                else:
                    print(f"Unrecognized option '{i}'.")
                    sys.exit()
            else:
                if i in available_themes:
                    uninstalling.append(i)
                    remove_theme(i, available_themes[i], themes)
                    remove_config(i)
                else:
                    print(f"Unrecognized theme '{i}'.")
                    sys.exit()
    args = []
    for i in sys.argv:
        if not i.startswith('-'):
            args.append(i)

    if len(args) <= 1:
        uninstalling = available_themes
        for key, value in available_themes.items():
            remove_theme(key, value, themes)
            for key in [CONFIG_FILE, OLD_CONFIG]:
                if os.path.isfile(key) and not dry_run:
                    os.remove(key)

    remove_empty(themes)

    if os.path.isfile(CONFIG_FILE) and not dry_run:
        conf = Config()

        conf.read()

        config = conf.ret_config()

        # Remove version of theme from config file if it is fully uninstalled
        for theme in VARIANTS['enableable']:
            found = False
            for part in config['enabled']:
                if part in VARIANTS['enableable'][theme]:
                    found = True
            if not found:
                remove_config(theme, True)

        enable_old(config, uninstalling)

if __name__ == "__main__":
    main()
