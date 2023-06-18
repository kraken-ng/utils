import tempfile, os, shutil, re, subprocess


class Precompiler(object):

    def __init__(self, netpath, lang, references):
        self.netpath    = netpath
        self.lang       = lang
        self.references = references
        self.compilers  = []
        self.runners    = []
    
    def __get_compiler_subversions(self, source_version):
        compiler_subversions = []
        for compiler in self.compilers:
            # Ex: cs4 -> [4.0, 4.5, 4.5.1, 4.5.2, 4.6, etc]
            if compiler["version"].startswith(source_version):
                compiler_subversions.append(compiler)
        return compiler_subversions

    def __get_compilers_for_source(self, source_name, command_name):
        # If source name has specific version try to get its compiler (ex: cs4.5)
        for compiler in self.compilers:
            compiler_version = compiler["version"]

            if source_name == f"{command_name}.{self.lang}{compiler_version}.{self.lang}":
                return [compiler]

        # If source name has global version try to get all subversions (ex: cs4 -> 4.*)
        source_version = source_name.replace(f"{command_name}.{self.lang}","")
        source_version = source_version.replace(f".{self.lang}","")
        return self.__get_compiler_subversions(source_version)

    def __get_runners(self, sources_path):
        for source_name in os.listdir(sources_path):
            abs_source_dir = f"{sources_path}\\{source_name}"
            if not os.path.isdir(abs_source_dir):
                continue
            
            for source_file in os.listdir(abs_source_dir):
                if not source_file.endswith(f".{self.lang}"):
                    continue

                abs_source_file = f"{abs_source_dir}\\{source_file}"
                
                compilers = self.__get_compilers_for_source(source_file, source_name)
                if not compilers:
                    print(f"[+] No compiler found for source file '{source_file}'")
                    continue

                for compiler in compilers:
                    self.runners.append({
                        "abs_source_file" : abs_source_file,
                        "source_name" : source_name,
                        "compiler" : compiler
                    })
        return

    def get_net_compilers(self):
        for net_version in os.listdir(self.netpath):
            abs_net_version = f"{self.netpath}\\{net_version}"
            if not os.path.isdir(abs_net_version):
                continue
            
            m = re.match(r"v\d\.\d", net_version)
            if not m:
                continue
            
            self.compilers.append({
                "version" : net_version[1:],
                "path" : f"{abs_net_version}\\csc.exe" # csc compiler under net path
            })
        return

    def __get_source_references(self, module_name):
        for reference in self.references:
            if reference["name"] == module_name:
                return ';'.join(reference["dlls"])
        return

    def compile_sources(self, sources_path):
        self.__get_runners(sources_path)
        for runner in self.runners:
            
            abs_source_file  = runner["abs_source_file"]
            module_name      = runner["source_name"]
            compiler_version = runner["compiler"]["version"]
            compiler_path    = runner["compiler"]["path"]
            source_name      = os.path.basename(abs_source_file)

            command = ""
            source_reference = self.__get_source_references(module_name)
            if not source_reference:
                command = f"{compiler_path} /target:library /out:{abs_source_file}.dll {abs_source_file}"
            else:
                command = f"{compiler_path} /r:{source_reference} /target:library /out:{abs_source_file}.dll {abs_source_file}"

            proc = subprocess.run(command.split(), capture_output=True)
            if proc.returncode == 0:
                print(f"[+] Module: '{source_name}' for version '{compiler_version}' compiled successfully")
            else:
                print(f"[!] Module: '{source_name}' for version '{compiler_version}' has compiled errors")
                print(f"{proc.stdout}")
                print(f"{proc.stderr}")
        return


MODULES_PATH = "..\\..\\modules"
NET_PATH = "C:\\Windows\\Microsoft.NET\\Framework64"
LANG = "cs"
REFERENCES = [
    {
        "name" : "powerpick",
        "dlls" : [
            "C:\\Windows\\assembly\\GAC_MSIL\\System.Management.Automation\\1.0.0.0__31bf3856ad364e35\\System.Management.Automation.dll"
        ]
    },
    {
        "name" : "dump_iis_secrets",
        "dlls" : [
            "C:\\Windows\\system32\\inetsrv\\Microsoft.Web.Administration.dll"
        ]
    }
]

precompiler = Precompiler(NET_PATH, LANG, REFERENCES)
precompiler.get_net_compilers()
precompiler.compile_sources(MODULES_PATH)
