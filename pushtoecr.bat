aws ecr get-login-password --region ap-southeast-5 | docker login --username AWS --password-stdin 720170540593.dkr.ecr.ap-southeast-5.amazonaws.com

docker build -t zus-coffee-api .

docker tag zus-coffee-api:latest 720170540593.dkr.ecr.ap-southeast-5.amazonaws.com/chatbot:latest

docker push 720170540593.dkr.ecr.ap-southeast-5.amazonaws.com/chatbot:latest