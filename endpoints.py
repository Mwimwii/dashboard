from models import Website
from typing import Optional



# FIXME: fix placeholder routes
@app.get('/')
async def read_root():
    # TODO: make it return list of all sites.
    return {"hello" : "world"}

# add a website to the dashboard
@app.post('/')
async def add_website(website: Website):
    # TODO: Save the website in a DB or soemthing
    pass

# get information about a particular website
@app.get('/{site_id}')
async def get_site_info(site_id: int):
    # TODO: get a website and its info from DB or something
    pass

# update a single field of a site
@app.patch('/{site_id}')
async def get_site_info(site_id: int, \
    host_name: Optional[str] = None, \
    protocol: Optional[str] = None, \
    port: Optional[int] = None, \
    domain: str = None, \
    sub_domain: Optional[str] = None):
    # TODO: update a website's info in DB or something
    if host_name is not None:
        pass
    if protocol is not None:
        pass
    if port is not None:
        pass
    if domain is not None:
        pass
    if sub_domain is not None:
        pass
    pass

# delete a website
@app.delete('/{site_id}')
async def get_site_info(site_id: int):
    # TODO: delete a website and its info from DB or something
    pass

# Check the status of a website.