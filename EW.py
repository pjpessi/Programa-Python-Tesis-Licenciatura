def EW(x,y,sigma0,f,la,my_file1,fr1,fr2): 
    import matplotlib.pyplot as plt
    import numpy as np
    import math

    from numpy import loadtxt
    from numpy import std

    def graph(formula, x_range):  
        x = np.array(x_range)  
        y = eval(formula) 
        plt.plot(x, y)  
        plt.show()

    def fc(x,p):
        return p[0]*x+p[1]

#Defino una funcion que encuentra el valor en la lista que sea mas cercano a un valor dado (find_nearest)
    def f_n(array,value):
        idx=(np.abs(array-value)).argmin()
        return array[idx]
 
#Defino los extremos de la recta
    lpR=la.lp['x']
    rpR=la.rp['x']
    xa = [lpR,rpR]
    ya = [la.lp['y'],la.rp['y']]
    
    p1=np.polyfit(xa,ya,deg=1)
    
    formula1 = str(p1[0])+'*x+'+str(p1[1])

    graph(formula1,range(int(lpR),int(rpR)))
    plt.title('Ancho_Equivalente_'+f)
    plt.xlabel(r'Longitud de onda [$\AA$]',fontsize=18)
    plt.ylabel('log(Flujo) + cte',fontsize=18)
    plt.savefig(fr1, transparent=True)

    lp=f_n(np.array(x),la.lp['x'])
    rp=f_n(np.array(x),la.rp['x'])

#Defino un arreglo con los datos a ajustar
    x1=np.array([float(n) for n in x[x.index(lp):x.index(rp)]])
    y1=np.array([float(n) for n in y[x.index(lp):x.index(rp)]])
    s1=np.array([float(n) for n in sigma0[x.index(lp):x.index(rp)]])
    
    ew=0
    for i in range(0,len(x1)-1):
        ew += (1- (y1[i]/fc(x1[i],p1)))*(x1[i+1]-x1[i])
        
    my_file1.write("# EW \n")
    my_file1.write("Extremos: %.0f %.0f \n " % (lp,rp))
    my_file1.write("Recta: %s \n" % (formula1))
    my_file1.write("EW= %.3f \n " % (ew))
    print 'EW = ', ew

#Hago la propagacion de errores para EW

    Sew=0
    for i in range(0,len(x1)-1):
        Sew += ((s1[i])**2/(fc(x1[i],p1))**2)*(x1[i+1]-x1[i])**2
        
    my_file1.write("Propagacion de errores= %.3f \n " % (math.sqrt(Sew)))
    print 'Propagacion de errores del EW = ', math.sqrt(Sew)

    raw_input('Para calcular el error de la medicion presione enter ')

#Calculo el error de la medicion
#Dimension de la ventana dentro de la cual muevo los limites del ajuste gaussiano. Es impar para tomar un ancho simetrico alrededor de los puntos extremos originales
    ws=15
#Este valor, que es aprox la mitad de ws, lo uso para generar los vectores con los datos ampliados, es decir que inolucren los datos dentro de la ventana
    mws=(ws-1)/2

#A continuacion los vectores ampliados:
    a=f_n(np.array(x),lp-mws)
    b=f_n(np.array(x),rp+mws)
    x2=np.array([float(n) for n in x[x.index(a):x.index((b))]])
    y2=np.array([float(n) for n in y[x.index(a):x.index((b))]])

    cont=0
    p2ew=[]
    for j in range(0,ws):
        for i in range(int(len(x2)-ws),int(len(x2))):
            cont += 1
            xb = [x2[j],x2[i]]
            yb = [y2[j],y2[i]]
            p2=np.polyfit(xb,yb,deg=1)
            formula2 = str(p2[0])+'*x+'+str(p2[1])
            graph(formula2,range(int(xb[0]),int(xb[1])))
            p2ew.append(p2)

    plt.title('Ancho_Equivalente_'+f)
    plt.xlabel(r'Longitud de onda [$\AA$]',fontsize=18)
    plt.ylabel('log(Flujo) + cte',fontsize=18)       
    plt.savefig(fr2, transparent=True)
    Sigmaew=np.zeros(int(len(p2ew)))

    for j in range(0,int(len(p2ew))):
        for i in range(0,len(x2)-1):
            Sigmaew[j] += (1- (y2[i]/fc(x2[i],p2ew[j])))*(x2[i+1]-x2[i])
    
    my_file1.write("Desviacion estandar= %.3f \n " % (std(Sigmaew)))
    my_file1.write("Iteraciones: %.0f \n " % (cont)) 
    my_file1.write("Ventana(WS): %.0f \n " % (ws))
    print 'Desviacion estandar luego de ', cont, ' iteraciones = ',std(Sigmaew)
    return ew,math.sqrt(Sew),std(Sigmaew)
 
