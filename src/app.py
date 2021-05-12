import cv2
import numpy as np
from matplotlib import pyplot as plt
from sys import argv
import math
import os
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
    'platesImagesError/Slide8.jpg',
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
color_default = "\033[0m"
color_green = "\033[32m"
color_red = "\033[31m"
color_title = "\033[1m"

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

def show_results():  
    width = 30+15  
    print("-" * width)
    for i in range(0, len(images_path)):
        print("{:<30} {:^15}".format(
            images_path[i][11:].replace("/", "").replace(".jpg", ""), 
            output_message[i]
        ))
    print("-" * width)
    print("\n\n")

os.system('cls' if os.name == 'nt' else 'clear')
print(color_title + 'Processing images...' + color_default)

for imageIndex in range(0, len(images_path)):
    cv2.destroyAllWindows()
    archivePath=images_path[imageIndex] #lê archivePath de acordo com o ciclo for
    original = cv2.imread(archivePath) #colorida
    originalBackup = cv2.imread(archivePath) #colorida
    img = cv2.imread(archivePath,0) #monocromática = binária
    (height, width) = img.shape[:2] #captura altura e largura
    ret, imgT = cv2.threshold(img, 230, 255, cv2.THRESH_BINARY)#230

    # descobrindo a inclinação da imagem
    p1=0
    p2=0
    xi=width
    inc=0
    for y in range (0,height,1):
        for x in range (0,width,1):
            cor = imgT[y,x] 
            if cor!=255 and(p1==0): 
                ponto1=(x,y)
                xi=x
                p1=1
                if x>(width/2):
                    inc=1 # para saber se a inclinação é positiva ou negativa                            
            if (p1==1) and (inc==1) and (cor!=255) and (x<xi):
                ponto2=(x,y)
                xi=x                
            if (p1==1) and (inc==0) and (cor!=255) and (x>xi):
                ponto2=(x,y)
                xi=x
    cv2.circle(original, (ponto1), 2, (0, 0, 255), -1)
    cv2.circle(original, (ponto2), 2, (0, 0, 255), -1)
    #cv2.imshow("Imagem original com marcações", original)
                        
    angulo = math.atan2 (ponto1[1]-ponto2[1],ponto1[0]-ponto2[0])
    if inc==1:
        angulo = math.degrees(angulo)
    if inc==0:
        angulo = math.degrees(angulo)+180
        aux=ponto1
        ponto1=ponto2
        ponto2=aux        

    # girando a imagem monocromatica          
    M = cv2.getRotationMatrix2D(ponto1, angulo, 1.0) 
    imgRotacionada = cv2.warpAffine(imgT, M, (width, height))
    # girando a imagem original  
    originalRotacionada = cv2.warpAffine(original, M, (width, height))
    # girando a originalBackup  
    originalBackupRotacionada = cv2.warpAffine(originalBackup, M, (width, height))
    # cortando a imagem original
    pontoInicial=ponto1
    larguraPlaca = 602
    alturaPlaca = 295
    xi=pontoInicial[0]-larguraPlaca+1
    xf=pontoInicial[0]+1
    yi=pontoInicial[1]
    yf=pontoInicial[1]+alturaPlaca
    cut = originalBackupRotacionada[yi:yf,xi:xf]
    # se a imagem não estiver com o tamanho correto corrija
    if cut.shape[0] != 295: 
        cut = originalBackupRotacionada[yi-4:yf,xi:xf]
    cv2.imwrite("cutResult/cut-%s"%images_path[imageIndex].replace("/", "-"), cut) #salva no disco    
    #limitando os caracteres e o tamanho de letra para 3
    custom_config = r'-c tessedit_char_whitelist=ABC012 --psm 3' 
    # realizando a leitura do código
    plateText = pytesseract.image_to_string("cutResult/cut-%s"%images_path[imageIndex].replace("platesImagesError/", "platesImagesError-").replace("platesImages/", "platesImages-"), config=custom_config).replace(" ", "").replace("\n","")
    images_align.append("cutResult/cut-%s"%images_path[imageIndex].replace("platesImagesError/", "platesImagesError-").replace("platesImages/", "platesImages-")) #adicionando a lista o caminho da imagem
    plate_model.append(plateText[:4]) # fatiamento do texto para evitar caracteres indesejados
    
