## Flatpak Apps
Run this command once to let all Flatpak apps access the themes:
```
flatpak override --user --filesystem=xdg-config/gtk-4.0 --filesystem=xdg-data/themes
```

## Snap Apps
If Snap is installed you can enable Snap support when configuring the theme.

If you really want Snaps to access the GTK4/Libadwaita configuration, you will have to run this command for each Snap, replacing `SNAP-NAME` with the name of the Snap:
```
sudo mount --bind --mkdir ~/.config/gtk-4.0 ~/snap/SNAP-NAME/current/.config/gtk-4.0
```
For this to persist after reboot, you need to add the following line to /etc/fstab for each Snap. Replace `USERNAME` and `SNAP-NAME` with the correct information.
```
/home/USERNAME/.config/gtk-4.0  /home/USERNAME/snap/SNAP-NAME/current/.config/gtk-4.0  none  bind  0  0
```

## GDM Theme
If you are using GNOME, I recommend using [Login Manager Settings](https://github.com/realmazharhussain/gdm-settings) to change the GDM theme to qualia.

If you change the GDM theme and later choose to uninstall the theme, reset the GDM theme to default first or you might encounter issues.

## Other Desktop Environments
Other GTK or GNOME based desktops (like Pantheon) may work with this theme. The install script will not be able to enable the themes though. Full support for Pantheon will be added when Elementary OS 7 releases. Open an issue to request support for other desktops.

Qt based desktops are unsupported by this theme and will likely remain that way.