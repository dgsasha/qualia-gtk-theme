#! /usr/bin/env bash

REPO_DIR="$(pwd)"
SRC_DIR="${REPO_DIR}/src"
GTK3_SRC_DIR="${REPO_DIR}/dg-adw-gtk3"
YARU_SRC_DIR="${REPO_DIR}/dg-yaru"
GTK4_DIR="$HOME/.config/gtk-4.0"

SASSC_OPT="-M -t expanded"

COLOR_VARIANTS=('orange' 'bark' 'sage' 'olive' 'viridian' 'prussiangreen' 'blue' 'purple' 'magenta' 'red')
FIREFOX_VARIANTS=('none' 'default' 'flatpak')

usage() {
cat << EOF
Usage: $0 [OPTION]...
OPTIONS:
	-a, --accent-color VARIANT      Specify yaru accent color variant [orange|bark|sage|olive|viridian|prussiangreen|blue|purple|magenta|red] (Default: orange)
	-f, --firefox-theme VARIANT     Specify where to install the firefox theme [none|default|flatpak] (Default: none)
	-h, --help                      Show help
EOF
}

install_theme() {
	git submodule init dg-adw-gtk3 dg-yaru && git submodule update

	echo Installing $color dg-adw-gtk3 theme in ${HOME}/.local/share
	cd $GTK3_SRC_DIR
	if [ ! -d "$GTK3_SRC_DIR/build" ] ; then
		meson -Dprefix="${HOME}/.local" build > /dev/null
	fi
	meson configure -Daccent=$color build > /dev/null
	ninja -C build install > /dev/null

	echo Installing dg-yaru theme in /usr/share
	cd $YARU_SRC_DIR
	if [ ! -d "$YARU_SRC_DIR/build" ] ; then
		meson build > /dev/null
	fi
	sudo ninja -C build install > /dev/null
	cd $REPO_DIR

	echo Installing $color gtk4 configuration in $GTK4_DIR
	mkdir -p                                            "$GTK4_DIR"
	rm -rf                                              "$GTK4_DIR/mac-icons"
	cp -R $SRC_DIR/assets/mac-icons$suffix              "$GTK4_DIR/mac-icons"
	sassc $SASSC_OPT "$SRC_DIR/gtk-4.0/gtk$suffix.scss" "$GTK4_DIR/gtk.css"

	if [ "$firefox" = "flatpak" ] ; then
	FIREFOX_THEME_OPT="-f $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox -c $color"
	else
	FIREFOX_THEME_OPT="-c $color"
	fi

	if [ "$firefox" = "none" ] ; then
		echo Not installing Firefox theme.
	else
		git submodule init dg-firefox-theme && git submodule update
		cd $REPO_DIR/dg-firefox-theme
		./scripts/install.sh $FIREFOX_THEME_OPT
	fi
}

color=()
firefox=()

while [ $# -gt 0 ]; do
	case "${1}" in
		-a|--accent-color)
			accent='true'
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
					-*|--*)
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
		-f|--firefox-theme)
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
						flatpak='true'
						firefox=("${FIREFOX_VARIANTS[2]}")
						shift
						;;
					-*|--*)
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
	cp -rf $SRC_DIR/gtk-4.0/_accent-colors.scss $SRC_DIR/gtk-4.0/_accent-colors-temp.scss
	sed -i "/\$accent_color:/s/orange/$color/" $SRC_DIR/gtk-4.0/_accent-colors-temp.scss
}

enable_theme() {
	gnome-extensions enable user-theme@gnome-shell-extensions.gcampax.github.com

	echo Changing gtk3 theme to dg-adw-gtk3$suffix.
	gsettings set org.gnome.desktop.interface gtk-theme "dg-adw-gtk3$suffix"

	if [ "$color" = "orange" ] ; then
		dg_yaru="dg-yaru$suffix"
	else
		dg_yaru="dg-yaru-$color$suffix"
	fi

	echo Changing cursor theme to dg-yaru.
	gsettings set org.gnome.desktop.interface cursor-theme dg-yaru
	echo Changing sound theme to dg-yaru.
	gsettings set org.gnome.desktop.sound theme-name dg-yaru
	echo Changing icon theme to $dg_yaru.
	gsettings set org.gnome.desktop.interface icon-theme $dg_yaru
	echo Changing Gnome Shell theme to $dg_yaru.
	gsettings set org.gnome.shell.extensions.user-theme name $dg_yaru
}

accent_color && install_theme && enable_theme

rm -rf $SRC_DIR/gtk-4.0/_accent-colors-temp.scss

echo Done.
echo 'Log out and log back in for everything to be updated :)'
