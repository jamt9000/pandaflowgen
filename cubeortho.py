import sys
import time
from math import cos, pi, sin

import numpy as np
import panda3d.core
import skimage.io
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import *
from panda3d.physics import ActorNode, ForceNode, LinearVectorForce

import computecolor
import double_pendulum
from flowgen import *

# np.random.seed(123)

TRANSLATION = True
PERSPECTIVE = False

u = lambda a=0.0, b=1.0: (b - a) * np.random.rand() + a

loadPrcFileData("", "basic-shaders-only #f")
loadPrcFileData("", "hardware-animated-vertices #f")
loadPrcFileData("", "win-size 150 150")


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Disable the camera trackball controls.
        # self.disableMouse()

        self.mybase = NodePath("MyBase")
        self.mybase.reparentTo(render)

        self.camholder = NodePath("CamHolder")
        self.camholder.reparentTo(render)
        self.camera.reparentTo(self.camholder)

        self.render.setShaderAuto()

        # Load the environment model.
        # self.environ = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        # self.environ.reparentTo(self.mybase)
        # Apply scale and position transforms on the model.
        # self.environ.setScale(0.25, 0.25, 0.25)
        # self.environ.setPos(-8, 42, 0)

        # Add the spinCameraTask procedure to the task manager.
        # self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.spinPandaTask, "SpinPandaTask")

        # Load and transform the panda actor.
        self.pandaActor = loader.loadModel("cube.egg")
        spheretex = loader.loadTexture("cube_tex_map.png")
        self.pandaActor.setTexture(spheretex, 1)
        self.pandaActor.setScale(1, 1, 1)

        if TRANSLATION:
            self.pendulumState = np.radians(100 * np.random.randn(4))
            x, y, xx, yy, s = double_pendulum.simulate(self.pendulumState)
            self.pendulumState = s
            print(x, y, xx, yy)
            self.pX = xx / 2
            self.pY = 0.0
            self.pZ = yy + 1.5
        else:
            self.pX = 0.0
            self.pY = 0.0
            self.pZ = 0.0

        self.pandaActor.setPos(self.pX, self.pY, self.pZ)
        self.pH = 0.0
        self.pP = 0.0
        self.pR = 0.0
        self.pandaActor.setHpr(self.pH, self.pP, self.pR)
        self.pandaActor.reparentTo(self.mybase)

        self.camholder.setPos(0, -17, 0)
        # self.camholder.setHpr(0, 20, 0)

        sky = loader.loadModel("smiley.egg")
        # sky.setTexture(skytex, 2)
        sky.setColor(0, 1, 0)
        sky.setTwoSided(True)
        sky.reparentTo(self.mybase)
        sky.setScale(30)

        self.flowgen = FlowGen()
        self.flowgen.flow_cam.reparentTo(self.camholder)

        if not PERSPECTIVE:
            lens = OrthographicLens()
            lens.setFilmSize(10, 10)
            self.camNode.setLens(lens)
            self.flowgen.flow_cam.node().setLens(lens)
        setup_flow_shading_on_node(self.mybase)

    # Define a procedure to move the camera.
    def spinCameraTask(self, task):
        tt = globalClock.get_frame_time()
        angleDegrees = tt * 6.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camholder.setPos(20 * sin(angleRadians), -20.0 * cos(angleRadians), 3)
        self.camholder.setHpr(angleDegrees, 5 * sin(tt), 0)
        return Task.cont

    def spinPandaTask(self, task):
        tt = globalClock.get_frame_time()
        tt = tt * float(sys.argv[1])
        self.pH = sin(tt) * 90
        self.pP = sin(0.5 * tt * np.exp(1)) * 90
        self.pR = sin(tt * np.sqrt(2)) * 90

        if TRANSLATION:
            x, y, xx, yy, s = double_pendulum.simulate(self.pendulumState)
            self.pendulumState = s
            self.pX = xx / 2
            self.pZ = yy + 1.5
            self.pandaActor.setPos(self.pX, self.pY, self.pZ)

        self.pandaActor.setHpr(self.pH, self.pP, self.pR)
        return Task.cont


app = MyApp()
# app.run()
# clock = ClockObject()
globalClock.setMode(ClockObject.M_non_real_time)
globalClock.set_dt(0.1)
# taskMgr.setClock(clock)

app.flowgen.store_prev_data(app.mybase)


def generateSequence():
    for t in range(1000):
        taskMgr.step()

        app.flowgen.save_images()

        app.flowgen.store_prev_data(app.mybase)


generateSequence()
