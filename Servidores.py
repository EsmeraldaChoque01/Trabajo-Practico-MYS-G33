import random
import numpy as np
import math
from collections import deque

#generacion de eventos
def Poisson_adelgazamiento_mejorado(T):
    interv = [4,8,12] #T<=6
    lamda = [5, 11, 7]
    j = 0 #recorre subintervalos.
    t = -math.log ( 1 - random.random() ) / lamda[j]
    Eventos = []
    while t <= T:
        if t <= interv[j]:
            Eventos.append(t)
            t += -math.log(1 - random.random()) / lamda[j]
        else: #t > interv[j]
            t = interv[j] + (t - interv[j]) * lamda[j] / lamda[j + 1]
            j += 1
    return Eventos

#generacion de tiempo de atencion con var exp

def exponencial(lamda):
    U = 1-random.random()
    return -math.log(U)/lamda

#Inicialización:
def servidores():
    t = Numero_Arribos = Clientes_atendidosS1 = Clientes_atendidosS2 = 0
    En_el_Sistema = i1 = i2 = 0
    eventos = Poisson_adelgazamiento_mejorado(12)
    j = 0
    tiempo_Arribo = eventos[j]
    tiempo_S1, tiempo_S2 = math.inf
    cola_S1 = deque() 
    cola_S2 = deque()
    Arribos = {}
    Salidas = {}

    while tiempo_Arribo < math.inf or tiempo_S1 < math.inf or tiempo_S2 < math.inf:
        eventoProximo = min (tiempo_Arribo, tiempo_S1, tiempo_S2)   
#si el evento es un arribo  
        if tiempo_Arribo == eventoProximo:     
            t = tiempo_Arribo                  #corremos a t al tiempo del arribo
            Numero_Arribos += 1
            j += 1
            if j < len(eventos):
                tiempo_prox_arribo = eventos[j]         #tiempo del proximo arribo
                tiempo_Arribo = t + tiempo_prox_arribo
            else :
                tiempo_Arribo = math.inf  #no hay mas clientes por
            if i1 == 0:                     #si el Servidor 1 esta vacio
                i1 =  Numero_Arribos          #atender al cliente
                tiempo_servicio = exponencial(12) #5min = E[x] -> 5/60horas -> lanmda =60/5 = 12
                tiempo_S1 = t + tiempo_servicio
            elif i2 == 0:
                i2 =  Numero_Arribos
                tiempo_servicio = exponencial(60/7)  #7min = E[x] -> lanmda = 60/7
                tiempo_S2 = t + tiempo_servicio
            else:    #encolar con politica
                if len(cola_S1) < len(cola_S2) or len(cola_S1) == len(cola_S2):    
                    cola_S1.append(Numero_Arribos)
                else: 
                    cola_S2.append(Numero_Arribos)
            En_el_Sistema = En_el_Sistema + 1
            Arribos[Numero_Arribos] = t
#si el evento es fin de atencion en el servidor 1
        elif eventoProximo == tiempo_S1: 
            t = tiempo_S1
            Clientes_atendidosS1 += 1
            En_el_Sistema = En_el_Sistema - 1
            clienteSaliente = i1
# Si hay clientes en la cola del servidor1
            if len(cola_S1) != 0:
                i1 = cola_S1.popleft()
                tiempo_servicio = exponencial(12)
                tiempo_S1 = t + tiempo_servicio
            else:
                i1 = 0
                tiempo_S1 = math.inf

            Salidas[clienteSaliente] = t
# si el evento es fin de atencion en el servidor 2
        else:
            t = tiempo_S2
            Clientes_atendidosS2 += 1
            En_el_Sistema = En_el_Sistema - 1
            clienteSaliente = i2
            if len(cola_S2) != 0:
                i2 = cola_S2.popleft()
                tiempo_servicio = exponencial(60/7)
                tiempo_S2 = t + tiempo_servicio
            else:
                i2 = 0
                tiempo_S2 = math.inf
            Salidas[clienteSaliente] = t