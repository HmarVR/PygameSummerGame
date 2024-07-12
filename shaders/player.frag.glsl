#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;
precision highp sampler2DArray;

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 fragPos;

uniform sampler2DArray u_texture_0;

#include "uniforms"


void main() {
    vec3 color = texture(u_texture_0, vec3(flip ? (uv_0.xy * vec2(-1, 1)) : (uv_0.xy), frame)).rgb;

    if (color == vec3(0, 0, 0)) {
        discard;
    }

    fragColor = vec4(color, 1);
}
