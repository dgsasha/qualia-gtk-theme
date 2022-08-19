#! /usr/bin/env bash
repo_dir="$(realpath "$(dirname -- "$0")")"
cd "${repo_dir}" || exit

src_dir="${repo_dir}/src"
gtk4_dir="${HOME}/.config/gtk-4.0"
installed_versions="${src_dir}/installed-versions.txt"

firefox_variants=('standard' 'flatpak' 'snap')
dg_yaru_parts=('gnome-shell' 'icons' 'cursors' 'sounds')

nc='\033[0m'
bold='\033[1m'
red='\033[0;31m'
bred='\033[1;31m'

usage() {
cat << EOF
Usage: ${0} [OPTION]...

OPTIONS:
  -f, --firefox [standard|flatpak|snap]
        Uninstall dg-firefox-theme.
        Using no arguments will remove all variants.
  -g, --gnome-shell
        Uninstall dg-yaru GNOME Shell theme.
  -i, --icons
        Uninstall dg-yaru icon theme.
  -c, --cursors
        Uninstall dg-yaru cursor theme.
  -s, --sounds
        Uninstall dg-yaru sound theme.
      --gtk3
        Uninstall dg-adw-gtk3.
      --gtk4"
        Uninstall dg-libadwaita.
      --snap
        Uninstall dg-adw-gtk3-theme Snap.
  -h, --help
        Show this screen.

Run '${0}' with any number of the above options to choose which parts of the theme to uninstall.
Or run '${0}' with no arguments to uninstall the entire theme.
EOF
}

