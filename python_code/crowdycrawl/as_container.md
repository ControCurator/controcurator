The crowdynews scraper has been implemented as a Docker container. 
Recommended usage:

```bash
$host>      docker run -it -v '$(pwd)':/data -p 9200:9200 -p 5601:5601 --name 'crowdy' rnvdv/crowdy /bin/bash
$container> cron # starts a cronjob that keeps elasticsearch and get crowdy running
```

** Note: *you can leave the container without stopping it by using `ctrl-p ctrl-q`* **

An elasticsearch instance within the container (here exposed on host port 9200) will be updated with incomming 
messages from the crowdynews endpoints of the project. 

Kibana can be launched within the container to index these items and allow for easy exploration. The above command
exposes the default kibana port to 5601 on the host. 

You can move files and data out of the container by using the mounted directory `/data` (linked to the `pwd` on the host. 

