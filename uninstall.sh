#! /usr/bin/env bash
GTK4_DIR="${HOME}/.config/gtk-4.0"

NC='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BRED='\033[1;31m'
BYELLOW='\033[1;33m'

echo -e "${YELLOW}Removing ${BYELLOW}dg-adw-gtk3${YELLOW}."
rm -rf ${HOME}/.local/share/themes/dg-adw-gtk3*

echo -e "${YELLOW}Removing gtk4 configuration."
rm -rf ${GTK4_DIR}/mac-icons ${GTK4_DIR}/gtk.css

echo -e "${YELLOW}Removing ${BYELLOW}dg-firefox-theme${YELLOW}."
rm -rf ${HOME}/snap/firefox/common/.mozilla/firefox/*/chrome ${HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome ${HOME}/.mozilla/firefox/*/chrome
rm -f ${HOME}/snap/firefox/common/.mozilla/firefox/*/user.js ${HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox/*/user.js ${HOME}/.mozilla/firefox/*/user.js

echo -e "${YELLOW}Removing ${BYELLOW}dg-yaru${YELLOW}."
sudo rm -rf /usr/share/themes/dg-yaru* /usr/share/icons/dg-yaru* /usr/share/gnome-shell/theme/dg-yaru* /usr/share/sounds/dg-yaru

if snap info dg-adw-gtk3-theme | grep -q "installed"; then
  echo -e "${YELLOW}Disconnecting ${BYELLOW}dg-adw-gtk3-theme${YELLOW} from installed snaps.${NC}"
  for i in $(snap connections | grep gtk-common-themes:gtk-3-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
	  sudo snap disconnect "${i}:gtk-3-themes" "dg-adw-gtk3-theme:gtk-3-themes"
	done

  echo -e "${YELLOW}Uninstalling ${BYELLOW}dg-adw-gtk3-theme${YELLOW} snap.${NC}"
  sudo snap remove dg-adw-gtk3-theme
fi

echo -e "${BRED}Log out and log back in for everything to be updated${NC}"
