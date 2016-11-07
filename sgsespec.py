def ajuste(x,y):
    import numpy as np
    import matplotlib.pyplot as plt
    import math

    from numpy import std
    from math import factorial

#1) Smoothing del espectro usando el algoritmo SavitzkyGolay (http://scipy.github.io/old-wiki/pages/Cookbook/SavitzkyGolay)

#Algoritmo de ajuste, en principio el mejor ajuste es con ws 31 y order 1
#window_size=int(raw_input('ingrese ws (impar) para hacer el smoothing: '))
#order=int(raw_input('ingrese orden del polinomio: '))   

    window_size=31
    order=1

    deriv=0
    rate=1
    
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError, msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
# precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
# pad the signal at the extremes with
# values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y1 = np.concatenate((firstvals, y, lastvals))
    ys=np.convolve( m[::-1], y1, mode='valid')

#2) Calculo de la desviacion estandar del ajuste

#Calculo de sigma
    ws=11
    paso=ws
    sigma=np.zeros(len(y))
   
#Calculo la desviacion estandar central para un rango medio
#Ej: Para ws=5, sigma(2) es la deviacion estandar de los valores correspondientes a las diferencias entre el flujo y el flujo ajustado en las posiciones 0,1,2,3,4,5
    for i in range((ws-1)/2,len(y)-((ws-1)/2)): 
        s=0. 
        for j in range(paso-ws,paso):
            s += (y[j]-ys[j])**2
        sigma[i]=math.sqrt(s/(ws-1))
        paso += 1
#Calculo la desviacion estandar para el extremo menor usando:
# sigma(i)=<sigma/flujo>*flujo(i)
#considerando el valor medio de los ws valores siguientes a sigma(i)
    for i in range(0,((ws-1)/2)):
        cociente=[]
        for j in range(i,ws+i):
            cociente.append(sigma[j]/y[j])
        sigma[i]=np.mean(cociente)*y[i]
#Calculo la desviacion estandar para el extremo mayor usando:
# sigma(i)=<sigma/flujo>*flujo(i)
#considerando el valor medio de los ws valores anteriores a sigma(i)
    for i in range(len(y)-((ws-1)/2),len(y)):
                        #print i
        cociente=[]
        for j in range(i-ws,i):
            cociente.append(sigma[j]/y[j])
        sigma[i]=np.mean(cociente)*y[i]
                            
    return sigma,ys

    


