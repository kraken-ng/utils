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
        for container in self.containers:
            c_version = container["version"]
            if source_name == f"{command_name}.{self.lang}{c_version}.{self.lang}":
                return container["container"]
            
            if c_version.endswith(".0"):
                c_version = c_version.replace(".0", "")
                if source_name == f"{command_name}.{self.lang}{c_version}.{self.lang}":
                    return container["container"]
        return

    def __get_runners(self, sources_path):
        for source_name in os.listdir(sources_path):
            abs_source_dir = f"{sources_path}/{source_name}"
            if not os.path.isdir(abs_source_dir):
                continue
            
            for source_file in os.listdir(abs_source_dir):
                if not source_file.endswith(f".{self.lang}"):
                    continue

                abs_source_file = f"{abs_source_dir}/{source_file}"

                container = self.__get_container_for_source(source_file, source_name)
                if not container:
                    print(f"{COLORS.WARNING}[+] No container found for source file '{source_file}'{COLORS.ENDCOLOR}")
                    continue

                self.runners.append({
                    "abs_source_file" : abs_source_file,
                    "source_name" : source_name,
                    "container" : container
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

            remote_source_name = os.path.basename(runner["abs_source_file"])
            container_filename = f"Module_" + runner["source_name"] + f".{self.lang}"
            cwd_source_file = os.getcwd() + "/" + container_filename

            shutil.copyfile(runner["abs_source_file"], cwd_source_file)
            self.__copy_to_container(runner["container"], cwd_source_file, f"/tmp/{container_filename}")

            exit_code, output = runner["container"].exec_run(f"javac /tmp/{container_filename}")

            output_str = output.decode()
            output_str = output_str.rstrip()
            if exit_code == 0:
                print(f"{COLORS.OKGREEN}[+] Module: {remote_source_name} compiled successfully{COLORS.ENDCOLOR}")
            else:
                print(f"{COLORS.ERROR}[!] Module: {remote_source_name} has syntax errors{COLORS.ENDCOLOR}")
                print(f"{COLORS.ERROR}{output_str}{COLORS.ENDCOLOR}")

            os.remove(cwd_source_file)


IMAGES = {
    "1.6" : "openjdk:6",
    "1.7" : "openjdk:7",
    "1.8" : "openjdk:8",
    "9" : "openjdk:9",
    "10" : "openjdk:10",
    "11" : "openjdk:11",
    "12" : "openjdk:12",
    "13" : "openjdk:13",
    "14" : "openjdk:14",
    "15" : "openjdk:15",
    "16" : "openjdk:16",
    "17" : "openjdk:17"
}
LANG = "java"
MODULES_PATH = "../../modules"


checker = Checker(IMAGES, LANG)
checker.setup()
checker.compile_sources(MODULES_PATH)
checker.teardown()
