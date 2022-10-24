# Set up environment
Install python etc
In terminal on root app level:
1. `python -m venv venv` (or `venv .venv`, somehow VSCode doesnt accept `.venv`)
Reload terminal
2. `pip install -r requirements.txt`

# Run with docker
1. In terminal, on the level of the Dockerfile: `docker build -t rest-apis-flask-python .`
2. In terminal: `docker run -d -p 5000:5000 rest-apis-flask-python`

With automatic reloading for development:
`docker run -dp 5000:5000 -w /app -v "/c/Users/kalle/OneDrive/Documenten/rest-apis-flask-python/project/01-first-rest-api:/app" rest-apis-flask-python`

# Run with flask
In terminal: `flask run`

# Run documentation? Not working!
When the app is running with `flask run`, the URL is `localhost:5000/swagger-ui`