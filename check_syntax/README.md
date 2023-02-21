# Check Syntax

This utility can be used to validate: the compilation and execution of Kraken modules in different languages and versions.

For PHP and Java modules, different Docker containers are used for the supported versions to validate that the modules work correctly (executable on Windows and Linux).

In the case of .NET, it is required to run on a Windows machine because it uses the .NET compiler (csc.exe) for each version of .NET installed on the machine.

## Requirements

In order to use this script, you need to have **Docker** installed (either on Windows or Linux). As well as the python `docker` library.

## Usage

First, you must download the images of the Docker containers of the language for which you want to test the syntax and execution of the modules.

For this you can use the scripts: [pull_php.sh](pull_php.sh) and [pull_java.sh](pull_java.sh).

Then, simply launch each script and start the orchestration.

```bash
python check_php.py
python check_java.py
python check_cs.py
```

> It is important that the modules are in the relative path: `../../modules`, otherwise the script will fail. If this is not the path where they are located, you must specify it inside the script.

> In the case of .NET, as some modules require references in the compilation process, these must be added within the script.
