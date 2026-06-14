import random
import numpy as np
import math
from collections import deque
#import matplotlib.pyplot as plt
import scipy.stats as stats
# --------------------------------------------- EJERCICIO 2)A)  -------------------------------------------------------------------------

#generacion de eventos usando poisson con adelgazamiento:

def funlanmda (t_actual):
    x = t_actual%12
    if x < 4:
        return 5
    if 4 <= x < 8:
        return 7
    if 8 <= x < 12:
        return 11

def Generar_Tiempo_Cliente(t_Actual):
    t_actual = t_Actual
    while True:
        v = random.random()
        if v < funlanmda(t_actual) / 11: #11 lanmda_max
            t_actual = t_actual - math.log(1 - random.random()) / 11 #T actual 
            return t_actual


#generacion de tiempo de atencion con var Generar_Tiempo_Cliente:

def Tiempo_de_Servicio(lamda):
    U = 1-random.random()
    return -math.log(U)/lamda


#Simulacion del sistema con 2 servicores trabajando en paralelo:

def simular_sistema_servidores(NumSim):
#Inicializacion de las variables

    t_actual = Numero_Arribos = Clientes_atendidosS1 = Clientes_atendidosS2 = 0
    En_el_Sistema = i1 = i2 = 0
    tiempo_Arribo = Generar_Tiempo_Cliente(t_actual)
    t_actual = tiempo_Arribo
    tiempo_S1 = tiempo_S2 = math.inf
    cola_S1 = deque() 
    cola_S2 = deque()
    Arribos = {}
    Salidas = {}
    area_cola1 = area_cola2 = 0
    tiempo_anterior = 0
    promedio_cola1 = promedio_cola2 = 0 

    while tiempo_Arribo < math.inf or tiempo_S1 < math.inf or tiempo_S2 < math.inf:
        eventoProximo = min (tiempo_Arribo, tiempo_S1, tiempo_S2)   

        #calculo de area de las colas:

        delta = eventoProximo - tiempo_anterior
        area_cola1 += len(cola_S1) * delta
        area_cola2 += len(cola_S2) * delta

        tiempo_anterior = eventoProximo

#Si el evento proximo es el arribo de un cliente:

        if tiempo_Arribo == eventoProximo:
            t_actual = tiempo_Arribo  
            Numero_Arribos += 1
            tiempo_Arribo = Generar_Tiempo_Cliente(t_actual) 

            if Numero_Arribos == NumSim: #Al llegar al numero de simulaciones paramos de generar clientes
                tiempo_Arribo = math.inf

         #si el Servidor 1 esta vacio:

            if i1 == 0:                    
                i1 =  Numero_Arribos          #atender al cliente numero x
                tiempo_servicio = Tiempo_de_Servicio(12) #5min = E[x] -> 5/60horas -> lanmda =60/5 = 12
                tiempo_S1 = t_actual + tiempo_servicio

        #Si el Servidor 2 esta vacio:

            elif i2 == 0:
                i2 =  Numero_Arribos
                tiempo_servicio = Tiempo_de_Servicio(60/7)  #7min = E[x] -> lanmda = 60/7
                tiempo_S2 = t_actual + tiempo_servicio

        #Si los dos Servidores estan ocupados:

            else:                                           
            #encolar con politica 2
                if (tiempo_S1 - t_actual) + len(cola_S1) * (5/60) <= (tiempo_S2 - t_actual) + len(cola_S2) * (7/60):    
                    cola_S1.append(Numero_Arribos)
        
                else: 
                    cola_S2.append(Numero_Arribos)
                

            En_el_Sistema = En_el_Sistema + 1
            Arribos[Numero_Arribos] = t_actual

#si el evento es fin de atencion a un cliente en el servidor 1:

        elif eventoProximo == tiempo_S1: 
            t_actual = tiempo_S1
            Clientes_atendidosS1 += 1
            En_el_Sistema = En_el_Sistema - 1
            clienteSaliente = i1

        # Si hay clientes en la cola del servidor1:
          
            if len(cola_S1) != 0:
                i1 = cola_S1.popleft()
                tiempo_servicio = Tiempo_de_Servicio(12)
                tiempo_S1 = t_actual + tiempo_servicio

            else:
                i1 = 0
                tiempo_S1 = math.inf

            Salidas[clienteSaliente] = t_actual

# si el evento es fin de atencion a un cliente en el Servidor 2:

        else:
            t_actual = tiempo_S2
            Clientes_atendidosS2 += 1
            En_el_Sistema = En_el_Sistema - 1
            clienteSaliente = i2
        
        #Si hay clientes en la cola del servidor2:

            if len(cola_S2) != 0:
                i2 = cola_S2.popleft()
                tiempo_servicio = Tiempo_de_Servicio(60/7)
                tiempo_S2 = t_actual + tiempo_servicio

            else:
                i2 = 0
                tiempo_S2 = math.inf

            Salidas[clienteSaliente] = t_actual
    
    #calculo del promedio de las colas:

    promedio_cola1 = area_cola1 / tiempo_anterior
    promedio_cola2 = area_cola2 / tiempo_anterior

    return Numero_Arribos, Salidas, Arribos, Clientes_atendidosS1, Clientes_atendidosS2, promedio_cola1, promedio_cola2

# --------------------------------------------------- EJERCICIO 2) B ) --------------------------------------------------------------
R = 10000
N = 10000

promedios = []
prop_s1 = []
prop_s2 = []
promedios_cola1 = []
promedios_cola2 = []

# como los tiempos de clientes no son independientes, realizamos  10mil muestras independientes de 10mil simulaciones cada una.  
for _ in range(R):

    Numero_Arribos, Salidas, Arribos, Clientes_atendidosS1, Clientes_atendidosS2, prom_cola1, prom_cola2 = simular_sistema_servidores(N)

    tiempos = []

    for cliente in Arribos:
        tiempos.append(Salidas[cliente] - Arribos[cliente])

    promedios.append(np.mean(tiempos))

    prop_s1.append(Clientes_atendidosS1 / Numero_Arribos)
    prop_s2.append(Clientes_atendidosS2 / Numero_Arribos)

    promedios_cola1.append(prom_cola1)
    promedios_cola2.append(prom_cola2)

media = np.mean(promedios)

print("Estimación:", media)


media_p1 = np.mean(prop_s1)
media_p2 = np.mean(prop_s2)

print("Proporción promedio S1:", media_p1)
print("Proporción promedio S2:", media_p2)

media_long_cola1 = np.mean(promedios_cola1)
media_long_cola2 = np.mean(promedios_cola2)

print("Promedio de la longitud de la cola 1:", media_long_cola1)
print("Promedio de la longitud de la cola 2:", media_long_cola2)
