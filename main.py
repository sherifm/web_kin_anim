from flask import Flask , render_template, redirect, \
    url_for, request, session, flash
import subprocess
import os
import logging
import psutil
from functools import wraps

app= Flask(__name__)
app.debug = True

# config
app.secret_key = os.urandom(24)

#Global vars
CALL_COUNT=0 #Counter
p = None #Subrocess
user_db = None

#Define User class
class User(object):

    def __init__(self,name, pwd):
        self.username = name
        self.password = pwd
        self.port = None

#Generate a proxy to database of users
def create_user_db(num_users):
    users={}
    for i in range(num_users):
        users[i]=User('User'+`i`,'ROS')
    return users

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

def assign_port(user_db,name,port):
    for i in range(len(user_db)):
        if user_db[i].username==name:
            user_db[i].port = port
            message = 'Set port %s for user %s'\
                % (user_db[i].port , user_db[i].username)
            return message
    message='Could not find user %s' % (name)
    return message

def kill_process(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.get_children(recursive=True):
        proc.kill()
    process.kill()

#################################################################################

# use decorators to link the function to a url
@app.route('/')
@login_required
def index_page():
    return render_template('index.html',\
        user=session['username'],\
        port=session['port'])  

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        for i in range(len(user_db)):
            if request.form['username'] == user_db[i].username:
                if request.form['password'] == user_db[i].password:
                    session['logged_in'] = True
                    session['user_index'] = i
                    session['username'] = request.form['username']
                    session['port'] = user_db[session['user_index']].port
                    flash('You were logged in.')
                return redirect(url_for('index_page'))
        else:
            flash('Invalid Credentials. Please try again.')
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))


#########################################################3

@app.route("/home")
def home():
  return render_template('home.html')

@app.route("/start_process")
@login_required
def start():

    global p
    try:
        #Use the -i interactive shell argument for web deployment
        # p = subprocess.Popen(["/bin/bash","-i","-c","roscore -p %s" %session['port']])
        p = subprocess.Popen(["/bin/bash","-c","roscore -p %s" %session['port']])
        logging.info('Child process started succesfully')
        flash("Started roscore for user %s on port %s" %(session['username'],session['port']))
    except:
        logging.error('Could not start process')
        flash('Could not start process')
    return render_template('index.html')

@app.route("/stop_process")
def stop():
    global p
    if p is not None:
        if p.poll() is None:
            try:
                kill_process(p.pid)
                p.wait()
            except:
                p_status='Running process not killed'
                logging.error('Could not kill process') 
        else:
            logging.warning('Process has already been stopped') 
        p_status = p.poll() 
    else:
        p_status = 'No running process found!'
    try:
        p_status = str(p_status)
    except:
        p_status = "conversion failed"
    flash('Attempting stop process.\n Returned status: {0:s}'.format(p_status))
    return render_template('index.html')   

@app.route("/find_process")
def find_process():
    global CALL_COUNT, p
    CALL_COUNT +=1
    if p is not None:
        p_status = p.poll()
    else:
        p_status = 'No running process found'
    try:
        p_status = str(p_status)
    except:
        p_status = "conversion failed"
    flash('This process has been called {0:d} times. \
        Current status: {1:s}'.format(CALL_COUNT, p_status))
    return render_template('index.html')  

@app.route("/list_process")
def list_process():
    ps = subprocess.Popen('ps aux'.split(), stdout=subprocess.PIPE)
    grep = subprocess.Popen('grep roscore'.split(), stdin=ps.stdout, stdout=subprocess.PIPE)
    ps.wait()
    ps.stdout.close()
    output = grep.communicate()[0]
    flash('%s' %output)
    return render_template('index.html')  

###################################################################################################

#Create a user database
user_db = create_user_db(3)
#Assign hard-coded ports to users
assign_port(user_db,'User0','1234')
assign_port(user_db,'User1','1235')
assign_port(user_db,'User2','1236')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    app.run()