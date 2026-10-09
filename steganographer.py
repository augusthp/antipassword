'''
The code in this file is based on the GeeksForGeeks page cited in our report.
'''

from PIL import Image


def formatInput(data):
    '''
    formatInput takes provided input and converts it from unicode characters to 
    a list of 8-bit binary strings. 
    @param data: the string to convert to binary
    '''
    return [format(ord(char), '08b') for char in data]

def modifyPixel(pixel, data):
    '''
    modifyPixel encodes a list of binary strings in the least-significant bits of
    the pixel object, overwriting their data. The difference in the modified pixel
    is imperceptible to the human eye - pixels with RGB values of 255,0,0 and 254,1,1
    are not different to register visually, especially since the process works on the 
    level of individual pixels. The binary string to encode is 8-bits long, and the RGB
    data has 9 LSB's in total; the final LSB contains a flag to indicate whether the 
    string has finished and the process is complete or if we need to continue.
    @param pixel: a tuple containing pixel values
    @param data: the information to encode in the image
    '''
    bin_data = formatInput(data)
    length = len(bin_data)
    imdata = iter(pixel)

    for i in range (length):
        # collect a list of the next 3 pixels
        pixels = [val for val in next(imdata)[:3] + next(imdata)[:3] + next(imdata)[:3]] 

        # encode one binary string in the least-significant bits of these 3 pixels; 8 of 9 lsbs modified here
        for j in range(8):
            if bin_data[i][j] == '0' and pixels[j] % 2 != 0:
                pixels[j] -= 1
            elif bin_data[i][j] == '1' and pixels[j] % 2 == 0:
                if pixels[j] != 0:
                    pixels[j] = pixels[j] - 1  
                else: 
                    pixels[j] + 1

        # encode termination flag in final lsb: even is continue, odd is stop
        if i == length - 1:
            pixels[-1] |= 1
        else:
            pixels[-1] &= ~1

        # output the three modified pixels as tuples
        yield tuple(pixels[:3])
        yield tuple(pixels[3:6])
        yield tuple(pixels[6:9])

def encodeModified(new_img, data):
    '''
    encodeModified controls the overall encoding process. It keeps track of our
    pixel position in the modified image and handles the actual modification of 
    RGB values, modifying the least-significant bits.
    @param new_img: the Image object that will contain the modified data
    @param data: the data to be encoded
    '''
    # Encodes modified pixel data into a new image
    w = new_img.size[0]
    (x,y) = (0,0)

    for pixel in modifyPixel(new_img.get_flattened_data(), data):
        new_img.putpixel((x,y), pixel)
        if x == w - 1:
            x = 0
        else:
            x += 1
        if x == 0:
            y += 1
        else:
            y = 0

def encode(img):
    # Collects necessary user input to encode a file; used for setup but not needed for password decryption process
    image = Image.open(img, 'r')
    data = input("Enter key to be encoded: ")

    if not data: 
        raise ValueError("Data not collected")

    new_img = image.copy()
    encodeModified(new_img, data)
    new_img_name = input("Enter the name of the new image with extension: ")
    new_img.save(new_img_name, new_img_name.split(".")[-1].upper())

def decode(img):
    '''
    decode undoes the operations performed in encodeModified, retrieving the 
    encoded data.
    @param img: the image filename containing encoded data
    '''
    image = Image.open(img, 'r')
    img_data = iter(image.get_flattened_data())
    data = ""

    while True:
        pixels = [value for value in next(img_data)[:3] + next(img_data)[:3] + next(img_data)[:3]]
        bin_str = ''.join(['1' if i % 2 else '0' for i in pixels[:8]])
        data += chr(int(bin_str, 2))

        if pixels[-1] % 2 != 0:
            break

    return data

def retrieve_data():
        # Wrapper function to collect input needed for password process
        img = input("Enter the filename for your campus's image, including extension: ")
        try:
            return decode(img)
        except FileNotFoundError:
            print('Filename "' + img + '" not found, try again.')