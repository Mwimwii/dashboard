# Dashboard

## Download & Installation

```bash
git clone https://github.com/Mwimwii/dashboard/
cd dashboard
```
## Configurations

### On Windows

```bash
  set FLASK_DIR=app
  set FLASK_ENV=development
```
### On Linux

```bash
  export FLASK_DIR=app
  export FLASK_ENV=development
```

## Running the app

You can run the app with `-h` option to allow other pc's to access the site on the network

```bash
flask run -h 0.0.0.0
'''

The web application should now be running on `127.0.0.1:5000` and `<your_ip>:5000`
