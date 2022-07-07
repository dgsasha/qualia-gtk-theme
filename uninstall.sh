#! /usr/bin/env bash

GTK3_DIR="$HOME/.config/gtk-3.0"
GTK4_DIR="$HOME/.config/gtk-4.0"

echo Removing gtk3 configuration.
rm -rf $GTK3_DIR/mac-icons $GTK3_DIR/gtk.css

echo Removing gtk4 configuration.
rm -rf $GTK4_DIR/mac-icons $GTK4_DIR/gtk.css

echo Removing Firefox theme.
rm -rf $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome $HOME/.mozilla/firefox/*/chrome
rm -f $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox/*/user.js $HOME/.mozilla/firefox/*/user.js

echo Done.
echo 'Log out and log back in for everything to be updated :)'
