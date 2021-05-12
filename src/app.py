import cv2
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
import math
import os
from numpy.lib.function_base import angle
from lib.format_output import format_output

try:
    from PIL import Image
except ImportError:
    import Image    
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

images_path = [
    'platesImages/Slide1.jpg',
    'platesImages/Slide2.jpg',
    'platesImages/Slide7.jpg',
    'platesImages/Slide8.jpg',
    'platesImagesError/Slide1.jpg',
    'platesImagesError/Slide2.jpg',
    'platesImagesError/Slide7.jpg',
    'platesImagesError/Slide8.jpg'
]

template_path = [
    "template/Template AB01.jpg",
    "template/Template AB02.jpg",
    "template/Template AC01.jpg",
    "template/Template AC02.jpg"
]

tolerance = 0.1
images_align = []
plate_model = []
output_message = []
default_color = "\033[0m"
green_color = "\033[32m"
red_color = "\033[31m"
title_color = "\033[1m"

# função para teste de coordenadas
def coord_test(x_coord, y_coord, message, invertPos, duplicate): 
    x=x_coord
    y=y_coord 
    if invertPos == True:
        (b,g,r) = duplicate[x,y]
    else:               
        (b,g,r) = duplicate[y,x]
    cv2.circle(duplicate, (y,x), 1, (0, 255, 0), -1)
    # se vermelho no ponto x:y , existe erros na imagem
    if (b==0 and g==0 and r==255): 
        auxT.append(message)
        return False                     
    else: # caso não tenha pontos vermelhor, é aceitável
        return True

def check_errors(a, b, c, d, e, f, g):
    if a and b and c and d and e and f and g == True:
        return green_color + "Approved" + default_color
    else:       
        return red_color + " ".join(sorted(set(auxT))) + default_color

os.system('cls' if os.name == 'nt' else 'clear')
print(title_color + 'Processing images...' + default_color)

# Align and cut the image
for imageIndex in range(0, len(images_path)):
    cv2.destroyAllWindows()
    original = cv2.imread(images_path[imageIndex]) #colorida
    original_backup = cv2.imread(images_path[imageIndex]) #colorida
    img = cv2.imread(images_path[imageIndex], 0) #monocromática = binária
    (height, width) = img.shape[:2] #captura altura e largura
    ret, imgT = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)#230

    # Image angle
    p1=0
    p2=0
    xi=width
    inc=0
    for y in range (0,height,1):
        for x in range (0,width,1):
            color = imgT[y,x] 
            if color!=255 and(p1==0): 
                point_one=(x,y)
                xi=x
                p1=1
                # Check if the inclination is positive or negative
                if x>(width/2):
                    inc=1 
            if (p1==1) and (inc==1) and (color!=255) and (x<xi):
                point_two=(x,y)
                xi=x                
            if (p1==1) and (inc==0) and (color!=255) and (x>xi):
                point_two=(x,y)
                xi=x
    cv2.circle(original, (point_one), 2, (0, 0, 255), -1)
    cv2.circle(original, (point_two), 2, (0, 0, 255), -1)
                        
    angle = math.atan2 (point_one[1]-point_two[1],point_one[0]-point_two[0])
    if inc==1:
        angle = math.degrees(angle)
    if inc==0:
        angle = math.degrees(angle)+180
        aux=point_one
        point_one=point_two
        point_two=aux        

    # Rotating the monocromatic image
    M = cv2.getRotationMatrix2D(point_one, angle, 1.0) 
    rotated_image = cv2.warpAffine(imgT, M, (width, height))
    # Rotating the original image
    original_rotated = cv2.warpAffine(original, M, (width, height))
    # Rotating the original_backup image  
    original_backup_rotated = cv2.warpAffine(original_backup, M, (width, height))
    # Currint the original image

    initial_point=point_one
    plate_width = 602
    plate_height = 295
    xi=initial_point[0]-plate_width+1
    xf=initial_point[0]+1
    yi=initial_point[1]
    yf=initial_point[1]+plate_height
    cut = original_backup_rotated[yi:yf,xi:xf]
    
    # If the image is not the correct size, a correction is made
    if cut.shape[0] != 295: 
        cut = original_backup_rotated[yi-4:yf,xi:xf]

    cv2.imwrite("cutResult/cut-%s"%images_path[imageIndex].replace("/", "-"), cut)
    
    # Creating a white list with fixed letters and letter size as 3
    white_list = r'-c tessedit_char_whitelist=ABC012 --psm 3' 
    
    # Reading the plate model text
    plate_text = pytesseract.image_to_string("cutResult/cut-%s"%images_path[imageIndex].replace("platesImagesError/", "platesImagesError-").replace("platesImages/", "platesImages-"), config=white_list).replace(" ", "").replace("\n","")
    # Adding the image path to list
    images_align.append("cutResult/cut-%s"%images_path[imageIndex].replace("platesImagesError/", "platesImagesError-").replace("platesImages/", "platesImages-"))
    plate_model.append(plate_text[:4])
    
