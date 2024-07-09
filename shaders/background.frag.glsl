#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;
precision highp sampler2DArray;

uniform sampler2D U_bg_image;

#include "uniforms"

in vec2 uv_0;
out vec4 fragColor;

vec2 pixellize(vec2 uv, float pixelSize) {
    // if you dont multiply by screenRes it wont work
    return floor(uv * screenResolution / pixelSize) / screenResolution * pixelSize;
}

void main() {	
    vec4 color = texture(U_bg_image, mos/1000.0).rgba * vec4(0.32, 0.45, 0.7, 1.0);
    fragColor = color + vec4(u_color_offset.rgb + uv_0.x*0.001, 1.0);
}
