# Traffic Dashboard



## Development Server

To run the dashboard in a temporary development server, run:

```
cd app
pipenv install
pipenv shell python app.py
```

Or, run the app manually with gunicorn on port 8000:

```
cd app
pipenv install
pipenv run gunicorn -w 5 app:server
```

Open http://localhost:8000



## Production Deployment

### Deploy with ansible on the localhost

```
cd provisioner
pipenv install
pipenv shell
./provisioner.yml -K
```

Then you can run this command to check the status of nginx and the gunicorn application server:

```
sudo systemctl status nginx
sudo systemctl status gunicorn.socket
```








