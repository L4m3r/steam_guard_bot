import base64
import hashlib
import hmac
import time
from steam_totm.guard import Guard

def int_to_bytestring(i: int, padding: int = 8) -> bytes:
	result = bytearray()
	while i != 0:
		result.append(i & 0xFF)
		i >>= 8

	return bytes(bytearray(reversed(result)).rjust(padding, b'\0'))

def timecode():
    return int(time.time()) // 30

def code(secret) -> str:

	v = hmac.new(
		base64.b64decode(secret),
		int_to_bytestring(timecode()),
		hashlib.sha1
	).digest()
	hmac_hash = bytearray(v)
	offset = hmac_hash[19] & 0xf
	code = ((hmac_hash[offset] & 0x7f) << 24 |
			(hmac_hash[offset + 1] & 0xff) << 16 |
			(hmac_hash[offset + 2] & 0xff) << 8 |
			(hmac_hash[offset + 3] & 0xff))

	chars = "23456789BCDFGHJKMNPQRTVWXY"
	code = int(code)
	str_code = ''

	for i in range(5):
		str_code += chars[int(code % len(chars))]
		code //= len(chars)

	return str_code



accs = {
	'stanaslove': '+TP5j1N5O4agsxCMWMEX/PRM9Z4=',
	'sobolek38': 'yFYoT3RSxF+oy/gfh0MhkpdtbmM=',
	'alexandr0ff1': 'iWyk8ryQ5vqLEYgJ5GUjy48uBHY='
}

for acc in accs.keys():
	g = Guard(accs[acc])
	print(f'{acc}: {g.get_code()}')




