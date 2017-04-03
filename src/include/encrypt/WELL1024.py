# PRNG implementation.

W = 32
R = 32
M1 = 3
M2 = 24
M3 = 10

z0 = 0
z1 = 0
z2 = 0

state_i = 0
FACT = 2.32830643653869628906e-10
STATE = []
for i in range(R):
	STATE.append(0)


def MAT0POS(t, v):
	return (v ^ (v >> t))


def MAT0NEG(t, v):
	return (v ^ (v << (-(t))))


def Identity(v):
	return (v)


init = [1, 2, 3, 4, 5, 6, 2, 8, 6, 0,
		1, 2, 3, 4, 5, 6, 7, 8, 9, 7,
		1, 2, 3, 4, 5, 6, 7, 8, 9, 0,
		1, 2]


def InitWELLRNG1024a():
	global state_i, STATE, init, R
	state_i = 0
	for j in range(R):
		STATE[j] = init[j]


def WELLRNG1024a():
	global state_i, z0, z1, z2, FACT, STATE
	z0 = STATE[(state_i + 31) & 0x0000001f]
	z1 = Identity(STATE[state_i]) ^ MAT0POS(8, STATE[(state_i + M1) & 0x0000001f])
	z2 = MAT0NEG(-19, STATE[(state_i + M2) & 0x0000001f]) ^ MAT0NEG(-14, STATE[(state_i + M3) & 0x0000001f])
	STATE[state_i] = z1 ^ z2
	STATE[(state_i + 31) & 0x0000001f] = MAT0NEG(-11, z0) ^ MAT0NEG(-7, z1) ^ MAT0NEG(-13, z2)
	state_i = (state_i + 31) & 0x0000001f

	STATE[state_i] %= 65536
	# return (STATE[state_i] * FACT)
	# return int((STATE[state_i] * FACT) * 10000000000) % 256
	return int((STATE[state_i] * FACT) * 10) % 10

# # Sample usage.
# InitWELLRNG1024a()
# for iterator in range(10):
# 	print(WELLRNG1024a())
