#!/usr/bin/env python3

import os, sys, argparse, subprocess, shutil, socket, time, threading
from re import sub
from urllib.request import urlopen

from paths import HOME, REPO_DIR, CONFIG_FILE, OLD_CONFIG, SRC, FIREFOX_DIR, installed_paths

NC = '\033[0m'
BOLD = '\033[1m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
BRED = '\033[1;31m'
BGREEN = '\033[1;32m'
BYELLOW = '\033[1;33m'
BLRED = '\033[1;91m'
BLYELLOW = '\033[1;93m'
BLBLUE = '\033[1;94m'
BLCYAN = '\033[1;96m'

VERSIONS = {
  'gnome-shell': (42, 43),
  'cinnamon-shell': (4, 5),
  'ubuntu-unity': (7,),
  'xfce': (4,),
  'mate': (1,),
  'budgie': (10.6,),
}

DG_YARU_PARTS = (
  'gnome-shell',
  'cinnamon-shell',
  'metacity',
  'ubuntu-unity',
  'xfwm4',
  'icons',
  'cursors',
  'gtksourceview',
  'sounds',
)

VARIANTS = { # all of the possible configurations, name: pretty-name
  'colors': {
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
    'red': 'Red',
  },
  'themes': {
    'light': 'Light',
    'dark': 'Dark',
    'auto': 'Auto',
  },
  'enableable': {
    'gtk3': 'GTK3',
    'gtk4': 'GTK4',
    'gnome-shell': 'GNOME Shell',
    'cinnamon-shell': 'Cinnamon Shell',
    'metacity': 'Marco (Metacity)',
    'ubuntu-unity': 'Unity',
    'xfwm4': 'Xfwm4',
    'firefox-standard': 'Standard Firefox',
    'firefox-snap': 'Snap Firefox',
    'firefox-flatpak': 'Flatpak Firefox',
    'icons': 'Icon',
    'cursors': 'Cursor',
    'sounds': 'Sound',
    'gtksourceview': 'GtkSourceView',
    'snap': 'Snap',
  },
}

config = {}