print(color_green + "OK\n" + color_default)
print(color_title + "Analyzing plates model..." + color_default)

for imageIndex in range(0, len(images_align)):    

    duplicate = cv2.imread(images_align[imageIndex].replace("platesImagesError/", "platesImagesError-").replace("platesImages/", "platesImages-")) #imagem a comparar
    model = plate_model[imageIndex] #modelo para comparar
    #definindo qual modelo utilizar no loop
    if plate_model[imageIndex] == "AB01":
        gabaritoModel = template_path[0]
    elif plate_model[imageIndex] == "AB02":
        gabaritoModel = template_path[1]
    elif plate_model[imageIndex] == "AC01":
        gabaritoModel = template_path[2]
    elif plate_model[imageIndex] == "AC02":
        gabaritoModel = template_path[3]
    
    #leitura do gabarito
    gabaritoImage = cv2.imread(gabaritoModel)

    #subtraindo as duas imagens para zerar os pixels de cores iguais
    difference = gabaritoImage - duplicate
    b, g, r = cv2.split(difference)
    
    # pintando pixel de vermelho
    for y in range (0,gabaritoImage.shape[0],1):
        for x in range (0,gabaritoImage.shape[1],1):
            if r[y,x] > 255*tolerance:
                duplicate [y,x]=(0,0,255)
            if g[y,x] > 255*tolerance:
                duplicate [y,x]=(0,0,255)
            if b[y,x] > 255*tolerance:
                duplicate [y,x]=(0,0,255)

    if cv2.countNonZero(b) != 0 or cv2.countNonZero(g) != 0 or cv2.countNonZero(r) != 0:        
        auxT=[] #auxiliar temporaria de mensagem
        aux="" #auxiliar para concatenação de mensagens

        # placas de modelo ...
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
            if a and b and c and d and e and f and g == True:
                aux = color_green + "Approved" + color_default
            else:       
                aux = color_red + " ".join(sorted(set(auxT))) + color_default        
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

            if a and b and c and d and e and f == True:
                aux = color_green + "Approved" + color_default
            else:
                aux = color_red + " ".join(sorted(set(auxT))) + color_default 
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
            
            if a and b and c and d and e and f and g == True:
                aux = color_green + "Approved" + color_default
            else:
                aux = color_red + " ".join(sorted(set(auxT))) + color_default 
            output_message.append(aux)

        if model == "AC02":
            a = coord_test(160, 180, "SQUARE", False, duplicate)
            b = coord_test(125, 260, "SQUARE", False, duplicate)
            c = coord_test(125, 100, "ERROR", False, duplicate)
            d = coord_test(175, 310, "SQUARE", True,  duplicate)
            e = coord_test(55,  460, "ERROR", True,  duplicate)
            f = coord_test(150, 435, "RECTANGLE", True,  duplicate)
            g = coord_test(245, 410, "RECTANGLE", True,  duplicate)
            
            if a and b and c and d and e and f and g == True:
                aux = color_green + "Approved" + color_default
            else:
                aux = color_red + " ".join(sorted(set(auxT))) + color_default 
            output_message.append(aux)
    
    
    cv2.imwrite("drawResult/Draw-%s"%images_path[imageIndex].replace("/", "-"), duplicate) #salva no disco
    # cv2.imshow("Original-%d-%s"%(imageIndex, gabaritoModel), gabaritoImage)
    cv2.imshow("Duplicate-%d-%s"%(imageIndex, gabaritoModel), duplicate)
    # cv2.waitKey(0)
    cv2.destroyAllWindows()

print(color_green + "OK\n" + color_default)
print(color_title + "Results" + color_default)

# Show the results
show_results()