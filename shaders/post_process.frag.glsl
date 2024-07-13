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


float size = 25.0;  // controls fbm size + rand function // 40 - 200
float seed = 3.4;
int OCTAVES = 2;  // between 2 - 20

float rand(vec2 coord) {
	coord = mod(coord, vec2(1.0, 1.0)*round(size));
	return fract(sin(dot(coord.xy ,vec2(12.9898,78.233))) * 15.5453 * seed);
}

float noise(vec2 coord){
	vec2 i = floor(coord);
	vec2 f = fract(coord);
	
	float a = rand(i);
	float b = rand(i + vec2(1.0, 0.0));
	float c = rand(i + vec2(0.0, 1.0));
	float d = rand(i + vec2(1.0, 1.0));

	vec2 cubic = f * f * (3.0 - 2.0 * f);

	return mix(a, b, cubic.x) + (c - a) * cubic.y * (1.0 - cubic.x) + (d - b) * cubic.x * cubic.y;
}

float fbm(vec2 coord){
	float value = 0.0;
	float scale = 0.5;

	for (int i = 0; i < OCTAVES ; i++){
		value += noise(coord) * scale;
		coord *= 2.0;
		scale *= 0.5;
	}
	return value;
}

float cloud(vec2 texture_uv) {
    float fbm1 = fbm(texture_uv * vec2(500.0));
    float fbm_val = fbm(texture_uv * size + fbm1 + vec2(time*1.0, 0.0));
    return mod(fbm_val, 1.0);
}

vec3 dust(vec3 col) {
    vec3 dustColor = vec3(0.6, 0.76, 0.8);
    // I cant get the screen coordinate of a tile correctly
    float rad = 20.0;

    float mul = dust_mul;

    vec2 curPixel = fragCoord + vec2(
        sin((time + 2.521) * 0.5) * 5.0 + 
        cos((time + 3.72) * 0.5) * 5.0
    );

    vec2 d0 = dustClouds[0].xy;
    vec2 d1 = dustClouds[1].xy;
    vec2 d2 = dustClouds[2].xy;
    vec2 d3 = dustClouds[3].xy;

    // check for dist for all 4 dust points.
    float l0 = distance(d0, curPixel);
    float l1 = distance(d1, curPixel);
    float l2 = distance(d2, curPixel);
    float l3 = distance(d3, curPixel);

    l0 = step(l0, rad * mul);
    l1 = step(l1, rad * mul);
    l2 = step(l2, rad * mul);
    l3 = step(l3, rad * mul);

    float combined = l0 + l1 + l2 + l3;
    float iscloud = clamp(combined, 0.0, 1.0);
    
    vec3 final = col * (1.0 - iscloud) + dustColor * iscloud;
    return final;
}

vec2 pixellize(vec2 uv, float pixelSize) {
    // if you dont multiply by screenRes it wont work
    return floor(uv * screenResolution / pixelSize) / screenResolution * pixelSize;
}


void main() {
    vec2 scaledUV = uv_0 * scaling_vector;
    
    vec2 offset = (scaling_vector - 1.0) / 2.0;
    
    vec3 color = texture(U_image, scaledUV - offset).rgb;

    color = dust(color); 

    fragColor = vec4(color, 1.0);
}