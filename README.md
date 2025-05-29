# recon7
A powerful and modular recon swiss army knife made in Python.

***DISCALIMER: Intended for educational/legal purposes ONLY. Don't misuse it.***
## Features
recon7 has a range of features that make it easy to work with and extend
### Modular config
We use a simple, custom configuration language (7cfg) built to make it easy to organize typed values, targets, secrets, and more. Here's an example:
```js
// recon7 example config

// targets

target:url "https://example.com" "Example URL"
target:domain "example.com" "Example domain"
target:ip "1.2.3.4" "Example IP"

// secrets (like api keys)

secret:api-ninjas "a1b2c3d4e5f6"
secret:hugging-face "a1b2c3d4e5f6"

// numbers

num:whois-wait-time-ms 1000

// themes!

theme:bg #000000
theme:fg #09FB00
theme:accent #FF0105
```
In addition, the `sevenconfig` module included in the code makes it easy to integrate recon7 config files into other (Python-based) software.