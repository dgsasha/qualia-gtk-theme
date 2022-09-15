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

color_variants=('orange' 'bark' 'sage' 'olive' 'viridian' 'prussiangreen' 'blue' 'purple' 'magenta' 'red')
theme_variants=('auto' 'light' 'dark')
firefox_variants=('standard' 'flatpak' 'snap')
gnome_versions=('42' '43')
enableable_themes=('gtk3' 'gnome-shell' 'icons' 'cursors' 'sounds') # Themes that can be enabled with gsettings
dg_yaru_parts=('gnome-shell' 'icons' 'cursors' 'sounds')

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

enabled_themes=()
firefox=()

while [ $# -gt 0 ]; do
  case "${1}" in
    -r|--reconfigure)
      reconfigure="true"
      shift
      ;;
    -f|--force)
      force="true"
      shift
      ;;
    -v|--verbose)
      verbose="true"
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

color_scheme=""
theme_variants() {
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
        failed="true"
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

gnome_version=""
if [[ "$(command -v gnome-shell)" ]]; then
  shell_version="$(gnome-shell --version | cut -d ' ' -f 3 | cut -d . -f -1)"
  for version in "${gnome_versions[@]}"; do
    if [[ "${shell_version:-}" == "${version}" ]]; then
      gnome_version="${version}"
    fi
  done
fi

configure() {
  num=""
  echo -e "${blgreen}Which accent color do you want to use?${nc}"
  echo "  1.  Orange		6.  Prussian Green"
  echo "  2.  Bark		7.  Blue"
  echo "  3.  Sage		8.  Purple"
  echo "  4.  Olive		9.  Magenta"
  echo "  5.  Viridian		10. Red"
  while ! [[ "${num}" -ge 1 && "${num}" -le 10 ]]; do
    echo -en "${bold}Enter the number corresponding to the accent color you want [Default: 1]: ${nc}"
    read -r num
    if [[ -z "${num}" ]]; then
      num=1
    fi
  done
  array_num="$(("${num}" - 1))"
  color="${color_variants["${array_num}"]}"

  num=""
  echo -e "${blgreen}Which theme variant do you want to use?${nc}"
  echo "  1.  Auto"
  echo "  2.  Light"
  echo "  3.  Dark"
  while true; do
    failed=""
    while ! [[ "${num}" -ge 1 && "${num}" -le 3 ]]; do
      echo -en "${bold}Enter the number corresponding to the theme variant you want [Default: 1]: ${nc}"
      read -r num
      if [[ -z "${num}" ]]; then
        num=1
      fi
    done
    array_num="$(("${num}" - 1))"
    theme="${theme_variants["${array_num}"]}"
    theme_variants
    if [[ "${failed}" != "true" ]]; then # let user pick another option if system theme cant be detected
      break
    fi
    num=""
  done
  yn=""
  while true; do
    echo -ne "${blgreen}Do you want to install the ${nc}${bold}GTK3${blgreen} theme?${nc} ${bold}[Y/n]: ${nc}"
    read -r yn
    if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
      if [[ ! "$(command -v meson)" ]]; then
        echo -e "${bold}'meson'${bred} not found, can't install GTK3 theme.${nc}"
        continue
      fi
      if [[ "$(command -v ninja)" ]]; then
        enabled_themes+=("gtk3")
        break
      else
         echo -e "${bold}'ninja'${bred} not found, can't install GTK3 theme.${nc}"
         continue
      fi
   elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
      break
    fi
  done

  yn=""
  while true; do
    echo -ne "${blgreen}Do you want to install the ${nc}${bold}GTK4/Libadwaita${blgreen} theme?${nc} ${bold}[Y/n]: ${nc}"
    read -r yn
    if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
      enabled_themes+=("gtk4")
      break
   elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
      break
    fi
  done

  if [[ -n "${gnome_version}" ]]; then
    yn=""
    while true; do
      echo -ne "${blgreen}Do you want to install the ${nc}${bold}GNOME Shell${blgreen} theme?${nc} ${bold}[Y/n]: ${nc}"
      read -r yn
      if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
        if [[ ! "$(command -v meson)" ]]; then
          echo -e "${bold}'meson'${bred} not found, can't install GNOME Shell theme.${nc}"
          continue
        fi
        if [[ "$(command -v ninja)" ]]; then
          enabled_themes+=("gnome-shell")
          break
        else
           echo -e "${bold}'ninja'${bred} not found, can't install GNOME Shell theme.${nc}"
           continue
        fi
    elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
        break
      fi
    done
  fi

  yn=""
  while true; do
    echo -ne "${blgreen}Do you want to install the ${nc}${bold}icon${blgreen} theme?${nc} ${bold}[Y/n]: ${nc}"
    read -r yn
    if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
      if [[ ! "$(command -v meson)" ]]; then
        echo -e "${bold}'meson'${bred} not found, can't install icon theme.${nc}"
        continue
      fi
      if [[ "$(command -v ninja)" ]]; then
        enabled_themes+=("icons")
        break
      else
         echo -e "${bold}'ninja'${bred} not found, can't install icon theme.${nc}"
         continue
      fi
   elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
      break
    fi
  done

  yn=""
  while true; do
    echo -ne "${blgreen}Do you want to install the ${nc}${bold}cursor${blgreen} theme?${nc} ${bold}[Y/n]: ${nc}"
    read -r yn
    if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
      if [[ ! "$(command -v meson)" ]]; then
        echo -e "${bold}'meson'${bred} not found, can't install cursor theme.${nc}"
        continue
      fi
      if [[ "$(command -v ninja)" ]]; then
        enabled_themes+=("cursors")
        break
      else
         echo -e "${bold}'ninja'${bred} not found, can't install cursor theme.${nc}"
         continue
      fi
   elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
      break
    fi
  done

  yn=""
  while true; do
    echo -ne "${blgreen}Do you want to install the ${nc}${bold}sound${blgreen} theme?${nc} ${bold}[Y/n]: ${nc}"
    read -r yn
    if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
      if [[ ! "$(command -v meson)" ]]; then
        echo -e "${bold}'meson'${bred} not found, can't install sound theme.${nc}"
        continue
      fi
      if [[ "$(command -v ninja)" ]]; then
        enabled_themes+=("sounds")
        break
      else
        echo -e "${bold}'ninja'${bred} not found, can't install sound theme.${nc}"
        continue
      fi
   elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
      break
    fi
  done

  if [[ -d "${HOME}/.mozilla/firefox" ]]; then
    yn=""
    while true; do
      echo -ne "${blgreen}Do you want to install the ${nc}${bold}Firefox${blgreen} theme in ${nc}${bold}${HOME}/.mozilla${nc}${blgreen}?${nc} ${bold}[Y/n]: ${nc}"
      read -r yn
      if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
        firefox+=("standard")
        break
      elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
        break
      fi
    done
  fi

  if [[ -d "${HOME}/snap/firefox/common/.mozilla/firefox" ]]; then
    yn=""
    while true; do
      echo -ne "${blgreen}Do you want to install the ${nc}${bold}Firefox${blgreen} theme in ${nc}${bold}${HOME}/snap/firefox${blgreen}?${nc} ${bold}[Y/n]: ${nc}"
      read -r yn
      if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
        firefox+=("snap")
        break
      elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
        break
      fi
    done
  fi

  if [[ -d "${HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox" ]]; then
    yn=""
    while true; do
      echo -ne "${blgreen}Do you want to install the ${nc}${bold}Firefox${blgreen} theme in ${nc}${bold}${HOME}/.var/app/org.mozilla.firefox${blgreen}?${nc} ${bold}[Y/n]: ${nc}"
      read -r yn
      if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
        firefox+=("flatpak")
        break
      elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
        break
      fi
    done
  fi

  if [[ "$(command -v snap)" ]]; then
    yn=""
    while true; do
      echo -ne "${blgreen}Do you want to enable ${nc}${bold}Snap${blgreen} support?${nc} ${bold}[Y/n]: ${nc}"
      read -r yn
      if [[ -z "${yn}" || "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "y" ]]; then
        enabled_themes+=("snap")
        break
    elif [[ "$(echo "${yn}" | tr '[:upper:]' '[:lower:]')" == "n" ]]; then
        break
      fi
    done
  fi
}

# Either configure theme or use previous configuration
if [[ -s "${installed_versions}" && "${reconfigure}" != "true" ]]; then
  if grep -q "^enabled: " "${installed_versions}" && grep -q "^color:" "${installed_versions}" && grep -q "^theme:" "${installed_versions}"; then
    read -r -a previously_enabled_themes <<< "$(grep "^enabled: " "${installed_versions}" | cut -f 2- -d ' ')"
    enabled_themes=("${previously_enabled_themes[@]}")
    color="$(grep "^color:" "${installed_versions}" | awk '{print $2}')"
    theme="$(grep "^theme:" "${installed_versions}" | awk '{print $2}')"
    echo -e "${byellow}Updating themes using previous configuration.${nc}"
    echo -e "${byellow}Use '${0} --reconfigure' if you want to change anything.${nc}"
    if grep -q "^firefox: " "${installed_versions}"; then
      read -r -a previously_enabled_firefox <<< "$(grep "^firefox: " "${installed_versions}" | cut -f 2- -d ' ')"
      firefox=("${previously_enabled_firefox[@]}")
    fi
    theme_variants
  else # if something is wrong with the file
    rm -rf "${installed_versions}"
    configure
  fi
else # user is either reconfiguring or installing for the first time
  if [[ -s "${installed_versions}" ]] && grep -q "^enabled: " "${installed_versions}"; then
    read -r -a previously_enabled_themes <<< "$(grep "^enabled: " "${installed_versions}" | cut -f 2- -d ' ')"
  fi
  if [[ -s "${installed_versions}" ]] && grep -q "^firefox: " "${installed_versions}"; then
    read -r -a previously_enabled_firefox <<< "$(grep "^firefox: " "${installed_versions}" | cut -f 2- -d ' ')"
  fi
  configure
fi

# Check if the themes need to be reinstalled because of changes to configuration
for f in "${firefox[@]}"; do
  if [[ -s "${installed_versions}" && "${f}" == "standard" && "${color}" != "$(grep "^dg-firefox-theme-standard:" "${installed_versions}" | awk '{print $3}')" ]]; then
    firefox_standard_changed="true"
  fi
  if [[ -s "${installed_versions}" && "${f}" == "snap" && "${color}" != "$(grep "^dg-firefox-theme-snap:" "${installed_versions}" | awk '{print $3}')" ]]; then
    firefox_snap_changed="true"
  fi
  if [[ -s "${installed_versions}" && "${f}" == "flatpak" && "${color}" != "$(grep "^dg-firefox-theme-flatpak:" "${installed_versions}" | awk '{print $3}')" ]]; then
    firefox_flatpak_changed="true"
  fi
done

if [[ -s "${installed_versions}" && "${gnome_version}" != "$(grep "^gnome-shell:" "${installed_versions}" | awk '{print $2}')" ]]; then
  gnome_shell_changed="true"
fi

if [[ -s "${installed_versions}" && ( "${color}" != "$(grep "^dg-libadwaita:" "${installed_versions}" | awk '{print $3}')" || "${suffix}" != "$(grep "^dg-libadwaita" "${installed_versions}" | awk '{print $4}')" ) ]]; then
  gtk4_changed="true"
fi

for p in "${dg_yaru_parts[@]}"; do
  if printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "${p}" && [[ -s "${installed_versions}" ]]; then
    if ! grep "^dg-yaru: " "${installed_versions}" | cut -f 3- -d ' ' | grep -q "${p}"; then
      dg_yaru_changed="true"
    fi
  elif [[ -s "${installed_versions}" ]]; then
    if grep "^dg-yaru: " "${installed_versions}" | cut -f 3- -d ' ' | grep -q "${p}"; then
      dg_yaru_changed="true"
    fi
  fi
done

# Is user updating?
if [[ -s "${installed_versions}" && "${force}" != "true" ]]; then
  update="true"
fi

# Either create or update installed-versions.txt
if [[ ! -s "${installed_versions}" ]]; then
  { echo "This file is used by the install script to find out what versions of the themes are installed"
    echo ""
    echo "color: ${color}"
    echo "theme: ${theme}"
    echo "enabled: ${enabled_themes[*]}"
    echo "firefox: ${firefox[*]}"
    echo "gnome-shell: ${gnome_version}"
  } >> "${installed_versions}"
else
  if grep -q "^color" "${installed_versions}"; then
    sed -i "/^color/c\color: ${color}" "${installed_versions}"
  else
    echo "color: ${color}" >> "${installed_versions}"
  fi
  if grep -q "^theme" "${installed_versions}"; then
    sed -i "/^theme/c\theme: ${theme}" "${installed_versions}"
  else
    echo "theme: ${theme}" >> "${installed_versions}"
  fi
  if grep -q "^enabled" "${installed_versions}"; then
    sed -i "/^enabled/c\enabled: ${enabled_themes[*]}" "${installed_versions}"
  else
    echo "enabled: ${enabled_themes[*]}" >> "${installed_versions}"
  fi
  if grep -q "^firefox" "${installed_versions}"; then
    sed -i "/^firefox/c\firefox: ${firefox[*]}" "${installed_versions}"
  else
    echo "firefox: ${firefox[*]}" >> "${installed_versions}"
  fi
  if grep -q "^gnome-shell" "${installed_versions}"; then
    sed -i "/^gnome-shell/c\gnome-shell: ${gnome_version}" "${installed_versions}"
  else
    echo "gnome-shell: ${gnome_version}" >> "${installed_versions}"
  fi
fi

install_dg_adw_gtk3() {
  if printf '%s\0' "${previously_enabled_themes[@]}" | grep -Fxqz -- "gtk3" && [[ "${force}" != "true" ]]; then
    echo -e "${green}Updating ${nc}${bold}dg-adw-gtk3${nc} theme in ${bold}${HOME}/.local/share${nc}"
  else
    echo -e "${green}Installing ${nc}${bold}dg-adw-gtk3${nc} theme in ${bold}${HOME}/.local/share${nc}"
  fi
  git submodule update --init "src/dg-adw-gtk3"
  cd "${gtk3_src_dir}" || exit
  dg_adw_gtk3_version="$(git rev-parse HEAD)"
  if [[ "$verbose" == "true" ]]; then
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
  if grep -q "^dg-adw-gtk3" "${installed_versions}"; then
    sed -i "/^dg-adw-gtk3/c\dg-adw-gtk3: ${dg_adw_gtk3_version}" "${installed_versions}"
  else
    echo "dg-adw-gtk3: ${dg_adw_gtk3_version}" >> "${installed_versions}"
  fi
}

install_dg_yaru() {
  if printf '%s\0' "${previously_enabled_themes[@]}" | grep -Exqz -- "gnome-shell|icons|cursors|sounds" && [[ "${force}" != "true" ]]; then
    echo -e "${green}Updating ${nc}${bold}dg-yaru${nc} theme in ${bold}/usr/share${nc}"
  else
    echo -e "${green}Installing ${nc}${bold}dg-yaru${nc} theme in ${bold}/usr/share${nc}"
  fi
  git submodule update --init "src/dg-yaru"
  cd "${dg_yaru_src_dir}" || exit
  dg_yaru_version="$(git rev-parse HEAD)"
  if [[ "$verbose" == "true" && ! -d "${dg_yaru_src_dir}/build" ]]; then
    meson build
  elif [[ "$verbose" != "true" && ! -d "${dg_yaru_src_dir}/build" ]]; then
    meson build > /dev/null
  fi
  for part in "${dg_yaru_parts[@]}"; do
    if ! printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "${part}" && [[ -n "$(meson configure build | awk -v part="${part}" '$1=="part"' | awk '$2=="true"')" ]]; then
      meson configure build "-D${part}=false"
    elif printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "${part}" && [[ -n "$(meson configure build | awk -v part="${part}" '$1=="part"' | awk '$2=="false"')" ]]; then
      meson configure build "-D${part}=true"
    fi
  done

  # Enable correct shell theme version if not already enabled
  if [[ -n "${gnome_version}" && -z "$(meson configure build | awk '$1=="gnome-shell-version"' | awk -v ver="${gnome_version}" '$2=="ver"')" ]]; then
    meson configure build "-Dgnome-shell-version=${gnome_version}"
  fi
  if [[ "$verbose" == "true" ]]; then
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
  if grep -q "^dg-yaru" "${installed_versions}"; then
    sed -i "/^dg-yaru/c\dg-yaru: ${dg_yaru_version}" "${installed_versions}"
  else
    echo "dg-yaru: ${dg_yaru_version}" >> "${installed_versions}"
  fi
  for enabled in "${enabled_themes[@]}"; do
    if printf '%s\0' "${dg_yaru_parts[@]}" | grep -Fxqz -- "${enabled}"; then
      sed -i "/^dg-yaru/s/$/ ${enabled}/" "${installed_versions}"
    fi
  done
}

install_dg_libadwaita() {
  if printf '%s\0' "${previously_enabled_themes[@]}" | grep -Fxqz -- "gtk4" && [[ "${gtk4_changed}" != "true" && "${force}" != "true" ]]; then
    echo -e "${green}Updating ${nc}${bold}dg-libadwaita${nc} theme in ${bold}${gtk4_dir}${nc}"
  else
    echo -e "${green}Installing ${nc}${bold}${color}${suffix} dg-libadwaita${nc} theme in ${bold}${gtk4_dir}${nc}"
  fi
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
}

install_dg_firefox_theme() {
  git submodule update --init "src/dg-firefox-theme"
  cd "${firefox_src_dir}" || exit
  dg_firefox_theme_version="$(git rev-parse HEAD)"
  if [[ "${1}" == "flatpak" ]]; then
    firefox_dir="${HOME}/.var/app/org.mozilla.firefox/.mozilla/firefox"
  elif [[ "${1}" == "snap" ]]; then
    firefox_dir="${HOME}/snap/firefox/common/.mozilla/firefox"
  elif [[ "${1}" == "standard" ]]; then
    firefox_dir="${HOME}/.mozilla/firefox"
  fi
  if printf '%s\0' "${previously_enabled_firefox[@]}" | grep -Fxqz -- "${1}" && [[ "${firefox_changed}" != "true" && "${force}" != "true" ]]; then
    update_firefox="true"
  fi
  firefoxfolder="${firefox_dir}"
  source install.sh
  installed_firefox="true"
  cd "${repo_dir}" || exit
  if grep -q "^dg-firefox-theme-${1}" "${installed_versions}"; then
    sed -i "/^dg-firefox-theme-${1}/c\dg-firefox-theme-${1}: ${dg_firefox_theme_version} ${color}" "${installed_versions}"
  else
    echo "dg-firefox-theme-${1}: ${dg_firefox_theme_version} ${color}" >> "${installed_versions}"
  fi
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
  if grep "^enabled:" "${installed_versions}" | grep -q "gtk3"; then
    for i in $(snap connections | grep gtk-common-themes:gtk-3-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap connect "${i}:gtk-3-themes" "dg-adw-gtk3-theme:gtk-3-themes"
    done
  else
    for i in $(snap connections | grep dg-adw-gtk3-theme:gtk-3-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap disconnect "${i}:gtk-3-themes" "dg-adw-gtk3-theme:gtk-3-themes"
    done
  fi
  if grep "^enabled:" "${installed_versions}" | grep -q "icons"; then
    for i in $(snap connections | grep gtk-common-themes:icon-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap connect "${i}:icon-themes" "dg-adw-gtk3-theme:icon-themes"
    done
  else
    for i in $(snap connections | grep dg-adw-gtk3-theme:icon-themes | awk '{print $2}' | cut -f1 -d: | sort -u); do
      sudo snap disconnect "${i}:icon-themes" "dg-adw-gtk3-theme:icon-themes"
    done
  fi
  if grep "^enabled:" "${installed_versions}" | grep -q "sounds"; then
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
if printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "gtk3"; then
  if [[ "${update}" == "true" ]]; then
    if [[ "$(git submodule status "src/dg-adw-gtk3" | tr -d '+' | awk '{print $1}' )" != "$(grep "^dg-adw-gtk3" "${installed_versions}" | awk '{print $2}')" ]]; then
      install_dg_adw_gtk3
      did_update="true"
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
if printf '%s\0' "${enabled_themes[@]}" | grep -Exqz -- "gnome-shell|icons|cursors|sounds"; then
  if [[ "${update}" == "true" ]]; then
    if [[ "$(git submodule status "src/dg-yaru" | tr -d '+' | awk '{print $1}' )" != "$(grep "^dg-yaru" "${installed_versions}" | awk '{print $2}')" || "${dg_yaru_changed}" == "true" || "${gnome_shell_changed}" == "true" ]]; then
      install_dg_yaru
      did_update="true"
    else
      echo -e "${bold}dg-yaru${nc} is up to date, not reinstalling"
    fi
  else
    install_dg_yaru
  fi
fi
if ! printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "gnome-shell"; then
  if [[ "$(compgen -G /usr/share/themes/dg-yaru*)" || "$(compgen -G /usr/share/gnome-shell/theme/dg-yaru*)" ]]; then
    echo -e "Use './uninstall.sh --gnome-shell' to remove ${bold}dg-yaru${nc} GNOME Shell theme, which was previously installed."
  fi
fi
if ! printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "icons"; then
  if [[ -d "/usr/share/icons/dg-yaru/index.theme" || "$(compgen -G /usr/share/icons/dg-yaru-*)" ]]; then
    echo -e "Use './uninstall.sh --icons' to remove ${bold}dg-yaru${nc} icon theme, which was previously installed."
  fi
fi
if ! printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "cursors"; then
  if [[ -d "/usr/share/icons/dg-yaru/cursor.theme" || -d "/usr/share/icons/dg-yaru/cursors" ]]; then
    echo -e "Use './uninstall.sh --cursors' to remove ${bold}dg-yaru${nc} cursor theme, which was previously installed."
  fi
fi
if ! printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "sounds"; then
  if [[ -d "/usr/share/sounds/dg-yaru" ]]; then
    echo -e "Use './uninstall.sh --sounds' to remove ${bold}dg-yaru${nc} sound theme, which was previously installed."
  fi
fi

# Install dg-libadwaita if it's enabled
if printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "gtk4"; then
  if [[ "${update}" == "true" ]]; then
    if [[ ( "$(git submodule status "src/dg-libadwaita" | tr -d '+' | awk '{print $1}' )" != "$(grep "^dg-libadwaita" "${installed_versions}" | awk '{print $2}')" ) ||
      "${gtk4_changed}" == "true" ]]; then
      install_dg_libadwaita
      did_update="true"
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
  if [[ "${update}" == "true" ]]; then
    if [[ ( "$(git submodule status "src/dg-firefox-theme" | tr -d '+' | awk '{print $1}' )" != "$(grep "^dg-firefox-theme-${f}" "${installed_versions}" | awk '{print $2}')" ) ]]; then
      install_dg_firefox_theme "${f}"
    elif [[ "${f}" == "standard" && "${firefox_standard_changed}" == "true" ]]; then
      install_dg_firefox_theme "${f}"
    elif [[ "${f}" == "snap" && "${firefox_snap_changed}" == "true" ]]; then
      install_dg_firefox_theme "${f}"
    elif [[ "${f}" == "flatpak" && "${firefox_flatpak_changed}" == "true" ]]; then
      install_dg_firefox_theme "${f}"
    elif ! printf '%s\0' "${previously_enabled_firefox[@]}" | grep -Fxqz -- "${f}"; then
      install_dg_firefox_theme "${f}"
    fi
  else
    install_dg_firefox_theme "${f}"
  fi
done
if [[ -n "${firefox[*]}" && "${installed_firefox}" != "true" ]]; then
  echo -e "${bold}dg-firefox-theme${nc} is up to date, not reinstalling"
elif [[ -n "${firefox[*]}" ]]; then
  did_update="true"
fi
if ! printf '%s\0' "${firefox[@]}" | grep -Fxqz -- "standard" && [[ "$(compgen -G "${HOME}"/.mozilla/firefox/*/chrome/dg-firefox-theme)" ]]; then
  echo -e "Use './uninstall.sh -f standard' to remove the standard variant of ${bold}dg-firefox-theme${nc}, which was previously installed."
fi
if ! printf '%s\0' "${firefox[@]}" | grep -Fxqz -- "snap" && [[ "$(compgen -G "${HOME}"/snap/firefox/common/.mozilla/firefox/*/chrome/dg-firefox-theme)" ]]; then
  echo -e "Use './uninstall.sh -f snap' to remove the Snap variant of ${bold}dg-firefox-theme${nc}, which was previously installed."
fi
if ! printf '%s\0' "${firefox[@]}" | grep -Fxqz -- "flatpak" && [[ "$(compgen -G "${HOME}"/.var/app/org.mozilla.firefox/.mozilla/firefox/*/chrome/dg-firefox-theme)" ]]; then
  echo -e "Use './uninstall.sh -f flatpak' to remove the Flatpak variant of ${bold}dg-firefox-theme${nc}, which was previously installed."
fi

# Install dg-adw-gtk3-theme snap if it's enabled
if printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "snap" && [[ "$(command -v snap)" ]]; then
  install_snap
elif printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "snap" && [[ ! "$(command -v snap)" ]]; then
  echo -e "${byellow}WARNING:${nc} ${bold}'snap'${nc} is not installed, not installing ${bold}dg-adw-gtk3-theme${nc} snap"
elif ! printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "snap" && snap list | grep -q "dg-adw-gtk3-theme"; then
  echo -e "Use './uninstall.sh --snap' to remove ${bold}dg-adw-gtk3-theme${nc} snap, which was previously installed."
fi

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
    if printf '%s\0' "${enabled_themes[@]}" | grep -Fxqz -- "${t}"; then
      function="$(echo "enable_${t}"| tr "-" "_" )"
      "${function}"
    fi
  done
else
  echo -e "${bold}'gsettings'${byellow} not found, not enabling themes.${nc}"
fi

if [[ ( "${did_update}" == "true" && "${update}" == "true" ) || "${update}" != "true" ]]; then
  echo -e "${byellow}Log out and log back in for everything to be updated${nc}"
fi
