def reversed_string(a_string):
	return a_string[::-1]


def rotate(l, n):
	return l[n:] + l[:n]


# TODO Rename me.
def sxor(s1):
	b1 = bytearray(s1)
	# b2 = bytearray(s2)
	b = bytearray(len(s1))
	for i in range(len(b1)):
		# b[i] = b1[i] ^ b2[i]
		# b[i] = b1[i] ^ 101
		b[i] = b1[i] ^ 0
	return str(b)

# TODO Create individual functions to encrypt and decrypt. Let them call sxor.
