import sys
import json
import requests
import commands
from optparse import OptionParser

TIMEOUT = 10
class Image():
    def __init__(self, image_name, image_tag, image_full_name):
        self.image_name = image_name
        self.image_tag = image_tag
        self.image_full_name = image_full_name

class Registry(object):
    def __init__(self, **kwargs):
        self.__registry_uri = kwargs['registry_uri']
        self.__user = kwargs['user']
        self.__password = kwargs['password']
        if 'scheme' in kwargs:
            self.scheme = kwargs['scheme']
        else:
            self.scheme = 'http'
    @property
    def registry_uri(self):
        return self.__registry_uri

    @property
    def user(self):
        return self.__user

    @property
    def password(self):
        return self.__password

    @property
    def auth(self):
        return (self.__user, self.__password)

    def gen_image_full_name(self, image_name, image_tag):
        return "%s/%s:%s" % (self.__registry_uri, image_name, str(image_tag))

class DockerRegistry(Registry):
    def __init__(self, **kwargs):
        super(DockerRegistry, self).__init__(**kwargs)
        self.__registry_version = kwargs['registry_version']

    @property
    def registry_version(self):
        return self.__registry_version

    @property
    def catalog_uri(self):
        return   "%s://%s/%s/_catalog" % (self.scheme, self.registry_uri, self.registry_version)

    @property
    def search_repo_uri(self):
        if self.registry_version == "v1":
            return "%s://%s/v1/search" % (self.scheme, self.registry_uri)
        else:
            return "%s://%s/v2/_catalog" % (self.scheme, self.registry_uri)           
 
    def get_repo_tags_uri(self, repo_name):
        if self.registry_version == "v1":
            return "%s://%s/v1/repositories/%/tags" % (self.scheme, self.registry_uri, repo_name)
        else:
            return "%s://%s/v2/%s/tags/list" % (self.scheme, self.registry_uri, repo_name)

    def get_images_list(self, repo_name):
        uri = self.get_repo_tags_uri(repo_name)
        response = requests.get(uri, timeout = TIMEOUT)
        image = None
        results = []
        if response.status_code == 200:
            image = response.json()
            if self.registry_version == "v1":
                for tag in image:
                    results.append(Image(repo_name, tag, self.gen_image_full_name(repo_name, tag)))
            else:
                for tag in image["tags"]:
                    results.append(Image(repo_name, tag, self.gen_image_full_name(repo_name, tag)))
        return results

    def get_repositories(self):
        response = requests.get(self.search_repo_uri, params={}, timeout = TIMEOUT)
        data = None
        if response.status_code == 200:
            data = response.json()
            if self.registry_version == 'v1':
                return map(lambda item:item['name'], data['results'])
            else:
                return data['repositories']

        return []

    def resolve_images(self):
        repositories = self.get_repositories()
        images = []
        for index, repo in enumerate(repositories):
            images.extend(self.get_images_list(repo))

        return images

class RegistryFactory():
    def __init__(self):
        pass

    @staticmethod
    def generate(is_original_registry, params):
        if is_original_registry:
            if 'registry_version' not in params:
                print ("Please specify version eg. v2) of the docker registry: %s" % params['registry_uri'])
                sys.exit()
            else:
                return DockerRegistry(registry_uri = params['registry_uri'],
                                           registry_version = params['registry_version'],
                                           user = params['user'],
                                           password = params['password'])
        else:
            return Registry(registry_uri = params['registry_uri'],
                                           user = params['user'],
                                           password = params['password'])

class DockerHelper():
    def __init__():
        pass

    @staticmethod
    def login_registry(registry, **kwargs):
        if kwargs['registry_version'] == 'v1':
            return True

        command = "docker login -u %s -p %s %s" % (kwargs['user'], kwargs['password'], registry)
        (status, output) = commands.getstatusoutput(command)
        if output == "Login Succeeded":
            return True
        else:
            return False

    @staticmethod
    def tag_image(original_name, target_name):
        command = "docker tag %s %s" % (original_name, target_name)
        (status, output) = commands.getstatusoutput(command)
        if output.find('succeeded'):
            return True
        else:
            return False
    
    @staticmethod
    def pull_image(image_full_name):
        command = "docker pull %s" % (image_full_name)
        (status, output) = commands.getstatusoutput(command)
        if output.find('succeeded'):
            return True
        else:
            return False

    @staticmethod
    def remove_image(image_full_name):
        command = "docker rmi %s -f" % (image_full_name)
        (status, output) = commands.getstatusoutput(command)
        if output.find('succeeded'):
            return True
        else:
            return False

    @staticmethod
    def push_image(image_full_name):
        command = "docker push %s" % (image_full_name)
        (status, output) = commands.getstatusoutput(command)
        if output.find('succeeded'):
            return True
        else:
            return False

