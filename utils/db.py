import bcrypt
import dotenv
import os

dotenv.load_dotenv(override = True)

BASEURL = "https://nationserver.vercel.app/static"
basepath = os.getenv('BASEPATH')
dbpath = os.path.join(basepath, "database")
logpath = os.path.join(basepath, "logs")
drivepath = os.path.normpath(os.getenv('DRIVEPATH'))

salt: bytes = b''

try:
	with open(".local/.salt", "rb") as _buffer:
		salt = _buffer.read()
except:
	with open(".local/.salt", "wb") as _buffer:
		if not os.path.exists('.local'):
			os.mkdir('.local')

		salt = bcrypt.gensalt()
		_buffer.write(salt)