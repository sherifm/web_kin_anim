from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_simple
from main import app 


app = DebuggedApplication(app, evalex=True)
run_simple('localhost',7070,app,use_reloader=True)