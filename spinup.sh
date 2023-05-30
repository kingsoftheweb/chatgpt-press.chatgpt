#!/bin/zsh

docker stop chatgptpress-container
docker rm -f chatgptpress-container
docker build -t chatgptpress .
docker run -d --name chatgptpress-container -p 5003:5003 chatgptpress