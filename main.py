from logging import Logger
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from pythonping.executor import Response
from sqlalchemy import exc
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.routing import request_response
from database import SessionLocal, engine
from datetime import datetime
from app_log import make_logger
from pythonping import ping
import sqlalchemy
import models
import schemas
import requests
import random

# create the database
models.Base.metadata.create_all(bind=engine)

# Initialise the app as a decorator
app = FastAPI()

# add middle ware classes
app.add_middleware(
    CORSMiddleware, # Enable Cross Origin Resource Sharing
    allow_origins=['127.0.0.1:8000',]
)

# Moount the static files folder
app.mount('/static', StaticFiles(directory='static'), name='static')

# Mount the templates directory
templates = Jinja2Templates(directory='templates')

# logger variable
log: Logger = make_logger()

# Dependancy returns a db connection and closses it once it's used
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# App startup events
@app.on_event('startup')
def startup_event():
    # creae the logger
    log = make_logger()
    # log app startup
    log.info("App starting up")
    # init db, get db objs, do whatever
    with open('log.txt', mode='a') as log_file:
        time = datetime.now()
        msg: str = f'[{time}]: Application starting\n'
        # log_file.write(msg)

# App shutdown events
@app.on_event('shutdown')
def shutdown_event():
    log.warning("App shutting down")
    # do shut down house cleaning
    with open('log.txt', mode='a') as log_file:
        time = datetime.now()
        msg: str = f'[{time}]: Application shutting down\n'
        # log_file.write(msg)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket = None):
        for connection in self.active_connections:
            if websocket is None:
                await connection.send_json(message)
                return
            if connection is not websocket:
                await connection.send_json(message)

# Instantiate the connection manager
manager = ConnectionManager()

# An endpoint tothe homepage (site root)
@app.get("/", response_class = HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})

# An endpoint to add a website
@app.post("/addsite")
async def add_site(new_site: schemas.WebsitePost, db: Session = Depends(get_db)):
    # Create the website based on request body
    website: models.Website = models.Website(
        name = new_site.name, 
        protocol = new_site.protocol, 
        url = new_site.url,
        port = new_site.port,
    )
    try:
        # add the website to the DB Session
        db.add(website)
        # Commit the transaction (save to DB)
        db.commit()
        # log the add
        log.info(f"Website {website.name} ({website.get_url}) with id '{website.id}' succsesfully added to the database")
        # Get list of sites
        sites = db.query(models.Website).all()
        # Broadcast site list to all clients
        await manager.broadcast(sites)
    except sqlalchemy.exc.InvalidRequestError as e:
        # log the exception
        msg = f'Error commiting a website add for site {website.name} ({website.get_url}):\n\t{e}'
        log.error(msg,exc_info=True)
    except Exception as e:
        # log unknown error
        msg = f'Unknown exception commiting add for site {website.name} ({website.get_url})::\n\t{e}'
        log.error(msg, exc_info=True)       

# An endpoint to modify a website
@app.patch("/update/{id}")
async def update_site(id:str, update: schemas.WebsitePatch, db: Session = Depends(get_db)):
    # get the object to be updated from DB
    website: models.Website = db.query(models.Website).filter_by(id = id)
    if website is None:
        # Log error
        msg = f"Update query for a website with id '{id}':\n\t No such website in the database."
        log.error(msg=msg, exc_info=True)
        return
    try:
        # update the site name if the name was in the body or leave it as is
        website.name = update.name if update.name else website.name
        # update the site port if the port was in the body or leave it as is
        website.port = update.port if update.port else website.port
        # update the site protocol if the protocol was in the body or leave it as is
        website.protocol = update.protocol if update.protocol else website.protocol
        # update the site url if the url was in the body or leave it as is
        website.url = update.url if update.url else website.url
        # Commit the changes
        db.commit()
        # Get list of all sites
        sites = db.query(models.Website).all()
        # Update all clients with new list
        await manager.broadcast(sites)
        # log successful update
        log.info(f"Succsefully updated site: {website.name} ({website.get_url}) with data:\n{update}")
    except Exception as e:
        # Log error
        msg = f"Delete query for a website with id '{id}':\n\t No such website in the database."
        log.error(msg=msg, exc_info=True)
    finally:
        # free resoures
        del(db)
        del(update)
        del(id)

# An endpoint to delete a website
@app.delete("/delete/{id}")
async def remove_site(id: str, db: Session = Depends(get_db)):
    website: models.Website = db.query(models.Website).filter_by(id = id)
    if website is None:
        # Log error
        msg = f"Delete query for a website with id '{id}':\n\t No such website in the database."
        log.error(msg=msg, exc_info=True)
        return
    try:
        db.delete(website)
        db.commit()
        log.info(f"Website {website.name}({website.get_url}) with id '{website.id}' succsesfully deleted from the database")
        # Get list of sites
        sites = db.query(models.Website).all()
        # update all socket clients of new list
        await manager.broadcast(sites)
    except Exception as e:
        # log unknown error
        msg = f"Unknown exception deleting website with id '{id}':\n\t{e}"
        log.error(msg, exc_info=True)

