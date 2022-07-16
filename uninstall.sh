#! /usr/bin/env bash

GTK4_DIR="$HOME/.config/gtk-4.0"

echo Removing dg-adw-gtk3.
rm -rf $HOME/.local/share/themes/dg-adw-gtk3*

echo Removing gtk4 configuration.
rm -rf $GTK4_DIR/mac-icons $GTK4_DIR/gtk.css

echo Removing Firefox theme.
rm -rf $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome $HOME/.mozilla/firefox/*/chrome
rm -f $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox/*/user.js $HOME/.mozilla/firefox/*/user.js

echo Done.
echo 'Log out and log back in for everything to be updated :)'
