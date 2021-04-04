from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import sqlalchemy
from sqlalchemy import exc
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.routing import request_response
from database import SessionLocal, engine
from datetime import datetime
from app_log import log
import crud
import models
import schemas

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
    # init db, get db objs, do whatever
    with open('log.txt', mode='a') as log:
        time = datetime.now()
        msg: str = f'[{time}]: Application starting\n'
        # log.write(msg)

# App shutdown events
@app.on_event('shutdown')
def shutdown_event():
    # do shut down house cleaning
    with open('log.txt', mode='a') as log:
        time = datetime.now()
        msg: str = f'[{time}]: Application shutting down\n'
        log.write(msg)

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
async def add_site(name: str = Form(...), url: str = Form(...), port: str = Form(...), protocol: str = Form(...), db: Session = Depends(get_db)):
    # Create the website based on form data
    website: models.Website = models.Website(name=name, protocol=protocol, url=url, port=port)
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
        manager.broadcast(sites)
    except sqlalchemy.exc.InvalidRequestError as e:
        # log the exception
        msg = f'Error commiting a website add for site {website.name} ({website.get_url}):\n\t{e}'
        log.error(msg,exc_info=True)
    except Exception as e:
        # log unknown error
        msg = f'Unknown exception:\n\t{e}'
        log.error(msg, exc_info=True)       

# An endpoint to modify a website
@app.patch("/update/{id}")
async def update_site(id:str, update: schemas.Website, db: Session = Depends(get_db)):
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
        manager.broadcast(sites)
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
        manager.broadcast(sites)
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
        # TODO: log the exception
        print(f'Websocket error:\n{e}')
        with open('error.txt', mode='a') as log:
            time = datetime.now()
            msg: str = f'[{time}]: Websocket error:\n\t{e}\nApplication shutting down\n'
            log.write(msg)
        manager.disconnect(websocket)

        await manager.broadcast(f"Client #{client_id} left the chat")
    except Exception as e:
        with open('error.txt', mode='a') as log:
            time = datetime.now()
            msg: str = f'[{time}]: Websocket error:\n\t{e}\nApplication shutting down\n'
            log.write(msg)
        # TODO: Make a log here.

# A method to ping the sites
def ping_sites():
    pass