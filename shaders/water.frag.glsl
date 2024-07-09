#version 300 es
precision highp float;
precision highp sampler2D;

uniform sampler2D Texture;
uniform sampler2D planetTexture;
uniform sampler2D planetNormalTexture;
uniform sampler2D planetUVTexture;

#include "uniforms"

in vec2 fragCoord;
out vec4 fragColor;


// https://www.shadertoy.com/view/XtjcRd
vec3 water() {
    float progress = time; //You can replace iTime with any variable that constantly increases
    float waveSize = 0.015; //How extreme the wavyness is
    float ripple = 30.0; //How "rippley" it is.
    float zoom = (waveSize*3.0) + 1.0; // Zoom correction

    vec3 waterColor = vec3(0.0, 0.07, 0.25);

    vec2 uv = fragCoord;

    //We offset the y by the x + progress
    uv.y -= sin(((progress * 0.1) +uv.x) * ripple) * waveSize;

    //We do the reverse for x. I used cosine instead to make the uv.y and uv.x sync differently
    uv.x -= cos(((progress * 0.1) +uv.y) * ripple)*waveSize;
    //To avoid glitchy borders from offsetting the texture
    //We need to zoom in a bit and re-center the texture.
    uv.xy /= vec2(zoom, zoom);
    uv.xy += vec2((zoom-1.0)/2.0,(zoom-1.0)/2.0);
    
    //Grab the rgb from our uv coord
    vec3 tex1 = texture(Texture, uv).bgr;

    return tex1 + waterColor * tex1 + vec3(0.001) * (
        texture(planetTexture, vec2(0.0,0.0)).bgr + 
        texture(planetUVTexture, vec2(0.0,0.0)).bgr +
        texture(planetNormalTexture, vec2(0.0,0.0)).bgr
    );
}

void main() {

    vec3 final;
    if (fragCoord.y > 0.6) {
        final = water();
    } else {
        final = texture(Texture, fragCoord).bgr;
    }
    

    fragColor = vec4(final, 1.0);
}
