import qrcode

def generate_qr(text, filename):
    img = qrcode.make(text)
    img.save(f"{filename}.png")

generate_qr('https://example.com', 'my_qr_code')