from pylab import *
import sys
import re


def MAT_m_VEC(m, v):
    p = [ 0.0 for i in range(len(v)) ]
    for i in range(len(m)):
        assert len(v) == len(m[i]), 'Length of the matrix row is not equal to the length of the vector'
        p[i] = sum( [ m[i][j]*v[j] for j in range(len(v)) ] )
    return p


def T(m):
    p = [[ m[i][j] for i in range(len( m[j] )) ] for j in range(len( m )) ]
    return p


def parse_poscar(poscar):
    # modified subroutine from phonopy 1.8.3 (New BSD license)
    poscar.seek(0) # just in case
    lines = poscar.readlines()

    scale = float(lines[1])
    if scale < 0.0:
        print("[parse_poscar]: ERROR negative scale not implemented.")
        sys.exit(1)

    b = []
    for i in range(2, 5):
        b.append([float(x)*scale for x in lines[i].split()[:3]])

    vol = b[0][0]*b[1][1]*b[2][2] + b[1][0]*b[2][1]*b[0][2] + b[2][0]*b[0][1]*b[1][2] - \
          b[0][2]*b[1][1]*b[2][0] - b[2][1]*b[1][2]*b[0][0] - b[2][2]*b[0][1]*b[1][0]

    try:
        num_atoms = [int(x) for x in lines[5].split()]
        line_at = 6
    except ValueError:
        symbols = [x for x in lines[5].split()]
        num_atoms = [int(x) for x in lines[6].split()]
        line_at = 7
    nat = sum(num_atoms)

    if lines[line_at][0].lower() == 's':
        line_at += 1

    if (lines[line_at][0].lower() == 'c' or lines[line_at][0].lower() == 'k'):
        is_scaled = False
    else:
        is_scaled = True

    line_at += 1
    positions = []
    for i in range(line_at, line_at + nat):
        pos = [float(x) for x in lines[i].split()[:3]]
        if is_scaled:
            pos = MAT_m_VEC(T(b), pos)
        positions.append(pos)
    poscar_header = ''.join(lines[1:line_at-1]) # will add title and 'Cartesian' later

    return nat, vol, b, positions, poscar_header



def projectmodes(outcar, nat, idealmode):

    eigvals     = [ 0.0 for i in range(nat*3) ]
    eigvecs     = [ 0.0 for i in range(nat*3) ]
    norms       = [ 0.0 for i in range(nat*3) ]
    projections = [ 0.0 for i in range(nat*3) ]

    outcar.seek(0) # just in case
    while True:
        line = outcar.readline()
        if not line:
            break
        if "Eigenvectors after division by SQRT(mass)" in line:
            outcar.readline() # empty line
            outcar.readline() # Eigenvectors and eigenvalues of the dynamical matrix
            outcar.readline() # ----------------------------------------------------
            outcar.readline() # empty line
            print("Mode    Freq (cm-1)")
            for i in range(nat*3):
                outcar.readline() # empty line
                p = re.search(r'^\s*(\d+).+?([\.\d]+) cm-1', outcar.readline())
                eigvals[i] = float(p.group(2))

                outcar.readline() # X         Y         Z           dx          dy          dz
                eigvec = []

                for j in range(nat):
                    tmp = outcar.readline().split()
                    eigvec.append([ float(tmp[x]) for x in range(3,6) ])

                ev = array(eigvec)
                for j in range(nat):
                    #projections[i] += dot(ev[j,:],idealmode[j,:]) / norm(idealmode[j,:])**2
                    #projections[i] += dot(ev[j,:],idealmode[j,:]) / (norm(idealmode[j,:])*norm(ev[j,:]))
                    projections[i] += abs(dot(ev[j,:],idealmode[j,:])) / (norm(idealmode[j,:])*norm(ev[j,:]))
                    
                eigvecs[i] = eigvec
                norms[i] = sqrt( sum( [abs(x)**2 for sublist in eigvec for x in sublist] ) )
                #writeVestaMode(i, eigvals[i], eigvecs[i], vesta_front, vesta_end, nat, scaling_factor)
                
                
                if abs(projections[i]/nat) > 0.1:
                    print("%4d %6.2f %6.2f" %(i+1, eigvals[i], projections[i]/nat))

    return eigvals, eigvecs, norms, projections/nat


