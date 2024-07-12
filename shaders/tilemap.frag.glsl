#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;
precision highp sampler2DArray;

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 fragPos;
in vec4 instance_pos_data;

uniform sampler2DArray Tiler;

#include "uniforms"

void main() {
	vec3 color = texture(Tiler, vec3(uv_0, int(instance_pos_data.z))).rgb;

	if (color==vec3(0)) {
		discard;
	}
	fragColor = vec4(color, 1);
}