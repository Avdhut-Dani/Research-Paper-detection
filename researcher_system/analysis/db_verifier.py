import requests

def check_doi(doi):
    url=f"https://api.crossref.org/works/{doi}"
    r=requests.get(url)
    return r.status_code==200
