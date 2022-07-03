#! /usr/bin/env bash

REPO_DIR="$(pwd)"
SRC_DIR="${REPO_DIR}/src"

GTK3_DIR="$HOME/.config/gtk-3.0"
GTK4_DIR="$HOME/.config/gtk-4.0"

SASSC_OPT="-M -t expanded"

THEME_VARIANTS=('light' 'dark')
COLOR_VARIANTS=('orange' 'bark' 'sage' 'olive' 'viridian' 'prussiangreen' 'blue' 'purple' 'magenta' 'red')
BUTTON_VARIANTS=('right' 'left')
FIREFOX_VARIANTS=('none' 'default' 'flatpak')

usage() {
cat << EOF
Usage: $0 [OPTION]...
OPTIONS:
  -t, --theme VARIANT             Specify theme variant [light|dark] (Default: light)
  -a, --accent-color VARIANT      Specify yaru accent color variant [orange|bark|sage|olive|viridian|prussiangreen|blue|purple|magenta|red] (Default: orange)
  -b, --button-placement VARIANT  Specify window titlebar button placement [right|left] (Default: right)
  -f, --firefox-theme VARIANT     Specify where to install the firefox theme [none|default|flatpak] (Default: none)
  -r, --remove                    Remove this theme
  -h, --help                      Show help
EOF
}

install_theme() {
  theme_tweaks

  echo Installing $color$suffix gtk3 configuration in $GTK3_DIR
  mkdir -p                                                  "$GTK3_DIR"
  rm -rf                                                    "$GTK3_DIR/mac-icons"
  cp -R $SRC_DIR/assets/mac-icons$suffix                    "$GTK3_DIR/mac-icons"
  sassc $SASSC_OPT "$SRC_DIR/main/gtk-3.0/gtk$suffix.scss"  "$GTK3_DIR/gtk.css"

  echo Installing $color$suffix gtk4 configuration in $GTK4_DIR
  mkdir -p                                                 "$GTK4_DIR"
  rm -rf                                                   "$GTK4_DIR/mac-icons"
  cp -R $SRC_DIR/assets/mac-icons$suffix                   "$GTK4_DIR/mac-icons"
  sassc $SASSC_OPT "$SRC_DIR/main/gtk-4.0/gtk$suffix.scss" "$GTK4_DIR/gtk.css"

  if [[ "$firefox" = "flatpak" ]] ; then
  FIREFOX_THEME_OPT="-f $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox -c $color"
  else
  FIREFOX_THEME_OPT="-c $color"
  fi

  if [[ "$firefox" = "none" ]] ; then
    echo Not installing Firefox theme.
  else
    git submodule init && git submodule update --remote
    cd $REPO_DIR/dg-firefox-theme
    ./scripts/install.sh $FIREFOX_THEME_OPT
  fi
}

remove_theme() {
echo Removing gtk3 configuration.
rm -rf $GTK3_DIR/mac-icons $GTK3_DIR/gtk.css

echo Removing gtk4 configuration.
rm -rf $GTK4_DIR/mac-icons $GTK4_DIR/gtk.css

echo Removing Firefox theme.
rm -rf $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome $HOME/.mozilla/firefox/*/chrome
rm -f $HOME/.var/app/org.mozilla.firefox/.mozilla/firefox/*/user.js $HOME/.mozilla/firefox/*/user.js
}

theme=()
color=()
button=()
firefox=()

while [[ $# -gt 0 ]]; do
  case "${1}" in
    -t|--theme)
      shift
      for variant in "${@}"; do
        case "${variant}" in
          light)
            theme=("${THEME_VARIANTS[0]}")
            shift
            ;;
          dark)
            theme=("${THEME_VARIANTS[1]}")
            shift
            ;;
          -*|--*)
            break
            ;;
          *)
            echo "ERROR: Unrecognized theme variant '$1'."
            echo "Try '$0 --help' for more information."
            exit 1
            ;;
        esac
      done
      ;;
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
    -b|--button-placement)
      shift
      for variant in "${@}"; do
        case "${variant}" in
          right)
            button=("${BUTTON_VARIANTS[0]}")
            shift
            ;;
          left)
            left='true'
            button=("${BUTTON_VARIANTS[1]}")
            shift
            ;;
          -*|--*)
            break
            ;;
          *)
            echo "ERROR: Unrecognized button placement '$1'."
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
            echo "ERROR: Unrecognized button placement '$1'."
            echo "Try '$0 --help' for more information."
            exit 1
            ;;
        esac
      done
      ;;
    -r|--remove)
      remove=yes
      remove_theme
      exit 0
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

if [[ "${#theme[@]}" -eq 0 ]] ; then
  theme=("${THEME_VARIANTS[0]}")
fi

if [[ "${#color[@]}" -eq 0 ]] ; then
  color=("${COLOR_VARIANTS[0]}")
fi

if [[ "${#button[@]}" -eq 0 ]] ; then
  button=("${BUTTON_VARIANTS[0]}")
fi

if [[ "${#firefox[@]}" -eq 0 ]] ; then
  firefox=("${FIREFOX_VARIANTS[0]}")
fi

variables_temp() {
  cp -rf $SRC_DIR/sass/_variables.scss $SRC_DIR/sass/_variables-temp.scss
}

button_placement() {
  sed -i "/\$button_placement:/s/right/left/" $SRC_DIR/sass/_variables-temp.scss
}

accent_color() {
  sed -i "/\$accent_color:/s/orange/$color/" $SRC_DIR/sass/_variables-temp.scss
}

theme_tweaks() {
  if [[ "$accent" = "true" ]] ; then
    accent_color
  fi

  if [[ "$left" = "true" ]] ; then
    button_placement
  fi
}

if [[ "$theme" = "light" ]] ; then
  color_scheme='default'
  suffix=''
else
  color_scheme='prefer-dark'
  suffix='-dark'
fi

enable_theme() {
  echo Enabling $theme theme.
  gsettings set org.gnome.desktop.interface color-scheme "$color_scheme"

  echo Changing gtk3 theme to adw-gtk3$suffix.
  gsettings set org.gnome.desktop.interface gtk-theme "adw-gtk3$suffix"

  if [[ "$color" = "orange" ]] ; then
    echo Changing icon theme to Yaru$suffix.
    gsettings set org.gnome.desktop.interface icon-theme "Yaru$suffix"
    echo Changing Gnome Shell theme to Yaru$suffix.
    gsettings set org.gnome.shell.extensions.user-theme name "Yaru$suffix"
  else
    echo Changing icon theme to Yaru-$color$suffix.
    gsettings set org.gnome.desktop.interface icon-theme "Yaru-$color$suffix" 
    echo Changing Gnome Shell theme to Yaru-$color$suffix.
    gsettings set org.gnome.shell.extensions.user-theme name "Yaru-$color$suffix"
  fi

  if [[ "$left" = "true" ]] ; then
    echo Changing window titlebar button placement to left.
    gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:appmenu'
  else
    echo Changing window titlebar button placement to right.
    gsettings set org.gnome.desktop.wm.preferences button-layout 'appmenu:minimize,maximize,close'
  fi
}

if [[ "$remove" != "yes" ]] ; then
  variables_temp && install_theme && enable_theme
fi

rm -rf $SRC_DIR/sass/_variables-temp.scss

echo Done.
echo 'Log out and log back in for everything to be updated :)'
