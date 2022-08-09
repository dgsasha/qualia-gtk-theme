#! /usr/bin/env bash

REPO_DIR="$(pwd)"
SRC_DIR="${REPO_DIR}/src"
GTK3_SRC_DIR="${REPO_DIR}/dg-adw-gtk3"
YARU_SRC_DIR="${REPO_DIR}/dg-yaru"
GTK4_DIR="${HOME}/.config/gtk-4.0"

COLOR_VARIANTS=('orange' 'bark' 'sage' 'olive' 'viridian' 'prussiangreen' 'blue' 'purple' 'magenta' 'red')
FIREFOX_VARIANTS=('none' 'default' 'flatpak' 'snap')

NC='\033[0m'
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BRED='\033[1;31m'
BGREEN='\033[1;32m'
BYELLOW='\033[1;33m'

usage() {
cat << EOF
Usage: $0 [OPTION]...
OPTIONS:
	-a, --accent VARIANT      Specify yaru accent color variant [orange|bark|sage|olive|viridian|prussiangreen|blue|purple|magenta|red] (Default: orange)
	-f, --firefox VARIANT     Specify where to install the firefox theme [none|default|flatpak|snap] (Default: none)
	-s, --snap                Use this option if you want to use the GTK3 theme with applications installed as snaps
	-v, --verbose             Shows meson output, use this option in case something isn't working and you want to know why
	-h, --help                Show help
EOF
}

install_theme() {
	git submodule init dg-adw-gtk3 dg-yaru && git submodule update

	echo -e "${GREEN}Installing ${BGREEN}dg-adw-gtk3${GREEN} theme${NC} in ${BOLD}${HOME}/.local/share"
	cd "$GTK3_SRC_DIR" || exit

	if [ "$verbose" = "true" ] ; then
		if [ ! -d "${GTK3_SRC_DIR}/build" ] ; then
			meson "-Dprefix=${HOME}/.local" build
		fi
		ninja -C build --verbose install
	else
		if [ ! -d "${GTK3_SRC_DIR}/build" ] ; then
			meson "-Dprefix=${HOME}/.local" build > /dev/null
		fi
		if ninja -C build install | grep --color -E "ERROR|FAILED"; then
		  exit 0
		fi
	fi

	echo -e "${GREEN}Installing ${BGREEN}dg-yaru${GREEN} theme${NC} in ${BOLD}/usr/share"

	if [ "$verbose" = "true" ] ; then
		cd "$YARU_SRC_DIR" || exit
		if [ ! -d "$YARU_SRC_DIR/build" ] ; then
			meson build
		fi
		sudo ninja -C build --verbose install
	else
		cd "$YARU_SRC_DIR" || exit
		if [ ! -d "$YARU_SRC_DIR/build" ] ; then
			meson build > /dev/null
		fi
		if sudo ninja -C build install | grep --color -E "ERROR|FAILED"; then
		  exit 0
		fi
	fi

	cd "$REPO_DIR" || exit

	echo -e "${GREEN}Installing ${BGREEN}${color}${GREEN} gtk4 configuration${NC} in ${BOLD}${GTK4_DIR}${NC}"
	mkdir -p                                                    "$GTK4_DIR"
	rm -rf                                                      "${GTK4_DIR}/mac-icons"
	cp -R "${SRC_DIR}/assets/mac-icons${suffix}"                "${GTK4_DIR}/mac-icons"
	sassc -M -t expanded "${SRC_DIR}/gtk-4.0/gtk${suffix}.scss" "${GTK4_DIR}/gtk.css"

	if [ "$firefox" = "flatpak" ] ; then
	  firefox_opt="-f ${HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox -c ${color}"
	elif [ "$firefox" = "snap" ] ; then
	  firefox_opt="-f ${HOME}/snap/firefox/common/.mozilla/firefox -c ${color}"
	else
	  firefox_opt="-c ${color}"
	fi

	if [ "$firefox" = "none" ] ; then
		echo "Not installing Firefox theme."
	else
		git submodule init dg-firefox-theme && git submodule update
		cd "${REPO_DIR}/dg-firefox-theme" || exit
		./scripts/install.sh $firefox_opt
	fi

	if [ "$snap" = "true" ] ; then
	  if ! snap info dg-adw-gtk3-theme | grep "installed" > /dev/null ; then
	    echo -e "${GREEN}Installing ${BGREEN}dg-adw-gtk3-theme${GREEN} snap.${NC}"
	    sudo snap install dg-adw-gtk3-theme
	  fi
	  echo -e "${GREEN}Connecting ${BGREEN}dg-adw-gtk3-theme${GREEN} to installed snaps.${NC}"
	  for i in $(snap connections | grep gtk-common-themes:gtk-3-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
	    sudo snap connect "${i}:gtk-3-themes" "dg-adw-gtk3-theme:gtk-3-themes"
	  done
	fi
}

color=()
firefox=()

while [ $# -gt 0 ]; do
	case "${1}" in
		-a|--accent)
			shift
			for variant in "$@"; do
				case "$variant" in
					orange)
						color=("${COLOR_VARIANTS[0]}")
						shift
						;;
					bark)
						color=("${COLOR_VARIANTS[1]}")
						shift
						;;
					sage)
						color=("${COLOR_VARIANTS[2]}")
						shift
						;;
					olive)
						color=("${COLOR_VARIANTS[3]}")
						shift
						;;
					viridian)
						color=("${COLOR_VARIANTS[4]}")
						shift
						;;
					prussiangreen)
						color=("${COLOR_VARIANTS[5]}")
						shift
						;;
					blue)
						color=("${COLOR_VARIANTS[6]}")
						shift
						;;
					purple)
						color=("${COLOR_VARIANTS[7]}")
						shift
						;;
					magenta)
						color=("${COLOR_VARIANTS[8]}")
						shift
						;;
					red)
						color=("${COLOR_VARIANTS[9]}")
						shift
						;;
					-*)
						break
						;;
					*)
						echo "ERROR: Unrecognized accent color variant '$1'."
						echo "Try '$0 --help' for more information."
						exit 1
						;;
				esac
			done
			;;
		-f|--firefox)
			shift
			for variant in "${@}"; do
				case "${variant}" in
					none)
						firefox=("${FIREFOX_VARIANTS[0]}")
						shift
						;;
					default)
						firefox=("${FIREFOX_VARIANTS[1]}")
						shift
						;;
					flatpak)
						firefox=("${FIREFOX_VARIANTS[2]}")
						shift
						;;
					snap)
						firefox=("${FIREFOX_VARIANTS[3]}")
						shift
						;;
					-*)
						break
						;;
					*)
						echo "ERROR: Unrecognized Firefox theme variant '$1'."
						echo "Try '$0 --help' for more information."
						exit 1
						;;
				esac
			done
			;;
		-s|--snap)
			shift
			snap="true"
			;;
		-v|--verbose)
			shift
			verbose="true"
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "ERROR: Unrecognized installation option '$1'."
			echo "Try '$0 --help' for more information."
			exit 1
			;;
	esac
