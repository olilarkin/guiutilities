// Sequential circuits style knob
// Oli Larkin 2011
// www.olilarkin.co.uk


#include "colors.inc" 
#include "textures.inc"

#declare VARIANT_TEST=0; 
#declare VARIANT_ALPHA=1;	// alpha render (for foreground)
#declare VARIANT_BKG=2;		// background render (for shadow color)
#declare VARIANT_SHADOW=3;	// shadow render (for shadow shape)

#ifndef (Variant)
	#declare Variant= VARIANT_TEST;
#end

#declare START_ANGLE = -150;
#declare END_ANGLE = 150;
#declare STARTVAL = 0;
#declare NUMSTEPS = 11;
#declare TEXTSIZE = 0.4;
#declare MARKLENGTH = 1.16;
#declare TEXT_DIST=1.35;
#declare DOTSIZE=0.05;
#declare MODE=1; // 0 = dots, 1 =  lines

//#declare SCITYPE=1; // 0 = black centre, silver pointer, 1 =	opposit

#declare FUDGE_FACTOR=2.65; //	is a bodge! To be fixed

#declare INCR= ((END_ANGLE - START_ANGLE)/NUMSTEPS+FUDGE_FACTOR); 

#ifndef (TOPDOWN)
	#declare TOPDOWN=1; 
#end

#if (TOPDOWN = 1) 
	camera 
	{
		orthographic 
		up <0, 3, 0> 
		right <3, 0, 0> 
		location <0, 0.001, -2> 
		look_at <0, 0, 0> 
	 //	  sky <0,0,1>
	} 
#else 
	// normal camera at angle 
	camera 
	{ 
		location <0, -2., -2.> 
		look_at 0 
		sky <0,0,1>
	} 
#end 
	
// soft light source 
light_source 
{ 
	<-30, 30, -200> 
	color White 
	//shadowless
	area_light <15, 0, 0>, <0, 0, 15>, 5, 5 
	adaptive 1 
} 

light_source 
{ 
	<10, 10, -1> 
//	area_light <15, 0, 0>, <0, 0, 15>, 5, 5 
	color White
//	shadowless
} 

plane 
{
	z, 0.0
	texture 
	{ 
	pigment { color White  }
			#switch (Variant)
				#case (VARIANT_TEST)
			finish { ambient 0 diffuse 0.08 }
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


#if (MODE = 0) 
	//dots
	#local dotmarker= cylinder 
	{ 
		<0, MARKLENGTH, -.0001>,// Center of one end 
		<0, MARKLENGTH, 0>, // Center of other end 
		DOTSIZE // Radius 
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
	}
	
	#declare Count=0;
	#while (Count < NUMSTEPS) 
		object
		{
			dotmarker
			rotate <0,0, -START_ANGLE -( Count * INCR)> 
		} 
		
		#declare Count=Count+1; 
	#end

#else

	//lines
	#local linemarker=box 
	{ 
		<-0.01, 0., -0.002>, // Near lower left corner 
		< 0.01, MARKLENGTH, 0> // Far upper right corner 
		
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
	}
	
	#declare Count=0;
	#while (Count < NUMSTEPS) 
		object
		{
			linemarker
			rotate <0,0, -START_ANGLE -( Count * INCR)> 
		} 
		
		#declare Count=Count+1; 
	#end
#end

//numbers

#declare Count=0;

#while (Count < NUMSTEPS)
	#local mytext= text 
	{
		ttf "crystal.ttf" str(Count + STARTVAL,1,0), 1, 0
		texture 
		{			
			pigment { color White  }
			finish { ambient 1 } 
		} 
		scale <TEXTSIZE, TEXTSIZE ,0.1>
	} 
	
	#declare TextMin  = min_extent( mytext );
	#declare TextMax  = max_extent( mytext );
	#declare TextSize = TextMax - TextMin;
	
	#declare Angle=(90+ -START_ANGLE -( Count * INCR))/360.;
	#declare Xpos=TEXT_DIST*cos(Angle*6.28318);
	#declare Ypos=TEXT_DIST*sin(Angle*6.28318);
	
	object
	 { 
		mytext
		translate -TextSize / 2.
		translate <Xpos,Ypos, 0.01>
		
		#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
		no_image
		#end
	 }
	 #declare Count=Count+1; 
#end



// grooves around outer knob

#declare Count=0;
#while (Count <= 30) 
	cylinder 
	{ 
		<0, 0.87, 0.>,// Center of one end 
		<0, 0.87, -0.6999>, // Center of other end 
		0.06 // Radius 
		texture 
		{ 
			pigment{ color Gray05}	
			
			finish 
			{ 
			phong 0.2 
			ambient 0.5 
			diffuse 0.4 
			} 
		} 
		rotate <0,0,( Count * ((360.)/30))>	 
		#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
		no_image
		#end
	} 
	
	#declare Count=Count+1; 
#end

// outer knob
cylinder 
{ 
	<0, 0, 0>,// Center of one end 
	<0, 0, -0.7>, // Center of other end 
	0.9 // Radius 
	
	texture
	{ 
		pigment{ color Gray05} 
		finish { phong 0.3 } 
	}
	#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
	no_image
	#end
}

union
{
	// chrome ring
	cylinder
	{
		<0, 0, 0>,// Center of one end 
		<0, 0, -0.85>, // Center of other end 
		0.81 // Radius
	}

	cone 
	{
		<0, 0, -0.87>, 0.81	  // Center and radius of one end
		<0, 0, -0.89>, 0.73	   // Center and radius of other end
	}
	
	texture
		{
			Chrome_Metal
			pigment{color Gray95}
			finish
			{ 
				ambient 0.1 
				diffuse 0.1
				phong 0.1
				reflection 1
			}
		}

	#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
	no_image
	#end
}

// inner knob
cylinder
{
	<0, 0, 0>,// Center of one end 
	<0, 0, -0.9>, // Center of other end 
	0.73 // Radius 
	
	texture
	{
		pigment{ color Gray35} 
		finish 
		{ 
			phong 0 
			ambient 0.1
			diffuse 0.1

		}
	}

	#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
	no_image
	#end
}

union
{
	cylinder
	{
		<0, 0, -0.95>,// Center of one end 
		<0, 0, 0.>, // Center of other end 
		0.06 // Radius 
	}
	// pointer line on knob 
	box
	{
		<-0.06, 0., -0.95>, // Near lower left corner 
		< 0.06, 0.73, -0.95> // Far upper right corner
		
		rotate <0,0,-START_ANGLE -( clock * (END_ANGLE - START_ANGLE))> 
	}
	
	 texture
		{
			Silver_Metal
			pigment{color White}
			finish
			{ 
				ambient 0.1 
			diffuse 0.7
				phong 0.1
				reflection 1
			}
		}

	#if ((Variant = VARIANT_BKG) | (Variant = VARIANT_SHADOW))
	no_image
	#end
}



