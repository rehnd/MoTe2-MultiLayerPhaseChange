from pylab import *
import numpy
rcParams.update({'font.size': 48, 'text.usetex': True})


def getnz(HL, folder):
    CHGCAR = open(folder + "/CHGCAR","r")

    # read the header
    i = HL # number of header lines
    while i >= 0:
        CHGCAR.readline()
        i -= 1
            
    (nx,ny,nz) = CHGCAR.readline().split()
    nx = int(nx)
    ny = int(ny)
    nz = int(nz)

    return nz


def getchargearray(HL,folder):

    CHGCAR = open(folder + "/CHGCAR","r")

    # read the header
    i = HL # number of header lines
    while i >= 0:
        CHGCAR.readline()
        i -= 1
            
    (nx,ny,nz) = CHGCAR.readline().split()
    nx = int(nx)
    ny = int(ny)
    nz = int(nz)
    charge = []
    
    i = 0
    while i < nx*ny*nz:
        line = CHGCAR.readline()
        for s in line.split():
            charge.append(float(s))
            i += 1
            
    charge = array(charge)
    print(nx*ny*nz)
    print(len(charge))
    print(sum(charge))
    
    totalcharge = sum(charge)
    
    chargez = zeros(nz)
    for k in range(nz):
        planesum = 0
        for j in range(ny):
            for i in range(nx):
                idx = i + j*nx + k*nx*ny
                planesum += charge[idx]
                chargez[k] = planesum

    nelectrons = 1

    return array(chargez)

        
if __name__ == '__main__':
    folders = ['3-electron-relax-bilayer-li', '4-electron-relax-bilayer']
    HLINES = [21,20]
    
    if len(folders) != len(HLINES):
        print("Error: folders and HLINES are not the same size")
        exit(1)
            
    nz = getnz(HLINES[0], folders[0])
    chargeresults = zeros([nz, len(folders)])
    
    for i in range(len(folders)):
        chargeresults[:,i] = getchargearray(HLINES[i], folders[i])
            

    if len(folders) == 2:
        diff = chargeresults[:,0] - chargeresults[:,1]

    totalcharge = sum(diff)
    nelectrons = 1
    figure(figsize=(9,15))
    plot(diff/totalcharge*nelectrons,arange(nz)/nz*35)
    ylim(0,35)
    xlim(-0.015, 0.1)
    xlabel('Charge fraction at location $z$',fontsize=34)
    ylabel('$z$ ($\AA$)')
    tight_layout()
    savefig('charge_vs_z.png', bbox_inches='tight')


    chargezsum = zeros(nz)
    for i in range(nz):
        chargezsum[i] = sum(diff[:i])

    nelectrons=1
    figure(figsize=(9,15))
    plot(chargezsum/totalcharge*nelectrons,arange(nz)/nz*35)
    axvline(1,color='g')
    ylabel('$z$ ($\AA$)')
    xlabel('Integrated \# electrons at location $z$',fontsize=34)
    ylim(0,35)
    xlim(-0.1,1.1)
    tight_layout()
    savefig("sumcharge_vs_z.png", bbox_inches='tight')        
