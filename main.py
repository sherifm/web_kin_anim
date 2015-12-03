from flask import Flask, render_template
import subprocess
from os import environ
import logging
import psutil

CALL_COUNT=0
p = None

app= Flask(__name__)
app.debug = True

environ['LC_ALL'] ='C'
environ['ROS_ROOT'] = '/opt/ros/indigo/share/ros'
environ['ROS_PACKAGE_PATH'] = '/home/vmagent/catkin_ws/src:\
	/opt/ros/indigo/share:/opt/ros/indigo/stacks'
environ['ROS_MASTER_URI'] = '//localhost:11311'
environ['ROS_DISTRO'] = 'indigo'
environ['ROS_ETC_DIR'] ='/opt/ros/indigo/etc/ros'
environ['LD_LIBRARY_PATH'] = '/home/vmagent/catkin_ws/devel/lib:\
	/home/vmagent/catkin_ws/devel/lib/x86_64-linux-gnu:\
	/opt/ros/indigo/lib:/opt/ros/indigo/lib/x86_64-linux-gnu'
environ['CPATH'] = '/home/vmagent/catkin_ws/devel/include:\
	/opt/ros/indigo/include'
environ['PATH'] = '/home/vmagent/catkin_ws/devel/bin:\
	/opt/ros/indigo/bin:/usr/local/sbin:\
	/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' 
environ['PYTHONPATH'] = '/home/vmagent/catkin_ws/devel/lib/python2.7/dist-packages:\
	/opt/ros/indigo/lib/python2.7/dist-packages'
environ['PKG_CONFIG_PATH'] = '/home/vmagent/catkin_ws/devel/lib/pkgconfig:\
	/home/vmagent/catkin_ws/devel/lib/x86_64-linux-gnu/pkgconfig:\
	/opt/ros/indigo/lib/pkgconfig:\
	/opt/ros/indigo/lib/x86_64-linux-gnu/pkgconfig'
environ['CMAKE_PREFIX_PATH'] ='/home/vmagent/catkin_ws/devel\
	:/opt/ros/indigo'

@app.route('/')
def home():
  return render_template('home.html')

@app.route("/start_process")
def start():
	global p
	try:
		# p = subprocess.Popen(["source","/opt/ros/indigo/setup.bash"])
		p = subprocess.Popen(["roscore"])
		logging.info('Child process started succesfully')
		message = 'Process started'
	except:
		logging.error('Could not start process')
		message = 'Could not start process'
	return message

@app.route("/stop_process")
def stop():
	global p
	if p is not None:
		if p.poll() is None:
			try:
				kill(p.pid)
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
	return 'Attempting stop process. <br> \
		Returned status: {0:s}'.format(p_status)

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
	return 'This process has been called {0:d} <br> p_status \
		= {1:s}'.format(CALL_COUNT, p_status)

def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.get_children(recursive=True):
        proc.kill()
    process.kill()

if __name__ == '__main__':
	logging.getLogger().setLevel(logging.DEBUG)
	app.run()