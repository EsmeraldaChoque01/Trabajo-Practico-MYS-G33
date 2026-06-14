import random
import numpy as np
import math
from collections import deque
import matplotlib.pyplot as plt
import scipy.stats as stats
# --------------------------------------------- EJERCICIO 1)A)  -------------------------------------------------------------------------

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
            #encolar con politica
                if len(cola_S1) < len(cola_S2) or len(cola_S1) == len(cola_S2):    
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

# --------------------------------------------------- EJERCICIO 1) B ) --------------------------------------------------------------
R = 10000
N = 10000

promedios = []
prop_s1 = []
prop_s2 = []
promedios_cola1 = []
promedios_cola2 = []

# como los tiempos de clientes no son independientes, realizamos  10mil muestras independientes de 10mil simulaciones cada una.  
for _ in range(R):

    Numero_Arribos, Salidas, Arribos, Clientes_atendidosS1, Clientes_atendidosS2, prom_cola1, prom_cola2  = simular_sistema_servidores(N)

    tiempos = []

    for cliente in Arribos:
        tiempos.append(Salidas[cliente] - Arribos[cliente])

    promedios.append(np.mean(tiempos))

    prop_s1.append(Clientes_atendidosS1 / Numero_Arribos)
    prop_s2.append(Clientes_atendidosS2 / Numero_Arribos)

    promedios_cola1.append(prom_cola1)
    promedios_cola2.append(prom_cola2)

media = np.mean(promedios)
s = np.std(promedios, ddof=1)

error = 1.96 * s / math.sqrt(R)

LI = media - error
LS = media + error

print("Estimación:", media)
print("IC95%:", (LI, LS))

media_p1 = np.mean(prop_s1)
media_p2 = np.mean(prop_s2)

print("Proporción promedio S1:", media_p1)
print("Proporción promedio S2:", media_p2)

media_long_cola1 = np.mean(promedios_cola1)
media_long_cola2 = np.mean(promedios_cola2)

print("Promedio de la longitud de la cola 1:", media_long_cola1)
print("Promedio de la longitud de la cola 2:", media_long_cola2)

# --------------------------------------------------- EJERCICIO 1) C ) --------------------------------------------------------------

#Grafico del histograma

tiempo_permanencia = []
simulaciones = simular_sistema_servidores(10000)
for  ts, ta in zip(simulaciones[1], simulaciones[2]):
  tiempo_permanencia.append(ts- ta)

fig, ax = plt.subplots()
ax.hist(tiempo_permanencia, bins=50, color='m', edgecolor='black', alpha=0.7)
plt.title("Histograma de tiempos de permanencia")
plt.xlabel("Tiempo de permanencia")
plt.ylabel("Frecuencia", rotation=0, labelpad=30)
plt.show()

#Propuesta de distribuciones teoricas:
frecuencias_obs, extremos = np.histogram(tiempo_permanencia, bins=5)

#GAMMA:
#Estimacion de parametros alfa y beta a partir de la muestra de datos
m_est = np.mean(tiempo_permanencia)
var_est = np.var(tiempo_permanencia, ddof=1)
alfa_est = m_est**2 / var_est
beta_est = var_est / m_est

#Calculo de las probabilidades teoricas
probs_est = []
for i in range(len(frecuencias_obs)):
  prob_i_est = stats.gamma.cdf(extremos[i+1], a=alfa_est, scale=beta_est) - stats.gamma.cdf(extremos[i], a=alfa_est, scale=beta_est)
  probs_est.append(prob_i_est)

#Conteo de las frecuecias observadas en la muestra de datos
Ni_obs = [val for val in frecuencias_obs]

#Construccion del estadistico T
n = len(tiempo_permanencia)
T = 0
for i in range(len(Ni_obs)):
  T += ((Ni_obs[i] - n*probs_est[i])**2) / (n*probs_est[i])
    
#Calculo del p-valor usando simulaciones
p_valor = 0
for sim in range(1000):
  muestra_sim = np.random.gamma(alfa_est, beta_est, size=10000)
  m = len(muestra_sim)
  frecuencias_sim, extremos_sim= np.histogram(muestra_sim, bins=5)

  m_sim = np.mean(muestra_sim)
  var_sim = np.var(muestra_sim, ddof=1)

  alfa_sim = m_sim**2 / var_sim
  beta_sim = var_sim / m_sim

  probs_sim = []
  for i in range(len(frecuencias_sim)):
    prob_i_sim = stats.gamma.cdf(extremos_sim[i+1], a=alfa_sim, scale=beta_sim) - stats.gamma.cdf(extremos_sim[i], a=alfa_sim, scale=beta_sim)
    probs_sim.append(prob_i_sim)
  
  Ni_sim = [val for val in frecuencias_sim]

  T_sim = 0
  for i in range(len(Ni_sim)):
    T_sim += ((Ni_sim[i] - m*probs_sim[i])**2) / (m*probs_sim[i])
  if T_sim > T:
    p_valor += 1
print(f"El p-valor es: {p_valor/1000}")

#EXPONENCIAL
#Estimacion del parametro lambda
m_est = np.mean(tiempo_permanencia)
lambda_est = 1/m_est

#Calculo de probabilidades
probs_est = []
for i in range(len(frecuencias_obs)):
  prob_i_est = stats.expon.cdf(extremos[i+1], scale=1/lambda_est) - stats.expon.cdf(extremos[i], scale=1/lambda_est)
  probs_est.append(prob_i_est)

#Frecuencias observadas
Ni_obs = [val for val in frecuencias_obs]

#Estadistico T
T = 0
for i in range(len(Ni_obs)):
  T += ((Ni_obs[i] - len(tiempo_permanencia)*probs_est[i])**2) / (len(tiempo_permanencia)*probs_est[i])
print(T)

#Calculo del p-valor con simulaciones
p_valor = 0
for sim in range(10000):
  muestra_sim = np.random.exponential(scale=1/lambda_est, size=10000)
  lamda_sim = 1/np.mean(muestra_sim)
  m = len(muestra_sim)
  frecuencias_sim, extremos_sim= np.histogram(muestra_sim, bins=5)
  probs_sim = []
  for i in range(len(frecuencias_sim)):
    prob_i_sim = stats.expon.cdf(extremos_sim[i+1], scale=1/lamda_sim) - stats.expon.cdf(extremos_sim[i], scale=1/lamda_sim)
    probs_sim.append(prob_i_sim)
  
  Ni_sim = [val for val in frecuencias_sim]

  T_sim = 0
  for i in range(len(Ni_sim)):
    T_sim += ((Ni_sim[i]-m*probs_sim[i])**2) / (m*probs_sim[i])
  
  if T_sim > T:
    p_valor += 1

print(f"El p-valor es: {p_valor/10000}")

