# docker-repository-migrator
The program help us to migrate repositories from one docker registry to another one
It will iterate all repositories and images existing on source registry,  
and then push them to target registry  

How to use  
step 0: 
```shell
git clone https://github.com/wangzhongchunongithub/docker-repository-migrator 
```
step 1: 
```shell
pip install requirements.txt  
```

step 2: edit vars.json and overwrite 'registry_uri', 'user', and 'password' of your own docker repositories 

step 3: 
```shell
python docker-repository-migrator.py -c 'vars.json'  
```

Output Sample:  
```python
2 images will be migrated.  
Pulling image: 192.168.158.128:8085/docker-hello-world:1.0  (1/2)  
Tag image: 192.168.158.128:8085/docker-hello-world:1.0 -> 192.168.158.128:8086/docker-hello-world:1.0  (1/2)  
Migrating image: 192.168.158.128:8085/docker-hello-world:1.0  (1/2)  
Successfully migrated image: 192.168.158.128:8085/docker-hello-world:1.0  (1/2)   
```
