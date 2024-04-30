import os
import time

import numpy as np
import panda3d.core
from numpy import cos, pi, sin
from numpy.random import rand, randn
from panda3d.core import *

FILEDIR = os.path.dirname(__file__)
import sys

sys.path.insert(0, FILEDIR + '/..')
import skimage.io

import computecolor


def unif(a,b):
    return (b-a) * np.random.rand() + a

def vertex_add_column(vdata):
    fmt = vdata.get_format()
    newfmt = GeomVertexFormat()

    formatArray=GeomVertexArrayFormat() 
    # At first I used Geom.Cpoint, but this gets altered by animation!!
    formatArray.addColumn(InternalName.make("vertprev"), 4, Geom.NTFloat32, Geom.COther)
    newfmt.addArray(formatArray)

    newfmt=GeomVertexFormat.registerFormat(newfmt)
    vdata.set_format(fmt.get_union_format(newfmt))

def color_to_float(c):
    out = (c[:,:,0] * 255.0/256) + (c[:,:,1] * 255.0/(256*256)) + (c[:,:,2] * 255.0/(256*256*256))
    out = (out*1000)-500;
    return out

def create_buffer(sort, xsize, ysize, auxrgba=0, auxfloat = 0, engine=None):
    winprops = WindowProperties.size(xsize,ysize)
    props = FrameBufferProperties()
    props.setRgbColor(1)
    props.setAlphaBits(1)
    props.setDepthBits(1)
    if auxrgba:
       props.setAuxRgba(auxrgba)
    if auxfloat:
        props.setAuxRgba(0)
        props.setAuxFloat(auxfloat)
    if engine:
       return engine.makeBuffer(base.win.getGsg(), "offscreen buff", sort, xsize, ysize)
    return base.graphicsEngine.makeOutput(
       base.pipe, "offscreenBuffer",
       sort, props, winprops,
       GraphicsPipe.BFSizeTrackHost | GraphicsPipe.BFCanBindEvery | 
         GraphicsPipe.BFRttCumulative | GraphicsPipe.BFRefuseWindow,
       base.win.getGsg(), base.win)

class FlowGen(object):
    def __init__(self):
        self.colour_tex = Texture()
        self.flow_tex_x = Texture()
        self.flow_tex_y = Texture()
        bwidth, bheight = base.getSize()
        self.buffer = create_buffer(-100, bwidth, bheight, 2)
        self.buffer.addRenderTexture(self.colour_tex, GraphicsOutput.RTMCopyRam, GraphicsOutput.RTPColor)
        self.buffer.addRenderTexture(self.flow_tex_x, GraphicsOutput.RTMCopyRam, GraphicsOutput.RTPAuxRgba0)
        self.buffer.addRenderTexture(self.flow_tex_y, GraphicsOutput.RTMCopyRam, GraphicsOutput.RTPAuxRgba1)
        self.flow_cam = base.makeCamera(self.buffer, clearColor=Vec4(1.0,1.0,1.0,1.0),
                                        lens=base.camLens, camName="flowcam")

        flow_shader = Shader.load(Shader.SL_GLSL, vertex=os.path.join(FILEDIR, "flow_vertex_shader.vert"),
                                  fragment=os.path.join(FILEDIR, "flow_fragment_shader.frag"))
        flowshadenode = NodePath("fsn")
        flowshadenode.setShader(flow_shader)
        self.flow_cam.node().setTagStateKey("Flow Shading")
        self.flow_cam.node().setTagState("True", flowshadenode.getState())

        self.framei = 0

    def save_images(self, path='out'):
        os.makedirs(path, exist_ok=True)
        colarr = np.array(self.colour_tex.get_ram_image_as('RGB'))
        colarr = colarr.reshape(self.colour_tex.getYSize(),self.colour_tex.getXSize(),3)[::-1]

        if self.framei > 1:
            flowarr_x = np.array(self.flow_tex_x.get_ram_image_as('RGB')).astype(np.float32)/255
            flowarr_x = flowarr_x.reshape(self.flow_tex_x.getYSize(), self.flow_tex_x.getXSize(),3)[::-1]
            flowarr_x_c = color_to_float(flowarr_x)
        
            flowarr_y = np.array(self.flow_tex_y.get_ram_image_as('RGB')).astype(np.float32)/255
            flowarr_y = flowarr_y.reshape(self.flow_tex_y.getYSize(), self.flow_tex_y.getXSize(),3)[::-1]
            flowarr_y_c = color_to_float(flowarr_y)
        
            flow = computecolor.computeColor(flowarr_x_c, -flowarr_y_c)
        
            skimage.io.imsave(os.path.join(path,'%05d_flow_vis.png' % (self.framei-1)), flow)
            np.save(os.path.join(path, '%05d_flow.npy' % (self.framei-1)), np.float32(np.dstack([flowarr_x_c, -flowarr_y_c])))
    
    
        if self.framei > 0:
            skimage.io.imsave(os.path.join(path, '%05d_imm.png' % (self.framei-1)), np.uint8(colarr))
            base.win.saveScreenshot(panda3d.core.Filename(os.path.join(path, '%05d_im.png' % self.framei)))
        self.framei += 1

    def store_prev_data(self, n):
        for child in n.findAllMatches('**'):
            for node in child.get_nodes():
    
                mv = child.getMat(self.flow_cam)
        
                pr = self.flow_cam.node().getLens().getProjectionMat()
        
                mvp = mv * pr
        
                child.set_shader_input('mvp_prev', mvp)
                child.set_shader_input('mv_prev', mv)
                child.set_shader_input('p_prev', pr)
        
                if type(node) is GeomNode:
                    for geom in node.modify_geoms():
                        vdata = geom.modify_vertex_data()
                        if vdata.get_format().has_column('vertprev'):
                            vread = GeomVertexReader(vdata.animate_vertices(True, Thread.get_current_thread()), 'vertex')
                            vprevwrite = GeomVertexWriter(vdata, 'vertprev')
            
                            while not vread.isAtEnd():
                                v = vread.getData4f()
                                vprevwrite.setData4f(v[0], v[1], v[2], v[3])

def setup_flow_shading_on_node(n):
    n.setTag("Flow Shading", "True")
    pixel_width, pixel_height = base.getSize()
    n.set_shader_input('pixel_height', pixel_height)
    n.set_shader_input('pixel_width', pixel_width)

    for child in n.findAllMatches('**'):
        for node in child.get_nodes():
            if type(node) is GeomNode:
                for geom in node.modify_geoms():
                    vdata = geom.modify_vertex_data()
                    vertex_add_column(vdata)


