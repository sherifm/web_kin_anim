# #Must use google's python compatible debian image as base
# FROM gcr.io/google_appengine/python-compat

# #Install linux packages
# RUN apt-get update && apt-get install -y \
# 	python-setuptools \
# 	wget \
# 	git \
# 	python-numpy python-scipy \
# 	gcc \
# 	make \
# 	cmake \
# 	build-essential \
# 	checkinstall \
# 	python-psutil \
# 	stress
# RUN easy_install pip

# #Install app requirements
# ADD requirements.txt /app/
# RUN pip install -r /app/requirements.txt
# ADD . /app/

# #Set-up ROS repos
# RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu wheezy main" \
# 	> /etc/apt/sources.list.d/ros-latest.list'
# RUN wget https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
# 	-O - | apt-key add -

# #Enable Wheezy Backports repo
# RUN sh -c 'echo "deb http://http.debian.net/debian \
# 	wheezy-backports main" > /etc/apt/sources.list.d/backports.list'
# RUN apt-get update && apt-get upgrade -y

# #Install rosdep and rosinstall to bootstrap ROS
# RUN pip install rosdep rosinstall_generator wstool

# #Initialize rosdep
# RUN rosdep init && rosdep update

# #Create ros workspace dir
# RUN mkdir -p /home/vmagent/ros_ws

# #Create ros_ws
# RUN cd /home/vmagent/ros_ws && \
# 	rosinstall_generator ros_comm geometry_msgs xacro \
# 	joint_state_publisher robot_state_publisher rosbridge_suite \
# 	tf2_web_republisher pr2_description --rosdistro indigo \
# 	--deps --wet-only --exclude roslisp \
# 	--tar > indigo-custom_ros.rosinstall
# RUN cd /home/vmagent/ros_ws && \
# 	wstool init -j4 src indigo-custom_ros.rosinstall

# #Create external source dir
# RUN mkdir -p /home/vmagent/ros_ws/external_src

# #Install libconsole-bridge-dev
# RUN apt-get install -y libboost-system-dev libboost-thread-dev
# RUN git clone https://github.com/ros/console_bridge.git \
# 	/home/vmagent/ros_ws/external_src/console_bridge
# RUN cd /home/vmagent/ros_ws/external_src/console_bridge && \
# 	cmake /home/vmagent/ros_ws/external_src/console_bridge/. && \
# 	checkinstall --nodoc -y --pkgname=libconsole-bridge-dev make install

# #Install liburdfdom-headers-dev
# RUN git clone https://github.com/ros/urdfdom_headers.git \
# 	/home/vmagent/ros_ws/external_src/urdfdom_headers
# RUN cd /home/vmagent/ros_ws/external_src/urdfdom_headers && \
# 	cmake /home/vmagent/ros_ws/external_src/urdfdom_headers/. && \
#  	checkinstall --nodoc -y --pkgname=liburdfdom-headers-dev make install

# #Install liburdfdom-dev
# RUN apt-get update -y &&\
# 	apt-get install -y libboost-test-dev libtinyxml-dev
# RUN git clone https://github.com/ros/urdfdom.git \
# 	/home/vmagent/ros_ws/external_src/urdfdom
# RUN cd /home/vmagent/ros_ws/external_src/urdfdom && \
# 	cmake /home/vmagent/ros_ws/external_src/urdfdom/. &&\
# 	checkinstall --nodoc -y --pkgname=liburdfdom-dev make install

# #Install liblz4-dev
# RUN apt-get -y -t wheezy-backports install liblz4-dev

# #Resolve some dependencies with rosdep
# RUN cd /home/vmagent/ros_ws/ && \
# 	rosdep install --from-paths src --ignore-src --rosdistro=indigo -y -r \
# 	--os=debian:wheezy --as-root="apt:false" \
# 	--skip-keys="python-rosdep python-rospkg python-catkin-pkg"

# #Build the ros workspace
# RUN cd /home/vmagent/ros_ws/ && \
# 	./src/catkin/bin/catkin_make_isolated --install -DCMAKE_BUILD_TYPE=Release \
# 	--install-space /opt/ros/indigo

# #Create and initialize catkin workspace dir
# RUN mkdir -p /home/vmagent/catkin_ws/src 
# RUN /bin/bash -c "source /opt/ros/indigo/setup.bash && \
# 	cd /home/vmagent/catkin_ws/src &&\
# 	catkin_init_workspace"

# #Clone kinematics_animation, universal_robot 
# #	,barrett_model and youbot description packages
# RUN git clone https://github.com/sherifm/universal_robot.git \
# 	/home/vmagent/catkin_ws/src/universal_robot
# RUN git clone -b web https://github.com/sherifm/kinematics_animation.git \
# 	/home/vmagent/catkin_ws/src/kinematics_animation
# RUN git clone https://github.com/sherifm/barrett_model.git \
# 	/home/vmagent/catkin_ws/src/barrett_model
# RUN git clone https://github.com/mas-group/youbot_description.git \
# 	/home/vmagent/catkin_ws/src/youbot_description

# RUN /bin/bash -c "source /opt/ros/indigo/setup.bash && \
# 	cd /home/vmagent/catkin_ws && \
# 	catkin_make"

# #Setup bashrc
# RUN sh -c 'echo "source /home/vmagent/catkin_ws/devel/setup.bash" >> ~/.bashrc'
# RUN sh -c 'echo "export LC_ALL=C" >> ~/.bashrc'

FROM sherifm/ros_webtool:latest

#Update app requirements
ADD requirements.txt /app/
RUN pip install -r /app/requirements.txt
ADD . /app/

#Setup bashrc
RUN sh -c 'echo "source /home/vmagent/catkin_ws/devel/setup.bash" >> ~/.bashrc'
RUN sh -c 'echo "export LC_ALL=C" >> ~/.bashrc'


# setup entrypoint
#COPY ./entrypoint.sh /

#ENTRYPOINT ["/entrypoint.sh"]
#CMD ["bash"]
