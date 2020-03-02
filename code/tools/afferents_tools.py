def compute_Ia_fr(stretch,stretchVel,muscActivation,species):
	""" Compute the firing rates of the Ia afferent fibers.

	Uses the experimetnally derived model devloped by Prochazka (1999 pag 136).
	Keyword arguments:
	stretch -- muscle stretch in mm.
	stretchVel -- muscle stretch velocity in mm/s.
	muscActivation -- normalized muscle activation [0 , 1].
	"""

	bias =50
	vCoef = 4.3
	expn = 0.6
	xCoef = 2
	musCoeff = 50

	if not stretchVel == 0 : stretchVelSign = stretchVel/abs(stretchVel)
	else: stretchVelSign = 1
	stretchVelPow = stretchVelSign*abs(stretchVel)**expn

	#compute firing rates
	fr_Ia = bias + xCoef*stretch + vCoef*stretchVelPow + musCoeff*muscActivation
	if fr_Ia<0: fr_Ia=0

	if species == "rat" or species == "mouse": return fr_Ia
	elif species == "human": return fr_Ia*0.25
	else: raise(Exception("Invalid species"))

def compute_II_fr(stretch,muscActivation,species):
	""" Compute the firing rates of the II afferent fibers.

	Uses the experimetnally derived model devloped by Prochazka (1999 (2)).
	Keyword arguments:
	stretch -- muscle stretch in mm.
	muscActivation -- normalized muscle activation [0 , 1].
	"""

	bias = 80
	xCoef = 13.5
	musCoeff = 20

	#compute firing rates
	fr_II = bias + xCoef*stretch + musCoeff*muscActivation
	if fr_II<0: fr_II=0

	if species == "rat" or species == "mouse": return fr_II
	elif species == "human": return fr_II*0.2
	else: raise(Exception("Invalid species"))
