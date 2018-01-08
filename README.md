## PLEASE NOTE
A Linux/Unix shell is recommended for this project; look into Bash on
Ubuntu on Windows or consider dual-booting. These installations and
commands are guarenteed to work on Bash on Ubuntu on Windows, mileage
may vary on other shells or OSs.

## Setting up server

### Prerequisites
* git
* python2
* gcloud
* virtualenv
* pip

Check you have all these commands before continuing.

gcloud components needed:

```bash
core
app-engine-python
app-engine-python-extras
```

Run `gcloud components list` to see which you have and install any missing according to
the above list.

### Clone repository / pull
By now you should have cloned the repository, make sure you have the
latest branch references
```bash
$ git fetch
```
### Create virtual environment
You should be in the root directory (directory with the `main.py`)
```bash
$ virtualenv env
```
Creating a virtual environment only needs to happen once, now you should
have an env folder

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
This will create a lib folder containing Flask and a bunch of other
modules. You only need to do this once.

### Exit virtual environment
You should now exit the virtual environment otherwise gcloud will get confused
```bash
$ deactivate
```

### Pushing to gcloud
You may need to first authenticate gcloud and point it to the project if
you have not done the initial setup
```bash
$ gcloud auth login
...
$ gcloud config set project various-plans
```
To deploy a new version of the app...
```bash
$ gcloud app deploy
```
If you're lazy and can't find the URL for the project...
```bash
$ gcloud app browse
```

### Setting up local Google Cloud SQL connection

Open the gcloud sql link [here][1]. This should take you to the _Install
the SQL proxy_ heading.
This will let you download the OS-specific file.

Please ensure you save the file as `cloud_sql_proxy` as this is ignored
in the `.gitignore`, otherwise we're gonna have some bad times.

To ensure the cloud proxy connection whatever can authenticate with
google properly, you will need to set up the default login

```bash
$ gcloud auth application-default login
```


## Run server locally
In order to run the local SQL database, which connects to the gcloud SQL
database, run
```bash
$ ./cloud_sql_proxy -instances="various-plans:europe-west1:library"=tcp:3306
```
For Windows users, note that the connection name is
`various-plans:europe-west1:library`.

To run the server
```bash
$ dev_appserver.py app.yaml
```
This will start the server at http://localhost:8080/

Quit the dev server with `Ctrl+C`

[1]: https://cloud.google.com/python/getting-started/using-cloud-sql#install_the_sql_proxy