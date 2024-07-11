#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;

uniform sampler2D T_ui;

#include "uniforms"

in vec2 uv_0;
out vec4 fragColor;

vec3 water() {
    float progress = time; //You can replace iTime with any variable that constantly increases
    float waveSize = 0.010; //How extreme the wavyness is
    float ripple = 25.0; //How "rippley" it is.
    float zoom = (waveSize*3.0) + 1.0; // Zoom correction

    vec3 waterColor = vec3(0.0, 0.07, 0.25);

    vec2 uv = uv_0;

    //We offset the y by the x + progress
    uv.y -= sin(((progress * 0.1) +uv.x) * ripple) * waveSize;

    //We do the reverse for x. I used cosine instead to make the uv.y and uv.x sync differently
    uv.x -= cos(((progress * 0.1) +uv.y) * ripple)*waveSize;
    //To avoid glitchy borders from offsetting the texture
    //We need to zoom in a bit and re-center the texture.
    uv.xy /= vec2(zoom, zoom);
    uv.xy += vec2((zoom-1.0)/2.0,(zoom-1.0)/2.0);
    
    //Grab the rgb from our uv coord
    vec3 tex1 = texture(T_ui, uv).rgb;

    return tex1 + waterColor * tex1;
}

void main() {	
    vec4 final;
    vec4 col = texture(T_ui, uv_0).rgba;

    if (col.g > 0.99) {
        final = vec4(water(), 1.0);
    } else {
        final = col;
    }

    fragColor = final + vec4(u_plsdriver, 0.0);
}
