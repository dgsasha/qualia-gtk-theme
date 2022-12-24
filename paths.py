'''This module is for getting paths to parts of the theme.'''
from os import path, environ
from glob import glob

SUDO_USER = environ.get('SUDO_USER')
USER = SUDO_USER if SUDO_USER is not None else environ.get('USER')
HOME = path.expanduser(f'~{USER}')
REPO_DIR = path.dirname(path.realpath(__file__))

GTK4_DIR = f'{HOME}/.config/gtk-4.0'
SRC = f'{REPO_DIR}/src'
CONFIG = f'{REPO_DIR}/config.txt'
OLD_CONFIG = f'{SRC}/installed-versions.txt'

SRC = {
    'gtk3': f'{SRC}/dg-adw-gtk3',
    'gtk4': f'{SRC}/dg-libadwaita',
    'yaru': f'{SRC}/dg-yaru',
    'firefox': f'{SRC}/dg-firefox-theme',
    'vscode': f'{SRC}/dg-vscode-adwaita',
}

FIREFOX_DIR = {
    'standard': f'{HOME}/.mozilla/firefox',
    'flatpak': f'{HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox',
    'snap': f'{HOME}/snap/firefox/common/.mozilla/firefox',
}

OLD_NAMES = {
    'dg-yaru': ['dg-yaru'],
    'dg-adw-gtk3': ['dg-adw-gtk3'],
    'dg-firefox-theme': ['dg-firefox-theme'],
}

CURRENT_NAMES = {
    'dg-yaru': ['qualia'],
    'dg-adw-gtk3': ['qualia'],
    'dg-firefox-theme': ['qualia'],
}

VSCODE_DIR = {
    'standard': f'{HOME}/.vscode/extensions',
    'flatpak': f'{HOME}/.var/app/com.visualstudio.code/data/vscode/extensions',
}

def installed(old_only = False, new_only = False, just_theme_dirs = False, directory = None):
    '''
    Return paths of installed themes.

    Parameters:
    old_only (bool) : True if we only care about dg-gnome-theme.
    new_only (bool) : True if we only care about the current theme.
    just_theme_dirs (bool) : Just return the path to the theme dirs, not all of the paths.
    directory (string) : Either 'root', 'home', or 'not_default'. Used for uninstalling from specific directories. Defaults to None.

    Returns:
        paths (dict) : Returns a dictionary with all of the paths if just_theme_dirs is false.
        paths['theme_dirs'] (list) : Returns a list with the paths to the theme dirs if just_theme_dirs is true.
    '''

    if directory == 'root':
        dg_yaru_prefixes = ('/usr/share',)
        dg_adw_gtk3_prefixes = dg_yaru_prefixes
    elif directory == 'home':
        dg_yaru_prefixes = (f'{HOME}/.local/share',)
        dg_adw_gtk3_prefixes = dg_yaru_prefixes
    elif directory == 'not_default':
        dg_yaru_prefixes = (f'{HOME}/.local/share',)
        dg_adw_gtk3_prefixes = ('/usr/share')
    else:
        dg_yaru_prefixes = ('/usr/share', f'{HOME}/.local/share')
        dg_adw_gtk3_prefixes = dg_yaru_prefixes

    names = {}

    for i in ('dg-yaru', 'dg-adw-gtk3', 'dg-firefox-theme'):
        if old_only:
            names[i] = (i,)
        elif new_only:
            names[i] = ('qualia',)
        else:
            names[i] = ('qualia', i)

    paths = { # These have to be lists even if they only have one value
        'gtk3': [],
        'gtk4': [],
        'gtk4-libadwaita': [],
        'gnome-shell': [],
        'cinnamon-shell': [],
        'metacity': [],
        'ubuntu-unity': [],
        'xfwm4': [],
        'firefox': [],
        'icons': [],
        'cursors': [],
        'sounds': [],
        'gtksourceview': [],
        'vscode': [],
        'theme_dirs': []
    }

    for name in names['dg-yaru']:
        for prefix in dg_yaru_prefixes:
            for directory in ('themes', 'icons', 'sounds', 'gnome-shell/theme'):
                paths['theme_dirs'] += [glob(f'{prefix}/{directory}/{name}*')]
            if just_theme_dirs:
                continue
            paths['gnome-shell'] += [glob(f'{prefix}/themes/{name}*/gnome-shell'), glob(f'{prefix}/gnome-shell/theme/{name}*')]
            paths['metacity'] += [glob(f'{prefix}/themes/{name}*/metacity')]
            paths['cinnamon-shell'] += [glob(f'{prefix}/themes/{name}*/cinnamon')]
            paths['ubuntu-unity'] += [glob(f'{prefix}/themes/{name}*/unity')]
            paths['xfwm4'] += [glob(f'{prefix}/themes/{name}*/xfwm4')]
            paths['icons'] += [glob(f'{prefix}/icons/{name}*/*')]
            paths['cursors'] += [f'{prefix}/icons/{name}/cursor.theme', f'{prefix}/icons/{name}/cursors']
            paths['sounds'] += [f'{prefix}/sounds/{name}']
            for i in ('gtksourceview-5', 'gtksourceview-4', 'gtksourceview-3.0', 'gtksourceview-2.0'):
                paths['gtksourceview'] += [glob(f'{prefix}/{i}/styles/{name}*')]

    for name in names['dg-adw-gtk3']:
        for prefix in dg_adw_gtk3_prefixes:
            paths['theme_dirs'] += [glob(f'{prefix}/themes/{name}*')]
            if just_theme_dirs:
                continue
            paths['gtk3'] += [
                glob(f'{prefix}/themes/{name}*/gtk-3.0'),
                glob(f'{prefix}/themes/{name}*/gtk-2.0')
            ]

    if not just_theme_dirs:
        if directory is None:
            for firefox_path in FIREFOX_DIR.values():
                for name in names['dg-firefox-theme']:
                    paths['firefox'] += [glob(firefox_path + f'/*/chrome/{name}')]
                if not old_only:
                    paths['firefox'] += [glob(firefox_path + '/*/user.js'), glob(firefox_path + '/*/chrome/userChrome.css'), glob(firefox_path + '/*/userContent.css')]

        if not old_only:
            if directory is None:
                paths['gtk4'] += [f'{GTK4_DIR}/mac-icons']
                paths['gtk4'] += [f'{GTK4_DIR}/gtk.css']
                for extensions_path in VSCODE_DIR.values():
                    paths['vscode'] += [f'{extensions_path}/qualia']
            for prefix in dg_adw_gtk3_prefixes:
                paths['gtk4-libadwaita'] += [glob(f'{prefix}/themes/qualia*/gtk-4.0')]

        return paths
    return paths['theme_dirs']