done

if [ "${#color[@]}" -eq 0 ] ; then
	color=("${COLOR_VARIANTS[0]}")
fi

if [ "${#firefox[@]}" -eq 0 ] ; then
	firefox=("${FIREFOX_VARIANTS[0]}")
fi

theme=$(gsettings get org.gnome.desktop.interface color-scheme)
case $theme in
	"'prefer-dark'")
		suffix="-dark"
	;;
	"'default'")
		suffix=""
	;;
esac

accent_color() {
	cp -rf "${SRC_DIR}/gtk-4.0/_accent-colors.scss" "${SRC_DIR}/gtk-4.0/_accent-colors-temp.scss"
	sed -i "/\$accent_color:/s/orange/${color}/" "${SRC_DIR}/gtk-4.0/_accent-colors-temp.scss"
}

enable_theme() {
	gnome-extensions enable user-theme@gnome-shell-extensions.gcampax.github.com

	echo -e "${YELLOW}Changing gtk3 theme to "${BYELLOW}dg-adw-gtk3${suffix}"${YELLOW}."
	gsettings set org.gnome.desktop.interface gtk-theme "dg-adw-gtk3-${color}${suffix}"

	if [ "$snap" = "true" ] ; then
	  cursor="Yaru"
  else
    cursor="dg-yaru"
  fi

	if [ "$color" = "orange" ] ; then
		icon="${cursor}${suffix}"
		dg_yaru="dg-yaru${suffix}"
	else
		icon="${cursor}-${color}${suffix}"
		dg_yaru="dg-yaru-${color}${suffix}"
	fi

	echo -e "${YELLOW}Changing cursor theme to ${BYELLOW}${cursor}${YELLOW}."
	gsettings set org.gnome.desktop.interface cursor-theme "$cursor"
	echo -e "${YELLOW}Changing sound theme to ${BYELLOW}dg-yaru${YELLOW}."
	gsettings set org.gnome.desktop.sound theme-name dg-yaru
	echo -e "${YELLOW}Changing icon theme to ${BYELLOW}${icon}${YELLOW}."
	gsettings set org.gnome.desktop.interface icon-theme "$icon"
	echo -e "${YELLOW}Changing Gnome Shell theme to ${BYELLOW}${dg_yaru}${YELLOW}."
	gsettings set org.gnome.shell.extensions.user-theme name "$dg_yaru"
}

accent_color && install_theme && enable_theme

rm -rf "${SRC_DIR}/gtk-4.0/_accent-colors-temp.scss"

echo -e "${BRED}Log out and log back in for everything to be updated${NC}"
