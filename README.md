



# Dashboard

## Introduction

This is a fork of mwimwi's  repository by the same name.
The Dashboard is a web app that allows for the real-time monitoring of websites and their status, status being whether their web server is online, and if they have an error or non `success` (200)  http response code, or an SSL error.

## Download & Installation

To download it you need to first clone the git repository and download the set of dependencies that the app requires to run by running the following commands:

```bash
git clone https://github.com/itisentropy/dashboard/
cd dashboard
pip install -r requirements.txt
```
If you do not have git installed on your system you can download it from [here](https://git-scm.com/download/), then run the commands again.

## Configurations

To configure the application, open the `.env example` file and create a new file named `.env` with the settings found in the `.env example` file.

## Running the app

This app runs on an ASGI server called `uvicorn`. This server is built into the project so to run it simply runt the `uvicorn <module>:<app name>` command with `<module>` being the name of the python file where the app is instantiated in and `<app name> `being the name that the app is instantiated with. In the case of this project the python file is named main and the app name is app so you type the following command:

```bash
uvicorn main:app
```
### Server command arguments

1. `--reload` automatically reloads whenever a file in the directory or its child directories is changed
2. ` --port` specifies the port which the server listens on
3. `--workers` specifies the number of workers the server will have
4. `--host` specifies the IP address the server will host itself on

It is possible to run the app and listen for changes to source files so the server automatically restarts to load your code changes by using the `--reload` argument. Be careful when using this feature though because it watches all files so only use it if your app does not write to log files during execution. You can watch for changes by running the following command:

```bash
uvicorn main:app --reload
```

You can change what port the webserver runs on by using the  optional `--port <port_number>`  command modifier so the server runs on the port specified in place of `<port_number>`. All together the command now looks like this:

```bash
uvicorn main:app --reload --port 8000 --workers 2 --host 127.0.0.1
```

The web application should now be running on `127.0.0.1:8000 `wit 2 worker threads and automatic reloading.