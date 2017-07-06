#version 120
 
// Uniform inputs
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat4 mvp_prev;
uniform mat4 mv_prev;
uniform mat4 p_prev;
 
// Vertex inputs
attribute vec4 p3d_Vertex;
attribute vec2 p3d_MultiTexCoord0;

attribute vec4 vertprev;
 
// Output to fragment shader
varying vec2 texcoord;

varying vec4 position_next;
varying vec4 position_prev;
varying vec4 vertpos;
 
void main() {
  position_next = p3d_ModelViewMatrix * p3d_Vertex;
  vertpos = p3d_Vertex;

  position_prev = mv_prev * vertprev;
  //position_prev = position_next;

  gl_Position = mvp_prev * vertprev;

  //gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;
}