# The websocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    # Get list of sites
    sites = db.query(models.Website).all()
    try:
        while True:
            #TODO: Figure out how to send objects to the users
            # Send list of sites to all clients
            await manager.broadcast(sites, websocket)
            # TODO: send models to websocket recipients
            data = await websocket.receive_text()
            # Recieve a message
            message = await websocket.receive_json()
            # add site to db
            # /notify the sender of succesful trans
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}", websocket)
            
    except WebSocketDisconnect as e:
        #print(f'Websocket  error:\n{e}')
        # log the exception
        msg: str = f'WebsocketDisconnect error:\n\t{e}\n'
        log.error(msg,exc_info=True)
        with open('error.txt', mode='a') as log:
            time = datetime.now()
            msg: str = f'WebsocketDisconnect error:\n\t{e}\nApplication shutting down\n'
            #log.write(msg)
        manager.disconnect(websocket)

        await manager.broadcast(f"Client #{client_id} left the chat")
    except Exception as e:
        # log the exception
        msg: str = f'Websocket error:\n\t{e}\n'
        log.error(msg,exc_info=True)
        with open('error.txt', mode='a') as log:
            time = datetime.now()
            msg: str = f'[{time}]: Websocket error:\n\t{e}\nApplication shutting down\n'
            #log.write(msg)

# A method to ping the sites
async def ping_site(website: models.Website) -> bool:
    '''
    This method uses the pythonping package to do ICMP echoes to a given host
    because ICMP can only be sent from root mode it means this script needs to be run as root
    '''
    is_online: bool = False
    try:
        response: Response = ping(website.get_url, count=1)
        if response.success:
            msg: str = f'Ping succsessfule for site {website.name} ({website.get_url})'
            log.info(msg)
            is_online =  True
        else:
            msg: str = f'Ping failed for site {website.name} ({website.get_url}):\n\t{response.error_message}'
            log.warning(msg)
            is_online =  False
    except Exception as e:
        is_online = False
        # log the exception
        msg: str = f'Ping error for site {website.name} ({website.get_url}):\n\t{e}\n'
        log.error(msg,exc_info=True)
    finally:
        return is_online

# A method to test webservers
async def test_site(website: models.Website) -> str:
    site_status : str = ''
    try:
        # headers for chrome browser to prevent a bot block making us report false errors
        user_agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]
        for i in range(1,4):
            #Pick a random user agent
            user_agent = random.choice(user_agent_list)
            #Set the headers 
            headers = {'User-Agent': user_agent}
            # send a request to the site and log the response
            response = requests.get(website.get_url, headers=headers)
            if response.status_code == 200:
                msg = f"site {website.name} ({website.get_url}) online with 200 response"
                log.info(msg=msg)
            else:
                msg = f"Warnign: site {website.name} ({website.get_url}) online but has a {response.status_code} response"
                log.warning(msg)
            site_status = str(response.status_code)
    except requests.exceptions.ConnectionError as e:
        site_status = 'Unable to connect'
        # log connection error
        msg: str = f'{site_status} site {website.name} ({website.get_url}):\n\t{e}\n'
        log.error(msg,exc_info=True)
    except Exception as e:
        site_status = 'Unknown Error checking page'
        # log the exception
        msg: str = f'Unknown exception checking site {website.name} ({website.get_url}):\n\t{e}\n'
        log.error(msg,exc_info=True)
    finally:
        return site_status

# Site checking method
async def site_checker(website: models.Website) -> bool:
    success: bool = False
    try:
        # get the database session
        db: Session = next(get_db())
        # create a new status object
        status: models.Status = models.Status()
        # connect the status to a site
        status.url_id = website.id
        # ping site and store onlineness
        status.online = await ping_site(website)
        # Check the site and store response code
        status.response_code = await test_site(website)
        # get the timestamp
        status.timestamp = datetime.datetime.now()
        # add the status to the DB
        db.add(status)
        db.commit()
        success = True
    except sqlalchemy.exc.InvalidRequestError as e:
        # log the exception
        msg = f'Error commiting a status add for site {website.name} ({website.get_url}):\n\t{e}'
        log.error(msg,exc_info=True)
    except Exception as e:
        # log unknown error
        msg = f'Unknown exception commiting a status add for site {website.name} ({website.get_url}):\n\t{e}'
        log.error(msg, exc_info=True)
    finally:
        return success 

# method that does the site checking (pings and requests)
async def do_checks():
    # get list of sites
    db: Session = next(get_db())
    sites: List[models.Website] = db.query(models.Website).all()
    # TODO: parralelise the call to sitecheck with list
    _ = [await site_checker(site) for site in sites]
    # get list of stati
    stati: List[models.Status] = db.query(models.Status).all()
    # Broadcast stati to the clients
    manager.broadcast(stati)
# TODO: run schedule to perform site checks here