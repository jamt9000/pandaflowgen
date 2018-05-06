
#from pandac.PandaModules import loadPrcFileData
#loadPrcFileData('', 'load-display tinydisplay')

import sys

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState

from panda3d.core import AmbientLight
from panda3d.core import DirectionalLight
from panda3d.core import Vec3
from panda3d.core import Vec4
from panda3d.core import Point3
from panda3d.core import TransformState
from panda3d.core import BitMask32
from panda3d.core import *

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletSoftBodyNode
from panda3d.bullet import BulletSoftBodyConfig
from panda3d.bullet import BulletConeTwistConstraint

import numpy as np
from flowgen import *

loadPrcFileData("", "basic-shaders-only #f")
loadPrcFileData("", "hardware-animated-vertices #f")
loadPrcFileData("", "win-size 150 150")

class Game(ShowBase):

  def __init__(self):
    ShowBase.__init__(self)
    base = self
    base.setBackgroundColor(0.1, 0.1, 0.8, 1)
    #base.setFrameRateMeter(True)

    self.mybase = NodePath("MyBase")
    self.mybase.reparentTo(render)

    self.camholder = NodePath("CamHolder")
    self.camholder.reparentTo(render)
    self.camera.reparentTo(self.camholder)

    self.camholder.setPos(0, 0, 90)
    self.camholder.lookAt(0, 0, 0)
    self.camholder.setH(np.random.randint(0,360))

    # Light
    alight = AmbientLight('ambientLight')
    alight.setColor(Vec4(0.6, 0.6, 0.6, 1))
    alightNP = render.attachNewNode(alight)

    dlight = DirectionalLight('directionalLight')
    #dlight.setDirection(Vec3(5, 0, -2))
    dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
    dlightNP = render.attachNewNode(dlight)
    dlightNP.lookAt(np.random.randint(-15,15), np.random.randint(-15,15), -2)

    render.clearLight()
    render.setLight(alightNP)
    render.setLight(dlightNP)

    # Input
    self.accept('escape', self.doExit)
    self.accept('r', self.doReset)
    self.accept('f1', self.toggleWireframe)
    self.accept('f2', self.toggleTexture)
    self.accept('d', self.toggleDebug)
    self.accept('f5', self.doScreenshot)

    # Task
    taskMgr.add(self.update, 'updateWorld')

    # Physics
    self.setup()

    sky = loader.loadModel('smiley.egg')
    sky.setColor(0,1,0)
    sky.setTwoSided(True)
    sky.reparentTo(self.mybase)
    sky.setScale(100)

    m = Material()
    m.clearDiffuse()
    sky.setMaterial(m)

    self.flowgen = FlowGen()
    self.flowgen.flow_cam.reparentTo(self.camholder)
    setup_flow_shading_on_node(self.mybase)

  # _____HANDLER_____

  def doExit(self):
    self.cleanup()
    sys.exit(1)

  def doReset(self):
    self.cleanup()
    self.setup()

  def toggleWireframe(self):
    base.toggleWireframe()

  def toggleTexture(self):
    base.toggleTexture()

  def toggleDebug(self):
    if self.debugNP.isHidden():
      self.debugNP.show()
    else:
      self.debugNP.hide()

  def doScreenshot(self):
    base.screenshot('Bullet')

  # ____TASK___
  tt = 0

  def update(self, task):
    dt = globalClock.getDt()
    #dt *= 0.01

    self.world.doPhysics(dt, 10, 0.008)

    self.tt += 1
    print self.tt

    if int(self.tt) % 200 == 0:
        gv = Vec3(np.random.randn()*3, np.random.randn()*3, 0)
        print gv
        print base.cam.getPos()
        print base.cam.getHpr()
        self.world.setGravity(gv)

    return task.cont

  def cleanup(self):
    self.world = None
    self.worldNP.removeNode()

  def setup(self):
    self.worldNP = render.attachNewNode('World')

    # World
    self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
    #self.debugNP.show()

    self.world = BulletWorld()
    self.world.setGravity(Vec3(np.random.randn()*3, np.random.randn()*3, 0))
    self.world.setDebugNode(self.debugNP.node())

    # Ground
    p0 = Point3(-20, -20, 0)
    p1 = Point3(-20, 20, 0)
    p2 = Point3(20, -20, 0)
    p3 = Point3(20, 20, 0)
    mesh = BulletTriangleMesh()
    mesh.addTriangle(p0, p1, p2)
    mesh.addTriangle(p1, p2, p3)
    shape = BulletTriangleMeshShape(mesh, dynamic=False)

    npp = self.worldNP.attachNewNode(BulletRigidBodyNode('Mesh'))
    npp.node().addShape(shape)
    npp.setPos(0, 0, -2)
    npp.setCollideMask(BitMask32.allOn())

    self.ground = npp

    self.world.attachRigidBody(npp.node())

    # Soft body world information
    info = self.world.getWorldInfo()
    info.setAirDensity(1.2)
    info.setWaterDensity(0)
    info.setWaterOffset(0)
    info.setWaterNormal(Vec3(0, 0, 0))

    # Softbody
    def makeSB(pos, hpr):
      model = loader.loadModel('moleculemesh/smoothed/clathrinfixsmth%02d.obj' % np.random.randint(1,21))
      geom = model.findAllMatches('**/+GeomNode').getPath(0).node().modifyGeom(0)

      geomNode = GeomNode('')
      geomNode.addGeom(geom)

      node = BulletSoftBodyNode.makeTriMesh(info, geom) 
      node.linkGeom(geomNode.modifyGeom(0))

      node.generateBendingConstraints(2)
      node.getCfg().setPositionsSolverIterations(6)
      node.getCfg().setCollisionFlag(BulletSoftBodyConfig.CFVertexFaceSoftSoft, True)
      node.randomizeConstraints()
      node.setTotalMass(50, True)
      node.getMaterial(0).setLinearStiffness(0.2)
      #node.getCfg().setDynamicFrictionCoefficient(1)
      #node.getCfg().setDampingCoefficient(0.001)
      node.getCfg().setPressureCoefficient(1500)


      softNP = self.worldNP.attachNewNode(node)
      softNP.setPos(pos)
      softNP.setHpr(hpr)
      self.world.attachSoftBody(node)

      geomNP = softNP.attachNewNode(geomNode)

      #softNP.node().appendAnchor(1, self.ground.node())
      softNP.node().appendAnchor(1217, self.ground.node())
      softNP.node().appendAnchor(1157, self.ground.node())
      softNP.node().appendAnchor(2052, self.ground.node())
      #softNP.node().appendAnchor(1800, self.ground.node())
      softNP.reparentTo(self.mybase)

    #makeSB(Point3(-3, 0, 4), (0, 0, 0))
    #makeSB(Point3(0, 0, 4), (0, 90, 90))
    makeSB(Point3(4+np.random.randn(), 2+np.random.randn(), 4), (0, 0, 0))


app = Game()
globalClock.setMode(ClockObject.M_non_real_time)
globalClock.set_dt(.5)
#app.run()
app.flowgen.store_prev_data(app.mybase)

def generateSequence():
    for t in range(10000):
        taskMgr.step()

        app.flowgen.save_images()
    
        app.flowgen.store_prev_data(app.mybase)

generateSequence()
