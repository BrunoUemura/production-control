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

nameImagesPath = [
    'images/platesImages/Slide1.jpg',
    'images/platesImages/Slide2.jpg',
    'images/platesImages/Slide3.jpg',
    'images/platesImages/Slide4.jpg',
    'images/platesImages/Slide5.jpg',
    'images/platesImages/Slide6.jpg',
    'images/platesImages/Slide7.jpg',
    'images/platesImages/Slide8.jpg',
    'images/platesImages/Slide9.jpg',
    'images/platesImages/Slide10.jpg',
    'images/platesImages/Slide11.jpg',
    'images/platesImages/Slide12.jpg',
    'images/platesImagesError/Slide1.jpg',
    'images/platesImagesError/Slide2.jpg',
    'images/platesImagesError/Slide3.jpg',
    'images/platesImagesError/Slide4.jpg',
    'images/platesImagesError/Slide5.jpg',
    'images/platesImagesError/Slide6.jpg',
    'images/platesImagesError/Slide7.jpg',
    'images/platesImagesError/Slide8.jpg',
    'images/platesImagesError/Slide9.jpg',
    'images/platesImagesError/Slide10.jpg',
    'images/platesImagesError/Slide11.jpg',
    'images/platesImagesError/Slide12.jpg'
]
gabaritoPath = [
    "images/template/templateAB01.jpg",
    "images/template/templateAB02.jpg",
    "images/template/templateAC01.jpg",
    "images/template/templateAC02.jpg"
]
tolerance = 0.3
imagePath = []
imageModel = []
gabaritoModel = ""
logSystem = []
colorDefault = "\033[0m"
colorYellow = "\033[33m"
colorGreen = "\033[32m"
colorRed = "\033[31m"
colorTitle = "\033[1m"
colorPercentual = "\033[90m"

def printPercentual(type):
    if type == 0:
        print(colorPercentual + "\033[K", "[ {:<30} ] {}%\033[0m".format("." * round((imageIndex * (30 / len(nameImagesPath)))), round((imageIndex * (100 / len(nameImagesPath))))), end="\r") #barrinha de porcentagem
    elif type == 1:
        print(colorPercentual + "\033[K", "[ {:<30} ] {}%\033[0m".format("." * round((imageIndex * (30 / len(imagePath)))), round((imageIndex * (100 / len(imagePath))))), end="\r") # carregamento iniciado

def printPercentualFull(type):
    if type == 0:        
        print(colorPercentual + "\033[K", "[ {:<30} ] {}%\033[0m\n\n".format("." * 30, 100), end="\r") #carregamento em 100%    
    elif type == 1:
        print(colorPercentual + "\033[K", "[ {:<30} ] {}%\033[0m\n\n".format("." * 30, 100), end="\r") # termina contador em 100%

def showResults():  
    width = 30+15  
    print("-" * width)
    for i in range(0, len(nameImagesPath)):
        print("{:<30} {:^15}".format(
            nameImagesPath[i][11:].replace("/", "").replace(".jpg", ""), 
            logSystem[i]
        ))
    print("-" * width)
    print("\n\n")

os.system('cls' if os.name == 'nt' else 'clear')
print(colorTitle + 'Processando imagens, por favor aguarde!' + colorDefault)

for imageIndex in range(0, len(nameImagesPath)):
    printPercentual(0)    
    cv2.destroyAllWindows()
    archivePath=nameImagesPath[imageIndex] #lê archivePath de acordo com o ciclo for
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
    recorte = originalBackupRotacionada[yi:yf,xi:xf]
    # se a imagem não estiver com o tamanho correto corrija
    if recorte.shape[0] != 295: 
        recorte = originalBackupRotacionada[yi-4:yf,xi:xf]
    cv2.imwrite("Recorte-%s"%nameImagesPath[imageIndex].replace("/", "-"), recorte) #salva no disco    
    #limitando os caracteres e o tamanho de letra para 3
    custom_config = r'-c tessedit_char_whitelist=ABC012 --psm 3' 
    # realizando a leitura do código
    plateText = pytesseract.image_to_string("Recorte-%s"%nameImagesPath[imageIndex].replace("FotosPlacasComErro/", "FotosPlacasComErro-").replace("FotosPlacas/", "FotosPlacas-"), config=custom_config).replace(" ", "").replace("\n","")
    imagePath.append("Recorte-%s"%nameImagesPath[imageIndex].replace("FotosPlacasComErro/", "FotosPlacasComErro-").replace("FotosPlacas/", "FotosPlacas-")) #adicionando a lista o caminho da imagem
    imageModel.append(plateText[:4]) # fatiamento do texto para evitar caracteres indesejados

printPercentualFull(0)
print(colorTitle + "Analisando modelos de placa!" + colorDefault)

