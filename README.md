# Traffic Dashboard


## Getting Started

Requirements:
- Operating system: Ubuntu 16.04
- User account with sudo privileges
- Python 2 and 3

```
sudo apt update && sudo apt -y install python python-pip python3 python3-pip
sudo -H pip3 install pipenv --system
```

Python can be weird, so if that doesn't work try this:

```
sudo -H python3 -m pip install pipenv
```

Either way, you need to end up with `/usr/local/bin/pipenv`.

## Installation

1. Login with a user with sudo privileges.
2. In the users home directory, clone this repository and go into the directory.

```
git clone https://github.com/jonahlyn/dashboard.git
cd dashboard
```

## Production Deployment with Ansible

The following steps will install Nginx, MariaDB and deploy the code in the `app` directory.

1. Go into the provisioner directory and execute the following to install the provisioner dependencies:

```
cd provisioner
pipenv install
```

2. Edit the `vars/main.yml` file and update the `server_name` variable with the host name of the server:

```
server_name: rgc1
```

3. Execute the ansible playbook. When prompted, type in the user's sudo password. 

```
pipenv shell
ansible-playbook provisioner.yml -K
```

When provisioning is complete, the application will be running on port 80.

Example: http://rgc1



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







