# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import math
import sys

from numpy import std
from numpy import loadtxt
from math import factorial

from lmfit.models import GaussianModel
from lmfit.models import PolynomialModel

#Importo la clase que me permite interactuar con el espectro (tiene la interaccion para el ajuste lineal y para la gaussian)
import Interact as inter

#Importo la funcion de ajuste
from sgsespec import ajuste
#Importo el calculo de EW
from EW import EW
#Importo el ajuste gaussiano
from gaussAjuLMfit import gauss

#------------------------------------------------------------------------------
#Definición de la SN a estudiar
#Ingreso el nombre de la SN, sin el sn porque las carpetas donde tengo los datos son del tipo ####aa (no sn####aa)
sn=raw_input('Ingrese el nombre de la SN a estudiar SIN el prefijo sn ')
redshift=float(raw_input('Ingrese el redshift de la galaxia anfitrión '))
#path indica el lugar de donde voy a leer los archivos y escribir los resultados
path='/home/pris/Documentos/Tesis/Trabajo/ProgramaPy/main1/'+sn+'/'

#------------------------------------------------------------------------------
#Lineas a estudiar:
#Halfa 6563
#HeI: 5876
#FeII: 5169

#------------------------------------------------------------------------------
#Lectura de datos

#y0*10**(-int(math.log(y0[0],10))) multiplico todos los terminos por si mismo al exponenete positivo del primer termino de la lista, para pasar de una notacion exponencial a una que no lo sea
l=loadtxt(path+'lista',dtype='str')
#En my_file1 guardo los resultados fundamentales y en my_file2 el resto (datos, iteraciones, etc..)

my_file3=open(path+'Graf_'+sn+'.dat','w')

for f in l:
    print f
    plt.close(1)
    lr1='Res1_'+f
    lr2='Res2_'+f
    my_file1=open(path+lr1,'w')
    my_file2=open(path+lr2,'w')
    data=loadtxt(path+f)
    x0=data[:,0] 
    x1=np.array(x0).tolist()
    y0=data[:,1]
    escala=10**(-int(math.log(abs(y0[0]),10)))
    y1=np.array(y0*escala).tolist()
    
    sigma,ys=ajuste(x0,y0)
        
    my_file2.write("# x  y  ys  sigma \n")
    for i in range(0,len(x0)):
        my_file2.write("%.3f %.5E %.5E %.5E \n" % (x0[i],y0[i],ys[i],sigma[i]))
        
    ys=np.array(ys*escala).tolist()
    sigma=np.array(sigma*escala).tolist()

    f1=plt.figure(1)
    plt.plot(x1,y1,label='original')
    plt.plot(x1,ys,color='red',label='smooth')
    plt.legend(loc='best')
    plt.title(f)
    plt.xlabel(r'Longitud de onda [$\AA$]',fontsize=18)
    plt.ylabel('log(Flujo) + cte',fontsize=18)
    plt.ion()
    f1.show() 
    
#Debo asegurarme que la línea de estudio exista
#control es quien indica si el usuario esta o no de acuerdo con los calculos
    my_file3.write("#    sn             Línea              EW    PropErrEw  stdEW  lambda(min)  Vel[km/s]  stdVel  stdVel[km/s] \n")
    control='N'
    while control=='N':
        linea=raw_input('Indique la línea a analizar (Halfa, HeI o FeII): ')
        my_file3.write("%s %s " % (f,linea))
        existencia=raw_input('¿Se distingue en el espectro dicha línea? (S/N): ')
        if existencia=='S':
           my_file1.write("################################################# \n")
           my_file1.write("RESULTADOS %s \n " % (linea))
           my_file2.write("################################################# \n")
           my_file2.write("RESULTADOS %s \n " % (linea))
              
           f2=plt.figure(2)
           plt.plot(x1,y1,label='original')
           plt.plot(x1,ys,color='red',label='smooth')
           plt.legend(loc='best')
           plt.title(f)
           plt.xlabel(r'Longitud de onda [$\AA$]',fontsize=18)
           plt.ylabel('log(Flujo) + cte',fontsize=18)
           plt.ion()
           f2.show() 
           
           my_file1.write("------------------------------------------------- \n")
           my_file2.write("------------------------------------------------- \n")
           
