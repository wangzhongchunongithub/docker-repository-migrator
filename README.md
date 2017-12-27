# docker-repository-migrator
The program help us to migrate repositories from one docker registry to another one

How to use  
step 0: git clone the project  
step 1: pip install requirements.txt  
step 2: edit vars.json and overwrite 'registry_uri', 'user', and 'password' of docker repositories  
step 3: python docker-repository-migrator.py -c 'vars.json'  

##########################
```shell
2 images will be migrated.  
Pulling image: 192.168.158.128:8085/docker-hello-world:1.0  (1/2)  
Tag image: 192.168.158.128:8085/docker-hello-world:1.0 -> 192.168.158.128:8086/docker-hello-world:1.0  (1/2)  
Migrating image: 192.168.158.128:8085/docker-hello-world:1.0  (1/2)  
Successfully migrated image: 192.168.158.128:8085/docker-hello-world:1.0  (1/2)   
```
