from math import pi, sin, cos
import time
import numpy as np

import sys
import computecolor
import skimage.io
 
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
import panda3d.core
from panda3d.core import *
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce

from flowgen import *

np.random.seed(123)

u = lambda a=0., b=1.: (b - a) * np.random.rand() + a

CHAIRMODELS = "/home/jdt/Downloads/chairs/chairmodels/"
BACKGROUNDS = "/home/jdt/Downloads/chairs/city/"
CHARACTERS = "/home/jdt/Code/code3d/asset-pack/000-characters-med/Assets/models/"

loadPrcFileData("", "basic-shaders-only #f")
loadPrcFileData("", "hardware-animated-vertices #f")
loadPrcFileData("", "win-size 75 75")


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
 
        # Disable the camera trackball controls.
        #self.disableMouse()

        self.mybase = NodePath("MyBase")
        self.mybase.reparentTo(render)

        self.camholder = NodePath("CamHolder")
        self.camholder.reparentTo(render)
        self.camera.reparentTo(self.camholder)

        self.render.setShaderAuto()
 
        # Load the environment model.
        #self.environ = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        #self.environ.reparentTo(self.mybase)
        # Apply scale and position transforms on the model.
        #self.environ.setScale(0.25, 0.25, 0.25)
        #self.environ.setPos(-8, 42, 0)
 
        # Add the spinCameraTask procedure to the task manager.
        #self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.spinPandaTask, "SpinPandaTask")
 
        # Load and transform the panda actor.

        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.007, 0.005, 0.006)
        self.pandaActor.setPos(0,0,-.2)
        self.pH = 0.;
        self.pP = 0.;
        self.pR = 0.;
        self.pandaActor.setHpr(self.pH,self.pP,self.pR) ;
        self.pandaActor.reparentTo(self.mybase)
        self.pandaActor.loop("walk")

        self.camholder.setPos(0, -17, 0)
        #self.camholder.setHpr(0, 20, 0)

        sky = loader.loadModel('smiley.egg')
        #sky.setTexture(skytex, 2)
        sky.setColor(0,1,0)
        sky.setTwoSided(True)
        sky.reparentTo(self.mybase)
        sky.setScale(30)

        self.flowgen = FlowGen()
        self.flowgen.flow_cam.reparentTo(self.camholder)
        setup_flow_shading_on_node(self.mybase)
 
    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        tt = globalClock.get_frame_time()
        angleDegrees = tt * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camholder.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camholder.setHpr(angleDegrees, 5*sin(tt), 0)
        return Task.cont

    def spinPandaTask(self, task):
        self.pH += u(-10,10) ;
        self.pP += u(-10,10) ;
        self.pR += u(-10,10) ;
        self.pandaActor.setHpr(self.pH,self.pP,self.pR) ;
        return Task.cont


 
app = MyApp()
#app.run()
#clock = ClockObject()
globalClock.setMode(ClockObject.M_non_real_time)
globalClock.set_dt(.1)
#taskMgr.setClock(clock)

app.flowgen.store_prev_data(app.mybase)

def generateSequence():
    for t in range(50000):
        taskMgr.step()

        app.flowgen.save_images()
    
        app.flowgen.store_prev_data(app.mybase)

generateSequence()
