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

###########Global vars and objects #############
user_db = None

#Define User class
class User(object):

    def __init__(self,name, pwd):
        self.username = name
        self.password = pwd
        self.process = None
        self.port = None

##########Non-routed helper functions###########

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

def get_external_ip():
    ps = subprocess.Popen('wget http://ipinfo.io/ip -qO -',\
                        shell=True, stdout=subprocess.PIPE)
    ps.wait()
    external_ip = ps.communicate()[0]
    ps.stdout.close()
    return external_ip

########## Routed functions ##################

# use decorators to link the function to a url
@app.route('/')
@login_required
def index_page():
    return render_template('index.html', ws_url=session['ros_ws_url'], \
                                user=session['username'], port=session['port'],\
                                ip=get_external_ip())  

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
                    session['ros_ws_url'] = 'ws://'+get_external_ip().rstrip()+':'+session['port']
                    flash('You were logged in.')
                return render_template('index.html', ws_url=session['ros_ws_url'], \
                                            user=session['username'], port=session['port'],\
                                            ip=get_external_ip()) 
        else:
            flash('Invalid Credentials. Please try again.')
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_index', None)
    session.pop('user_name', None)
    session.pop('port', None)
    flash('You were logged out.')
    return redirect(url_for('login'))

@app.route("/home" , methods=['GET', 'POST'])
@login_required
def home():
    # ros_ws_url = 'ws://'+get_external_ip().rstrip()+':'+session['port']
    return render_template('index.html', ws_url=session['ros_ws_url'], \
                            user=session['username'], port=session['port'],\
                            ip=get_external_ip())

@app.route("/start_process" , methods=['GET', 'POST'])
@login_required
def start():
    try:
        #Use the -i interactive shell argument for server deployment. #Omit for local testing
        user_db[session['user_index']].process = subprocess.Popen(["/bin/bash","-i","-c",\
                                "roslaunch kinematics_animation pr2_web_animation.launch \
                                ws_port:=%s" %session['port']])
        # user_db[session['user_index']].process = subprocess.Popen(["/bin/bash","-i","-c","roscore -p %s" %session['port']])
        logging.info('Child process started succesfully')   
        flash("Started roscore for user %s on port %s" %(session['username'],session['port']))
    except:
        logging.error('Could not start process')
        flash('Could not start process')
    return render_template('index.html', ws_url=session['ros_ws_url'],\
                                user=session['username'], port=session['port'],\
                                ip=get_external_ip()) 

@app.route("/stop_process", methods=['GET', 'POST'])
@login_required
def stop():
    p = user_db[session['user_index']].process
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
    return render_template('index.html', ws_url=session['ros_ws_url'], \
                                user=session['username'], port=session['port'],\
                                ip=get_external_ip())    

@app.route("/find_process" , methods=['GET', 'POST'])
@login_required
def find_process():
    p = user_db[session['user_index']].process
    if p is not None:
        p_status = p.poll()
        try:
            if p_status == None:
                p_status = 'Process Running'
            else:
                p_status = 'Process exited with exit code '+str(p_status)
            p_status = str(p_status)
        except:
            p_status = "conversion failed"
    else:
        p_status = 'No running process found'
    flash('Current process status: {0:s}'.format(p_status))
    return render_template('index.html', ws_url=session['ros_ws_url'], \
                                user=session['username'], port=session['port'],\
                                ip=get_external_ip())  

@app.route("/list_process")
@login_required
def list_process():
    ps = subprocess.Popen('ps aux'.split(), stdout=subprocess.PIPE)
    grep = subprocess.Popen('grep roslaunch'.split(), stdin=ps.stdout, stdout=subprocess.PIPE)
    ps.wait()
    ps.stdout.close()
    output = grep.communicate()[0]
    flash('%s' %output)
    return render_template('index.html')  

############## Create DB and start app ################

#Create a user database
user_db = create_user_db(3)
#Assign hard-coded ports to users
assign_port(user_db,'User0','1234')
assign_port(user_db,'User1','1235')
assign_port(user_db,'User2','1236')

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    app.run()