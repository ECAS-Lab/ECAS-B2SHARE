from requests import Request, Session

s = Session()

req = requests('POST', url, data=data, headers=headers)

