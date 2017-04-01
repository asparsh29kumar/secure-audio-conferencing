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


def is_prime(value):
	i = 2
	while i * i <= value:
		if value % i == 0:
			return 0
		i += 1
	return 1


def get_prime_factors(value):
	prime_factors = []
	d = 2
	while d * d <= value:
		if value % d == 0:
			prime_factors.append(d)
		while (value % d) == 0:
			value //= d
		d += 1
	if value > 1:
		prime_factors.append(value)
	return prime_factors


def get_next_prime(value):
	if value % 2 == 0:
		value += 1
	while is_prime(value) == 0:
		value += 2
	return value


def is_primitive(prime_array, a, p):
	for i in prime_array:
		if exponent_with_modulo(a, (p - 1) / i, p) == 1:
			return False
	return True


def get_closest_primitive_root(value):
	m = value - 1
	i = value - 2
	prime_array = get_prime_factors(m)
	while not is_primitive(prime_array, i, value):
		i -= 1
	return i


# exponent_with_modulo returns result = (a^b)%c
def exponent_with_modulo(base, exponent, modulo):
	result = 1
	for i in range(exponent):
		result = (result * base) % modulo
	return result
