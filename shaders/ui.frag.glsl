#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;

uniform sampler2D T_ui;

#include "uniforms"

in vec2 uv_0;
out vec4 fragColor;

void main() {	
    fragColor = texture(T_ui, uv_0) + vec4(u_plsdriver, 0.0);
}
