#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;
precision highp sampler2DArray;

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 fragPos;

uniform sampler2D U_image;

#include "uniforms"



vec2 pixellize(vec2 uv, float pixelSize) {
    // if you dont multiply by screenRes it wont work
    return floor(uv * screenResolution / pixelSize) / screenResolution * pixelSize;
}


void main() {
    vec2 scaledUV = uv_0 * scaling_vector;
    vec2 offset = (scaling_vector - 1.0) / 2.0;
    vec3 color = texture(U_image, scaledUV - offset).rgb;
    fragColor = vec4(color, 1.0);
}