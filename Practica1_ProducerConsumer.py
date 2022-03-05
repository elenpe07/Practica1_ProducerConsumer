 # -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 10:31:53 2022

@author: Elena
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore
from multiprocessing import current_process
from multiprocessing import Array
from time import sleep
import random

N = 10
NPROD = 3


def prod_min(storage): #función para calcular el mínimo del almacén
    aux = [] #lista auxiliar 
    prod_max = max(storage) 
    for i in range(len(storage)): #vamos metiendo en la lista auxiliar los productos del almacén pero cambiando los -1 por otro que no esté en el almacén, por ejemplo el máximo + 1
        if storage[i] == -1:
            aux.append(prod_max + 1)
        else:
            aux.append(storage[i])
    prod_min = aux[0]
    pos = 0
    for i in range(len(aux)): #y calculamos el minimo comparando todos los productos
        if aux[i] < prod_min and aux[i] != -1:
            prod_min = aux[i]
            pos = i
    return prod_min, pos

def producer(storage, pid, sem_empty, sem_nonempty):
    v = 0 
    for i in range(N):
        print (f"Productor {current_process().name} produciendo")
        sleep(random.random()/3)
        v += random.randint(0,5)
        sem_empty[pid].acquire() #espera a que esté vacío
        storage[pid] = v
        sem_nonempty[pid].release()  #avisa de que ya no está vacío
        print (f"El productor {current_process().name} ha almacenado {v}")
        
    print(f"El productor {current_process().name} ha terminado de producir los N productos") 
    sem_empty[pid].acquire() #espera a que esté vacío
    storage[pid] = -1
    sem_nonempty[pid].release() #avisa de que ya no está vacío
    
    
    
def consumer(storage, sem_empty, sem_nonempty, lista_cons):  
    list_neg = [-1]*NPROD
    for i in range(NPROD):
        sem_nonempty[i].acquire() #espera a que todos produzcan
    while list_neg != list(storage):
        print ("El consumidor está desalmacenando")
        dato, posicion = prod_min(storage)
        lista_cons.append(dato)
        sem_empty[posicion].release() #avisa que está vacío porque acaba de consumir
        print (f"El consumidor consume {dato} del productor {posicion}")
        sem_nonempty[posicion].acquire() #espera a que se llene
        
    #cuando todos los productores han terminado de producir los N productos, acaba el bucle 
    #y por tanto el consumidor ya no puede consumir más
    print ('Lista de productos en el orden en el que se han ido consumiendo:', lista_cons)



def main():
    storage = Array('i',NPROD)
    sem_empty=[]
    sem_nonempty=[]
    lista_cons = [] #para almacenar los productos en el orden en el que se consumen
    for i in range(NPROD):
        non_empty = Semaphore(0)
        empty = BoundedSemaphore(1)
        sem_empty.append(empty)
        sem_nonempty.append(non_empty)

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage, i, sem_empty, sem_nonempty))
                for i in range(NPROD) ]

    conslst = [ Process(target=consumer,
                      name="cons",
                      args=(storage, sem_empty, sem_nonempty, lista_cons))]

    for p in prodlst + conslst:
        p.start()

    for p in prodlst + conslst:
        p.join()



if __name__ == "__main__":
    main()    
           
         
    
    
