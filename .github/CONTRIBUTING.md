<div align="center">

# Contributing

If you notice any bugs or issues with the theme or any of the scripts, please open an issue. If you want to fix it yourself, open a pull request. If you notice any design inconsistencies or think something should look different, you can also open an issue or pull request and provide an explanation for why you think it should be changed. I'm open to criticism as long as you are respectful.

If you want to help out with development, start by making sure you are familiar with CSS and Sass. These are the languages that most of the themes are written in. Knowledge of Meson, Python 3, and Bash will also be useful, as most of the scripts are written in these languages.

If you go to in the 'src' dir, you should see multiple directories. These are submodules, and are separate git repositiories. If you make any contributions to the themes, they will probably be in one of these repositories.

This repository (qualia-gtk-theme) contains the main scripts used for installing and uninstalling the themes. Be careful running these scripts when you have local changes, as they may get overwritten. Use the `--no-update` option with the install script to prevent this.

Editing any of the icons or assets can be done with Inkscape. In most cases there will be a main asset file to edit and a script to export each individual asset from the file.

When you are ready to share your contribution, make a fork of the repo on GitHub, push it there, and open a pull request. 

Try to avoid any major design changes, I will be less likely to merge those.

</div>
