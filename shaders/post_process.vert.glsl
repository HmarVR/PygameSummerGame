#version 300 es
precision highp float;
precision highp int;

layout (location = 0) in vec2 in_texcoord_0;
layout (location = 1) in vec3 in_position;

out vec2 uv_0;
out vec2 fragCoord;

#include "uniforms"

void main() {
    // basically, pygame uses topleft as origin but opengl uses bottom left, this reverses that
    // we need this bcuz we calculate the planet pos in python, according to topleft.
    uv_0 = in_texcoord_0;
    fragCoord = uv_0 * screenResolution;
    // * vec2(1.0, -1.0) + vec2(0.0, 1.0)  // ==> converts to pygame topleft
    gl_Position = vec4(in_position.xy, 0.0001, 1.0);
}
