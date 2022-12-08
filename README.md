<div align="center">

# qualia GTK theme
**A Yaru and Libadwaita inspired theme designed to provide a consistent experience on GTK desktops.**

**Supports GNOME 42+, Budgie 10.6+, Cinnamon, Unity7, Xfce, and Mate.**

**[Other Desktop Environments](.github/OTHER.md#other-desktop-environments)**

![Screenshot of the dark theme](.github/images/dark.png)

![Screenshot of the light theme](.github/images/light.png)

More screenshots can be seen [here](.github/SCREENSHOTS.md).

**This repo contains a GTK3 theme, a configuration for Libadwaita, a Firefox theme, a VS Code theme, and themes for the desktops listed above.**
  
**The Yaru icon, cursor, sound, and GtkSourceView themes are also included.**

# How to Install

## Installing Dependencies

A modern version of Python is required. Any currently supported version should work.

You will also need a Meson version greater than 0.59.

#### Arch based distros

```
sudo pacman -S sassc git ninja meson rsync gnome-shell-extensions
```

#### Debian/Ubuntu based distros

```
sudo apt install sassc git ninja-build meson gnome-shell-extensions
```

#### Fedora

```
sudo dnf install sassc git ninja-build meson gnome-shell-extension-user-theme
```

#### openSUSE

```
sudo zypper install sassc git ninja meson gnome-shell-extension-user-theme
```

#### Solus

```
sudo eopkg install sassc git ninja meson rsync gnome-shell-extensions
```

<br>

**If you aren't using GNOME, you shouldn't install `gnome-shell-extensions` / `gnome-shell-extension-user-theme`.**

**If you are using GNOME, and it wasn't already installed, log out and log back in before you proceed.**


## Downloading and Installing

Download the repository and run the install script to configure and install the theme.

When configuring the theme you get to choose an [accent color](#available-accent-colors), choose between the light and dark variants, and choose which themes you want to install.

```
git clone https://github.com/dgsasha/qualia-gtk-theme -b main && cd qualia-gtk-theme
```
```
./install.py
```

</div>

```
usage: install.py [-h] [-c] [-r] [-t] [-s] [-a] [-f] [-v]

This script is used to install, update, and reconfigure the theme

options:
  -h, --help         show this help message and exit
  -c, --clean        clean build directories and exit
  -r, --reconfigure  reconfigure the theme
  -t, --theme        change theme variant
  -s, --syntax       change VS Code syntax highlighting
  -a, --accent       change accent color
  -f, --force        force install the theme
  -v, --verbose      display entire output
```

<div align="center">

#### Available Accent Colors:
![Accent Colors](.github/images/accents-dark.svg#gh-dark-mode-only)
![Accent Colors](.github/images/accents-light.svg#gh-light-mode-only)

## Updating

Pull in changes from the git repo and run the install script again.

```
git pull
```
```
./install.py
```

Your previous configuration will be used again unless you use the `--reconfigure` option.

Only the themes that need updates will be reinstalled, if you want to force reinstall everything, use the `--force` option.

If you ever update GNOME, reinstall the theme with the `--force` option to install the new GNOME Shell theme.

You can also use `--accent` or `--theme` to just change the accent color or the theme variant.

If you installed the VS Code theme, you can use `--syntax` to change the syntax highlighting.

## Uninstalling
```
./uninstall.py
```

</div>

```
Usage:
    ./uninstall.py <theme> ...
    ./uninstall.py <option> 

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
    -h, --help      Show this screen.

Run './uninstall.py' followed by any number of the above themes to choose what to uninstall.
Or run './uninstall.py' with no arguments to uninstall the entire theme.

Run './uninstall.py firefox' to remove the theme from all firefox variants.
```

<div align="center">

## Other things you should read

### [Flatpak Apps](.github/OTHER.md#flatpak-apps) &nbsp; [Snap Apps](.github/OTHER.md#snap-apps) &nbsp; [GDM Theme](.github/OTHER.md#gdm-theme) &nbsp; [Copying](.github/OTHER.md#copying) &nbsp; [Issues](.github/OTHER.md#issues) &nbsp; [Contributing](.github/CONTRIBUTING.md)

## Credits :)
### A huge thanks to:
### [Ubuntu](https://ubuntu.com/) for [Yaru](https://github.com/ubuntu/yaru), [vinceliuice](https://github.com/vinceliuice) for [WhiteSur-gtk-theme](https://github.com/vinceliuice/WhiteSur-gtk-theme), [rafaelmardojai](https://github.com/rafaelmardojai) for [firefox-gnome-theme](https://github.com/rafaelmardojai/firefox-gnome-theme), [piousdeer](https://github.com/piousdeer) for [vscode-adwaita](https://github.com/piousdeer/vscode-adwaita), and [lassekongo83](https://github.com/lassekongo83) for [adw-gtk3](https://github.com/lassekongo83/adw-gtk3).
