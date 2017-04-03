import WELL1024
string__expanded_key = "\0"

def reversed_string(a_string):
	return a_string[::-1]


def rotate(l, n):
	return l[n:] + l[:n]


def string_xor__old(s1):
	b1 = bytearray(s1)
	# b2 = bytearray(s2)
	b = bytearray(len(s1))
	for i in range(len(b1)):
		# b[i] = b1[i] ^ b2[i]
		b[i] = b1[i] ^ 101
	# b[i] = b1[i] ^ 0
	return str(b)


def string_xor(s1, s2):
	b1 = bytearray(s1)
	b2 = bytearray(s2)
	b = bytearray(len(s1))
	for i in range(len(b1)):
		b[i] = b1[i] ^ b2[i % len(b2)]
	return str(b)


def encrypt(s1, string__expanded_key):
	return reversed_string(string_xor(s1, string__expanded_key))


def decrypt(s1, string__expanded_key):
	return reversed_string(string_xor(s1, string__expanded_key))

# TODO Get the PRNG code.
