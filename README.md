# recon7
A powerful and modular recon swiss army knife made in Python.
## Features
### Modular config
recon7 uses a simple, custom configuration language (7cfg) built to make it easy to organize theming, secrets, constants, and more. Here's an example:
```js
// basically string values
secret:api-ninjas "a1b2c3d4e5f6"
// numbers (ints and floats)
num:req-wait 1000
// theming!
theme:bg #000000
theme:fg #00FF00
theme:accent #FF0000
```
### TUI
<img src="images/themedtui.png" alt="Themed TUI" width="250" style="margin-right:30px"/>
<img src="images/themedtui2.png" alt="Themed TUI" width="250"/>

recon7 uses a fully themable curses-based TUI that aims to be both intuitive and efficient for users
### Hotswap Config
recon7 supports hotswapping configs, just press `r` to reload
### Backups
recon7 makes backups of the last valid config when hotswapping and backs up target lists when making changes
### Target Lock
recon7 stores targets in a computer and human readable lockfile so targets are restored from the last session
```bash
target1 "192.168.1.1" "Internal LAN"
mysite "example.com" "Example site"
scan1 "http://example.com" "Landing page"
```