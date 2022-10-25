#! /usr/bin/env bash

repo_dir="$(realpath "$(dirname -- "$0")")"
cd "${repo_dir}" || exit

src_dir="${repo_dir}/src"
gtk4_dir="${HOME}/.config/gtk-4.0"
gtk4_src_dir="${src_dir}/dg-libadwaita"
gtk3_src_dir="${src_dir}/dg-adw-gtk3"
dg_yaru_src_dir="${src_dir}/dg-yaru"
firefox_src_dir="${src_dir}/dg-firefox-theme"
installed_versions="${src_dir}/installed-versions.txt"
firefox_dir_standard="${HOME}/.mozilla/firefox"
firefox_dir_snap="${HOME}/snap/firefox/common/.mozilla/firefox"
firefox_dir_flatpak="${HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox"

config_array=('enabled' 'firefox')
config_string=('color' 'theme')

themes=('gtk3' 'gtk4' 'gnome-shell' 'icons' 'cursors' 'sounds' 'gtksourceview' 'snap') # Available themes, not including firefox theme
firefox_variants=('standard' 'flatpak' 'snap')
color_variants=('orange' 'bark' 'sage' 'olive' 'viridian' 'prussiangreen' 'lightblue' 'blue' 'purple' 'magenta' 'pink' 'red') # Accent Colors
theme_variants=('auto' 'light' 'dark')
gnome_versions=('42' '43')
enableable_themes=('gtk3' 'gnome-shell' 'icons' 'cursors' 'sounds') # Themes that can be enabled with gsettings
dg_yaru_parts=('gnome-shell' 'icons' 'cursors' 'gtksourceview' 'sounds')

nc='\033[0m'
bold='\033[1m'
green='\033[0;32m'
yellow='\033[0;33m'
bred='\033[1;31m'
byellow='\033[1;33m'
blgreen='\033[1;92m'

verbose="false"
update="false"

usage() {
cat << EOF
Usage: ${0} [OPTION]...

OPTIONS:
  -r, --reconfigure	Reconfigure the theme.
  -f, --force		Force reinstall the theme.
  -c, --clean		Clean build directories and exit.
  -v, --verbose		Show full meson output.
  -h, --help		Show this screen.

This script allows you to configure, install, and update the theme.
EOF
}

if [[ ! "$(command -v sassc)" ]]; then
  echo -e "${bold}'sassc'${bred} not found, exiting.${nc}"
  exit 1
fi
if [[ ! "$(command -v git)" ]]; then
  echo -e "${bold}'git'${bred} not found, exiting.${nc}"
  exit 1
fi

enabled=()
firefox=()

while [ $# -gt 0 ]; do
  case "${1}" in
    -r|--reconfigure)
      reconfigure=true
      shift
      ;;
    -f|--force)
      force=true
      shift
      ;;
    -v|--verbose)
      verbose=true
      shift
      ;;
    -c|--clean)
      sudo rm -rf "${gtk3_src_dir}/build" "${dg_yaru_src_dir}/build"
      exit 0
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

#####################
#  Configure Theme  #
#####################

theme_variants() {
  failed=false
  if [[ "${theme}" == "auto" ]]; then
    theme_setting="$(gsettings get org.gnome.desktop.interface color-scheme)"
    case "${theme_setting}" in
     "'prefer-dark'")
        suffix="-dark"
        ;;
      "'default'")
        suffix=""
        ;;
      *)
        echo -e "${bred}Can't detect system light/dark theme preference.${nc}"
        failed=true
        ;;
    esac
  elif [[ "${theme}" == "light" ]]; then
    suffix=""
    color_scheme="default"
  elif [[ "${theme}" == "dark" ]]; then
    suffix="-dark"
    color_scheme="prefer-dark"
  fi
}

if [[ "$(command -v gnome-shell)" ]]; then
  shell_version="$(gnome-shell --version | cut -d ' ' -f 3 | cut -d . -f -1)"
  for version in "${gnome_versions[@]}"; do
    if [[ "${shell_version:-}" == "${version}" ]]; then
      gnome_version="${version}"
    fi
  done
fi

