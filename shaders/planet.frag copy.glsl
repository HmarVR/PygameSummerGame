#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;

uniform sampler2D T_planet;
uniform sampler2D T_planetNormal;
uniform sampler2D T_planetUV;

#include "uniforms"

in vec2 uv_0;
out vec4 fragColor;

bool shouldPixellize = false;
bool shouldDither = true;

vec3 cloudColor = vec3(1.0);
vec3 lightColor = vec3(1.0);

float PI = 3.1415926535897932384626433832795;
vec2 light_origin = vec2(0.7, 0.5);
float pixelSize = 8.0;

// Planet Gen Godot Parameters //
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
/*
float getZSphere(float rad, float x, float y) { // WHY ARE THESE ***STILL*** HERE
    return sqrt(pow(rad, 2.0) - pow(x, 2.0) - pow(y, 2.0));
}

float getZSphere2(vec2 uv, float dis) {
    vec3 result = vec3(uv.xy, sqrt(bodyRadius*bodyRadius - dis*dis))/bodyRadius;
    return result.z;
}
*/
vec2 pixellize(vec2 uv) {
    // if you dont multiply by screenRes it wont work
    return floor(uv * screenResolution / pixelSize) / screenResolution * pixelSize;
}
/*
vec2 rotate_uv(vec2 uv, float rotation) // I CAN GENERATE A ROTATED UV MAP BTW
{
    float cosAngle = cos(rotation);
    float sinAngle = sin(rotation);
    vec2 p = uv - vec2(0.5);
    return vec2(
        cosAngle * p.x + sinAngle * p.y + 0.5,
        cosAngle * p.y - sinAngle * p.x + 0.5
    );
}

vec2 texture_uv_sphere(vec3 normal) {  // NOW ABSOLUTLY USELESS, KKEP FOR TEXTURE GEN
    float theta = acos(-normal.y);  // - to flip img vertically
    float phi = atan(normal.z, -normal.x);

    // Convert spherical coordinates to texture coordinates
    float u = (phi + PI) / (2.0 * 3.141592653589793);
    float v = theta / 3.141592653589793;

    // Now u and v are the 2D UV coordinates for the planet texture
    return vec2(u, v);
}
*/

float cloud(vec2 texture_uv) {
    float fbm1 = fbm(texture_uv * vec2(500.0));
    float fbm_val = fbm(texture_uv * size+fbm1+vec2(time*time_speed, 0.0));
    return mod(fbm_val, 1.0);
}
/*
vec3 normal_sphere(vec2 uv_remap, float dis) {  // NOW ABSOLUTLY USELESS, KKEP FOR TEXTURE GEN
    vec3 normal = vec3(uv_remap.xy, sqrt(bodyRadius*bodyRadius - dis*dis))/bodyRadius;
    normal = normalize(normal);
    normal.z = clamp(normal.z, 0.1, 1.0);  // gets rid of weird jagged pixels
    return normal;
}
*/

vec2 LightandDither(vec3 normal, vec2 texture_uv) {
    float ringcount = 0.2001; // 1/ringcount
    float graincount = 128.0; // really its just totalGrainsInGrid
    float edge = 0.05; // must be less than 1/ringcount

    float fbm1 = fbm(texture_uv);
    float fbm_val = fbm(texture_uv * size + fbm1 + vec2(time*time_speed, 0.0)) * 0.3;
    
    float ls = max(dot(normal, -normalize(movedLightDirection)), 0.04); // luminosity
    ls -= fbm_val;  // apply fbm
    
    float dithered_ls = ls;
    if (mod(ls, ringcount) >= edge && ls < 0.899) {
        if ((mod(texture_uv.x*graincount, 2.0) < 1.0 && mod(texture_uv.y*graincount, 2.0) < 1.0) ||
            (mod(texture_uv.x*graincount, 2.0) > 1.0 && mod(texture_uv.y*graincount, 2.0) > 1.0)) {
            dithered_ls += 0.1001;  // dither
        }
    }

    return vec2(ls, dithered_ls);
}

vec3 cloudFinal(float ls, vec2 texture_uv) {
    // ld.x = ls
    // ld.y = dithered_ls
    vec3 NotfragColor = texture(T_planet, texture_uv).rgb * lightColor;
    if (!isStar) {  // if planet(has shadows)
		vec3 nodither_shadow_mul = vec3(1.0 * max(ls - mod(ls, 0.1001), 0.04));
		vec3 cloud_result = cloudColor * nodither_shadow_mul;
        return cloud_result + vec3(0.1) * NotfragColor; //lightDirection is also a uniform
		// adds a slight hint of planet with max refraction index
    }
    else {
        return NotfragColor;  // star, no need for lighting
    }
}

vec3 planetFinal(float dithered_ls, vec2 texture_uv) {
    vec3 NotfragColor = texture(T_planet, texture_uv).rgb * lightColor;
    vec3 dithered_shadow_mul = vec3(1.0 * max(dithered_ls - mod(dithered_ls, 0.1001), 0.04));

    vec3 planet_result = vec3(1.5) * NotfragColor * dithered_shadow_mul;

    vec3 result;
    if (!isStar) {  // should do lighting
        result =  planet_result; //lightDirection is also a uniform
    }
    else {
        result = NotfragColor;
    }
    return result;
}

void main() {
    vec2 pos = uv_0 * screenResolution;

    float dis = distance(planetCenter, pos);
    
    if (false) {
        vec2 k = vec2(0.0);
        vec4 g = texture(T_planet, uv_0) + texture(T_planetNormal, k) + texture(T_planetUV, k);
        fragColor = vec4(1.0,0.0,0.0,1.0) + vec4(0.001) * g;
    }

    if (true) {
        if (dis<=cloudRadius) {
            vec2 uv_remap = (pos - planetCenter) / (cloudRadius * 2.0) + 0.5; // just replace bodyRadius with cloudRadius
            vec3 normal = texture(T_planetNormal, uv_remap * vec2(1, -1)).rgb; // * 2.0 - 1.0;

            vec2 texture_uv = texture(T_planetUV, uv_remap * vec2(1, -1)).rg;

            // for this to work you need to use "wrap_x":"repeat" in the texture settings
            texture_uv.x += planetOffset;

            if (shouldPixellize) {
                texture_uv = pixellize(texture_uv);
            }

            // float cloud_val = cloud(texture_uv);
            float isCloud = 1.0;// step(cloud_val, 0.35);

            vec2 ld = LightandDither(normal, texture_uv); // ls + dithered_ls
            vec4 final;

            if (isCloud == 1.0) {
                fragColor = vec4(cloudFinal(ld.x, texture_uv), 1.0);
            }
            else if (dis <= bodyRadius) {
                uv_remap = (pos - planetCenter)/(bodyRadius*2.0) + 0.5;
                normal = texture(T_planetNormal, uv_remap * vec2(1, -1)).rgb; // * 2.0 - 1.0;
                texture_uv = texture(T_planetUV, uv_remap * vec2(1, -1)).rg;
                
                texture_uv.x += planetOffset;
                if (shouldPixellize) {
                    texture_uv = pixellize(texture_uv);
                }
                
                ld = LightandDither(normal, texture_uv); // ls + dithered_ls
                
                fragColor = vec4(planetFinal(ld.y, texture_uv).rgb, 1.0);
            } else {
                discard;
            }
        } else {
            discard;
        }
    }
}
