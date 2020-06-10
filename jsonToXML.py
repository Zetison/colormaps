# This script takes colormap exported by paraview in the .json file format and converts it into the corresponding xml format with an interpolation of the opacities
import click
import re
import copy
import scipy.interpolate as interpolate
import numpy as np

@click.command()
@click.option('--inputname', type=str, required=True)
@click.option('--outputname', type=str, required=False)
def main(inputname,outputname):
	f = open(inputname,'r')
	if not(outputname):
		outputname = inputname[:-4]+'xml'
	fout = open(outputname, 'w')
	foundName = False
	extractPoints = False
	data = []
	block = 0
	for x in f:
		if "ColorSpace" in x:
			temp = re.findall('"([^"]*)"', x)
			space = temp[1]
		elif "Name" in x:
			temp = re.findall('"([^"]*)"', x)
			scheme = temp[1]
			fout.write('<ColorMap name="%s" space="%s">\n' % (scheme, space) );
			foundName = True
		if '[' in x and foundName:
			extractPoints = True
		if extractPoints:
			subData = re.findall(r"[-+]?\d*\.\d+|\d+", x)
			data += subData
		
		if ']' in x:
			extractPoints = False
			if block == 0:
				points = [float(s) for s in copy.deepcopy(data[::4])]
				values = [float(s) for s in copy.deepcopy(data[1::4])]
			elif block == 1:
				RGBpoints = [float(s) for s in copy.deepcopy(data)]
			block += 1
			data=[]
	f.close()
	spl = interpolate.UnivariateSpline(points, values, k=1, s=0)
	noPoints = len(RGBpoints)//4
	for i in range(0,noPoints):
		x = RGBpoints[4*i]
		o = spl(x)
		fout.write('\t<Point x="%.15f" o="%.15f" r="%.15f" g="%.15f" b="%.15f"/>\n' % (x, o, RGBpoints[4*i+1], RGBpoints[4*i+2], RGBpoints[4*i+3]) );

	fout.write('</ColorMap>')
	fout.close()
	

if __name__ == '__main__':
    main()
