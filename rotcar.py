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
from flowgen import *

np.random.seed(123)

u = lambda a=0.0, b=1.0: (b - a) * np.random.rand() + a

CHAIRMODELS = "/home/jdt/Downloads/chairs/chairmodels/"
BACKGROUNDS = "/home/jdt/Downloads/chairs/city/"
CHARACTERS = "/home/jdt/Code/code3d/asset-pack/000-characters-med/Assets/models/"

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
        self.pandaActorModel = loader.loadModel(
            "/home/jdt/Code/code3d/asset-pack/000-vehicles-med/Assets/models/sedanj.egg"
        )
        self.pandaActor = render.attachNewNode("pandaActor")
        self.pandaActorModel.reparentTo(self.pandaActor)
        self.pandaActorModel.setPos(0, 0, -2)

        self.pandaActor.setScale(0.6, 0.4, 0.7)
        self.pH = 0.0
        self.pP = 0.0
        self.pR = 0.0

        self.pX = 0.0
        self.pY = 0.0
        self.pZ = 0.0

        self.rphase = 0

        self.xphase = 0
        self.yphase = 0
        self.zphase = 0

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
        mode = "randHeadingVaryPitchRoll"
        if mode == "rot360":
            self.pH += 0.5  # u(-10,10) ;
            if self.pH > 360:
                exit()
        elif mode == "randHeading":
            self.pH += u(-10, 10)
        elif mode == "randHeadingVaryPitch":
            self.pH += u(-10, 10)
            tt = globalClock.get_frame_time()
            forwardness = np.cos(self.pH * np.pi / 180.0)
            self.pP = sin(tt) * 15 + 15 * forwardness
        elif mode == "randHeadingVaryPitchRoll":
            self.pH += u(-10, 10)
            tt = globalClock.get_frame_time()
            forwardness = np.cos(self.pH * np.pi / 180.0)
            self.pP = sin(tt) * 15 + 15 * forwardness
            self.rphase += np.maximum(0, u(-5, 0.5))
            rphase = self.rphase
            print(rphase)
            self.pR = sin(rphase + tt) * 15 - sin(rphase + tt) * 15 * (
                1 - np.abs(forwardness)
            )

            self.pX = sin(0.1 * tt + self.xphase) * 1.5
            self.pY = sin(0.1 * tt + self.yphase) * 1
            self.pZ = sin(0.1 * tt + self.zphase) * 2 - 2

            self.xphase += np.maximum(0, u(-5, 0.2))
            self.yphase += np.maximum(0, u(-5, 0.2))
            self.zphase += np.maximum(0, u(-5, 0.2))

        self.pandaActor.setHpr(self.pH, self.pP, self.pR)
        self.pandaActorModel.setPos(self.pX, self.pY, self.pZ)
        return Task.cont


app = MyApp()
# app.run()
# clock = ClockObject()
globalClock.setMode(ClockObject.M_non_real_time)
globalClock.set_dt(0.1)
# taskMgr.setClock(clock)

app.flowgen.store_prev_data(app.mybase)


def generateSequence():
    for t in range(30000):
        for s in range(5):
            taskMgr.step()

        app.flowgen.save_images()

        app.flowgen.store_prev_data(app.mybase)


generateSequence()
