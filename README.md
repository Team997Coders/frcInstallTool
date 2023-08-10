# frcInstallTool
A tool to automate software downloads meant for student programmers in the FIRST Robotics Competition.

Currently, the tool's default profile downloads binaries assuming that the host is running Windows (with an x86_64 processor). Unix/ARM users can still use the tool, but may need a different profile to get useful software.

frcInstallTool is reliant on code derived from [Jamie Sinn's CSA-USB-Tool](https://github.com/JamieSinn/CSA-USB-Tool). Their project is definitely better for its use as a CSA tool, while this is intended for a different use and reflects the needs of a single team.

## Prerequisites
This tool requires git to be installed on your system and added to your PATH. Follow the instructions for Windows found [here](https://git-scm.com/download/win).

This tool is written in Python 3 and needs it installed to run. Windows users can find it in the Microsoft Store.

A fast internet connection (consider wired) is _highly recommended_. The tool downloads approximately 5 GB, so also ensure you have plenty of storage space.

## Usage
Run the script with `python frcInstallTool.py <PATH TO CSV> <PATH TO INSTALL LOCATION>`.

## Next Steps
Some modules this program installs are not finished, but require user interaction to finish installing. The program will print these out as it finishes executing.

## CSV File Format
The CSV format used by this tool is similar but incompatible with CSA-USB-Tool.

It is important to remember that whitespace is significant, e.g. `,git,` != `, git,`. There should also be no spaces in names.

| Field | Meaning |
| --- | --- |
| friendlyName | A human-readable name for the module. |
| filename | Filename to install the module under. Not significant for git/pip modules. |
| id | Source to download the file from. This can be a URL, a remote git repository, or a pip package on PyPI. |
| md5 | MD5 hash of the file used for checksums. Can be 0 if the file changes often, or has a built-in checksum (git, pip). |
| type | Type of the object. Currently, `git`, `pip`, `unzipped`, `zipped`, `unzipped-installer`, and `zipped-installer` are supported. |
| subfolder | Path relative to the install directory to install to. If empty or `.`, installs in the root. |

Note: For zipped files, the program expects the filename to have a `.zip` file extension.

### Excluding Files
The program respects CSV comments, so to exclude a particular download simply add a \# symbol to the beginning of its line.

## Licensing
Portions of this project are based on CSA-USB-Tool, which is licensed under the MIT License.

The remainder of this project, including modifications and new code, is licensed under the GPL v3.0.

## Developing
Update the date at the top of installLists.csv when you update the packages included.

This project should be formatted with [Black](https://github.com/psf/black): `black .`