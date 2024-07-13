#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;

uniform sampler2D T_ui;

#include "uniforms"

in vec2 uv_0;
out vec4 fragColor;



// taken from: https://www.shadertoy.com/view/XtlSD7
vec2 CRTCurveUV(vec2 uv)
{
    uv = uv * 2.0 - 1.0;
    // Increase the offset factors to make the curvature more pronounced
    vec2 offset = abs(uv.yx) / vec2(3.0, 2.5); // Adjust these values for stronger curvature
    uv = uv + uv * offset * offset;
    uv = uv * 0.5 + 0.5;
    return uv;
}

void DrawVignette( inout vec3 color, vec2 uv )
{    
    float vignette = uv.x * uv.y * ( 1.0 - uv.x ) * ( 1.0 - uv.y );
    vignette = clamp( pow( 24.0 * vignette, 0.3 ), 0.0, 1.0 );
    color *= vignette;
}

void DrawScanline(inout vec3 color, vec2 uv)
{
    // 900 --> scanline size(also affects speed)
    // you should change the 0.008 for speed 
    float scanline = clamp(0.90 + 0.10 * cos(3.14 * (uv.y + 0.008 * time) * 1000.0 * 1.0), 0.0, 1.0);
    // Adjusted the grille frequency similarly and increased the amplitude
    float grille = 0.80 + 0.20 * clamp(1.5 * cos(3.14 * uv.x * 320.0 * 1.0), 0.0, 1.0);    
    color *= scanline * grille * 1.2;
}



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
    vec2 uv = uv_0;
    float crt_scale = 1.1;
    vec2 crtUV = CRTCurveUV( uv * crt_scale - vec2((crt_scale - 1.0) / 2.0) );
    
    // replace with normal uv if you dont want the uv to be curved
    vec4 col = texture(T_ui, crtUV).rgba;

    if (col.g > 0.99 && col.r < 0.5) {
        final = vec4(water(), 1.0);
    } else {
        final = col;
    }

    vec2 fragCoord = uv_0 * screenResolution;

    // crt stuff
    float resMultX  = floor( screenResolution.x / 640.0 );
    float resMultY  = floor( screenResolution.y / 480.0 );
    float resRcp	= 1.0 / max( min( resMultX, resMultY ), 1.0 );
    
    float screenWidth	= floor( screenResolution.x * resRcp );
    float screenHeight	= floor( screenResolution.y * resRcp );
    float pixelX 		= floor( fragCoord.x * resRcp );
    float pixelY 		= floor( fragCoord.y * resRcp );


    // CRT effects (curvature, vignette, scanlines and CRT grille)
    if ( crtUV.x < 0.0 || crtUV.x > 1.0 || crtUV.y < 0.0 || crtUV.y > 1.0 )
    {
        final.rgb = vec3( 0.0, 0.0, 0.0 );
    }
    DrawVignette(final.rgb, crtUV );
    DrawScanline(final.rgb, uv );

    fragColor = final + vec4(u_plsdriver, 0.0);
}
