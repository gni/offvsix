# offvsix: Offline Visual Studio Code Extension Downloader

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

`offvsix` is a Python CLI utility designed to streamline the process of downloading Visual Studio Code extensions for offline installations. Whether you're preparing for a coding session without internet access or simply want to keep your favorite extensions handy, `offvsix` has you covered!

## Features

- Download specific versions of extensions.
- Download extensions to a custom directory.
- Use a proxy server for downloading.
- Avoid redundant downloads with optional caching.
- Get detailed logs with verbose mode.
- **Bulk download**: Supply a text file with a list of extensions to download them all at once!

## Installation

You can install the package from PyPI:

```bash
pip install offvsix
```

Or for offline installation, download the wheel file and run:

```bash
pip install offvsix-<version>.whl
```

## Usage

### Basic usage:

```bash
offvsix <publisher.extension>
```

For example:

```bash
offvsix ms-python.python
```

### Using a Text File:

To download multiple extensions, you can use a text file where each line is an extension name:

```bash
offvsix --file extensions.txt
```

### Install downloaded extension
```bash
code --install-extension ./extensions/ms-python.python-2023.17.12561009.vsix
```

### Options:

- `--version` to specify the version.
- `--destination` to specify the destination folder.
- `--no-cache` to force re-download.
- `--no-print` without output.
- `--file` to specify a text file containing a list of extensions to download.
- `--proxy` to use a proxy server.

## Contributing

All contributions are welcome! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT Licensed. See [LICENSE](LICENSE) for full details.

## Author

- [Lucian BLETAN](https://github.com/gni)