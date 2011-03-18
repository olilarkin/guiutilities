#include "colors.inc" 
 
#declare VARIANT_TEST=0; 
#declare VARIANT_ALPHA=1;   // alpha render (for foreground)
#declare VARIANT_BKG=2;     // background render (for shadow color)
#declare VARIANT_SHADOW=3;  // shadow render (for shadow shape)

#ifndef (Variant)
	#declare Variant=VARIANT_TEST;
#end

#declare TICKS = 20; 
#declare START_ANGLE = -135;
#declare END_ANGLE = 135;

#declare Count = 0; 
 
// set this to 0 to see the knob from an angle (helps to visualize it) 
#declare TOPDOWN=1; 

#if (TOPDOWN = 1) 
    camera 
    {
        orthographic 
        up <0, 2.6, 0> 
        right <2.6, 0, 0> 
        location <0, 0.001, 2> 
        look_at <0, 0, 0> 
    } 
#else 
    // normal camera at angle 
    camera 
    { 
        location <2.0, 0.0, 3.> 
        look_at 0 
    } 
#end 

// soft light source 
light_source 
{ 
    <4, 4, 30> 
    color White 
    area_light <15, 0, 0>, <0, 0, 15>, 5, 5 
    adaptive 1 
} 

// soft light source 
//light_source 
//{ 
//    <0, 0, -100> 
//    color <0.3,0.3,0.3> 
//    area_light <15, 0, 0>, <0, 0, 15>, 5, 5 
//    adaptive 1
//    shadowless
//} 

plane 
{
	z, 0.0
	texture 
	{ 
	pigment { color rgb 1  }
    		#switch (Variant)
    			#case (VARIANT_TEST)
			finish { ambient 0 diffuse 0.5 }
			#break
		#case (VARIANT_ALPHA)
			finish { ambient 0 diffuse 0.5 }
			#break
		#case (VARIANT_BKG)
			finish { ambient 0 diffuse 0.25 }
			#break
		#case (VARIANT_SHADOW)
			finish { ambient 0.05 diffuse 1.05 }
			#break
   		 #end
   	 }
   	 
   	 #if (Variant = VARIANT_ALPHA)
   	 no_image
 	#end
}

// white TICKS around knob on background

#while (Count <= TICKS) 
	cylinder 
	{ 
		<0, 1.2, .0001>,// Center of one end 
		<0, 1.2, 0>, // Center of other end 
		0.05 // Radius 
		texture 
		{ 
			pigment{ color White}  
			
			finish 
			{ 
			phong 1 
			ambient 0.5 
			diffuse 0.6 
			} 
		} 
		rotate <0,0,START_ANGLE +( Count * ((END_ANGLE - START_ANGLE)/TICKS))> 
		#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
		no_image
		#end
	} 
	
	#declare Count=Count+1; 
#end 
	
// inner part of knob
cylinder 
{ 
	<0, 0, 0>,// Center of one end 
	<0, 0, 0.8>, // Center of other end 
	0.9 // Radius 
	
	texture
	{ 
		pigment{ color White} 
		//finish { phong 0.5 } 
	}

	#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
	no_image
	#end
}
	
// outer knob
cylinder 
{ 
	<0, 0, 0>,// Center of one end 
	<0, 0, 0.6>, // Center of other end 
	0.99 // Radius 
	
	texture
	{ 
		pigment{ color Red} 
		//finish { phong 0.5 } 
	}
	#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
	no_image
	#end
}

// centre round bit of pointer
cylinder 
{ 
	<0, 0, 0.9>,// Center of one end 
	<0, 0, 0.>, // Center of other end 
	0.05 // Radius 
	
	texture
	{ 
		pigment{ color Black} 
		//finish { phong 0.5 } 
	}
	#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
	no_image
	#end
}
	
// pointer line on knob 
box 
{ 
	<-0.05, 0., 0.9>, // Near lower left corner 
	< 0.05, 1., 0.> // Far upper right corner 
	texture 
	{ 
		pigment{ color Black} 
		finish 
		{ 
			phong 0.01 
			ambient 0.5 
			diffuse 0.6 
		} 
	} 

	rotate <0,0,START_ANGLE +( clock * (END_ANGLE - START_ANGLE))> 
	#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
	no_image
	#end
}

