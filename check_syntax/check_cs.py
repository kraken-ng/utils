import tempfile, os, shutil, re, subprocess


class Checker(object):

    def __init__(self, netpath, lang, references):
        self.netpath    = netpath
        self.lang       = lang
        self.references = references
        self.tempdir    = None
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

    def __get_net_compilers(self):
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

    def setup(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.__get_net_compilers()

    def teardown(self):
        self.tempdir.cleanup()

    def compile_sources(self, sources_path):
        self.__get_runners(sources_path)
        with self.tempdir as tmpdirname:
            for runner in self.runners:
                
                abs_source_file  = runner["abs_source_file"]
                module_name      = runner["source_name"]
                compiler_version = runner["compiler"]["version"]
                compiler_path    = runner["compiler"]["path"]
                source_name      = os.path.basename(abs_source_file)
                
                abs_temp_filepath = os.path.join(tmpdirname, os.path.basename(abs_source_file))
                shutil.copy2(abs_source_file, abs_temp_filepath)
                
                command = ""
                source_reference = self.__get_source_references(module_name)
                if not source_reference:
                    command = f"{compiler_path} /target:exe /out:{abs_temp_filepath}.exe {abs_temp_filepath}"
                else:
                    command = f"{compiler_path} /r:{source_reference} /target:exe /out:{abs_temp_filepath}.exe {abs_temp_filepath}"
                
                proc = subprocess.run(command.split(), capture_output=True)
                if proc.returncode == 0:
                    print(f"[+] Module: '{source_name}' for version '{compiler_version}' compiled successfully")
                
                    command = f"{abs_temp_filepath}.exe"
                    proc = subprocess.run(command.split(), capture_output=True)
                    if proc.returncode == 0:
                        print(f"[+] Module: '{source_name}' for version '{compiler_version}' executed successfully")
                    else:
                        print(f"[!] Module: '{source_name}' for version '{compiler_version}' has runtime errors")
                        print(f"{proc.stderr}")             
                else:
                    print(f"[!] Module: '{source_name}' for version '{compiler_version}' has compiled errors")
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

checker = Checker(NET_PATH, LANG, REFERENCES)
checker.setup()
checker.compile_sources(MODULES_PATH)
checker.teardown()
