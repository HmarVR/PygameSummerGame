#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;
precision highp sampler2DArray;

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_position;

out vec2 uv_0;
out vec3 fragPos;

#include "uniforms"



void main() {
    uv_0 = in_texcoord_0;
    fragPos = vec3(m_model * vec4(in_position, 1.0));
	vec4 place = m_view * vec4(in_position, 1.0);
    gl_Position = vec4(place.xy/(place.w), place.z/1000.0, 1.0);
}