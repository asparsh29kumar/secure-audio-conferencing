import logging
import WELL1024 as prng

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s',
					datefmt='%m/%d/%Y %I:%M:%S %p',
					level=logging.DEBUG)

prng.InitWELLRNG1024a()
expanded_key = []
for i in range(30000):
	expanded_key.append(prng.WELLRNG1024a())
string__expanded_key = "".join(map(str, expanded_key))
logging.info("Generated expanded key: %s", string__expanded_key)