for imageIndex in range(0, len(imagePath)):    
    printPercentual(1)

    duplicate = cv2.imread(imagePath[imageIndex].replace("FotosPlacasComErro/", "FotosPlacasComErro-").replace("FotosPlacas/", "FotosPlacas-")) #imagem a comparar
    model = imageModel[imageIndex] #modelo para comparar
    #definindo qual modelo utilizar no loop
    if imageModel[imageIndex] == "AB01":
        gabaritoModel = gabaritoPath[0]
    elif imageModel[imageIndex] == "AB02":
        gabaritoModel = gabaritoPath[1]
    elif imageModel[imageIndex] == "AC01":
        gabaritoModel = gabaritoPath[2]
    elif imageModel[imageIndex] == "AC02":
        gabaritoModel = gabaritoPath[3]
    #leitura do gabarito
    gabaritoImage = cv2.imread(gabaritoModel)
    #subtraindo as duas imagens para zerar os pixels de cores iguais
    difference = gabaritoImage - duplicate
    b, g, r = cv2.split(difference)
    # pintando pixel de vermelho
    for y in range (0,gabaritoImage.shape[0],1):
        for x in range (0,gabaritoImage.shape[1],1):
            if b[y,x] > 255*tolerance or g[y,x] > 255*tolerance or r[y,x] > 255*tolerance:
            #if b[y,x] !=0 or g[y,x] !=0 or r[y,x] !=0:
                duplicate [y,x]=(0,0,255)
    if cv2.countNonZero(b) != 0 or cv2.countNonZero(g) != 0 or cv2.countNonZero(r) != 0:        
        auxT=[] #auxiliar temporaria de mensagem
        aux="" #auxiliar para concatenação de mensagens

        # função para teste de coordenadas
        def coordTest(x_coord,y_coord, message, invertPos, duplicate): 
            x=x_coord
            y=y_coord 
            if invertPos == True:
                (b,g,r) = duplicate[x,y]
            else:               
                (b,g,r) = duplicate[y,x]
            #cv2.circle(duplicate, (y,x), 1, (0, 255, 0), -1)
            # se vermelho no ponto x:y , existe erros na imagem
            if (b==0 and g==0 and r==255): 
                auxT.append(message)
                return False                     
            else: # caso não tenha pontos vermelhor, é aceitavel
                return True

        # placas de modelo ...
        if model == "AB01": 
            a = coordTest(80,  80,  "Q", False, duplicate)
            b = coordTest(65,  55,  "Q", False, duplicate)
            c = coordTest(95,  110, "Q", False, duplicate)
            d = coordTest(235, 300, "R", True,  duplicate)
            e = coordTest(210, 400, "R", True,  duplicate)
            f = coordTest(100, 400, "E", True,  duplicate)
            g = coordTest(195, 500, "R", True,  duplicate)

            #se não tiver erros
            if a and b and c and d and e and f and g == True:
                aux = colorGreen + "Aceitavel" + colorDefault
            else:       
                aux = colorRed + " ".join(sorted(set(auxT))) + colorDefault        
            logSystem.append(aux) #adiciona a mensagem a lista de logSystem

        if model == "AB02":
            a = coordTest(125, 119, "Q", False, duplicate)
            b = coordTest(150, 90,  "Q", False, duplicate)
            c = coordTest(175, 63,  "Q", False, duplicate)
            d = coordTest(125, 284, "R", True,  duplicate)
            e = coordTest(150, 400, "R", True,  duplicate)
            f = coordTest(175, 500, "R", True,  duplicate)

            if a and b and c and d and e and f == True:
                aux = colorGreen + "Aceitavel" + colorDefault
            else:
                aux = colorRed + " ".join(sorted(set(auxT))) + colorDefault 
            logSystem.append(aux)

        if model == "AC01":
            a = coordTest(220, 110, "Q", False, duplicate)
            b = coordTest(195, 85,  "Q", False, duplicate)
            c = coordTest(100, 85,  "E", False, duplicate)
            d = coordTest(245, 135, "Q", False, duplicate)
            e = coordTest(55,  455, "R", True,  duplicate)
            f = coordTest(150, 430, "R", True,  duplicate)
            g = coordTest(235, 405, "R", True,  duplicate)
            
            if a and b and c and d and e and f and g == True:
                aux = colorGreen + "Aceitavel" + colorDefault
            else:
                aux = colorRed + " ".join(sorted(set(auxT))) + colorDefault 
            logSystem.append(aux)

        if model == "AC02":
            a = coordTest(160, 180, "Q", False, duplicate)
            b = coordTest(125, 260, "Q", False, duplicate)
            c = coordTest(125, 100, "E", False, duplicate)
            d = coordTest(175, 310, "Q", True,  duplicate)
            e = coordTest(55,  460, "E", True,  duplicate)
            f = coordTest(150, 435, "R", True,  duplicate)
            g = coordTest(245, 410, "R", True,  duplicate)
            
            if a and b and c and d and e and f and g == True:
                aux = colorGreen + "Aceitavel" + colorDefault
            else:
                aux = colorRed + " ".join(sorted(set(auxT))) + colorDefault 
            logSystem.append(aux)

    cv2.imwrite("Draw-%s"%nameImagesPath[imageIndex].replace("/", "-"), duplicate) #salva no disco
    #cv2.imshow("Original-%d-%s"%(imageIndex, gabaritoModel), gabaritoImage)
    #cv2.imshow("Duplicate-%d-%s"%(imageIndex, gabaritoModel), duplicate)
    cv2.waitKey(0) #aguardo uma tecla para continuar
    cv2.destroyAllWindows() #fecha todas as janelas

printPercentualFull(1)
print(colorTitle + "Resultados" + colorDefault)
# imprime resultados
showResults()