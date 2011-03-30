#!/usr/bin/env python

# python shell script to help rendering transparent animation scenes for gui controls, using povray
# Oli Larkin 2011 http://www.olilarkin.co.uk
# License: WTFPL http://sam.zoy.org/wtfpl/COPYING
# transparent background thanks to Christoph Hormann's tutorial here http://www.imagico.de/pov/icons.html
# example knob based on synthedit knob example by Jeff Mclintock

# requires povray and imagemagick
# get them by installing macports http://www.macports.org/ and typing 
# sudo port install ImageMagick
# sudo port install povray
# you may also want to get megapov for mac, which seems to be the nicest editor

# tested on osx 10.6, may work on other *nix based systems

import optparse, os, string, sys

def main():
	p = optparse.OptionParser()
	p.add_option('--frames', '-f', default="10")
	p.add_option('--scene', '-s', default="knob")
	p.add_option('--rdim', '-r', default="300")
	p.add_option('--odim', '-o', default="48")
	p.add_option('--tile', '-t', default="v")
	p.add_option('--alpha', '-a', default="y")
	#p.add_option('--height', '-h', default="100")
	options, arguments = p.parse_args()

	scn = options.scene
	frms = options.frames
	lz = ''
	
	base, extension = os.path.splitext(scn)
	
	if extension == '.pov':
		scn = base
	
	if os.path.isfile(scn + '.pov') == False:
		print "error: scene not found",
		sys.exit(1)
	
	if int(frms) == 1:
		lz = ''
	elif int(frms) < 10:
		lz = '%01d'
	elif int(frms) < 100:
		lz = '%02d'
	elif int(frms) < 1000:
		lz = '%03d'
	
	stitch = '-append'
	if options.tile == 'v':
			stitch = '-append'
	elif options.tile == 'h':
			stitch = '+append'
	else:
		print "error: incorrect stitch option",
		sys.exit(1)

	#povray options supplied to all renders	
	popt = 'All_Console=Off All_File="false" Antialias=On Antialias_Depth=3 Antialias_Threshold=0.3 Bits_Per_Color=8 Bounding=On Bounding_Threshold=10 Continue_Trace=Off Create_Histogram=Off Debug_Console=On Debug_File="false" Display=Off Draw_Vistas=On End_Column=300 End_Row=300 Fatal_Console=On Fatal_File="false" Height=' + options.rdim + ' Input_File_Name=' +  scn + '.pov Jitter_Amount=1 Jitter=On Light_Buffer=On Output_File_Type=n Output_To_File=On Quality=9 Remove_Bounds=On Render_Console=On Render_File="false" Sampling_Method=1 Split_Unions=On Start_Column=1 Start_Row=1 Statistic_Console=On Statistic_File="false" Vista_Buffer=On Warning_Console=On Warning_File="false" Width=' + options.rdim + ' Initial_Frame=1 Final_Frame=' + frms + ' Initial_clock=0.0 Final_clock=1.0 '
	
	if options.alpha == 'y':
		#render three times. once for alpha, once for background and once for shadow
		os.system('povray Output_Alpha=On DECLARE=Variant=1 ' + popt + 'Output_File_Name=' + scn + '-alpha.png') #Create_Ini=' + scn + '-alpha.ini'
		os.system('povray Output_Alpha=Off DECLARE=Variant=2 ' + popt + 'Output_File_Name=' + scn + '-bg.png')
		os.system('povray Output_Alpha=Off DECLARE=Variant=3 ' + popt + 'Output_File_Name=' + scn + '-shadow.png')
	
		#stitch the frames together vertically or horizontally
		os.system('convert ' + scn + '-alpha' + lz + '.png' + '[1-' + frms + '] ' + stitch + ' st-' + scn + '-alpha.png')
		os.system('convert ' + scn + '-bg' + lz + '.png' + '[1-' + frms + '] ' + stitch + ' st-' + scn + '-bg.png')
		os.system('convert ' + scn + '-shadow' + lz + '.png' + '[1-' + frms + '] ' + stitch + ' st-' + scn + '-shadow.png')
		
		#split the background RGB channels to seperate files
		os.system('convert -channel R -separate st-' + scn + '-bg.png st-' + scn + '-bg-red.png')
		os.system('convert -channel G -separate st-' + scn + '-bg.png st-' + scn + '-bg-green.png')
		os.system('convert -channel B -separate st-' + scn + '-bg.png st-' + scn + '-bg-blue.png')
	
		#join the backround's RGB channels with the shadow
		os.system('convert -depth 8 -channel RGBA -combine st-' + scn + '-bg-red.png st-' + scn + '-bg-green.png st-' + scn + '-bg-blue.png st-' + scn + '-shadow.png st-' + scn + '-bg-tmp.png' )
		
		#composite with the alpha channel
		os.system('composite -depth 8 -compose over st-' + scn + '-alpha.png st-' + scn + '-bg-tmp.png rendered-' + scn + '.png')
		
	elif options.alpha == 'n':
		#render once
		os.system('povray ' + popt + ' DECLARE=Variant=0 Output_File_Name=' + scn + '.png')
		#stitch
		os.system('convert ' + scn + lz + '.png' + '[1-' + frms + '] ' + stitch + ' rendered-' + scn + '.png')
	else:
		print "error: bad alpha option",
		sys.exit(1)
		
	#clean up (osx/linux only)
	os.system('rm ' + scn + '*.png')
	os.system('rm st-' + scn + '*.png')

	od = options.odim
	oh = str(int(frms) * int(od))
	
	#resize the image
	os.system('convert rendered-' + scn + '.png -resize ' + od + 'x' + oh + ' resized-' + scn + '-' + od + 'x' + od + '.png') 

	#open the image
	os.system('open resized-' + scn + '-' + od + 'x' + od + '.png')
	
if __name__ == '__main__':
	main()