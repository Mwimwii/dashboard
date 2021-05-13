



# Dashboard

## Introduction

This is a fork of mwimwi's  repository by the same name

## Download & Installation

To download it you need to first clone the repository and download the set of dependencies that the app requires to run by running the following commands:

```bash
git clone https://github.com/itisentropy/dashboard/
cd dashboard
pip install -r requirements.txt
```
## Configurations
## Running the app

This app runs on an ASGI server called `uvicorn`. This server is built into the project so to run it simply runt the `uvicorn <module>:<app name>` command with `<module>` being the name of the python file where the app is instantiated in and `<app name> `being the name that the app is instantiated with. In the case of this project the python file is named main and the app name is app so you type the following command:

```bash
uvicorn main:app
```
It is also possible to run the app and listen for changes to source files so the server automatically restarts to load your code changes. Be careful when using this feature though because it watches all files so only use it if your app does not write to log files during execution. You can watch for changes by running the following command.

```bash
uvicorn main:app --reload
```

The web application should now be running on `127.0.0.1:5000` and `<your_ip>:5000`