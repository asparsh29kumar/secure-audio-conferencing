MAX_BUF_SIZE = 16

CMD_HELLO = "h"
CMD_BEGIN = "b"
CMD_RECYCLE_RETRIEVE = "r1"
CMD_RECYCLE_RESHARE = "r2"
CMD_REQ_PUBLIC_KEY = "p"
CMD_ACK = "1"
CMD_NACK = "0"

PRIMES_LOWER_BOUND = 50
PRIMES_UPPER_BOUND = 700

PRIVATE_KEY_MIN_VAL = 10


def isprime(a):
	i = 2
	while i * i <= a:
		if a % i == 0:
			return 0
		i += 1
	return 1


def prime_factors(a):
	primfac = []
	d = 2
	while d * d <= a:
		if a % d == 0:
			primfac.append(d)
		while (a % d) == 0:
			a //= d
		d += 1
	if a > 1:
		primfac.append(a)
	return primfac


def get_next_prime(a):
	if a % 2 == 0:
		a += 1
	while isprime(a) == 0:
		a += 2
	return a


def check_primitive(parr, a, p):
	for i in parr:
		if exponent_with_modulo(a, (p - 1) / i, p) == 1:
			return 0
	return 1


def find_primitive(p):
	m = p - 1
	i = p - 2
	parr = prime_factors(m)
	while check_primitive(parr, i, p) != 1:
		i -= 1
	return i


def exponent_with_modulo(a, b, c):
	res = 1
	for i in range(b):
		res = (res * a) % c
	return res
