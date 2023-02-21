# Fix Symbolic Links

This utility allows you to fix corrupted symbolic links in the Kraken module directory.

Sometimes it happens that when you move the Kraken project, or clone it in Windows, the symbolic links used for version maintenance, breaks.

To make a correction and not have to do it by hand, this script has been designed to automate it.

It is important that, if the script is executed in **Windows**, it is done with **administrator privileges** because otherwise, it will not allow to create the symbolic links.

## Usage

Its use is simple, just pass the path where the modules are located:

```
python fix_symbolic_links.py --modules-path ../../modules
```