uninstall_gtk3() {
  if [[ "$(compgen -G "${HOME}"/.local/share/themes/dg-adw-gtk3* )" ||
  ( -s "${installed_versions}" && ( "$(grep "^dg-adw-gtk3" "${installed_versions}")" ||
  "$(grep "^enabled" "${installed_versions}" | grep "gtk3")" ) ) ]]; then
    echo -e "${red}Removing ${nc}${bold}dg-adw-gtk3${nc}."
    rm -rf "${HOME}"/.local/share/themes/dg-adw-gtk3*
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^enabled/s/ gtk3//' "${installed_versions}"
      sed -i '/^dg-adw-gtk3/d' "${installed_versions}"
    fi
    if [[ "$(command -v snap)" ]] && snap list | grep -q "dg-adw-gtk3-theme"; then
      for i in $(snap connections | grep dg-adw-gtk3-theme:gtk-3-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
        sudo snap disconnect "${i}:gtk-3-themes" "dg-adw-gtk3-theme:gtk-3-themes"
      done
    fi
  fi
}

uninstall_gtk4() {
  if [[ -d "${gtk4_dir}/mac-icons" && -d "${gtk4_dir}/gtk.css" ||
  ( -s "${installed_versions}" && ( "$(grep "^dg-libadwaita" "${installed_versions}")" ||
  "$(grep "^enabled" "${installed_versions}" | grep "gtk4")" ) ) ]]; then
    echo -e "${red}Removing ${nc}${bold}dg-libadwaita${nc}."
    rm -rf "${gtk4_dir}"/mac-icons "${gtk4_dir}"/gtk.css
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^enabled/s/ gtk4//' "${installed_versions}"
      sed -i '/^dg-libadwaita/d' "${installed_versions}"
    fi
  fi
}

uninstall_firefox_standard() {
  if [[ "$(compgen -G "${HOME}"/.mozilla/firefox/*/chrome)" &&
  "$(compgen -G "${HOME}"/.mozilla/firefox/*/user.js)" ||
  ( -s "${installed_versions}" && "$(grep "^firefox" "${installed_versions}" | grep "standard")" ) ]]; then
    echo -e "${red}Removing${nc} standard variant of ${bold}dg-firefox-theme${nc}."
    rm -rf "${HOME}"/.mozilla/firefox/*/chrome
    rm -f "${HOME}"/.mozilla/firefox/*/user.js
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^firefox/s/ standard//' "${installed_versions}"
      sed -i '/^dg-firefox-theme-standard/d' "${installed_versions}"
    fi
  fi
}

uninstall_firefox_snap() {
  if [[ "$(compgen -G "${HOME}"/snap/firefox/common/.mozilla/firefox/*/chrome)" &&
  "$(compgen -G "${HOME}"/snap/firefox/common/.mozilla/firefox/*/user.js)" ||
  ( -s "${installed_versions}" && "$(grep "^firefox:" "${installed_versions}" | grep "snap")" ) ]]; then
    echo -e "${red}Removing${nc} snap variant of ${bold}dg-firefox-theme${nc}."
    rm -rf "${HOME}"/snap/firefox/common/.mozilla/firefox/*/chrome
    rm -f "${HOME}"/snap/firefox/common/.mozilla/firefox/*/user.js
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^firefox/s/ snap//' "${installed_versions}"
      sed -i '/^dg-firefox-theme-snap/d' "${installed_versions}"
    fi
  fi
}

uninstall_firefox_flatpak() {
  if [[ "$(compgen -G "${HOME}"/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome)" &&
  "$(compgen -G "${HOME}"/.var/app/org.mozilla.firefox/.mozilla/firefox/*/user.js)" ||
  ( -s "${installed_versions}" && "$(grep "^firefox:" "${installed_versions}" | grep "flatpak")" ) ]]; then
    echo -e "${red}Removing${nc} flatpak variant of ${bold}dg-firefox-theme${nc}."
    rm -rf "${HOME}"/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome
    rm -f "${HOME}"/.var/app/org.mozilla.firefox/.mozilla/firefox/*/user.js
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^firefox/s/ flatpak//' "${installed_versions}"
      sed -i '/^dg-firefox-theme-flatpak/d' "${installed_versions}"
    fi
  fi
}

uninstall_firefox() {
  uninstall_firefox_standard && uninstall_firefox_snap && uninstall_firefox_flatpak
}

uninstall_shell() {
  if [[ "$(compgen -G /usr/share/themes/dg-yaru*)" || "$(compgen -G /usr/share/gnome-shell/theme/dg-yaru*)" || 
  ( -s "${installed_versions}" && ( "$(grep "^dg-yaru" "${installed_versions}" | grep "gnome-shell")" ||
  "$(grep "^enabled" "${installed_versions}" | grep "gnome-shell")" ) ) ]]; then
    echo -e "${red}Removing ${nc}${bold}dg-yaru${nc} GNOME Shell theme."
    sudo rm -rf /usr/share/themes/dg-yaru* /usr/share/gnome-shell/theme/dg-yaru*
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^enabled/s/ gnome-shell//' "${installed_versions}"
      sed -i '/^dg-yaru/s/ gnome-shell//' "${installed_versions}"
    fi
  fi
}

uninstall_icons() {
  if [[ -d "/usr/share/icons/dg-yaru/index.theme" || "$(compgen -G /usr/share/icons/dg-yaru-*)" || 
  ( -s "${installed_versions}" && ( "$(grep "^dg-yaru" "${installed_versions}" | grep "icons")" ||
  "$(grep "^enabled" "${installed_versions}" | grep "icons")" ) ) ]]; then
    echo -e "${red}Removing ${nc}${bold}dg-yaru${nc} icon theme."
    for f in /usr/share/icons/dg-yaru/*; do
      case $f in
        *cursor.theme|*cursors)
          true
          ;;
        *)
          sudo rm -rf "${f}"
          ;;
      esac
    done
    sudo rm -rf /usr/share/icons/dg-yaru-* 
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^enabled/s/ icons//' "${installed_versions}"
      sed -i '/^dg-yaru/s/ icons//' "${installed_versions}"
    fi
    if [[ "$(command -v snap)" ]] && snap list | grep -q "dg-adw-gtk3-theme"; then
      for i in $(snap connections | grep dg-adw-gtk3-theme:icon-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
        sudo snap disconnect "${i}:icon-themes" "dg-adw-gtk3-theme:icon-themes"
      done
    fi
  fi
}

uninstall_cursors() {
  if [[ ( -d "/usr/share/icons/dg-yaru/cursor.theme" || -d "/usr/share/icons/dg-yaru/cursors" ) ||
  ( -s "${installed_versions}" && ( "$(grep "^dg-yaru" "${installed_versions}" | grep "cursors")" ||
  "$(grep "^enabled" "${installed_versions}" | grep "cursors")" ) ) ]]; then
    echo -e "${red}Removing ${nc}${bold}dg-yaru${nc} cursor theme."
    sudo rm -rf /usr/share/icons/dg-yaru/cursor.theme /usr/share/icons/dg-yaru/cursors
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^enabled/s/ cursors//' "${installed_versions}"
      sed -i '/^dg-yaru/s/ cursors//' "${installed_versions}"
    fi
  fi
}

uninstall_sounds() {
  if [[ ( -d "/usr/share/sounds/dg-yaru" ) || ( -s "${installed_versions}" &&
  ( "$(grep "^dg-yaru" "${installed_versions}" | grep "sounds")" ||
  "$(grep "^enabled" "${installed_versions}" | grep "sounds")" ) ) ]]; then
    echo -e "${red}Removing ${nc}${bold}dg-yaru${nc} sound theme."
    sudo rm -rf /usr/share/sounds/dg-yaru
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^enabled/s/ sounds//' "${installed_versions}"
      sed -i '/^dg-yaru/s/ sounds//' "${installed_versions}"
    fi
    if [[ "$(command -v snap)" ]] && snap list | grep -q "dg-adw-gtk3-theme"; then
      for i in $(snap connections | grep dg-adw-gtk3-theme:sound-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
        sudo snap disconnect "${i}:sound-themes" "dg-adw-gtk3-theme:sound-themes"
      done
    fi
  fi
}

uninstall_snap() {
  if [[ "$(command -v snap)" ]] && snap list | grep -q "dg-adw-gtk3-theme"; then
    echo -e "${red}Removing ${nc}${bold}dg-adw-gtk3-theme${nc} snap."
    sudo snap remove dg-adw-gtk3-theme
    if [[ -s "${installed_versions}" ]]; then
      sed -i '/^enabled/s/ snap//' "${installed_versions}"
    fi
  fi
}

if [[ $# -eq 0 ]]; then 
  uninstall_gtk3 && uninstall_gtk4 && uninstall_firefox && uninstall_shell && uninstall_icons && uninstall_cursors && uninstall_sounds && uninstall_snap
  rm -f "${installed_versions}"
fi

while [[ $# -gt 0 ]]; do
  case "${1}" in
    -f|--firefox)
      if [[ -z "${2}" ]]; then
        uninstall_firefox
      fi
      while true; do
        if [[ -n "${2}" ]] && ! printf '%s\0' "${firefox_variants[@]}" | grep -Fxqz -- "${2}"; then
          echo -e "${bred}ERROR:${nc} Unrecognized Firefox variant '${2}'."
          echo "Try '${0} --help' for more information."
          exit 1
        elif [[ -n "${2}" ]]; then
          "uninstall_firefox_${2}"
          shift
        else
          break
        fi
      done
      shift
      ;;
    -g|--gnome-shell)
      uninstall_shell
      shift
      ;;
    -i|--icons)
      uninstall_icons
      shift
      ;;
    -c|cursors)
      uninstall_cursors
      shift
      ;;
    -s|sounds)
      uninstall_sounds
      shift
      ;;
    --gtk3)
      uninstall_gtk3
      shift
      ;;
    --gtk4)
      uninstall_gtk4
      shift
      ;;
    --snap)
      uninstall_snap
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -)
      shift
      break
      ;;
    *)
      echo -e "${bred}ERROR:${nc} Unrecognized installation option '${1}'."
      echo "Try '${0} --help' for more information."
      exit 1
      ;;
  esac
done

# Remove icons/dg-yaru if empty
if [[ -d "/usr/share/icons/dg-yaru" && -z "$(ls -A /usr/share/icons/dg-yaru)" ]]; then
  sudo rm -rf /usr/share/icons/dg-yaru
fi

# If no parts of dg-yaru are installed, remove it from installed-versions.txt
for p in "${dg_yaru_parts[@]}"; do
  if [[ -s "${installed_versions}" ]] && grep "^dg-yaru:" "${installed_versions}" | grep -q "${p}"; then
    dg_yaru_installed="true"
  fi
done

if [[ -s "${installed_versions}" && "${dg_yaru_installed}" != "true" ]]; then
  sed -i '/^dg-yaru/d' "${installed_versions}"
fi