def writeVestaMode(i, eigval, eigvec, vesta_front, vesta_end, nat, scaling_factor):
    modef = open("mode_%.2f.vesta"%eigval, 'w')

    modef.write(vesta_front)

    sf = scaling_factor
    towrite = "VECTR\n"
    for i in range(1,1+nat):
        towrite += "%4d%9.5f%9.5f%9.5f\n"%(i,eigvec[i-1][0]*sf,eigvec[i-1][1]*sf,eigvec[i-1][2]*sf)
        towrite += "%5d  0   0    0    0\n 0 0 0 0 0\n"%i
    towrite += " 0 0 0 0 0\n"
    towrite += "VECTT\n"
    for i in range(1,1+nat):
        towrite += "%4d%6.3f 255   0   0 1\n"%(i,0.5)
        towrite += " 0 0 0 0 0\n"

    if i==0:
        print(towrite)
        
    modef.write(towrite)

    return 0


def openVestaOutcarPoscar():
    if len(sys.argv) == 1:
        try:
            vesta  = open('poscar.vesta','r')
        except:
            print("Cannot find poscar.vesta in current directory")
            print("Usage:\n\tpython modes_to_vesta.py <vesta-filename.vesta>")
            sys.exit(0)
    elif len(sys.argv) == 2:
        try:
            print("Opening ", sys.argv[1])
            vesta = open(sys.argv[1],'w')
        except:
            print("Cannot find file ", sys.argv[1])
            sys.exit(0)
    else:
        print("Cannot parse >1 command-line argument")
        sys.exit(0)

    try:
        outcar = open('OUTCAR', 'r')
    except:
        print("Cannot find OUTCAR in current directory")
        sys.exit(0)

    try:
        poscar = open('POSCAR', 'r')
    except:
        print("Cannot find POSCAR in current directory")
        sys.exit(0)

    return vesta, outcar, poscar


def getVestaFrontEnd(vesta):

    vfile = vesta.read()
    vesta_front = vfile.split("VECTR")[0]
    vesta_end   = vfile.split("VECTT\n 0 0 0 0 0")[1]

    return vesta_front, vesta_end

if __name__ == '__main__':

    scaling_factor = 70
    
    vesta, outcar, poscar = openVestaOutcarPoscar()
    #vesta_front, vesta_end = getVestaFrontEnd(vesta)
    nat, vol, b, positions, poscar_header = parse_poscar(poscar)

    print("# atoms   vol of unit cell (Ang^3)   # modes")
    print("  %d      %4.2f       %d" %(nat,vol,nat*3))

    idealmode = genfromtxt('mode-159.25.dat')[:,3:]    
    eigvals, eigvecs, norms, projections = projectmodes(outcar, nat, idealmode)
    projections = array(projections)
    eigvals = array(eigvals)
    sortedlist = argsort(abs(projections))[::-1]
    savelist = zeros([len(projections), 3])
    savelist[:,0] = array(arange(nat*3)[sortedlist])
    savelist[:,1] = array(eigvals[sortedlist])
    savelist[:,2] = array(projections[sortedlist])
    hdr = "%14s%15s%15s"%("mode #","freq (cm-1)", "proj value")
    savetxt('m159.25compare.out',savelist,fmt="%15.2f",header=hdr)
    
    idealmode = genfromtxt('mode-162.58.dat')[:,3:]
    eigvals, eigvecs, norms, projections = projectmodes(outcar, nat, idealmode)
    projections = array(projections)
    eigvals = array(eigvals)
    sortedlist = argsort(abs(projections))[::-1]
    savelist = zeros([len(projections), 3])
    savelist[:,0] = array(arange(nat*3)[sortedlist])
    savelist[:,1] = array(eigvals[sortedlist])
    savelist[:,2] = array(projections[sortedlist])
    hdr = "%14s%15s%15s"%("mode #","freq (cm-1)", "proj value")
    savetxt('m162.58compare.out',savelist,fmt="%15.2f",header=hdr)

