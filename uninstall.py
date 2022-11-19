#!/usr/bin/env python3

import os, sys, shutil, subprocess

from install import BRED, BOLD, VARIANTS, BYELLOW, NC
from paths import installed_paths, CONFIG_FILE, OLD_CONFIG

OLD = [
  'gtk3',
  'gnome-shell',
  'icons',
  'cursors',
  'gtksourceview',
  'sounds',
  'firefox-standard',
  'firefox-snap',
  'firefox-flatpak'
]

HELP = f'''Usage:
  {sys.argv[0]} <theme> ...
  {sys.argv[0]} <option> 

Themes:
  gtk3            gtk4              libadwaita
  gnome-shell     cinnamon-shell    metacity
  marco           ubuntu-unity      xfwm4
  firefox         firefox-standard  firefox-snap
  firefox-flatpak icons             cursors
  sounds          gtksourceview     snap

Options:
  -o, --old       Removes the old version of the theme (dg-gnome-theme).
  -h, --help      Show this screen.

Run '{sys.argv[0]}' followed by any number of the above themes to choose what to uninstall.
Or run '{sys.argv[0]}' with no arguments to uninstall the entire theme.

Run '{sys.argv[0]} firefox' to remove the theme from all firefox variants.
Also, 'metacity' and 'marco' do the same thing, as well as 'gtk4' and 'libadwaita'.'''

def remove_config(name):
  if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
      filedata = f.read()
    for line in filedata.split('\n'):
      if line.startswith("enabled"):
        newline = line.replace(f' {name}', '')
        filedata = filedata.replace(line, newline)
    with open(CONFIG_FILE, 'w') as f:
      f.write(filedata)

def delete(path):
  try:
    os.remove(path)
  except(IsADirectoryError):
    shutil.rmtree(path)
  except(FileNotFoundError):
    pass

pretty = ''
def remove_theme(name, pretty, themes, old = False , disconnect = True):
  shown = False
  if not old:
    message = f'{BRED}Removing{NC} the {BOLD}{pretty} theme{NC}.'
  else:
    message = f'{BRED}Removing{NC} the {BOLD}old {pretty} theme{NC}.'
  # Get root access
  if os.getuid() != 0:
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    os.execlpe('sudo', *args)

  if not disconnect:
    if name == 'snap' and shutil.which('snap') is not None:
      snap_list = subprocess.run(['snap', 'list'], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
      for line in snap_list:
        line = line.split()
        if "dg-adw-gtk3-theme" in line:
          print(message)
          subprocess.run(['snap', 'remove', 'dg-adw-gtk3-theme'])
          return

  paths = installed_paths(themes, old)
  if name != 'snap':
    for i in paths[name]:
      if type(i) == list:
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

  if disconnect:
    if name in ['gtk3', 'icons', 'sounds'] and shutil.which('snap') is not None:
      connections = subprocess.run(['snap', 'connections'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip().split('\n')
      for line in connections:
        line = line.split()
        for key, value in {'gtk3': 'gtk-3', 'icons': 'icon', 'sounds': 'sound'}.items():
          if key == name:
            if line[2] == f'dg-adw-gtk3-theme:{value}-themes':
              subprocess.run(['snap', 'disconnect', line[1], f'dg-adw-gtk3-theme:{value}-themes'])

def remove_old():
  themes = {
    'yaru': ['dg-yaru'],
    'gtk3': ['dg-adw-gtk3'],
    'firefox': ['dg-firefox-theme'],
  }
  for i in OLD:
    remove_theme(i, VARIANTS["enableable"][i], themes, True, False)

themes = {
  'yaru': ['dg-yaru', 'qualia'],
  'gtk3': ['dg-adw-gtk3', 'qualia'],
  'firefox': ['dg-firefox-theme', 'qualia'],
}

for i in sys.argv:
  if i == 'unity':
    i = 'ubuntu-unity'
  if i == 'marco':
    i = 'metacity'
  if i == 'libadwaita':
    i = 'gtk4'
  if i == 'firefox':
    for f in ['firefox-standard', 'firefox-snap', 'firefox-flatpak']:
      remove_theme(f, VARIANTS["enableable"][f], themes)
      remove_config(f) 
  if i != sys.argv[0]:
    if i in ['-h', '--help']:
      print(HELP)
      exit()
    elif i in ['-o', '--old']:
      remove_old()
      exit()
    elif i in VARIANTS["enableable"]:
      remove_theme(i, VARIANTS["enableable"][i], themes)
      remove_config(i)
    else:
      print(f"Unrecognized theme or option '{i}'.")
      exit()

if len(sys.argv) <= 1:
  for i in VARIANTS["enableable"]:
    remove_theme(i, VARIANTS["enableable"][i], themes)
    for i in [CONFIG_FILE, OLD_CONFIG]:
      if os.path.isfile(i):
        os.remove(i)

print(f"{BYELLOW}Log out and log back in for everything to be updated.{NC}")