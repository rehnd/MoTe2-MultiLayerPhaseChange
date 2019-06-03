from pylab import *
rcParams.update({'font.size': 48, 'text.usetex': True})

lowmode  = array([159.25, 158.02, 159.58,160.24])
highmode = array([162.58, 162.84,163.85, 164.00])


figure()
plot(lowmode)
plot(highmode)
xlabel('\# vacancies')
ylabel('frequency (cm$^{-1}$)')
tight_layout()
show()
