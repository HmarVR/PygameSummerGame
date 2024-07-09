#version 300 es
precision highp float;
precision highp int;

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_position;
layout (location = 2) in vec4 position;

out vec2 uv_0;
out vec3 fragPos;
out vec4 instance_pos_data;

#include "uniforms"


void main() {
    uv_0 = in_texcoord_0;
    vec3 vert_position = in_position + vec3(position.xy*2.0, position.w);
    instance_pos_data = position;

    fragPos = vec3(m_model * vec4(vert_position, 1.0));
	vec4 place = m_view * vec4(vert_position, 1.0);
    gl_Position = vec4(place.xy/(place.w), place.z/1000.0, 1.0);
}