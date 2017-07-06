#version 120

#define round(x) floor((x)+0.5)

uniform sampler2D p3d_Texture0;

// Input from vertex shader
varying vec2 texcoord;

varying vec4 position_next;
varying vec4 position_prev;
varying vec4 vertpos;

// Uniform inputs
uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p_prev;

uniform int pixel_height;
uniform int pixel_width;

float colorToFloat(vec3 color) {
    float f = dot( color.xyz, vec3( 255.0/256, 255.0/(256*256), 255.0/(256*256*256) ) );
    f = (f * 1000)-500;
    return f;
}

vec3 floatToColor(float f) {
   // Map -500:500 to 0:1
   f = (f + 500.)/1000.;
   float max24int = 256*256*256-1;
   vec3 decomp = floor( f * vec3( max24int/(256*256), max24int/256, max24int ) ) / 255.0;
   decomp.z -= decomp.y * 256.0;
   decomp.y -= decomp.x * 256.0;
   return decomp;
}



void main() {
  vec4 color = texture2D(p3d_Texture0, texcoord);

  // Screen position
  // Note gl_FragCoord is ALREADY offset by 0.5 to get pixel center!
  float posx = gl_FragCoord.x;
  float posy = gl_FragCoord.y;

  vec4 position_next_p = p3d_ProjectionMatrix * position_next;
  vec4 position_prev_p = p_prev * position_prev;

  float next_ndc_x = position_next_p.x/position_next_p.w;
  float next_ndc_y = position_next_p.y/position_next_p.w;
  float prev_ndc_x = position_prev_p.x/position_prev_p.w;
  float prev_ndc_y = position_prev_p.y/position_prev_p.w;

  //float next_ndc_x = position_next.x;
  //float next_ndc_y = position_next.y;
  //float prev_ndc_x = position_prev.x;
  //float prev_ndc_y = position_prev.y;



  float next_pix_x = (next_ndc_x * 0.5 + 0.5) * pixel_width - 0.5;
  float next_pix_y = (next_ndc_y * 0.5 + 0.5) * pixel_height - 0.5;
  float prev_pix_x = (prev_ndc_x * 0.5 + 0.5) * pixel_width - 0.5;
  float prev_pix_y = (prev_ndc_y * 0.5 + 0.5) * pixel_height - 0.5;

  //float next_pix_x = clamp( ((next_ndc_x * 0.5 + 0.5) * pixel_width - 0.5), 0, pixel_width-1 );
  //float next_pix_y = clamp( ((next_ndc_y * 0.5 + 0.5) * pixel_height - 0.5), 0, pixel_height-1 );
  //float prev_pix_x = clamp( ((prev_ndc_x * 0.5 + 0.5) * pixel_width - 0.5), 0, pixel_width-1 );
  //float prev_pix_y = clamp( ((prev_ndc_y * 0.5 + 0.5) * pixel_height - 0.5), 0, pixel_height-1 );

  float dx = next_pix_x - prev_pix_x;
  float dy = next_pix_y - prev_pix_y;



  gl_FragData[0] = (vec4(normalize(vertpos.xyz),1) + 1)/2; //color.rgba;
  gl_FragData[1] = vec4(floatToColor(dx),1);
  gl_FragData[2] = vec4(floatToColor(dy),1);
}
