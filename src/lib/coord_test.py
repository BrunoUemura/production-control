import cv2
import numpy as np

default_color = "\033[0m"
green_color = "\033[32m"
red_color = "\033[31m"
title_color = "\033[1m"
auxT=[]

# Coordinates test
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

# check errors after coordinates test
def check_errors(a, b, c, d, e, f, g):
    if a and b and c and d and e and f and g == True:
        return green_color + "Approved" + default_color
    else:       
        return red_color + " ".join(sorted(set(auxT))) + default_color