if __name__ == "__main__":
  ##############################
  ##   Command Line Options   ##
  ##############################

  reconfigure = False
  verbose = False
  clean = False
  update_color = False
  update_theme = False

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
    '-a', '--accent',
    action = 'store_true',
    help = 'change accent color'
  )
  parser.add_argument(
    '-v', '--verbose',
    action = 'store_true',
    help = 'display entire output'
  )

  args = parser.parse_args()

  reconfigure = args.reconfigure
  verbose = args.verbose
  clean = args.clean
  update_color = args.accent
  update_theme = args.theme

  if clean:
    if os.getuid() != 0:
      args = ['sudo', sys.executable] + sys.argv + [os.environ]
      os.execlpe('sudo', *args)

    for i in [SRC['yaru'], SRC['gtk3']]:
      try:
        shutil.rmtree(f'{i}/build')
      except(NotADirectoryError):
        os.remove(f'{i}/build')
      except(FileNotFoundError):
        pass
    exit()

  if not clean and os.getuid() == 0:
    print(f"{BRED}Don't run this script as root, exiting.")
    exit()

  #######################################
  ##   Check what user has installed   ##
  #######################################

  if shutil.which('sassc') is None:
    print(f"{BLRED}'sassc'{BRED} not found, exiting.{NC}")
    exit()

  if shutil.which('git') is None:
    print(f"{BLRED}'git'{BRED} not found, exiting.{NC}")
    exit()

  config['enableable'] = VARIANTS["enableable"].copy()

  def check_de(command, regex, name, delete, fp = False):
    try:
      ver = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')
      ver = sub(regex, '', ver)

      if fp and float(ver) in VERSIONS[name]:
        version = float(ver)
      elif int(ver) in VERSIONS[name]:
        version = int(ver)
      else:
        if delete != None:
          del config['enableable'][delete]
        version = None
    except(FileNotFoundError):
      if delete != None:
        del config['enableable'][delete]
      version = None

    return version

  config['gnome-shell'] = check_de(['gnome-shell', '--version'], r'\.[0-9]?\n?$|\D', 'gnome-shell', 'gnome-shell')

  config['cinnamon-shell'] = check_de(['cinnamon', '--version'], r'\.[0-9]\.?[0-9]?[0-9]?\n?$|^Cinnamon ', 'cinnamon-shell', 'cinnamon-shell')

  config['ubuntu-unity'] = check_de(['unity', '--version'], r'\.[0-9]\.[0-9]?\n?$|\D', 'ubuntu-unity', 'ubuntu-unity')

  config['mate'] = check_de(['mate-session', '--version'], r'\.[0-9][0-9]?\.[0-9][0-9]?\n?$|^mate-session ', 'mate', 'metacity')

  config['budgie'] = check_de(['budgie-desktop', '--version'], r'Copyright.*\n|\.[0-9]\n|^budgie-desktop', 'budgie', None, True)

  if shutil.which('xfce4-session') is not None:
    config['xfce'] = VERSIONS['xfce'][0]
  else:
    config['xfce'] = None
    del config['enableable']['xfwm4']

  if not os.path.isdir(FIREFOX_DIR['standard']):
    del config['enableable']['firefox-standard']

  if not os.path.isdir(FIREFOX_DIR['snap']):
    del config['enableable']['firefox-snap']

  if not os.path.isdir(FIREFOX_DIR['flatpak']):
    del config['enableable']['firefox-flatpak']

  if shutil.which('snap') is None:
    del config['enableable']['snap']

  #########################
  ##    Configuration    ##
  #########################

  configured = False

  config['color'] = VARIANTS['colors']
  config['theme'] = VARIANTS['themes']
  config['enabled'] = config['enableable']

  def theme_variants(config):
    global color_scheme
    if config == 'auto':
      try:
        theme_setting = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        theme_setting = theme_setting.strip('\'\n')
      except(FileNotFoundError):
        theme_setting=None
      if theme_setting == 'prefer-dark':
        color_scheme='prefer-dark'
      elif theme_setting == 'default':
        color_scheme='default'
      else:
        print(f"{BRED}Can't detect system light/dark theme preference.{NC}")
        return False # Failure
    elif config == 'light':
      color_scheme='default'
    elif config == 'dark':
      color_scheme='prefer-dark'
    return True # Success

  def config_menu(message, dictionary, default):
    print (f'{BLBLUE}Which {NC}{BLCYAN}{message}{NC}{BLBLUE} do you want?{NC}')

    for i in range(len(dictionary)):
      array = list(dictionary.keys())
      name = array[i]
      pretty_name = list(dictionary.values())[i]
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
      if dictionary == VARIANTS['themes'] and not theme_variants(ret): # If auto and cant detect theme
        continue
      break

    return ret

  def config_yn(name, pretty):
    while True:
      if name == 'snap' and shutil.which('snap') is None:
        break
      val = input(f'{BLBLUE}Do you want to install the {NC}{BLCYAN}{pretty}{NC}{BLBLUE} theme?{NC}{BOLD} [Y/n]: {NC}')
      if val.casefold() == 'y'.casefold() or val == '':
        if name in DG_YARU_PARTS or name == 'gtk3':
          if shutil.which('meson') is None:
            print(f"{BLRED}'meson'{BRED} not found, can't install {pretty} theme.{NC}")
            continue
          if shutil.which('ninja') is None:
            print(f"{BLRED}'ninja'{BRED} not found, can't install {pretty} theme.{NC}")
            continue
        config['enabled'][name] = pretty
        break
      elif val.casefold() == 'n'.casefold():
        break

  def configure(just_color = False, just_theme = False):
    global configured

    if not just_theme:
      config['color'] = config_menu('accent color', VARIANTS['colors'], 1)

    if not just_color:
      config['theme'] = config_menu('theme variant', VARIANTS['themes'], 1)

    if not just_color and not just_theme:
      config['enabled'] = {}
      for key, value in config['enableable'].items():
        config_yn(key, value)
      
    print()
    configured = True

  # Move old config file
  if os.path.isfile(OLD_CONFIG) and not os.path.isfile(CONFIG_FILE):
    shutil.move(OLD_CONFIG, CONFIG_FILE)

  # Whether or not to configure
  if not os.path.isfile(CONFIG_FILE) or reconfigure:
    configure()
    if os.path.isfile(CONFIG_FILE):
      os.remove(CONFIG_FILE)

  ##########################
  ##   Read Config File   ##
  ##########################

  config['version'] = ''
  enabled = []

  try:
    for line in open(CONFIG_FILE).readlines():
      line = line.strip().split(': ')
      if len(line) > 1 and ' ' in line[1]:
        line[1] = line[1].split(' ')
      else:
        line.append(None)
      if line[0] == 'firefox' or line[0] == 'enabled': # old config file was a little different
        prefix = 'firefox-' if line[0] == 'firefox' else ''
        if type(line[1]) == list:
          for i in line[1]:
            enabled.append(prefix + i)
        elif type(line[1]) == str:
          enabled.append(prefix + line[1])
      elif type(line[1]) == str:
        try:
          if line[0] in config and line[1] in config[line[0]]:
            config[line[0]] = line[1]
          elif line[0] == 'version':
            config[line[0]] = line[1]
        except(TypeError):
          pass
  except(FileNotFoundError):
    pass

  for i in list(config['enabled']):
    if i not in enabled and not configured:
      config['enabled'].pop(i)

  # Reconfigure if something went wrong
  if ( type(config['color']) != str or type(config['theme']) != str ) or not theme_variants(config['theme']):
    configure()

  # Reconfigure color or theme variant if user wants to
  if not reconfigure:
    if update_color:
      configure(just_color=True)
    if update_theme:
      configure(just_theme=True)

  ##############################
  ##   Write to Config File   ##
  ##############################

  if os.path.isfile(CONFIG_FILE):
    os.remove(CONFIG_FILE)
  elif os.path.isdir(CONFIG_FILE):
    shutil.rmtree(CONFIG_FILE)

  f = open(CONFIG_FILE, 'x')
  f.write("This file is generated and used by the install script.\n")
  f.write('color: ' + config['color'] + '\n')
  f.write('theme: ' + config['theme'] + '\n')
  f.write('enabled: ' + ' '.join(map(str, config['enabled'].keys())) + '\n')
  f.close()

  ###################
  #  Install Theme  #
  ###################

  if not configured:
    print(f'{BYELLOW}Updating themes using previous configuration.{NC}')
    print(f"{BYELLOW}Use {BLYELLOW}'{sys.argv[0]} --reconfigure'{BYELLOW} if you want to change anything.{NC}")

  suffix='-dark' if color_scheme == 'prefer-dark' else ''
  libadwaita_theme='dark' if color_scheme == 'prefer-dark' else 'light'

  theme_name = {}
  for i in ['yaru', 'gtk3', 'firefox']:
    theme_name[i]=['qualia']

  paths = installed_paths(theme_name)

  config['new_version'] = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

  if config['new_version'] != config['version']:
    updated = True
  else:
    updated = False
  
  def cd(dir):
    if verbose:
      print(f"Changing directory to {dir}")
    os.chdir(dir)

  def run_command(command, meson = False, override_verbose = False):
    if verbose:
      print('Running ' + ' '.join(command))
    try:
      subprocess.run(command, capture_output = False if verbose or override_verbose else True).check_returncode()
    except subprocess.CalledProcessError as error:
      if not verbose:
        print('\n' + error.output.decode("utf-8"))
        print(f"{BRED}Something went wrong, run {BLRED}'{sys.argv[0]} --verbose'{BRED} for more info.{NC}")
      else:
        print(f'{BRED}Something went wrong. Check the log above.{NC}')
      if meson:
        print(f"{BRED}Also, running {BLRED}'{sys.argv[0]} --clean'{BRED} might fix the issue.{NC}")
      os._exit(1)

  def install_dg_adw_gtk3():
    cd(REPO_DIR)
    run_command(['git', 'submodule', 'update', '--init', 'src/dg-adw-gtk3'])
    cd(SRC['gtk3'])
    if not os.path.isdir('build'):
      run_command(['meson', f'-Dprefix={HOME}/.local', 'build'], True)
    run_command(['ninja', '-C', 'build', 'install'], True)

  def install_dg_yaru():
    cd(REPO_DIR)
    if 'ubuntu-unity' in config['enabled'] or 'mate' in config['enabled']:
      panel_icons=True
    else:
      panel_icons=False

    options = []

    for p in config['dg_yaru_parts'].keys():
      options.append('-D' + p + '=true')

    for i in DG_YARU_PARTS:
      if i not in config['dg_yaru_parts'].keys():
        options.append('-D' + i + '=false')

    if panel_icons:
      options.append('-Dpanel-icons=true')
    else:
      options.append('-Dpanel-icons=false')

    if config['gnome-shell'] is not None:
      options.append('-Dgnome-shell-version=' + str(config['gnome-shell']))

    run_command(['git', 'submodule', 'update', '--init', 'src/dg-yaru'])
    cd(SRC['yaru'])

    if not os.path.isdir('build'):
      run_command(['meson', 'build'] + options, True)
    else:
      run_command(['meson', 'configure', 'build'] + options, True)
    run_command(['ninja', '-C', 'build', 'install'], True)

  def install_dg_libadwaita():
    cd(REPO_DIR)
    run_command(['git', 'submodule', 'update', '--init', 'src/dg-libadwaita'])
    if verbose:
      print(f"Changing dir to {SRC['gtk4']}")
    cd(SRC['gtk4'])
    run_command(['./install.sh', '-c', config['color'], '-t', libadwaita_theme], override_verbose = True)

  def install_dg_firefox_theme(directory):
    cd(REPO_DIR)
    run_command(['git', 'submodule', 'update', '--init', 'src/dg-firefox-theme'])
    cd(SRC['firefox'])
    run_command(['./install.sh', '-c', config['color'], '-f', directory], override_verbose = True)

  def install_snap():
    snap_list = subprocess.run(['snap', 'list'], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
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

    connections = subprocess.run(['snap', 'connections'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip().split('\n')
    for line in connections:
      line = line.split()
      for key, value in {'gtk3': 'gtk-3', 'icons': 'icon', 'sounds': 'sound'}.items():
        if key in config["enabled"]:
          if line[2] == f'gtk-common-themes:{value}-themes':
            run_command(['sudo', 'snap', 'connect', line[1], f'qualia-gtk-theme:{value}-themes'])
        else:
          if line[2] == f'qualia-gtk-theme:{value}-themes':
            run_command(['sudo', 'snap', 'disconnect', line[1], f'qualia-gtk-theme:{value}-themes'])

  def install_msg(theme, directory, process):
    message = f'{BGREEN}Installing{NC} the {BOLD}{theme}{NC} in {BOLD}{directory}{NC}'
    message_len = len(f'Installing the {theme} in {directory}') # without the color escape codes
    if verbose:
      print(message)
    else:
      while process.is_alive():
        for cursor in '|/-\\':
          columns = int(os.popen('stty size', 'r').read().split()[1])
          sys.stdout.write(f'\r\033[?25l' + message + f'\033[J\033[{columns - 1}G' + cursor + '\n')
          sys.stdout.write(f'\033[{message_len // (columns - 1) + 1}A')
          sys.stdout.flush()
          time.sleep(0.1)
      sys.stdout.write('\r' + message + '\033[J\n\033[?25h')
      sys.stdout.flush()

  def check_path(name, dict = paths, ret = False):
    exists = False
    for i in dict[name]:
      if type(i) == list:
        for path in i:
          if name == 'icons' and path in dict['cursors']:
            pass
          else:
            exists = os.path.exists(path)
      else:
        if name == 'icons' and i in dict['cursors']:
          pass
        else:
          exists = os.path.exists(i)
    if ret:
      return exists
    elif exists:
      print(f"The {VARIANTS['enableable'][name]} theme was installed previously, use './uninstall.py {name}' to remove it.")

  # Install dg-adw-gtk3
  if 'gtk3' in config['enabled']:
    if ( not update_theme and not update_color ) or updated:
      gtk3 = threading.Thread(target=install_dg_adw_gtk3)
      gtk3.start()
      install_msg('qualia GTK3 theme', f'{HOME}/.local/share', gtk3)
      gtk3.join()
  else:
    check_path('gtk3')

  # Symlink to /usr dir if using mate
  targets = []
  if config['mate'] != None:
    for path in paths['gtk3']:
      if type(path) == list:
        for i in path:
          targets.append(i)
      else:
        targets.append(path)
    for target in targets:
      if target.startswith(f'{HOME}/.local'):
        dest = f'/usr' + target.split(f'{HOME}/.local')[1]
        run_command(['sudo', 'mkdir', '-p', dest])
        for i in ['gtk-3.0', 'index.theme']:
          if not os.path.exists(f'{dest}/{i}'):
            run_command(['sudo', 'ln', '-sf', f'{target}/{i}', f'{dest}/{i}'])

  # Install dg-yaru
  config['dg_yaru_parts'] = {}

  for i in DG_YARU_PARTS:
    for e in config['enabled']:
      if i == e:
        config['dg_yaru_parts'][i] = ''.join([config['enabled'][e]])

  pretty_string = 'qualia '
  for i in range(len(config['dg_yaru_parts'])):
    if i == len(config['dg_yaru_parts']) - 1:
      sep = ', and '
    elif i == 0:
      sep = ''
    else:
      sep = ', '
    pretty_string += sep + list(config['dg_yaru_parts'].values())[i]
  if len(config['dg_yaru_parts']) > 1:
    pretty_string += ' themes'
  else:
    pretty_string += ' theme'

  if len(config['dg_yaru_parts']) > 0:
    if ( not update_theme and not update_color ) or updated:
      yaru = threading.Thread(target=install_dg_yaru)
      yaru.start()
      install_msg(pretty_string, '/usr/share', yaru)
      yaru.join()
  for i in DG_YARU_PARTS:
    if i not in config['dg_yaru_parts'].keys():
      check_path(i)

  # Install dg-libadwaita
  if 'gtk4' in config['enabled'] :
    install_dg_libadwaita()
  else:
    check_path('gtk4')

  # Install dg-firefox-theme
  for key, value in FIREFOX_DIR.items():
    if f'firefox-{key}' in config['enabled']:
      if not update_theme or update_color or updated:
        install_dg_firefox_theme(value)
    else:
      check_path(f'firefox-{key}')

  # Install snap theme
  if 'snap' in config['enabled']:
    try:
      # Check that there is an internet connection
      urlopen('https://www.google.com/', timeout=3)
      install_snap()
    except:
      pass
  elif shutil.which('snap'):
    snap_list = subprocess.run(['snap', 'list'], stderr=subprocess.DEVNULL, stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
    for line in snap_list:
      line = line.split()
      if 'qualia-gtk-theme' in line:
        print("Snap theme was installed previously, use './uninstall.py snap' to remove it.")

  #####################
  #   Enable Themes   #
  #####################

  cd(REPO_DIR)

  def check_output(command):
    ret = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\'\n')
    return ret

  # Theme naming
  if config['color'] == 'orange':
    qualia = f'qualia{suffix}'
  else:
    qualia = f"qualia-{config['color']}{suffix}"

  if config['color'] == 'orange':
    icon_name = f'qualia-dark' # set it to dark because panel is always dark now
  else:
    icon_name = f"qualia-{config['color']}-dark"

  def enable_theme(theme, schema, key, name, property = None, channel = 'xsettings'):
    for de, value in schema.items():
      if shutil.which('gsettings') is not None:
        if config[de] != None and check_output(['gsettings', 'get', value, key]) != name:
          print(f'Changing {theme} theme to {BOLD}{name}{NC}.')
          run_command(['gsettings', 'set', value, key, name])
      else:
        print(f"{BLYELLOW}'gsettings'{BYELLOW} not found, not {theme} theme.{NC}")
        break
    if shutil.which('xfconf-query') is not None:
      if property != None and config['xfce'] != None and check_output(['xfconf-query', '-c', channel, '-p', property]) != name:
          print(f'Changing {theme} theme to {BOLD}{name}{NC}.')
          run_command(['xfconf-query', '-c', channel, '-p', property, '-s', name])
    elif property != None and config['xfce'] != None:
      print(f"{BLYELLOW}'xfconf-query'{BYELLOW} not found, not enabling {theme} theme.{NC}")

  schemas = {
    'gnome-shell': 'org.gnome.desktop.interface',
    'cinnamon-shell': 'org.cinnamon.desktop.interface',
    'ubuntu-unity': 'org.gnome.desktop.interface',
    'mate': 'org.mate.interface',
    'budgie': 'org.gnome.desktop.interface',
  }

  # Enable GTK3 theme
  if 'gtk3' in config['enabled']:
    enable_theme('GTK3', schemas, 'gtk-theme', qualia, '/Net/ThemeName')

  # Enable icon theme
  if 'icons' in config['enabled']:
    enable_theme('icon', schemas, 'icon-theme', icon_name, '/Net/IconThemeName')

  schemas['mate'] = 'org.mate.peripherals-mouse'

  # Enable cursor theme
  if 'cursors' in config['enabled']:
    enable_theme('cursor', schemas, 'cursor-theme', 'qualia', '/Gtk/CursorThemeName')

  # Enable sound theme
  sound_schemas = {
    'gnome-shell': 'org.gnome.desktop.sound',
    'cinnamon-shell': 'org.cinnamon.desktop.sound',
    'ubuntu-unity': 'org.gnome.desktop.sound',
    'mate': 'org.mate.sound',
    'budgie': 'org.gnome.desktop.sound',
  }

  if 'sounds' in config['enabled']:
    enable_theme('sound', sound_schemas, 'theme-name', 'qualia', '/Net/SoundThemeName')

  # Enable GNOME Shell theme
  gs_schema = {'gnome-shell': 'org.gnome.shell.extensions.user-theme'}

  if 'gnome-shell' in config['enabled']:
    if shutil.which('gnome-extensions') is not None:
      gnome_extensions = subprocess.run(['gnome-extensions', 'list'], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')
      if 'user-theme@gnome-shell-extensions.gcampax.github.com' in gnome_extensions:
        run_command(['gnome-extensions', 'enable', 'user-theme@gnome-shell-extensions.gcampax.github.com'])
        enable_theme('GNOME Shell', gs_schema, 'name', qualia)
      else:
        print(f"{BLYELLOW}'User Themes'{BYELLOW} GNOME Shell Extension not found, not enabling GNOME Shell theme.{NC}")
    else:
      print(f"{BLYELLOW}'gnome-extensions'{BYELLOW} not found, not enabling GNOME Shell theme.{NC}")

  # Enable Cinnamon Shell theme
  cinnamon_schema = {'cinnamon-shell': 'org.cinnamon.theme'}

  if 'cinnamon-shell' in config['enabled']:
    enable_theme('Cinnamon Shell', cinnamon_schema, 'name', qualia)

  # Enable Marco (Metacity) theme
  marco_schema = {'mate': 'org.mate.Marco.general'}

  if 'metacity' in config['enabled']:
    enable_theme('Marco (Metacity)', marco_schema, 'theme', f'qualia{suffix}')

  # Enable Xfwm4 theme
  if 'xfwm4' in config['enabled']:
    enable_theme('Xfwm4', {}, None, f'qualia{suffix}', '/general/theme', 'xfwm4')

  # Set color scheme
  if color_scheme is not None and shutil.which('gsettings') is not None:
    run_command(['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', color_scheme])

  # If everything was a success, write the version to the config file
  f = open(CONFIG_FILE, 'a')
  f.write('version: ' + config['new_version'])
  f.close()

  ########################
  #   Remove old theme   #
  ########################

  from uninstall import OLD_NAMES

  old_paths = installed_paths(OLD_NAMES, True)

  for i in old_paths:
    old_exists = check_path(i, old_paths, True)
    if old_exists:
      print("Removing old theme.")
      subprocess.run(['sudo', './uninstall.py', '--old'])
      break

  print(f"{BYELLOW}Log out and log back in for everything to be updated.{NC}")
