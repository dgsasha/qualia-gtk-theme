#! /usr/bin/env bash

if (( $EUID != 0 )); then
    echo Please run as root.
    exit
fi

GTK4_DIR="$HOME/.config/gtk-4.0"

echo Removing dg-yaru.
rm -rf /usr/share/themes/dg-yaru*
rm -rf /usr/share/icons/dg-yaru*
rm -rf /usr/share/gnome-shell/theme/dg-yaru*
rm -rf /usr/share/sounds/dg-yaru

echo Removing dg-adw-gtk3.
rm -rf $HOME/.local/share/themes/dg-adw-gtk3*

echo Removing gtk4 configuration.
rm -rf $GTK4_DIR/mac-icons $GTK4_DIR/gtk.css

echo Removing Firefox theme.
rm -rf $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome $HOME/.mozilla/firefox/*/chrome
rm -f $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox/*/user.js $HOME/.mozilla/firefox/*/user.js

echo Done.
echo 'Log out and log back in for everything to be updated :)'
