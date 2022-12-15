<div align="center">

# qualia GTK theme
**A Yaru and Libadwaita inspired theme designed to provide a consistent experience on GTK desktops.**

**Supports GNOME 42+, Budgie 10.6+, Cinnamon, Unity7, Xfce, and Mate.**

**[Other Desktop Environments](https://github.com/dgsasha/qualia-gtk-theme/wiki/Other-Desktop-Environments)**

![Screenshot of the dark theme](.github/images/dark.png)

![Screenshot of the light theme](.github/images/light.png)

More screenshots can be seen [here](.github/SCREENSHOTS.md).

**This repo contains a GTK3 theme, a configuration for Libadwaita, a Firefox theme, a VS Code theme, and themes for the desktops listed above.**
  
**The Yaru icon, cursor, sound, and GtkSourceView themes are also included.**

# How to Install

## Installing Dependencies

A modern version of Python is required. Any currently supported version should work.

Open an issue or a pull request if your distro is not listed below.

<details>
<summary>

### Arch based distros

</summary>

*Includes Arch, Manjaro, Garuda Linux, EndeavourOS, etc.*

```
sudo pacman -S sassc git ninja meson rsync
```

**If using GNOME, also run this and then log out and log back in:**

```
sudo pacman -S gnome-shell-extensions
```

</details>

<details>
<summary>

### Debian/Ubuntu based distros

</summary>

<details>
<summary>

### Debian base >= 'bookworm' or Ubuntu base >= 22.04

</summary>

*Also includes [bullseye-backports](https://backports.debian.org/Instructions/) or Debian branches like sid/testing*

```
sudo apt-get install sassc git ninja-build meson
```

**If using GNOME, also run this and then log out and log back in:**

```
sudo apt-get install gnome-shell-extensions
```

</details>

<details>
<summary>

### Debian base <= 'bullseye' or Ubuntu base <= 20.04

</summary>

*Includes some Ubuntu based distros like Zorin OS*
```
sudo apt-get install sassc git ninja-build python3-pip gnome-shell-extensions
```
```
sudo pip install meson ninja
```

**If using GNOME, also run this and then log out and log back in:**

```
sudo apt-get install gnome-shell-extensions
```

</details>

</details>

<details>
<summary>

### Fedora

</summary>

```
sudo dnf install sassc git ninja-build meson gnome-shell-extension-user-theme
```

**If using GNOME, also run this and then log out and log back in:**

```
sudo dnf install gnome-shell-extension-user-theme
```


</details>

<details>
<summary>

### openSUSE Tumbleweed

</summary>

```
sudo zypper install sassc git ninja meson gnome-shell-extension-user-theme
```

**If using GNOME, also run this and then log out and log back in:**

```
sudo zypper install gnome-shell-extension-user-theme
```

</details>

<details>
<summary>

### Solus

</summary>

```
sudo eopkg install sassc git ninja meson rsync gnome-shell-extensions
```

**If using GNOME, also run this and then log out and log back in:**

```
sudo eopkg install gnome-shell-extensions
```

</details>

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
usage: install.py [-h] [-c] [-r] [-t] [-s] [-a] [-f] [-n] [-v]

This script is used to install, update, and reconfigure the theme

options:
  -h, --help         show this help message and exit
  -c, --clean        clean build directories and exit
  -r, --reconfigure  reconfigure the theme
  -t, --theme        change theme variant
  -s, --syntax       change VS Code syntax highlighting
  -a, --accent       change accent color
  -f, --force        force install the theme
  -n, --no-update    don't update the submodules, useful if you made local changes
  -v, --verbose      verbose mode
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

You can also use `--accent` or `--theme` to just change the accent color or the theme variant.

If you installed the VS Code theme, you can use `--syntax` to change the syntax highlighting.

**Warning about GNOME**

The GNOME Shell often changes a lot between major releases. For this reason you will always need to run `./install.py` after updating GNOME to make sure the latest version of the theme is installed. You should probably do this for other desktops as well, just in case there are changes.

You should also probably avoid using alpha builds of GNOME because I might not have the theme updated to support them yet.

## Uninstalling
```
./uninstall.py
```

</div>

```
Usage:
    ./uninstall.py <option> <theme> ...

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

Run './uninstall.py' followed by any number of the above themes to choose what to uninstall.
Or run './uninstall.py' with no arguments to uninstall the entire theme.

Run './uninstall.py firefox' to remove the theme from all Firefox variants.
```

<div align="center">

## Other things you should read

### [Flatpak Apps](https://github.com/dgsasha/qualia-gtk-theme/wiki/Flatpak-Apps) &nbsp; [Snap Apps](https://github.com/dgsasha/qualia-gtk-theme/wiki/Snap-Apps) &nbsp; [GDM Theme](https://github.com/dgsasha/qualia-gtk-theme/wiki/GDM-Theme) &nbsp; [Copying](https://github.com/dgsasha/qualia-gtk-theme/wiki/Copying) &nbsp; [Issues](https://github.com/dgsasha/qualia-gtk-theme/wiki/Issues) &nbsp; [Contributing](https://github.com/dgsasha/qualia-gtk-theme/wiki/Contributing)

## Credits :)
### A huge thanks to:
### [Ubuntu](https://ubuntu.com/) for [Yaru](https://github.com/ubuntu/yaru), [vinceliuice](https://github.com/vinceliuice) for [WhiteSur-gtk-theme](https://github.com/vinceliuice/WhiteSur-gtk-theme), [rafaelmardojai](https://github.com/rafaelmardojai) for [firefox-gnome-theme](https://github.com/rafaelmardojai/firefox-gnome-theme), [piousdeer](https://github.com/piousdeer) for [vscode-adwaita](https://github.com/piousdeer/vscode-adwaita), and [lassekongo83](https://github.com/lassekongo83) for [adw-gtk3](https://github.com/lassekongo83/adw-gtk3).
