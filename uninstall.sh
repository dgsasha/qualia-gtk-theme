#! /usr/bin/env bash
GTK4_DIR="${HOME}/.config/gtk-4.0"

NC='\033[0m'
BOLD='\033[1m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BYELLOW='\033[1;33m'

echo -e "${RED}Removing ${NC}${BOLD}dg-adw-gtk3${NC}."
rm -rf ${HOME}/.local/share/themes/dg-adw-gtk3*

echo -e "${RED}Removing ${NC}gtk4 configuration."
rm -rf ${GTK4_DIR}/mac-icons ${GTK4_DIR}/gtk.css

echo -e "${RED}Removing ${NC}${BOLD}dg-firefox-theme${NC}."
rm -rf ${HOME}/snap/firefox/common/.mozilla/firefox/*/chrome ${HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome ${HOME}/.mozilla/firefox/*/chrome
rm -f ${HOME}/snap/firefox/common/.mozilla/firefox/*/user.js ${HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox/*/user.js ${HOME}/.mozilla/firefox/*/user.js

echo -e "${RED}Removing ${NC}${BOLD}dg-yaru${NC}."
sudo rm -rf /usr/share/themes/dg-yaru* /usr/share/icons/dg-yaru* /usr/share/gnome-shell/theme/dg-yaru* /usr/share/sounds/dg-yaru

if snap info dg-adw-gtk3-theme | grep -q "installed"; then
  echo -e "${RED}Disconnecting ${NC}${BOLD}dg-adw-gtk3-theme${NC} from installed snaps."
  for i in $(snap connections | grep gtk-common-themes:gtk-3-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
	  sudo snap disconnect "${i}:gtk-3-themes" "dg-adw-gtk3-theme:gtk-3-themes"
	done
	for i in $(snap connections | grep gtk-common-themes:icon-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
	  sudo snap disconnect "${i}:icon-themes" "dg-adw-gtk3-theme:icon-themes"
	done
	for i in $(snap connections | grep gtk-common-themes:sound-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
	  sudo snap disconnect "${i}:sound-themes" "dg-adw-gtk3-theme:sound-themes"
	done

  echo -e "${RED}Removing ${NC}${BOLD}dg-adw-gtk3-theme${NC} snap."
  sudo snap remove dg-adw-gtk3-theme
fi

echo -e "${BYELLOW}Log out and log back in for everything to be updated${NC}"