#------------------------------------------------------------------------------
#Calculo EW
           if raw_input('¿Desea calcular el ancho equivalente? (S/N): ')=='S':    
               fr1EW=path+'Fig1EW_'+linea+'_'+f.replace(".dat",".eps")
               fr2EW=path+'Fig2EW_'+linea+'_'+f.replace(".dat",".eps")
           
               controlEW='N'
               while controlEW=='N':
                   plt.close(2)
                   f2=plt.figure(2)
                   plt.plot(x1,y1,label='original')
                   plt.plot(x1,ys,color='red',label='smooth')
                   plt.legend(loc='best')
                   plt.title(f)
                   plt.xlabel(r'Longitud de onda [$\AA$]',fontsize=18)
                   plt.ylabel('log(Flujo) + cte',fontsize=18)
                   plt.ion()
                   f2.show() 
                   raw_input( 'EW: Presione enter para elegir los extremos de la línea y vuelva a hacerlo cuando termine ')
                   la=inter.LineAdjuster(f2)
                   la.startPointSelection()
                   raw_input('')
                   ew,Sew,Sigmaew=EW(x1,y1,sigma,f,la,my_file1,fr1EW,fr2EW)
                   controlEW=raw_input( '¿Está de acuerdo con el ajuste? (S/N): ')
               my_file3.write("%.3f %.3f %.3f " % (ew,Sew,Sigmaew))
               my_file1.write("------------------------------------------------- \n")
               my_file2.write("------------------------------------------------- \n")
#------------------------------------------------------------------------------
#Ajuste gaussiano
           if raw_input('¿Desea calcular la velocidad? (S/N): ')=='S':    
               fr1Vel=path+'Fig1Vel_'+linea+'_'+f.replace(".dat",".eps")
               fr2Vel=path+'Fig2Vel_'+linea+'_'+f.replace(".dat",".eps")
           
               f3=plt.figure(3)
               plt.plot(x1,y1)
               plt.title('Ajuste_Gaussiano_'+f)
               plt.xlabel(r'Longitud de onda [$\AA$]',fontsize=18)
               plt.ylabel('log(Flujo) + cte',fontsize=18)
               plt.ion()
               f3.show() 

               controlGauss='N'
               while controlGauss=='N':
                   plt.close(4)
                   plt.close(5)
                   raw_input('Vel: Presione enter para elegir los extremos de la gaussiana y vuelva a hacerlo cuando termine ')
                   ga=inter.GaussAdjuster(f3)
                   raw_input('')
                   minimo,vel,elambda,evel=gauss(x1,y1,sigma,f,ga,redshift,linea,my_file1,my_file2,fr1Vel,fr2Vel)
                   controlGauss=raw_input( '¿Está de acuerdo con el ajuste? (S/N): ') 
               my_file3.write("%.3f %.10s %.3f %.3f " % (minimo,vel,elambda,evel))   
               my_file3.write("\n")
               my_file1.write("------------------------------------------------- \n")
               my_file2.write("------------------------------------------------- \n")
           
           control=raw_input(r'¿Análisis finalizado? (S/N): ')
           #control=raw_input('Le resulta satisfactorio el anslisis S/N: ')
           plt.close(2)
           plt.close(3)
           plt.close(4)
           plt.close(5)
        
        else :
           my_file1.write("################################################# \n") 
           my_file1.write("La línea %s no se distingue o no existe \n" % (linea))
           my_file2.write("################################################# \n") 
           my_file2.write("La línea %s no se distingue o no existe \n" % (linea))
           my_file3.write("La línea %s no se distingue o no existe \n" % (linea))
           control=raw_input( '¿Análisis finalizado? (S/N): ')
           pass
    raw_input('Presione enter para continuar... ')
    
my_file1.close()
my_file2.close()
my_file3.close()
