# This script takes colormap exported by paraview in the .json file format and converts it into the corresponding xml format with an interpolation of the opacities
import click
import re
import copy
import scipy.interpolate as interpolate
import numpy as np
import os

@click.command()
@click.option('--inputname', type=str, required=True)
@click.option('--outputname', type=str, required=False)
@click.option('--nrgbpts', default=1024)
def main(inputname,outputname,nrgbpts):
	f = open(inputname,'r')
	if not(outputname):
		outputname = inputname[:-4]+'xml'
	filename, file_extension = os.path.splitext(outputname)

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
			if file_extension == '.xml':
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
	noPoints = len(RGBpoints)//4
	if file_extension == '.rgb':
		RGBpoints = np.reshape(np.array(RGBpoints),(noPoints,4))
		temp = np.zeros((nrgbpts,3))
		for i in range(1,4):
			spl1 = interpolate.UnivariateSpline(RGBpoints[:,0], RGBpoints[:,i], k=1, s=0)
			temp[:,i-1] = spl1(np.linspace(RGBpoints[0,0],RGBpoints[-1,0],nrgbpts))
		RGBpoints = 255*temp
		noPoints = nrgbpts
		fout.write('ncolors=%d\n#  r   g   b\n' % (noPoints) )
	elif file_extension == '.xml':
		spl = interpolate.UnivariateSpline(points, values, k=1, s=0)

	for i in range(0,noPoints):
		if file_extension == '.xml':
			x = RGBpoints[4*i]
			o = spl(x)
			fout.write('\t<Point x="%.15f" o="%.15f" r="%.15f" g="%.15f" b="%.15f"/>\n' % (x, o, RGBpoints[4*i+1], RGBpoints[4*i+2], RGBpoints[4*i+3]) );
		elif file_extension == '.rgb':
			fout.write('%d %d %d\n' % (RGBpoints[i,0], RGBpoints[i,1], RGBpoints[i,2]) );

	if file_extension == '.xml':
		fout.write('</ColorMap>')
		fout.close()
	

if __name__ == '__main__':
    main()
