#!/usr/bin/env python

import optparse, os, string, sys

def main():
	p = optparse.OptionParser()
	p.add_option('--frames', '-f', default="10")
	p.add_option('--scene', '-s', default="knob")
	p.add_option('--rdim', '-r', default="300")
	p.add_option('--odim', '-o', default="48")
	p.add_option('--tile', '-t', default="v")
	p.add_option('--alpha', '-a', default="y")
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
	popt = ""
	popt += 'End_Column='
	popt += options.rdim
	popt += ' End_Row='
	popt += options.rdim
	popt += ' Height='
	popt += options.rdim
	popt += ' Width='
	popt += options.rdim
	popt += ' Input_File_Name='
	popt += scn + '.pov '
	popt += 'Final_Frame='
	popt += frms
	
	popt += 'All_Console=Off '
	popt += 'All_File="false" '
	popt += 'Antialias=On '
	popt += 'Antialias_Depth=5 '
	popt += 'Antialias_Threshold=0.3 '
	popt += 'Bits_Per_Color=8 '
	popt += 'Bounding=On '
	popt += 'Bounding_Threshold=10 '
	popt += 'Continue_Trace=Off '
	popt += 'Debug_Console=On '
	popt += 'Debug_File="false" '
	popt += 'Bounding=On '
	popt += 'Bounding=On '
	popt += 'Display=Off '
	popt += 'Draw_Vistas=On '
	popt += 'Fatal_Console=On '
	popt += 'Fatal_File="false" '
	popt += 'Jitter_Amount=1 '
	popt += 'Jitter=On '
	popt += 'Light_Buffer=On '
	popt += 'Output_File_Type=n '
	popt += 'Output_To_File=On '
	popt += 'Quality=9 '
	popt += 'Remove_Bounds=On '
	popt += 'Render_Console=On '
	popt += 'Render_File="false" '
	popt += 'Sampling_Method=1 '
	popt += 'Split_Unions=On '
	popt += 'Statistic_Console=On '
	popt += 'Statistic_File="false" '
	popt += 'Vista_Buffer=On '
	popt += 'Warning_Console=On '
	popt += 'Warning_File="false" '
	popt += 'Initial_Frame=1 '
	popt += 'Initial_clock=0.0 '
	popt += 'Final_clock=1.0 '
	
	if options.alpha == 'y':
		#render three times. once for alpha, once for background and once for shadow
		os.system('povray Output_Alpha=On DECLARE=Variant=1 ' + popt + 'Output_File_Name=' + scn + '-alpha.png') #Create_Ini=' + scn + '-alpha.ini'
		os.system('povray Output_Alpha=Off DECLARE=Variant=2 ' + popt + 'Output_File_Name=' + scn + '-bg.png')
		os.system('povray Output_Alpha=Off DECLARE=Variant=3 ' + popt + 'Output_File_Name=' + scn + '-shadow.png')
	
		#stitch the frames together vertically or horizontally
		os.system('convert ' + scn + '-alpha*.png ' + stitch + ' st-' + scn + '-alpha.png')
		os.system('convert ' + scn + '-bg*.png '  + stitch + ' st-' + scn + '-bg.png')
		os.system('convert ' + scn + '-shadow*.png '  + stitch + ' st-' + scn + '-shadow.png')
		
		#split the background RGB channels to seperate files
		os.system('convert -channel R -separate st-' + scn + '-bg.png st-' + scn + '-bg-red.png')
		os.system('convert -channel G -separate st-' + scn + '-bg.png st-' + scn + '-bg-green.png')
		os.system('convert -channel B -separate st-' + scn + '-bg.png st-' + scn + '-bg-blue.png')
	
		#join the backround's RGB channels with the shadow
		os.system('convert -depth 8 -channel RGBA st-' + scn + '-bg-red.png st-' + scn + '-bg-green.png st-' + scn + '-bg-blue.png st-' + scn + '-shadow.png -negate -combine st-' + scn + '-bg-tmp.png' )
		
		#composite with the alpha channel
		os.system('composite -depth 8 -compose over st-' + scn + '-alpha.png -negate st-' + scn + '-bg-tmp.png rendered-' + scn + '.png')
		
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
	os.system('rm false')

	od = options.odim
	oh = str(int(frms) * int(od))
	
	#resize the image
	os.system('convert rendered-' + scn + '.png -resize ' + od + 'x' + oh + ' resized-' + scn + '-' + od + 'x' + od + '.png') 

	#open the image
	os.system('open resized-' + scn + '-' + od + 'x' + od + '.png')
	
if __name__ == '__main__':
	main()