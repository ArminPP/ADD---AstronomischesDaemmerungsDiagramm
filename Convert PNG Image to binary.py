###########################################################################################
# (C) 2025 by Armin Pressler
# Version 1.0 vom 2025-03-20
# License: MIT
###########################################################################################
#
# Helper-Funktion zum Konvertieren eines PNG-Bildes in ein binäres Array
# Die Funktion nimmt den Pfad zu einem PNG-Bild und optional einen Skalierungsfaktor entgegen
# und gibt ein binäres Array zurück, dass das Bild repräsentiert
#
#
# Siehe im Script "Astronomische Daemmerung V3.py" die Verwendung dieser Funktion:
#
# Icons als binäre Arrays
# load_icon_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR(..)'
# save_icon_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR(..)'

from PIL import Image
import io

def convert_image_to_binary_array(image_path, scale_factor=0.5):
    # Bild öffnen
    image = Image.open(image_path)
    
    # Bild skalieren
    new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
    scaled_image = image.resize(new_size, Image.LANCZOS)
    
    # Bild in binäre Daten umwandeln
    with io.BytesIO() as output:
        scaled_image.save(output, format="PNG")
        binary_data = output.getvalue()
    
    return binary_data

# Konvertieren eines PNG-Icons in ein binäres Array
save_icon_path = 'save_icon.png'
load_icon_path = 'load_icon.png'

save_icon_binary = convert_image_to_binary_array(save_icon_path)
load_icon_binary = convert_image_to_binary_array(load_icon_path)

# Ausgabe der binären Arrays
print(f"save_icon_data = {save_icon_binary}")
print(f"load_icon_data = {load_icon_binary}")