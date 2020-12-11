#Generate QR Code
import pyqrcode
import sys # for argument(sys.argv)

qr = pyqrcode.create('www.google.com')
qr.png('abd.png', scale=8)

#Read QR Code
from pyzbar.pyzbar import decode
from PIL import Image

d = decode(Image.open('abd.png'))

print(d)
print(d[0].data.decode('ascii'))