import docker, tarfile, os, shutil


class COLORS:
    HEADER    = '\033[95m'
    INFO      = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    ERROR     = '\033[91m'
    ENDCOLOR  = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'


class Checker(object):

    def __init__(self, images, lang):
        self.images     = images
        self.lang       = lang
        self.containers = []
        self.runners    = []
        self.dockercli  = docker.from_env()
        
    def __image_exists(self, image):
        try:
            self.dockercli.images.get(image)
            return True
        except docker.errors.ImageNotFound:
            return False

    def __is_in_containers(self, image):
        for elem in self.containers:
            if image == elem["image"]:
                return True
        return False
    
    def __get_container_subversions(self, source_version):
        container_subversions = []
        for container in self.containers:
            # Ex: php7 -> [7.0, 7.1, 7.2, 7.3, 7.4]
            if container["version"].startswith(source_version):
                container_subversions.append(container)
        return container_subversions

    def __create_containers(self):
        for version, image in self.images.items():
            if not self.__image_exists(image):
                print(f"{COLORS.WARNING}[!] Image: '{image}' not exists on system{COLORS.ENDCOLOR}")
                continue
            
            if self.__is_in_containers(image):
                continue
            
            print(f"{COLORS.INFO}[*] Creating a docker container for image: '{image}'{COLORS.ENDCOLOR}")
            container = self.dockercli.containers.run(image, "tail -f /dev/null", detach=True, auto_remove=True)
            self.containers.append({"image" : image, "version" : version, "container" : container})

    def __get_container_for_source(self, source_name, command_name):
        # If source name has specific version try to get its container (ex: php5.6)
        for container in self.containers:
            c_version = container["version"]
            if source_name == f"{command_name}.{self.lang}{c_version}.{self.lang}":
                return [container]

        # If source name has global version try to get all subversions (ex: php5 -> 5.*)
        source_version = source_name.replace(f"{command_name}.{self.lang}","")
        source_version = source_version.replace(f".{self.lang}","")
        return self.__get_container_subversions(source_version)

    def __get_runners(self, sources_path):
        for source_name in os.listdir(sources_path):
            abs_source_dir = f"{sources_path}/{source_name}"
            if not os.path.isdir(abs_source_dir):
                continue
            
            for source_file in os.listdir(abs_source_dir):
                if not source_file.endswith(f".{self.lang}"):
                    continue

                abs_source_file = f"{abs_source_dir}/{source_file}"

                containers = self.__get_container_for_source(source_file, source_name)
                if not containers:
                    print(f"{COLORS.WARNING}[+] No container found for source file '{source_file}'{COLORS.ENDCOLOR}")
                    continue

                for container in containers:
                    self.runners.append({
                        "abs_source_file" : abs_source_file,
                        "source_name" : source_name,
                        "container" : container["container"],
                        "container_version" : container["version"]
                    })

    def __copy_to_container(self, container, src, dst):
        cwd = os.getcwd()
        os.chdir(os.path.dirname(src))
        srcname = os.path.basename(src)
        tar = tarfile.open(src + '.tar', mode='w')
        try:
            tar.add(srcname)
        finally:
            tar.close()
        data = open(src + '.tar', 'rb').read()
        container.put_archive(os.path.dirname(dst), data)
        os.remove(src + '.tar')
        os.chdir(cwd)

    def setup(self):
        self.__create_containers()

    def teardown(self):
        for container in self.containers:
            image = container["image"]
            print(f"{COLORS.INFO}[*] Stopping a docker container for image: '{image}'{COLORS.ENDCOLOR}")
            container["container"].stop()

    def compile_sources(self, sources_path):
        self.__get_runners(sources_path)
        for runner in self.runners:

            container_version = runner["container_version"]
            remote_source_name = os.path.basename(runner["abs_source_file"])
            container_filename = f"Module_" + runner["source_name"] + f".{self.lang}"
            cwd_source_file = os.getcwd() + "/" + container_filename

            shutil.copyfile(runner["abs_source_file"], cwd_source_file)
            self.__copy_to_container(runner["container"], cwd_source_file, f"/tmp/{container_filename}")

            # Check for syntax errors when analyze module content
            exit_code, output = runner["container"].exec_run(f"php -l /tmp/{container_filename}")

            output_str = output.decode()
            output_str = output_str.rstrip()
            if exit_code == 0:
                print(f"{COLORS.OKGREEN}[+] Module: '{remote_source_name}' for version '{container_version}' compiled successfully{COLORS.ENDCOLOR}")

                # Check for runtime errors when module is executed
                exit_code_2, output_2 = runner["container"].exec_run(f"php /tmp/{container_filename}")

                output_str_2 = output_2.decode()
                output_str_2 = output_str_2.rstrip()
                if exit_code_2 == 0:
                    print(f"{COLORS.OKGREEN}[+] Module: '{remote_source_name}' for version '{container_version}' executed successfully{COLORS.ENDCOLOR}")
                else:
                    print(f"{COLORS.ERROR}[!] Module: '{remote_source_name}' for version '{container_version}' has runtime errors{COLORS.ENDCOLOR}")
                    print(f"{COLORS.ERROR}{output_str_2}{COLORS.ENDCOLOR}") 
            
            else:
                print(f"{COLORS.ERROR}[!] Module: '{remote_source_name}' for version '{container_version}' has syntax errors{COLORS.ENDCOLOR}")
                print(f"{COLORS.ERROR}{output_str}{COLORS.ENDCOLOR}")

            os.remove(cwd_source_file)


IMAGES = {
    "5.4" : "php:5.4-cli",
    "5.5" : "php:5.5-cli",
    "5.6" : "php:5.6-cli",
    "7.0" : "php:7.0-cli",
    "7.1" : "php:7.1-cli",
    "7.2" : "php:7.2-cli",
    "7.3" : "php:7.3-cli",
    "7.4" : "php:7.4-cli",
    "8.0" : "php:8.0-cli",
    "8.1" : "php:8.1-cli",
    "8.2" : "php:8.2-cli",
}
LANG = "php"
MODULES_PATH = "../../modules"


checker = Checker(IMAGES, LANG)
checker.setup()
checker.compile_sources(MODULES_PATH)
checker.teardown()
