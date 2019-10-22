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
    folders = ['3-Li-bilayer-0.5', '4-Li-bilayer-0.45', '5-Li-bilayer-0.4', '6-bilayer-only']
    HLINES = [21,21,21,20]
    
    if len(folders) != len(HLINES):
        print("Error: folders and HLINES are not the same size")
        exit(1)
            
    nz = getnz(HLINES[0], folders[0])
    chargeresults = zeros([nz, len(folders)])
    
    for i in range(len(folders)):
        chargeresults[:,i] = getchargearray(HLINES[i], folders[i])
            

    if len(folders) == 4:
        diff1 = chargeresults[:,0] - chargeresults[:,3]
        diff2 = chargeresults[:,1] - chargeresults[:,3]
        diff3 = chargeresults[:,2] - chargeresults[:,3]

    totalcharge1 = sum(diff1)
    totalcharge2 = sum(diff2)
    totalcharge3 = sum(diff3)

    nelectrons = 1
    figure(figsize=(9,15))
    plot(diff1/totalcharge1*nelectrons,arange(nz)/nz*35,color="#B1D1D0")
    plot(diff2/totalcharge2*nelectrons,arange(nz)/nz*35,color="#69A4A0")
    plot(diff3/totalcharge3*nelectrons,arange(nz)/nz*35,color="#517878")
    ylim(0,35)
    xlim(-0.015, 0.1)
    xlabel('$q(z)$')
    ylabel('$z$ ($\mathrm{\AA}$)')
    tight_layout()
    savefig('pics/charge_vs_z.png', bbox_inches='tight')
    #show()

    chargezsum1 = zeros(nz)
    chargezsum2 = zeros(nz)
    chargezsum3 = zeros(nz)

    for i in range(nz):
        chargezsum1[i] = sum(diff1[:i])
        chargezsum2[i] = sum(diff2[:i])
        chargezsum3[i] = sum(diff3[:i])
        
    nelectrons=1
    figure(figsize=(9,15))
    plot(chargezsum1/totalcharge1*nelectrons,arange(nz)/nz*35,color="#B1D1D0")
    plot(chargezsum2/totalcharge2*nelectrons,arange(nz)/nz*35,color="#69A4A0")
    plot(chargezsum3/totalcharge3*nelectrons,arange(nz)/nz*35,color="#517878")
    #axvline(1,color='g')
    ylabel('$z$ ($\mathrm{\AA}$)')
    xlabel('$N(z)$')
    ylim(0,35)
    xlim(-0.1,1.1)
    tight_layout()
    savefig("pics/sumcharge_vs_z.png", bbox_inches='tight')        
    #show()
