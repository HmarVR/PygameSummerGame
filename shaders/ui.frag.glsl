#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;

uniform sampler2D T_ui;

uniform sampler2DArray T_stars;

#include "uniforms"

in vec2 uv_0;
out vec4 fragColor;

vec4 stars() {
    vec2 starPositions[10];
    starPositions[0] = vec2(0.17, 0.5);
    starPositions[1] = vec2(0.45, 0.7 );
    starPositions[2] = vec2(0.1, 0.83 );
    starPositions[3] = vec2(0.58, 0.3 );
    starPositions[4] = vec2(0.59, 0.32);
    starPositions[5] = vec2(0.86, 0.9 );
    starPositions[6] = vec2(0.38, 0.66);
    starPositions[7] = vec2(0.19, 0.48);
    starPositions[8] = vec2(0.79, 0.76);
    starPositions[9] = vec2(0.42, 0.27);

    for (int i = 0; i < 10; i++) {
        starPositions[i] = starPositions[i] * screenResolution;
    }

    float threshold = 9.0;

    vec2 fragCoord = uv_0 * screenResolution;

    for (int i = 0; i < 10; i++) {
        vec2 pos = starPositions[i];
        float difx = fragCoord.x - pos.x;
        if (0.0 <= difx && difx <= threshold) {
            float dify = fragCoord.y - pos.y;
            if (0.0 <= dify && dify <= threshold) {
                vec2 relativeCoord = vec2(0.0,0.0);// fragCoord / screenResolution;// (fragCoord - pos) / screenResolution;
                int star_id = i%4;

                return texture(T_stars, vec3(relativeCoord, 0));
                // return texture(T_stars, vec3(relativeCoord, star_id));
            }
        }
    }

    return texture(T_ui, uv_0);
}

void main() {	
    fragColor = texture(T_stars, vec3(0.0,0.0,0)) + stars() + vec4(u_plsdriver, 0.0);
}
