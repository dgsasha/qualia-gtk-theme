'''This module is for getting paths of parts of the theme.'''
from os import path, environ
from glob import glob

SUDO_USER = environ.get('SUDO_USER')
USER = SUDO_USER if SUDO_USER is not None else environ.get('USER')
HOME = path.expanduser(f'~{USER}')
REPO_DIR = path.dirname(path.realpath(__file__))

GTK4_DIR = f'{HOME}/.config/gtk-4.0'
SRC_DIR = f'{REPO_DIR}/src'
CONFIG_FILE = f'{REPO_DIR}/config.txt'
OLD_CONFIG = f'{SRC_DIR}/installed-versions.txt'

SRC = {
    'gtk3': f'{SRC_DIR}/dg-adw-gtk3',
    'gtk4': f'{SRC_DIR}/dg-libadwaita',
    'yaru': f'{SRC_DIR}/dg-yaru',
    'firefox': f'{SRC_DIR}/dg-firefox-theme',
    'vscode': f'{SRC_DIR}/dg-vscode-adwaita',
}

FIREFOX_DIR = {
    'standard': f'{HOME}/.mozilla/firefox',
    'flatpak': f'{HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox',
    'snap': f'{HOME}/snap/firefox/common/.mozilla/firefox',
}

def installed_paths(themes, old_only = False):
    '''
    Return paths of installed themes.

    Parameters:
    themes (dict) : The possible names of the directories of the themes. theme: [name1, name2]
    old_only (bool) : True if we only care about dg-gnome-theme.
    '''
    paths = {
        'gtk3': [],
        'gtk4': [],
        'gtk4-libadwaita': [],
        'gnome-shell': [],
        'cinnamon-shell': [],
        'metacity': [],
        'ubuntu-unity': [],
        'xfwm4': [],
        'firefox-standard': [],
        'firefox-snap': [],
        'firefox-flatpak': [],
        'icons': [],
        'cursors': [],
        'sounds': [],
        'gtksourceview': [],
        'vscode': [],
        'themes': [],
    }

    for name in themes['dg-yaru']:
        paths['gnome-shell'] += [glob(f'/usr/share/themes/{name}*/gnome-shell'), glob(f'/usr/share/gnome-shell/theme/{name}*')]
        paths['metacity'] += [glob(f'/usr/share/themes/{name}*/metacity')]
        paths['cinnamon-shell'] += [glob(f'/usr/share/themes/{name}*/cinnamon')]
        paths['ubuntu-unity'] += [glob(f'/usr/share/themes/{name}*/unity')]
        paths['xfwm4'] += [glob(f'/usr/share/themes/{name}*/xfwm4')]
        paths['icons'] += [glob(f'/usr/share/icons/{name}*/*')]
        paths['cursors'] += [f'/usr/share/icons/{name}/cursor.theme', f'/usr/share/icons/{name}/cursors']
        paths['sounds'] += [f'/usr/share/sounds/{name}']
        for i in ['gtksourceview-5', 'gtksourceview-4', 'gtksourceview-3.0', 'gtksourceview-2.0']:
            paths['gtksourceview']+=[glob(f'/usr/share/{i}/styles/{name}*')]
        paths['themes'] += [glob(f'/usr/share/themes/{name}*')]

    for name in themes['dg-adw-gtk3']:
        paths['gtk3'] += [glob(f'{HOME}/.local/share/themes/{name}*/gtk-3.0'), glob(f'/usr/share/themes/{name}*')]
        paths['themes'] += [glob(f'{HOME}/.local/share/themes/{name}*')]

    for key, value in FIREFOX_DIR.items():
        for name in themes['dg-firefox-theme']:
            paths['firefox-' + key] += [glob(value + f'/*/chrome/{name}')]
        if not old_only:
            paths['firefox-' + key] += [glob(value + '/*/user.js'), glob(value + '/*/chrome/userChrome.css'), glob(value + '/*/userContent.css')]
    if not old_only:
        paths['gtk4'] += [f'{GTK4_DIR}/mac-icons']
        paths['gtk4'] += [f'{GTK4_DIR}/gtk.css']
        paths['gtk4-libadwaita'] += [glob(f'{HOME}/.local/share/themes/qualia*/gtk-4.0'), glob('/usr/share/themes/qualia*/gtk-4.0')]
        paths['vscode'] += [f'{HOME}/.vscode/extensions/qualia']

    return paths