config_num() {
  local num
  while ! [[ "${num}" -ge 1 && "${num}" -le ${2} ]]; do
    echo -en "${bold}Enter the number corresponding to the ${1} you want [Default: 1]: ${nc}"
    read -r num
    if [[ -z "${num}" ]]; then
      num=1
    fi
  done
  array_num="$(("${num}" - 1))"
}

config_yn() {
  local yn
  while true; do
    if [[ -n "${4}" ]]; then
      echo -ne "${blgreen}Do you want to install the ${nc}${bold}${2}${blgreen} theme in ${nc}${bold}${4}${blgreen}?${nc} ${bold}[Y/n]: ${nc}"
    else
      echo -ne "${blgreen}Do you want to install the ${nc}${bold}${2}${blgreen} theme?${nc} ${bold}[Y/n]: ${nc}"
    fi
    read -r yn
    if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
      if [[ "${3}" == true && ! "$(command -v meson)" ]]; then
        echo -e "${bold}'meson'${bred} not found, can't install ${2} theme.${nc}"
        continue
      fi
      if [[ "$(command -v ninja)" && -z "${4}" ]]; then
        enabled+=("${1}")
        break
      elif [[ "$(command -v ninja)" && -n "${4}" ]]; then
        firefox+=("${1}")
        break
      elif [[ "${3}" == true ]]; then
         echo -e "${bold}'ninja'${bred} not found, can't install ${2} theme.${nc}"
         continue
      fi
   elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
      break
    fi
  done
}

configure() {
  echo -e "${blgreen}Which accent color do you want to use?${nc}"
  echo "  1.  Orange		7.  Light Blue"
  echo "  2.  Bark		8.  Blue"
  echo "  3.  Sage		9.  Purple"
  echo "  4.  Olive		10. Magenta"
  echo "  5.  Viridian		11. Pink"
  echo "  6.  Prussian Green	12. Red"
  config_num "accent color" 12
  color="${color_variants["${array_num}"]}"

  echo -e "${blgreen}Which theme variant do you want to use?${nc}"
  echo "  1.  Auto"
  echo "  2.  Light"
  echo "  3.  Dark"
  while true; do
    config_num "theme variant" 3
    theme="${theme_variants["${array_num}"]}"
    theme_variants
    if [[ "${failed}" != true ]]; then # let user pick another option if system theme cant be detected
      break
    fi
  done

  config_yn "gtk3" "GTK3" "true"

  config_yn "gtk4" "GTK4/Libadwaita" "false"

  if [[ -n "${gnome_version}" ]]; then
    config_yn "gnome-shell" "GNOME Shell" "true"
  fi

  config_yn "icons" "icon" "true"

  config_yn "cursors" "cursor" "true"

  config_yn "sounds" "sound" "true"

  config_yn "gtksourceview" "GtkSourceView" "true"

  if [[ -d "${firefox_dir_standard}" ]]; then
    config_yn "standard" "Firefox" "true" "${firefox_dir_standard}"
  fi

  if [[ -d "${firefox_dir_snap}" ]]; then
    config_yn "snap" "Firefox" "true" "${firefox_dir_snap}"
  fi

  if [[ -d "${firefox_dir_flatpak}" ]]; then
    config_yn "flatpak" "Firefox" "true" "${firefox_dir_flatpak}"
  fi

  if [[ "$(command -v snap)" ]]; then
    config_yn "snap" "Snap" "false"
  fi
}

##############################################################
#  Read previous config and reconfigure if there are issues  #
##############################################################

declare -A variants # An associative array is needed to read the configuration
variants[theme]="${theme_variants[*]}"
variants[color]="${color_variants[*]}"
variants[firefox]="${firefox_variants[*]}"
variants[enabled]="${themes[*]}"

