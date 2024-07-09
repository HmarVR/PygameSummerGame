#version 300 es
precision highp float;
precision highp int;

#include "uniforms"

in vec2 uv_0;
out vec4 fragColor;

void main() {	
    fragColor = vec4(uv_0.x, uv_0.y, 0.0 + 0.001 * u_plsdriver.x, 0.0);  // or just discard;
}
