import base64
import time
import hashlib
import hmac


class Guard:
	def __init__(self, secret: str) -> None:
		self.secret = secret

	@staticmethod
	def int_to_bytestring(i: int, padding: int = 8) -> bytes:
		result = bytearray()
		while i != 0:
			result.append(i & 0xff)
			i >>= 8

		return bytes(bytearray(reversed(result)).rjust(padding, b'\0'))

	@staticmethod
	def timecode():
		return int(time.time()) // 30

	def get_code(self):
		v = hmac.new(
			base64.b64decode(self.secret),
			self.int_to_bytestring(self.timecode()),
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

		for _ in range(5):
			str_code += chars[int(code % len(chars))]
			code //= len(chars)

		return str_code