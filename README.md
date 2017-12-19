## PLEASE NOTE
A Linux/Unix shell is recommended for this project; look into Bash on Ubuntu on Windows or consider dual-booting. These installations and commands are guarenteed to work on Bash on Ubuntu on Windows, mileage may vary on other shells or OSs.

### Prerequisites
* git
* python2
* gcloud
* virtualenv
* pip

Check you have all these commands before continuing

### Clone repository / pull
By now you should have cloned the repository, make sure you have the latest branch references
```bash
$ git fetch
```
### Create virtual environment
You should be in the root directory (directory with the main.py)
```bash
$ virtualenv env
```
Creating a virtual environment only needs to happen once, now you should have an env folder

### Use virtual environment
Whenever you begin working, you will need to activate the environment
```bash
$ source env/bin/activate
```
### Install modules
Now you can use pip to install the module requirements
```bash
$ pip install -t lib -r requirements.txt
```
This will create a lib folder containing Flask and a bunch of other modules. You only need to do this once.
Now that a virtual environment with all the modules you need is set up, you can run the server locally

### Run server locally
```bash
$ dev_appserver.py app.yaml
```
This will start the server at http://localhost:8080/

The dev server is super smart and will restart itself if it detects a change to a file, so you can go off programming, refresh the localhost page and see how badly you fucked things up.

Quit the dev server with `Ctrl+C`

### Exit virtual environment
To exit the virtual environment...
```bash
$ deactivate
```

### Pushing to gcloud
You may need to first authenticate gcloud and point it to the project if you have not done the initial setup
```bash
$ gcloud auth login
...
$ gcloud config set project various-artists
```
To deploy a new version of the app...
```bash
$ gcloud app deploy
```
If you're lazy and can't find the URL for the project...
```bash
$ gcloud app browse
```
