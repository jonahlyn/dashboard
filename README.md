# Traffic Dashboard


## Getting Started

Requirements:
- Operating system: Ubuntu 16.04
- User account with sudo privileges
- Python 2 and 3

```
sudo apt install python python-pip python3 python3-pip
pip3 install pipenv
```

## Installation

1. Login with a user with sudo privileges.
2. In the users home directory, clone this repository and go into the directory.

```
git clone https://github.com/jonahlyn/dashboard.git
cd dashboard
```

## Production Deployment

Configure the server and deploy the application with ansible:

```
cd provisioner
pipenv install
pipenv shell
./provisioner.yml -K
```

When prompted, type in the user's sudo password. 
When provisioning is complete, the application will be running on port 80 and accessible over a web browser.

## Troubleshooting

Check the status of nginx and the gunicorn application services:

```
sudo systemctl status nginx
sudo systemctl status gunicorn.socket
```

Log files are located at:
  - access_log: `/var/log/nginx/access.log`
  - error_log: `/var/log/nginx/error.log`


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







