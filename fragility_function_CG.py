# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 17:35:01 2023

@author: vabuc
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns

import statsmodels.api as sm
from scipy import stats
from scipy.stats import norm

import warnings
warnings.simplefilter('ignore')


def fragility_function_CG(IM, EDP, j):
    
    # ----------------------------------------------------------------
    # 1. ORDENAR DATOS DE MENOR A MAYOR IM:
    IM_EDP = pd.DataFrame()
    IM_EDP['IM'] = IM
    IM_EDP['EDP'] = EDP

    IM_EDP = IM_EDP.sort_values('IM')
    
    # ----------------------------------------------------------------
    # 2. BINEADO:

    IM_min = 3.0
    IM_max = 5.0
    d_im = 0.1

    IM_bin_ref = np.arange(IM_min, IM_max + d_im, d_im)
        
    IM_bin = np.zeros(len(IM_EDP['IM']))

    # Dataframe con tres columnas: IM, nuevo IM bineado y EDP
    matriz_IM_EDP = pd.DataFrame()
    matriz_IM_EDP['IM'] = IM_EDP['IM']
    matriz_IM_EDP['IM_bin'] = IM_bin
    matriz_IM_EDP['EDP'] = IM_EDP['EDP']

    # Dataframe que contará cuantos IMs incluyen cada clase IM bineado
    conteo_IM_bin = pd.DataFrame()
    conteo_IM_bin['IM_bin_ref'] = IM_bin_ref
    conteo_IM_bin['Cantidad'] = np.zeros(len(IM_bin_ref)) 

    # Llenado de DataFrames
    indice = 0      # Revisa los indices de la matriz IM_bin_ref
    ind_ref = 0     # Indice de la matriz conteo_IM_bin
    cont1 = 0       # Contador de datos en los bines
    cont2 = 0       # Contador para el último bin
    flag = 0        # Indica que la data ya entró al elif, es decir, a la ultima clase de IM_bin_ref si no lo detecta el primer if

    for i in range (0, len(IM_EDP['IM'])):
        ok = 0
        
        while ok == 0:
            if matriz_IM_EDP.iloc[i,0] <= (IM_bin_ref[indice] + IM_bin_ref[indice+1])/2 - d_im/10:
                ok = 1
                matriz_IM_EDP.iloc[i,1] = IM_bin_ref[indice]
                cont1 = cont1 + 1
                
            elif matriz_IM_EDP.iloc[i,0] > (IM_bin_ref[-1] + IM_bin_ref[-2])/2 + d_im/10:
                flag = 1
                ok = 1
                matriz_IM_EDP.iloc[i,1] = IM_bin_ref[-1]
                cont2 = cont2 + 1
                
            else:
                # Este else indica que ya salió de un bin_ref y pasa al siguiente
                conteo_IM_bin.iloc[ind_ref,1] = cont1
                indice = indice + 1
                cont1 = 0 # se reinicia el contador de bines
                ind_ref = ind_ref + 1

    # Asignación de cantidad de data por si el i = len(IM_EDP['IM']) y no alcanza a entrar al else
    conteo_IM_bin.iloc[ind_ref,1] = cont1

    # Si el algoritmo entra al elif entonces se asigna el conteo de esa última categoria
    if flag == 1:
        conteo_IM_bin.iloc[ind_ref+1,1] = cont2

    # Dataframe que no incluye bines con cero
    conteo_IM_bin = conteo_IM_bin[conteo_IM_bin['Cantidad']>0]
    
    # ----------------------------------------------------------------
    # 3. CREACIÓN DE MATRIZ DE VALORES J:

    # j = 1: si la observación SÍ supera el límite del EDP
    # j = 0: si la observación NO supera el límie del EDP
    # La matriz tendrá tantas columnas como valores j+1 haya en el vector j
    # La primera columna corresponde al IM bineado

    matriz_j = pd.DataFrame()
    matriz_j['IM_bin'] = matriz_IM_EDP['IM_bin']

    # Se resetea la numeracion del indice para que se peguen bien los datos j
    matriz_j.reset_index(level=None, drop=True, inplace=True)
    #matriz_j = matriz_j['IM_bin']


    for k in range(0, len(j)):
        j_aux = pd.DataFrame()
        j_aux['Superó lim?'] = np.zeros(len(matriz_j))
        
        for i in range(0, len(matriz_IM_EDP['IM_bin'])):
            if matriz_IM_EDP.iloc[i,2] >= j[k]:
               j_aux.iloc[i] = 1
        
        matriz_j['j = ' + str(j[k])] = j_aux
        del j_aux
    
    # ----------------------------------------------------------------
    # 4. CREACIÓN DE MATRIZ FRAGILITY DE LA FORMA IM_BIN - N - Zi

    # IM_BIN es la columna que contiene todas las categorías de los bines
    # N es el número de observaciones que tiene un IM_BIN específico
    # Zi es el número de observaciones que superan un j especifico
    # Zi NO es una única columna ¿ habrán tantos Zi comom j hayan

    fragility = pd.DataFrame()
    fragility['IM_bin'] =  conteo_IM_bin['IM_bin_ref']
    fragility['N'] = conteo_IM_bin['Cantidad']

    # Estimación de Zi
    for k in range(0,len(j)):
        fragility['Zi - j = ' + str(j[k])] = matriz_j.groupby(['IM_bin']).aggregate({'j = ' + str(j[k]): 'sum'}).values

    # ----------------------------------------------------------------
    # 5. CÁLCULO DE PARÁMETROS DE CURVAS DE FRAGILIDAD

    # Se crea una matriz con tres columnas:
    # (1) Niveles j
    # (2) Mediana de cada curva j
    # (3) Desviación de cada curva j

    parameters = pd.DataFrame()
    parameters['j'] = j
    parameters['tetha'] = np.zeros(len(j))
    parameters['beta'] = np.zeros(len(j))

    delta_im = 0.01 # Delta para graficar
    IM_plot = np.arange(0, 8, delta_im)

    # Matriz con primera columna IM_plot y las demás columnas son los puntos que arman la curva para cada j
    matriz_plot = pd.DataFrame()
    matriz_plot['IM'] =  IM_plot


    for i in range(0,len(j)):
        Y = pd.DataFrame()
        
        Y['Zi'] = fragility['Zi - j = ' + str(j[i])]
        
        Y['N-Zi'] = fragility['N'] - fragility['Zi - j = ' + str(j[i])]
        
        sm_probit_Link = sm.genmod.families.links.probit
        x = np.log(fragility['IM_bin'])
        #glm_binom = sm.GLM(Y, sm.add_constant(x), family=sm.families.Binomial(link=sm_probit_Link))
        glm_binom = sm.GLM(Y, sm.add_constant(x), family=sm.families.Binomial(link=sm_probit_Link()))
        
        glm_result = glm_binom.fit()
        weights_py = glm_result.params
        
        # Conversion de coeficientes probit a parámetros de la distribucion lognormal
        sigma_ln = 1/weights_py[1]
        mu_ln = -weights_py[0]/weights_py[1]
          
        parameters.iloc[i,1] = np.exp(mu_ln)
        parameters.iloc[i,2] = sigma_ln
        
        matriz_plot['j = ' + str(j[i])] = norm.cdf(np.log(IM_plot), mu_ln, sigma_ln)
    
    return parameters, matriz_plot, fragility, matriz_IM_EDP, conteo_IM_bin


