# CasparCG Media Scanner

This is an alternate implementation of the [CasparCG Media
Scanner](https://github.com/CasparCG/media-scanner) written in Python. It can
be used as a drop-in replacement for the original, or as a standalone
background service on both Linux and Windows.

The Scanner operates alongside [CasparCG
Server](https://github.com/CasparCG/server) to index and monitor media,
templates, and fonts. It leverages FFmpeg to extract stream metadata (codecs,
video format, resolution, etc.) and generate thumbnails, exposing this data to
the Server and connected client applications via an HTTP API.

The Scanner exposes both classic AMCP-compatible text responses and structured
JSON endpoints:

* **AMCP-Compatible Endpoints**

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/cls` | `GET` | List available media files |
| `/tls` | `GET` | List available template files |
| `/fls` | `GET` | List available font files |
| `/cinf/<name>` | `GET` | Retrieve metadata for a specific media file |
| `/thumbnail` | `GET` | List available thumbnail filenames |
| `/thumbnail/<name>` | `GET` | Retrieve the thumbnail image for a specific media file |

* **JSON Endpoints**

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/media` | `GET` | List available media files with detailed metadata |
| `/media/info/<name>` | `GET` | Retrieve detailed metadata for a specific media file |
| `/media/thumbnail/<name>` | `GET` | Retrieve the thumbnail image for a specific media file |
| `/templates` | `GET` | List available templates with detailed metadata |

## Installation

You can install the Scanner using a native Debian package or as a standalone
portable executable.

### Prerequisites

The Scanner relies on [FFmpeg](https://ffmpeg.org/) to process media, and you
must have it installed and available on your system.

* **Linux:** If you install the Scanner using the Debian package, FFmpeg will
  be installed automatically as a dependency. If you use the standalone binary,
  install FFmpeg via your package manager (e.g., `sudo apt install ffmpeg`).
  
* **Windows:** Download the latest build from the [official FFmpeg
  website](https://ffmpeg.org/download.html) and follow their installation
  instructions. Be sure to add it to your system's `PATH` so the Scanner can
  find it.

### Option A: Debian Package

Binary packages for Debian, Ubuntu, Raspberry Pi and other Debian-based
distributions can be installed from the [CCCP Linux Package
Archive](https://github.com/cccp-linux/archive). Follow their instructions to
set up the archive and be sure to add the _**casparcg**_ component. After that:

```shell
sudo apt install casparcg-scanner
```

Debian packages for the CasparCG Server are also available from them:

```shell
sudo apt install casparcg-server
```

### Option B: Portable Executable

If you are on Windows, or prefer not to install the Debian package on Linux,
download the standalone portable executable for your architecture from the
[Releases
page](https://github.com/dimitry-ishenko-casparcg/scanner/releases/latest).
These executables are built automatically using PyInstaller via GitHub Actions.

* **Available for:** Windows (x86_64), Linux (x86_64), and Linux (ARM64).

* **No installation required:** Simply download the file and place it in your
  CasparCG directory to use it as a drop-in replacement for the official
  scanner.

## Configuration

CasparCG Media Scanner supports the following options:

```console
usage: casparcg-scanner [-h] [--db-path path] [--http-addr addr] [--http-port port] [-v] [--debug] [config]

CasparCG Media Scanner

positional arguments:
  config            path to the casparcg.config file (default: casparcg.config)

options:
  -h, --help        show this help message and exit
  --db-path path    override database location (default: scanner.db in the config directory)
  --http-addr addr  host address to bind the server to (default: 0.0.0.0)
  --http-port port  port to bind the server to (default: 8000)
  -v, --version     show program's version number and exit
  --debug           show full stack trace on errors
```

### Running as a Background Service

Running the Scanner as a background service is preferred. This ensures it
starts automatically on login and runs continuously without needing an open
terminal window.

#### Linux: Systemd User Service

If you installed the Debian package, a systemd user service is automatically
installed. By default, the service is configured to run from your home
directory (`~`). The Scanner looks for the `casparcg.config` file at that
location and uses it to determine where the `media`, `fonts`, and `templates`
are stored.

If your `casparcg.config` file is located elsewhere, you need to do the
following:

1. Open the service configuration file:

   ```bash
   systemctl --user edit casparcg-scanner
   ```

2. Change the working directory by adding these lines (replace with the actual
   path to the directory containing your `casparcg.config`):

   ```ini
   [Service]
   WorkingDirectory=/path/to/your/config/directory
   ```

3. Save, exit, and (re)start the service:

   ```bash
   systemctl --user enable --now casparcg-scanner
   ```

#### Windows: NSSM

To run the standalone Windows executable in the background as a Windows
Service, you can use [NSSM (Non-Sucking Service
Manager)](https://nssm.cc/).

1. Download NSSM from the [Download page](https://nssm.cc/download) and extract it.

2. Open an Administrator Command Prompt and run:

   ```dos
   nssm install "CasparCG Scanner" "C:\path\to\casparcg-scanner-windows-amd64.exe"
   ```

3. (Optional) The Scanner looks for `casparcg.config` in its working directory
   (which defaults to the executable's location). If both files are in the same
   directory, you don't need to do anything.

   Otherwise, you need to set the Scanner's working directory:

   ```dos
   nssm set "CasparCG Scanner" AppDirectory "C:\path\to\casparcg\server"
   ```

   **Using the GUI:** You can also configure all the settings through a
   graphical interface by running:

   ```dos
   nssm edit "CasparCG Scanner"
   ```

   This opens the NSSM configuration window, where you can easily change the
   startup directory, add arguments, or configure the service to run under a
   specific Windows user account.

4. Start the service:

   ```dos
   nssm start "CasparCG Scanner"
   ```

To stop or remove the service later, run:

```dos
nssm stop "CasparCG Scanner"
```

and:
```dos
nssm remove "CasparCG Scanner"
```

Share and enjoy.

## Authors

* **Dimitry Ishenko** - dimitry (dot) ishenko (at) (gee) mail (dot) com

## License

This project is distributed under the GNU GPL license. See the
[LICENSE.md](LICENSE.md) file for details.
