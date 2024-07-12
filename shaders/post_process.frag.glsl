#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;
precision highp sampler2DArray;

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec2 fragCoord;

uniform sampler2D U_image;

#include "uniforms"

vec3 dust(vec2 offset) {
    // I cant get the screen coordinate of a tile correctly
    float rad = 300.0;

    vec2 curPixel = uv_0 * screenResolution;
    curPixel += camPos.xy;

    // check for dist for all 4 dust points.
    float l0 = distance(dustClouds[0].xy, curPixel);
    float l1 = distance(dustClouds[1].xy, curPixel);
    float l2 = distance(dustClouds[2].xy, curPixel);
    float l3 = distance(dustClouds[3].xy, curPixel);

    l0 = step(l0, rad);
    l1 = step(l1, rad);
    l2 = step(l2, rad);
    l3 = step(l3, rad);

    float combined = clamp(l0 + l1 + l2 + l3, 0.0, 1.0);

    vec3 col = vec3(combined);
    return col;
}

vec2 pixellize(vec2 uv, float pixelSize) {
    // if you dont multiply by screenRes it wont work
    return floor(uv * screenResolution / pixelSize) / screenResolution * pixelSize;
}


void main() {
    vec2 scaledUV = uv_0 * scaling_vector;
    
    vec2 offset = (scaling_vector - 1.0) / 2.0;
    
    vec3 color = texture(U_image, scaledUV - offset).rgb;

    color += dust(offset);

    fragColor = vec4(color, 1.0);
}