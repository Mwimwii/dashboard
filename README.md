# Dashboard

## Introduction

This was initially a fork of mwimwi's  repository by the same name, but has now pivoted to using FastAPI instead of Flask.

## Download & Installation

```bash
git clone https://github.com/itisentropy/dashboard/
cd dashboard
pip install -r requirements.txt
```
## Configurations
## Running the app
```bash
You can run the app usng the `uvicorn` server and a hot reload functionality that reloads the server whenever the source code has a saved change.  
if you do not want hot reloads you can exclude it byt omiting the `--reload` argument of the command. 
```
```bash
uvicorn main:app --reload
```

The web application should now be running on `127.0.0.1:5000` and `<your_ip>:5000`