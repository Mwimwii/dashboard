from fastapi import FastAPI, WebSocket
from fastapi.param_functions import File
from starlette.requests import Request
from models import Website
from typing import Optional
from uuid import UUID
from fastapi import Header
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()


# Mount the static dir
app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

# TODO: Read an HTML file that calls the API to return an html list of data to the user
websites = {}

# FIXME: fix placeholder routes
@app.get('/')
async def get_sites(request: Request):
    return templates.TemplateResponse('home.html', {'request': request})

# add a website to the dashboard
@app.post('/', response_model = Website)
async def add_website(website: Website):
    # TODO: Save the website in a DB or soemthing
    pass

# get information about a particular website
@app.get('/{site_id}', response_class=HTMLResponse)
async def get_site_info(site_id: UUID, request: Request):
    # TODO: get a website and its info from DB or something
    return templates.TemplateResponse('siteinfo.html', {'request' : request, 'site_id' : site_id})
    
    

# update a single field of a site
@app.patch('/{site_id}', response_model = Website)
async def update_site_info(site_id: UUID, website: Website):
    curent_site_data = websites[site_id]
    curent_site_model = Website(**curent_site_data)
    update_data = website.dict(exclude_unset=True)
    updated_site = curent_site_model.copy(update=update_data)
    websites[site_id] = jsonable_encoder(updated_site)
    return updated_site

# delete a website
@app.delete('/{site_id}')
async def delete_site(site_id: UUID):
    # TODO: delete a website and its info from DB or something
    pass

@app.websocket('/ws')
async def socketdemo(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f'Message text was:: {data}')

# Check the status of a website.