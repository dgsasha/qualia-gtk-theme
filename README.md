# dg GNOME theme
**A Libadwaita + macOS + Yaru theme for GNOME**

*Kinda crazy but I like the look of it.*

![Screenshot of the theme](Screenshot.png)

## Dependencies
Fedora: `sassc` `git` `gnome-shell-extension-user-theme` `yaru-theme`

Arch: `sassc` `git` `gnome-shell-extensions` 
- You will also need `yaru` from the AUR.

Open a pull request if you want to add the dependencies for the distro you use :) 

**This isn't really much of a theme, it's mostly just a configuration for Libadwaita and adw-gtk3, so you also need to have [adw-gtk3](https://github.com/lassekongo83/adw-gtk3) installed.**

## Installation
```
git clone https://github.com/dgmarie/dg-gnome-theme

cd dg-gnome-theme

./install.sh
```
#### OPTIONS:
- `-t, --theme` `[light|dark]`     
	- Specify theme variant
	- Default: `light`
- `-a, --accent-color` `[orange|bark|sage|olive|viridian|prussiangreen|blue|purple|magenta|red]`
	- Specify yaru accent color variant
	- Default: `orange`
- `-b, --button-placement` `[right|left]`
	- Specify window titlebar button placement
	- Default: `right`
- `-f, --firefox-theme` `[none|default|flatpak]`
	- Specify where to install the firefox theme
	- Default: `none`
- `-r, --remove`
	- Remove this theme
- `-h, --help`
	- Show help

#### Example:
```
./install.sh -t dark -a orange -b left -f default
```
**Log out and log back in for everything to be updated.**

### Warning!

**The installation script changes some preferences in GNOME depending on the options you choose.**

The preferences being changed are `org.gnome.desktop.interface color-scheme` `org.gnome.desktop.interface icon-theme` `org.gnome.desktop.interface gtk-theme` `org.gnome.shell.extensions.user-theme name` and `org.gnome.desktop.wm.preferences button-layout`.

## Flatpak
Install adw-gtk3 as a Flatpak:
```
flatpak install org.gtk.Gtk3theme.adw-gtk3 org.gtk.Gtk3theme.adw-gtk3-dark
```
Also let flatpak access the configuration for this theme:
```
flatpak override --user --filesystem=xdg-config/gtk-4.0 && flatpak override --user --filesystem=xdg-config/gtk-3.0
```

## Updating
```
git pull
```
And then run installation script again

## Uninstalling
```
./install.sh --remove
```

## Extra Stuff
I'm using [Dash to Dock for Cosmic](https://extensions.gnome.org/extension/5004/dash-to-dock-for-cosmic) as the dock

I would also recommend using [gdm-tools](https://github.com/realmazharhussain/gdm-tools) to change the GDM theme to Yaru

## Credits
Thanks to Ubuntu for [Yaru](https://github.com/ubuntu/yaru), [vinceliuice](https://github.com/vinceliuice) for [WhiteSur-gtk-theme](https://github.com/vinceliuice/WhiteSur-gtk-theme) and [Colloid-gtk-theme](https://github.com/vinceliuice/Colloid-gtk-theme), [rafaelmardojai](https://github.com/rafaelmardojai) for [firefox-gnome-theme](https://github.com/rafaelmardojai/firefox-gnome-theme) and [lassekongo83](https://github.com/lassekongo83) for [adw-gtk3](https://github.com/lassekongo83/adw-gtk3)