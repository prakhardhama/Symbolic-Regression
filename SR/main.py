import bottle
from bottle import route, request, error, debug, response, post, redirect
from google.appengine.ext.webapp.util import run_wsgi_app
import GP

@route('/')
def usage():
	str="<h2>Usage: arc-tron.appspot.com/{hidden function}</h2><br/>"
	str=str + "<h4>For ex: http://arc-tron.appspot.com/x+10</h4>"
	str=str + "<h4>For ex: http://arc-tron.appspot.com/x+y+10</h4><br/>"
	return str
	
@route('/<func>') 
def index(func):
	return GP.getgenfunction(func,False)
		
@post('/<func>') 
def realTime(func):
	return GP.getgenfunction(func,True)
				
#@error(500)
#def error500(error):
#   return '<h2><center>What the f*ck did you just do?Asshole...</center></h2>'

@error(404)
def error404(error):
    return '<h2><center>What the f*ck are you trying to do?Asshat...</center></h2>'	

def main():
    debug(True)
    run_wsgi_app(bottle.default_app())
 		
if __name__=="__main__":
    main()