def gauss(x1,y1,sigma1,f,ga,redshift,linea,my_file1,my_file2,fr1,fr2):
    import numpy as np
    import matplotlib.pyplot as plt
    import math
    import astropy.units as u

    from numpy import std
    from numpy import loadtxt
    from lmfit.models import GaussianModel
    from lmfit.models import ExponentialModel
 
#Defino una recta para restarle al pseudo-continuo  
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

#Defino los parametros de la recta
    lpR=ga.left_point['x']
    rpR=ga.right_point['x']
    xa = [lpR,rpR]
    ya = [ga.left_point['y'],ga.right_point['y']]

    p1=np.polyfit(xa,ya,deg=1)

#Guardo en variables la informacion de los clicks que hice sobre el espectro
#cp=int(ga.center_point['x'])
    lp=f_n(np.array(x1),ga.left_point['x'])
    rp=f_n(np.array(x1),ga.right_point['x'])
    cp=(lp+rp)/2

#Acoto los datos a la region que me interesa del espectro, es decir, la region donde esta la linea
    recta=[]
    x=np.array([float(n) for n in x1[x1.index(lp):x1.index(rp)]])
    for i in range(0,len(x)):
        recta.append(fc(x[i],p1))
    y=np.array([float(n) for n in y1[x1.index(lp):x1.index(rp)]])
    sigma=np.array([float(n) for n in sigma1[x1.index(lp):x1.index(rp)]])
    y=y-recta

#Para definir la amp inicial me conviene calcularlo como base*altura/2 del 'rectangulo' que involucra la gaussiana
#Sigma lo defino mas o menos como el ancho de la linea
    ga_mod=GaussianModel(prefix='g_')
    pars=ga_mod.guess(y,x=x)
    pars.update(ga_mod.make_params())
    pars['g_center'].set(cp)
    pars['g_sigma'].set(lp-rp)
    pars['g_amplitude'].set(50.)


#A modelo lo defino como la combinacion de los distintos ajustes
    modelo= ga_mod

    init=modelo.eval(pars,x=x)
    out=modelo.fit(y,pars,x=x,weights=sigma)

    print(out.fit_report(min_correl=0.25))

    minimo=out.best_values
    print 'g_center: ',minimo['g_center']

#En caso de que haya muchos ajustes componentes guarda cada uno de los ajustes
    componentes = out.eval_components()

    my_file1.write("# Velocidad \n")
    my_file1.write("Extremos: %.0f %.0f \n " % (lp,rp))
    my_file1.write("Longitud de onda central: %.3f \n" % (minimo['g_center']))
    my_file1.write("  \n")
    my_file1.write("Ajuste principal \n")
    my_file1.write(out.fit_report(min_correl=0.25))
    my_file1.write("  \n")
    my_file2.write("  \n")
     
    f4=plt.figure(4)
    ax = f4.add_subplot(111)
    plt.plot(x,out.best_fit,'r-',label='Best_Fit')
    plt.plot(x,y,label='Original')
    plt.legend(loc='best')
    plt.title('Ajuste_Gaussiano_'+f)
    plt.xlabel(r'Longitud de onda [$\AA$]',fontsize=18)
    plt.ylabel('log(Flujo) + cte',fontsize=18)
    plt.vlines(minimo['g_center'],min(out.best_fit),1.25*min(out.best_fit),linestyles='solid')
    ax.annotate('MINIMO', xy=(minimo['g_center']-1,1.25*min(out.best_fit)),xytext=(minimo['g_center'],1.25*min(out.best_fit)))
    plt.ion()
    f4.show()
    plt.savefig(fr1, transparent=True)
 
#Calculo la velocidad
    long_onda_medida=minimo['g_center']/(1+redshift)
    if (linea=='Halfa'):
        long_onda_reposo=6563
    elif(linea=='HeI'):
        long_onda_reposo=5876
    else:
        long_onda_reposo=5169

    restfreq = long_onda_reposo*u.AA
    relativistic_equiv = u.doppler_relativistic(restfreq)
    measured_freq = long_onda_medida*u.AA
    relativistic_velocity = measured_freq.to(u.km/u.s, equivalencies=relativistic_equiv)
    my_file1.write("Velocidad : %.10s \n " % (relativistic_velocity))
    print 'Velocidad de ',linea,' : ',relativistic_velocity

#Calculo el error sigma en el calculo de lambda0
#WS=Dimension de la ventana dentro de la cual muevo los limites del ajuste gaussiano. Es impar para tomar un ancho simetrico alrededor de los puntos extremos originales
    ws= 15
    mws=(ws-1)/2

#A continuacion los vectores ampliados:
    recta2=[]
    a=f_n(np.array(x1),lp-mws)
    b=f_n(np.array(x1),rp+mws) 
    x2=np.array([float(n) for n in x1[x1.index(a):x1.index((b))]])
    for i in range(0,len(x2)):
        recta2.append(fc(x2[i],p1))
    y2=np.array([float(n) for n in y1[x1.index(a):x1.index((b))]])
    y3=y2-recta2
#Ahora itero sobre los valores del ws ajustando una gaussiana por cada posicion del mismo
    my_file2.write("Ajustes calculo error \n")
    
    cont=0
    m=[]
    f5=plt.figure(5)
    plt.plot(x2,y3,label='Original')
    for j in range(0,ws):
       for i in range(int(len(x2)-ws),int(len(x2))):
           cont += 1
           #y3=y4
           lp2=x2[j]
           rp2=x2[i]
           recta3=[]
           xrecta=[lp2,rp2]
           yrecta=[y2[j],y2[i]]
           p2=np.polyfit(xrecta,yrecta,deg=1)
           for i in range(0,len(x2)):
               recta3.append(fc(x2[i],p2))
           y4=y2-recta3
           #z=(y3[j]+y3[len(x2)-1-j])/2
           #y3=y3-z
           cp2=(lp2+rp2)/2
           ga2_mod=GaussianModel(prefix='g2_')
           pars2=ga2_mod.guess(y4,x=x2)
           pars2.update(ga2_mod.make_params())
           pars2['g2_center'].set(cp2)
           pars2['g2_sigma'].set(lp2-rp2)
           pars2['g2_amplitude'].set(50.)
           modelo= ga2_mod
           init=modelo.eval(pars2,x=x2)
           out=modelo.fit(y4,pars2,x=x2)
           my_file2.write(out.fit_report(min_correl=0.25))
           minimo2=out.best_values
           m.append(minimo2['g2_center'])
           plt.vlines(minimo2['g2_center'],min(out.best_fit),1.025*min(out.best_fit),linestyles='solid',label='')
           componentes2 = out.eval_components()
           #plt.plot(x2,out.best_fit+z)
           plt.plot(x2,out.best_fit)
    print 'Iteraciones: ',cont
    plt.title('Ajuste_Gaussiano_'+f)
    plt.xlabel(r'Longitud de onda [$\AA$]',fontsize=18)
    plt.ylabel('log(Flujo) + cte',fontsize=18)
    plt.ion() 
    f5.show() 
    plt.savefig(fr2, transparent=True)
    my_file1.write("  \n")
    my_file1.write("Desviacion estandar= %.3f \n " % (std(m)))
    my_file1.write("Iteraciones: %.0f \n " % (cont))
    
    print 'Dispersion: ',std(m)
    
#Paso la dispersion a velocidad
    
    c=300000
    deltav=c*std(m)/(long_onda_reposo*(1+redshift))
    
    print 'Dispersion [km/s]: ',deltav
    my_file1.write("Dispersion [km/s]: %.3f \n " % (deltav))
    return minimo['g_center'],relativistic_velocity,std(m),deltav
    