class RepositoryMigrator():
    def __init__(self, original_registry_info, target_registry_info):
        self.original_registry = RegistryFactory.generate(True, original_registry_info)
        self.target_registry = RegistryFactory.generate(False, target_registry_info)

    def migrate(self, original_images):
        target_image = None
        pulling_state = True
        pushing_state = True
        image_count = len(original_images)
        print ("%s images will be migrated." % (str(image_count)))
        if True:
            for idx, o_image in enumerate(original_images):
                index = idx + 1
                print ("Pulling image: %s  (%s/%s)" % (o_image.image_full_name, index, image_count))
                pulling_state = pulling_state and DockerHelper.pull_image(o_image.image_full_name)
                if pulling_state == True:
                    target_image = self.target_registry.gen_image_full_name(o_image.image_name, o_image.image_tag)
                    print ("Tag image: %s -> %s  (%s/%s)" % (o_image.image_full_name, target_image, index, image_count))
                    DockerHelper.tag_image(o_image.image_full_name, target_image)
                    print ("Migrating image: %s  (%s/%s)" % (o_image.image_full_name, index, image_count))
                    pushing_state = DockerHelper.push_image(target_image)
                    if pushing_state == True:
                        print ("Successfully migrated image: %s  (%s/%s) \n" % (o_image.image_full_name, index, image_count))
                    else:
                        print ("Failed to migrate image: %s" % (o_image.image_full_name))
                    
                    DockerHelper.remove_image(target_image)
                    DockerHelper.remove_image(o_image.image_full_name)
                else:
                    print ("Failed to pull image: %s" % (o_image.image_full_name))

    def login_registries(self):
        login_state = DockerHelper.login_registry(self.original_registry.registry_uri,
                                    registry_version = self.original_registry.registry_version,
                                    user = self.original_registry.user,
                                    password = self.original_registry.password)

        login_state = login_state and DockerHelper.login_registry(self.target_registry.registry_uri,
                                    registry_version = self.original_registry.registry_version,
                                    user = self.target_registry.user,
                                    password = self.target_registry.password)

        return login_state

    def exe_migration(self):
        registry_login_state = self.login_registries()
        if registry_login_state == True:
            original_images = self.original_registry.resolve_images()
            #print original_images
            self.migrate(original_images)
        else:
            print ("Failed to login regisitriy: %s or %s" % (self.original_registry.registry_uri, self.target_registry.registry_uri))

class JsonHelper():
    def __init__(self):
        pass

    @staticmethod
    def read_json(file_path):
        result = None
        try:
            with open(file_path, 'r') as file:
                result = json.load(file)
                return result
        except Exception, err:
            print (err)
            print ("Failed to load json from the file: %s" % (file_path))
            sys.exit()

class AttrValidater():
    def __init__(self):
        pass

    @staticmethod
    def has_attr(object_dict, *args):
        for index, arg in enumerate(args):
            if arg not in object_dict:
                return False
        return True

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-c', '--configuration',
                      action = 'store',
                      default = None,
                      dest = 'config_path')

    (options, arges) = parser.parse_args()
    if options.config_path is None:
        print ("Failed to find args: -c or --configuration")
        sys.exit()
    else:
        params = JsonHelper.read_json(options.config_path)
        if AttrValidater.has_attr(params, 'original_registry', 'target_registry') and \
           AttrValidater.has_attr(params['original_registry'], 'type', 'registry_uri', 'user', 'password') and \
           AttrValidater.has_attr(params['target_registry'], 'type', 'registry_uri', 'user', 'password'):
               migrator = RepositoryMigrator(params['original_registry'], params['target_registry'])
               migrator.exe_migration()
        else:
            print ("[Parameters Error]")
            sys.exit()
