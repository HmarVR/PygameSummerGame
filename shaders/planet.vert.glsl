#version 300 es
precision highp float;
precision highp int;

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec2 in_position;

out vec2 uv_0;


void main() {
    uv_0 = in_texcoord_0;
    gl_Position = vec4(in_position.xy, 0.9999, 1.0);
}
