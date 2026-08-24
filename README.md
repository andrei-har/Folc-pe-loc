# folc pe loc

full-stack web app for booking traditional romanian folk dance performances. built with flask and mysql.

## what it does

- clients can register, browse available dances, and book a performance for their event in a 3-step reservation flow
- the coregraf (dance group admin) can review booking requests, accept/reject them, and manage the dance catalog (crud)
- clients can pay for accepted events and leave a review afterwards
- public reviews page, visible without logging in
- history/report views with filters (status, past/future) for the coregraf

## tech stack

- python + flask
- mysql + sqlalchemy (orm)
- flask-login, flask-wtf, wtforms
- tailwind css (via cdn)
- jinja2 templates