print(green_color + "OK\n" + default_color)
print(title_color + "Analyzing plates model..." + default_color)

# Draw the image and find the errors
for imageIndex in range(0, len(images_align)):    

    duplicate = cv2.imread(images_align[imageIndex].replace("platesImagesError/", "platesImagesError-").replace("platesImages/", "platesImages-")) #imagem a comparar
    model = plate_model[imageIndex]

    # Defining what model to use
    if plate_model[imageIndex] == "AB01":
        template_model = template_path[0]
    elif plate_model[imageIndex] == "AB02":
        template_model = template_path[1]
    elif plate_model[imageIndex] == "AC01":
        template_model = template_path[2]
    elif plate_model[imageIndex] == "AC02":
        template_model = template_path[3]
    
    # Reading template
    template_image = cv2.imread(template_model)

    # Subtracting the two images colors
    difference = template_image - duplicate
    b, g, r = cv2.split(difference)
    
    # Drawing red pixel in areas that does not match
    for y in range (0,template_image.shape[0],1):
        for x in range (0,template_image.shape[1],1):
            if r[y,x] > 255*tolerance:
                duplicate [y,x]=(0,0,255)
            if g[y,x] > 255*tolerance:
                duplicate [y,x]=(0,0,255)
            if b[y,x] > 255*tolerance:
                duplicate [y,x]=(0,0,255)

    if cv2.countNonZero(b) != 0 or cv2.countNonZero(g) != 0 or cv2.countNonZero(r) != 0:        
        auxT=[]
        # Checking if the models contains error
        if model == "AB01":
            # Test if square matches the template
            a = coord_test(80,  80,  "SQUARE", False, duplicate)
            b = coord_test(65,  55,  "SQUARE", False, duplicate)
            c = coord_test(95,  110, "SQUARE", False, duplicate)

            # Test if rectangle matches the template
            d = coord_test(235, 300, "RECTANGLE", True,  duplicate)
            e = coord_test(210, 400, "RECTANGLE", True,  duplicate)
            f = coord_test(195, 500, "RECTANGLE", True,  duplicate)
            g = coord_test(100, 400, "ERROR", True,  duplicate)

            # Check if there is no error
            aux = check_errors(a, b, c, d, e, f, g)       
            output_message.append(aux) #adiciona a mensagem a lista de output_message

        if model == "AB02":
            # Test if square matches the template
            a = coord_test(125, 119, "SQUARE", False, duplicate)
            b = coord_test(150, 90,  "SQUARE", False, duplicate)
            c = coord_test(175, 63,  "SQUARE", False, duplicate)

            # Test if rectangle matches the template
            d = coord_test(125, 284, "RECTANGLE", True,  duplicate)
            e = coord_test(150, 400, "RECTANGLE", True,  duplicate)
            f = coord_test(175, 500, "RECTANGLE", True,  duplicate)
            g = coord_test(70, 400, "ERROR", True,  duplicate)

            aux = check_errors(a, b, c, d, e, f, g) 
            output_message.append(aux)

        if model == "AC01":
            # Test if square matches the template
            a = coord_test(220, 110, "SQUARE", False, duplicate)
            b = coord_test(195, 85,  "SQUARE", False, duplicate)
            c = coord_test(245, 135, "SQUARE", False, duplicate)

            # Test if rectangle matches the template
            d = coord_test(55,  455, "RECTANGLE", True,  duplicate)
            e = coord_test(150, 430, "RECTANGLE", True,  duplicate)
            f = coord_test(235, 405, "RECTANGLE", True,  duplicate)
            g = coord_test(100, 85,  "ERROR", False, duplicate)
            
            aux = check_errors(a, b, c, d, e, f, g)
            output_message.append(aux)

        if model == "AC02":
            # Test if square matches the template
            a = coord_test(160, 180, "SQUARE", False, duplicate)
            b = coord_test(125, 260, "SQUARE", False, duplicate)
            d = coord_test(175, 310, "SQUARE", True,  duplicate)
            
            # Test if rectangle matches the template
            f = coord_test(150, 435, "RECTANGLE", True,  duplicate)
            g = coord_test(245, 410, "RECTANGLE", True,  duplicate)
            
            c = coord_test(125, 100, "ERROR", False, duplicate)
            e = coord_test(55,  460, "ERROR", True,  duplicate)

            aux = check_errors(a, b, c, d, e, f, g) 
            output_message.append(aux)
    
    cv2.imwrite("drawResult/Draw-%s"%images_path[imageIndex].replace("/", "-"), duplicate) #salva no disco
    cv2.imshow("Duplicate-%d-%s"%(imageIndex, template_model), duplicate)
    # cv2.waitKey(0)
    cv2.destroyAllWindows()

print(green_color + "OK\n" + default_color)
print(title_color + "Results" + default_color)

# Show the results
format_output(images_path, output_message)