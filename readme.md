## build image 
```docker build . --platform=linux/amd64 -t rehina1010/hw4:0.0.1```

## push image to dockerhub

```docker push rehina1010/hw4:0.0.1```

## pull image to server
```docker pull rehina1010/hw4:0.0.1```

## run container
```docker run --name Rehina_hw4 -it -v /home/storage:/storage -p 3000:3000 -p 5000:5000 rehina1010/hw4:0.0.1```