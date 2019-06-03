from pylab import *
import numpy
rcParams.update({'font.size': 48, 'text.usetex': True})

HLINES = 21
fileh = open("LOCPOT","r")

# read the header
i = HLINES
while i >= 0:
	fileh.readline()
	i -= 1
	
(nx,ny,nz) = fileh.readline().split()
nx = int(nx)
ny = int(ny)
nz = int(nz)
locpot = []

i = 0
while i < nx*ny*nz:
    line = fileh.readline()
    for s in map(float, line.split()):
        locpot.append(s)
        i += 1

locpot = array(locpot)
print(nx*ny*nz)
print(len(locpot))
print(sum(locpot))

totallocpot = sum(locpot)

locpotz = zeros(nz)
for k in range(nz):
    planesum = 0
    for j in range(ny):
        for i in range(nx):
            idx = i + j*nx + k*nx*ny
            planesum += locpot[idx]
    locpotz[k] = planesum

#nelectrons = 73

#locpotzfront = locpotz[nz-nz/8:]
#locpotz = append(locpotzfront, locpotz[:nz-nz/8])
nelectrons = 1
plot(arange(nz)/nz*35,locpotz)
ylabel('LOCPOT in-plane sum at location $z$',fontsize=34)
xlabel('$z$ ($\AA$)')
show()
#savefig('locpot_vs_z.png', bbox_inches='tight')
