# Mantras

## Developing
This project uses [docker](https://docs.docker.com/)
and [docker-compose](https://docs.docker.com/compose)

go to [docker installation](https://docs.docker.com/engine/install/)
and [docker compose installation](https://docs.docker.com/compose/install/) first
later on, please make sure docker is running on your machine (or docker desktop)
```
docker build . -f Dockerfile -t hey --no-cache
```
later on, run docker-compose :
```
docker-compose up -d
```
## Launching postman and testing the API
Open [postman](http://www.postman.com) and import Mantras.postman_collection.json inside postman
Start sending requests. You should be able to see data inside the route 
`Mantras->get_all_mantras`  and `Users -> get_all_users`
and `Hashtags->get_all_hashtags` (in postman)


run `docker ps` to see whether you have 2 containers. 

to enter the container (in shell), please run `docker exec -it <container_id> sh`


