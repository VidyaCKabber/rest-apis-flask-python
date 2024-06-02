# rest-apis-flask-python

# Run as flask app execute following cmd
## flask run

# Run as docker container
#### 1. Install docker desktop
#### 2. create docker image -> docker build -t rest-apis-flask-python .
#### 3. Create container -> docker run -dp 5000:5000 rest-apis-flask-python

### Auto reload of container
#### docker run -dp 5000:5000 -w /app -v "$(pwd):/app" rest-apis-flask-python   

### Swagger doc
#### http://localhost:5000/swagger-ui