if [[ -s "${installed_versions}" && "${reconfigure}" != true ]]; then
  for line in "${config_array[@]}"; do
    declare -a "${line}"
    read -r -a previous_array <<< "$(grep "^${line}: " "${installed_versions}" | cut -f 2- -d ' ')"
    end=$((${#previous_array[@]} - 1))
    for ((i=0;i<=end;i++)); do
      if echo "${variants[${line}]}" | grep -q "${previous_array[${i}]}" ; then
        declare "${line}[${i}]"="${previous_array[${i}]}"
      else
        config_issue=true
      fi
    done
  done

  for line in "${config_string[@]}"; do
    previous_string="$(grep "^${line}: " "${installed_versions}" | awk '{print $2}')"
    if echo "${variants[${line}]}" | grep -q "${previous_string}"; then
      declare "${line}"="${previous_string}"
    else
      config_issue=true
    fi
  done

  if [[ "${config_issue}" == true ]]; then
    configure
  else
    echo -e "${byellow}Updating themes using previous configuration.${nc}"
    echo -e "${byellow}Use '${0} --reconfigure' if you want to change anything.${nc}"

    theme_variants
  fi
else
  configure
fi

####################################################################################
#  Check if the themes need to be reinstalled because of changes to configuration  #
####################################################################################

for f in "${firefox[@]}"; do
  if [[ -s "${installed_versions}" && "${color}" != "$(grep "^dg-firefox-theme-${f}:" "${installed_versions}" | awk '{print $3}')" ]]; then
    declare "firefox_${f}_changed"=true
  fi
done

if [[ -s "${installed_versions}" && "${gnome_version}" != "$(grep "^gnome-shell:" "${installed_versions}" | awk '{print $2}')" ]]; then
  gnome_shell_changed=true
fi

if [[ -s "${installed_versions}" && ( "${color}" != "$(grep "^dg-libadwaita:" "${installed_versions}" | awk '{print $3}')" || "${suffix}" != "$(grep "^dg-libadwaita" "${installed_versions}" | awk '{print $4}')" ) ]]; then
  gtk4_changed=true
fi

for p in "${dg_yaru_parts[@]}"; do
  if printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "${p}" && [[ -s "${installed_versions}" ]]; then
    if ! grep "^dg-yaru: " "${installed_versions}" | cut -f 3- -d ' ' | grep -q "${p}"; then
      dg_yaru_changed=true
    fi
  elif [[ -s "${installed_versions}" ]]; then
    if grep "^dg-yaru: " "${installed_versions}" | cut -f 3- -d ' ' | grep -q "${p}"; then
      dg_yaru_changed=true
    fi
  fi
done

# Is user updating?
if [[ -s "${installed_versions}" && "${force}" != true && "${config_issue}" != true ]]; then
  update=true
fi

#############################################################
#  Update installed-versions.txt or create it if necessary  #
#############################################################

if [[ ! -f "${installed_versions}" ]]; then
  echo "This file is used by the install script to find out what versions of the themes are installed" > "${installed_versions}"
fi

add_config() {
  if grep -q "^${1}" "${installed_versions}"; then
    sed -i "s/^${1}.*/${1}: ${2}/g" "${installed_versions}"
  else
    echo "${1}: ${2}" >> "${installed_versions}"
  fi
}

add_config "color" "${color}"
add_config "theme" "${theme}"
add_config "enabled" "${enabled[*]}"
add_config "firefox" "${firefox[*]}"
add_config "gnome-shell" "${gnome_version}"

###################
#  Install Theme  #
###################

install_dg_adw_gtk3() {
  echo -e "${green}Installing ${nc}${bold}dg-adw-gtk3${nc} theme in ${bold}${HOME}/.local/share${nc}"
  git submodule update --init "src/dg-adw-gtk3"
  cd "${gtk3_src_dir}" || exit
  dg_adw_gtk3_version="$(git rev-parse HEAD)"
  if [[ "$verbose" == true ]]; then
    if [[ ! -d "${gtk3_src_dir}/build" ]]; then
      meson "-Dprefix=${HOME}/.local" build
    fi
    ninja -C build --verbose install
  else
    if [[ ! -d "${gtk3_src_dir}/build" ]]; then
      meson "-Dprefix=${HOME}/.local" build  > /dev/null
    fi
    if ninja -C build install | grep --color -E "ERROR|FAILED"; then
      echo ""
      echo -e "Run ${bold}${0} --verbose${nc} to see full log."
      echo -e "You can also try running ${bold}${0} --clean${nc} and then run ${bold}${0}${nc} again."
      exit 1
    fi
  fi
  cd "${repo_dir}" || exit
  add_config "dg-adw-gtk3" "${dg_adw_gtk3_version}"
}

install_dg_yaru() {
  echo -e "${green}Installing ${nc}${bold}dg-yaru${nc} theme in ${bold}/usr/share${nc}"
  git submodule update --init "src/dg-yaru"
  cd "${dg_yaru_src_dir}" || exit
  dg_yaru_version="$(git rev-parse HEAD)"
  if [[ "$verbose" == true && ! -d "${dg_yaru_src_dir}/build" ]]; then
    meson build
  elif [[ "$verbose" != true && ! -d "${dg_yaru_src_dir}/build" ]]; then
    meson build > /dev/null
  fi

  # Enable/disable parts of the theme based on user configuration
  for part in "${dg_yaru_parts[@]}"; do
    if ! printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "${part}" && [[ -n "$(meson configure build | awk -v part="${part}" '$1=="part"' | awk '$2==true')" ]]; then
      meson configure build "-D${part}=false"
    elif printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "${part}" && [[ -n "$(meson configure build | awk -v part="${part}" '$1=="part"' | awk '$2=="false"')" ]]; then
      meson configure build "-D${part}=true"
    fi
  done

  # Enable correct shell theme version if not already enabled
  if [[ -n "${gnome_version}" && -z "$(meson configure build | awk '$1=="gnome-shell-version"' | awk -v ver="${gnome_version}" '$2=="ver"')" ]]; then
    meson configure build "-Dgnome-shell-version=${gnome_version}"
  fi
  if [[ "$verbose" == true ]]; then
    sudo ninja -C build --verbose install
  else
    if sudo ninja -C build install | grep --color -E "ERROR|FAILED"; then
      echo ""
      echo -e "Run ${bold}${0} --verbose${nc} to see full log."
      echo -e "You can also try running ${bold}${0} --clean${nc} and then run ${bold}${0}${nc} again."
      exit 1
    fi
  fi
  cd "${repo_dir}" || exit
  add_config "dg-yaru" "${dg_yaru_version}"
  for i in "${enabled[@]}"; do
    if printf '%s\0' "${dg_yaru_parts[@]}" | grep -Fxqz -- "${i}"; then
      sed -i "/^dg-yaru/s/$/ ${i}/" "${installed_versions}"
    fi
  done
}

install_dg_libadwaita() {
  echo -e "${green}Installing ${nc}${bold}dg-libadwaita${nc} theme in ${bold}${gtk4_dir}${nc}"
  git submodule update --init "src/dg-libadwaita"
  cd "${gtk4_src_dir}" || exit
  dg_libadwaita_version="$(git rev-parse HEAD)"
  source install.sh "${color}" "${suffix}"
  cd "${repo_dir}" || exit
  if grep -q "^dg-libadwaita" "${installed_versions}"; then
    sed -i "/^dg-libadwaita/c\dg-libadwaita: ${dg_libadwaita_version} ${color} ${suffix}" "${installed_versions}"
  else
    echo "dg-libadwaita: ${dg_libadwaita_version} ${color} ${suffix}" >> "${installed_versions}"
  fi
  add_config "dg-libadwaita" "${dg_libadwaita_version}"
  sed -i "/^dg-libadwaita/s/$/ ${color} ${suffix}/" "${installed_versions}"
}

install_dg_firefox_theme() {
  git submodule update --init "src/dg-firefox-theme"
  cd "${firefox_src_dir}" || exit
  dg_firefox_theme_version="$(git rev-parse HEAD)"
  firefoxdir="firefox_dir_${1}"
  firefoxfolder=${!firefoxdir}
  source install.sh
  installed_firefox=true
  cd "${repo_dir}" || exit
  add_config "dg-firefox-theme-${1}" "${dg_firefox_theme_version}"
  sed -i "/^dg-firefox-theme-${1}/s/$/ ${color}/" "${installed_versions}"
}

install_snap() {
  if ! snap info gtk-common-themes | grep -q "installed"; then
    echo -e "${green}Installing ${nc}${bold}gtk-common-themes${nc} snap."
    sudo snap install gtk-common-themes
  fi
  if ! snap info dg-adw-gtk3-theme | grep -q "installed"; then
    echo -e "${green}Installing ${nc}${bold}dg-adw-gtk3-theme${nc} snap."
    sudo snap install dg-adw-gtk3-theme
  else
    echo -e "Checking if ${bold}dg-adw-gtk3-theme${nc} snap can be updated."
    sudo snap refresh dg-adw-gtk3-theme
  fi
  if printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "gtk3"; then
    for i in $(snap connections | grep gtk-common-themes:gtk-3-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap connect "${i}:gtk-3-themes" "dg-adw-gtk3-theme:gtk-3-themes"
    done
  else
    for i in $(snap connections | grep dg-adw-gtk3-theme:gtk-3-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap disconnect "${i}:gtk-3-themes" "dg-adw-gtk3-theme:gtk-3-themes"
    done
  fi
  if printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "icons"; then
    for i in $(snap connections | grep gtk-common-themes:icon-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap connect "${i}:icon-themes" "dg-adw-gtk3-theme:icon-themes"
    done
  else
    for i in $(snap connections | grep dg-adw-gtk3-theme:icon-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap disconnect "${i}:icon-themes" "dg-adw-gtk3-theme:icon-themes"
    done
  fi
  if printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "sounds"; then
    for i in $(snap connections | grep gtk-common-themes:sound-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap connect "${i}:sound-themes" "dg-adw-gtk3-theme:sound-themes"
    done
  else
    for i in $(snap connections | grep dg-adw-gtk3-theme:sound-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap disconnect "${i}:sound-themes" "dg-adw-gtk3-theme:sound-themes"
    done
  fi
}

# Install dg-adw-gtk3 if it's enabled
if printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "gtk3"; then
  if [[ "${update}" == true ]]; then
    if [[ "$(git submodule status "src/dg-adw-gtk3" | tr -d '+' | awk '{print $1}' )" != "$(grep "^dg-adw-gtk3" "${installed_versions}" | awk '{print $2}')" ]]; then
      install_dg_adw_gtk3
      did_update=true
    else
      echo -e "${bold}dg-adw-gtk3${nc} is up to date, not reinstalling"
    fi
  else
    install_dg_adw_gtk3
  fi
else
  if [[ "$(compgen -G "${HOME}"/.local/share/themes/dg-adw-gtk3*)" ]]; then
    echo -e "Use './uninstall.sh --gtk3' to remove ${bold}dg-adw-gtk3${nc}, which was previously installed."
  fi
fi

# Install dg-yaru if it's enabled
if printf '%s\0' "${enabled[@]}" | grep -Exqz -- "gnome-shell|icons|cursors|sounds"; then
  if [[ "${update}" == true ]]; then
    if [[ "$(git submodule status "src/dg-yaru" | tr -d '+' | awk '{print $1}' )" != "$(grep "^dg-yaru" "${installed_versions}" | awk '{print $2}')" || "${dg_yaru_changed}" == true || "${gnome_shell_changed}" == true ]]; then
      install_dg_yaru
      did_update=true
    else
      echo -e "${bold}dg-yaru${nc} is up to date, not reinstalling"
    fi
  else
    install_dg_yaru
  fi
fi
if ! printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "gnome-shell"; then
  if [[ "$(compgen -G /usr/share/themes/dg-yaru*)" || "$(compgen -G /usr/share/gnome-shell/theme/dg-yaru*)" ]]; then
    echo -e "Use './uninstall.sh --gnome-shell' to remove dg-yaru ${bold}GNOME Shell${nc} theme, which was previously installed."
  fi
fi
if ! printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "icons"; then
  if [[ -d "/usr/share/icons/dg-yaru/index.theme" || "$(compgen -G /usr/share/icons/dg-yaru-*)" ]]; then
    echo -e "Use './uninstall.sh --icons' to remove dg-yaru ${bold}icon${nc} theme, which was previously installed."
  fi
fi
if ! printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "cursors"; then
  if [[ -d "/usr/share/icons/dg-yaru/cursor.theme" || -d "/usr/share/icons/dg-yaru/cursors" ]]; then
    echo -e "Use './uninstall.sh --cursors' to remove dg-yaru ${bold}cursor${nc} theme, which was previously installed."
  fi
fi
if ! printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "sounds"; then
  if [[ -d "/usr/share/sounds/dg-yaru" ]]; then
    echo -e "Use './uninstall.sh --sounds' to remove dg-yaru ${bold}sound${nc} theme, which was previously installed."
  fi
fi
if ! printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "gtksourceview"; then
  if [[ "$(compgen -G /usr/share/gtksourceview-5/styles/dg-yaru*)" || "$(compgen -G /usr/share/gtksourceview-4/styles/dg-yaru*)" ||"$(compgen -G /usr/share/gtksourceview-3.0/styles/dg-yaru*)" || "$(compgen -G /usr/share/gtksourceview-2.0/styles/dg-yaru*)" ]]; then
    echo -e "Use './uninstall.sh --gtksourceview' to remove dg-yaru ${bold}GtkSourceView${nc} theme, which was previously installed."
  fi
fi

# Install dg-libadwaita if it's enabled
if printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "gtk4"; then
  if [[ "${update}" == true ]]; then
    if [[ ( "$(git submodule status "src/dg-libadwaita" | tr -d '+' | awk '{print $1}' )" != "$(grep "^dg-libadwaita" "${installed_versions}" | awk '{print $2}')" ) ||
      "${gtk4_changed}" == true ]]; then
      install_dg_libadwaita
      did_update=true
    else
      echo -e "${bold}dg-libadwaita${nc} is up to date, not reinstalling"
    fi
  else
    install_dg_libadwaita
  fi
else
  if [[ -d "${gtk4_dir}/mac-icons" && -s "${gtk4_dir}/gtk.css" ]]; then
    echo -e "Use './uninstall.sh --gtk4' to remove ${bold}dg-libadwaita${nc}, which was previously installed."
  fi
fi

# Install dg-firefox-theme if it's enabled
for f in "${firefox[@]}"; do
  if [[ "${update}" == true ]]; then
    changed="firefox_${f}_changed"
    if [[ ( "$(git submodule status "src/dg-firefox-theme" | tr -d '+' | awk '{print $1}' )" != "$(grep "^dg-firefox-theme-${f}" "${installed_versions}" | awk '{print $2}')" ) || "${!changed}" == true ]]; then
      install_dg_firefox_theme "${f}"
    fi
  else
    install_dg_firefox_theme "${f}"
  fi
done
if [[ -n "${firefox[*]}" && "${installed_firefox}" != true ]]; then
  echo -e "${bold}dg-firefox-theme${nc} is up to date, not reinstalling"
elif [[ -n "${firefox[*]}" ]]; then
  did_update=true
fi
if ! printf '%s\0' "${firefox[@]}" | grep -Fxqz -- "standard" && [[ "$(compgen -G "${firefox_dir_standard}"/*/chrome/dg-firefox-theme)" ]]; then
  echo -e "Use './uninstall.sh -f standard' to remove the standard variant of ${bold}dg-firefox-theme${nc}, which was previously installed."
fi
if ! printf '%s\0' "${firefox[@]}" | grep -Fxqz -- "snap" && [[ "$(compgen -G "${firefox_dir_snap}"/*/chrome/dg-firefox-theme)" ]]; then
  echo -e "Use './uninstall.sh -f snap' to remove the Snap variant of ${bold}dg-firefox-theme${nc}, which was previously installed."
fi
if ! printf '%s\0' "${firefox[@]}" | grep -Fxqz -- "flatpak" && [[ "$(compgen -G "${firefox_dir_flatpak}"/*/chrome/dg-firefox-theme)" ]]; then
  echo -e "Use './uninstall.sh -f flatpak' to remove the Flatpak variant of ${bold}dg-firefox-theme${nc}, which was previously installed."
fi

# Install dg-adw-gtk3-theme snap if it's enabled and there is an internet connection
if printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "snap"; then
  if [[ "$(command -v snap)" ]] && echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1 ; then
    install_snap
  elif ! snap list | grep -q "dg-adw-gtk3-theme" && ! echo -e "GET http://google.com HTTP/1.0\n\n" | nc google.com 80 > /dev/null 2>&1 ; then
    echo -e "You are offline, not installing ${bold}dg-adw-gtk3-theme${nc} Snap."
  elif [[ ! "$(command -v snap)" ]]; then
    echo -e "${byellow}WARNING:${nc} ${bold}'snap'${nc} is not installed, not installing ${bold}dg-adw-gtk3-theme${nc} snap"
  fi
else
  if snap list | grep -q "dg-adw-gtk3-theme"; then
    echo -e "Use './uninstall.sh --snap' to remove ${bold}dg-adw-gtk3-theme${nc} snap, which was previously installed."
  fi
fi
##################
#  Enable Theme  #
##################

enable_gtk3() {
  if [[ "$(gsettings get org.gnome.desktop.interface gtk-theme)" != "'dg-adw-gtk3-${color}${suffix}'" ]]; then
    echo -e "Changing gtk3 theme to ${bold}dg-adw-gtk3-${color}${suffix}${nc}."
    gsettings set org.gnome.desktop.interface gtk-theme "dg-adw-gtk3-${color}${suffix}"
  fi
}

enable_icons() {
  if [[ "$(gsettings get org.gnome.desktop.interface icon-theme)" != "'${dg_yaru}'" ]]; then
    echo -e "Changing icon theme to ${bold}${dg_yaru}${nc}."
    gsettings set org.gnome.desktop.interface icon-theme "${dg_yaru}"
  fi
}

enable_cursors() {
  if [[ "$(gsettings get org.gnome.desktop.interface cursor-theme)" != "'dg-yaru'" ]]; then
    echo -e "Changing cursor theme to ${bold}dg-yaru${nc}."
    gsettings set org.gnome.desktop.interface cursor-theme "dg-yaru"
  fi
}

enable_sounds() {
  if [[ "$(gsettings get org.gnome.desktop.sound theme-name)" != "'dg-yaru'" ]]; then
    echo -e "Changing sound theme to ${bold}dg-yaru${nc}."
    gsettings set org.gnome.desktop.sound theme-name dg-yaru
  fi
}

enable_gnome_shell() {
  if [[ "$(command -v gnome-extensions)" ]] && gnome-extensions list | grep -q user-theme@gnome-shell-extensions.gcampax.github.com; then
    gnome-extensions enable user-theme@gnome-shell-extensions.gcampax.github.com
    if [[ "$(gsettings get org.gnome.shell.extensions.user-theme name)" != "'${dg_yaru}'" ]]; then
      echo -e "Changing GNOME Shell theme to ${bold}${dg_yaru}${nc}."
      gsettings set org.gnome.shell.extensions.user-theme name "${dg_yaru}"
    fi
  else
    echo -e "${bold}'User Themes'${byellow} GNOME Shell Extension not found, not enabling GNOME Shell theme.${nc}"
  fi
}

# dg-yaru naming
if [[ "${color}" == "orange" ]]; then
  dg_yaru="dg-yaru${suffix}"
else
  dg_yaru="dg-yaru-${color}${suffix}"
fi

# Set color scheme
if [[ -n "${color_scheme}" && "$(command -v gsettings)" ]]; then
  gsettings set org.gnome.desktop.interface color-scheme "${color_scheme}"
fi

# Enable themes
if [[ "$(command -v gsettings)" ]]; then
  for t in "${enableable_themes[@]}"; do
    if printf '%s\0' "${enabled[@]}" | grep -Fxqz -- "${t}"; then
      function="$(echo "enable_${t}"| tr "-" "_" )"
      "${function}"
    fi
  done
else
  echo -e "${bold}'gsettings'${byellow} not found, not enabling themes.${nc}"
fi

if [[ ( "${did_update}" == true && "${update}" == true ) || "${update}" != true ]]; then
  echo -e "${byellow}Log out and log back in for everything to be updated${nc}"
fi
