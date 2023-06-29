#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 14:52:17 2023

@author: wsantos
"""

import numpy as np
import matplotlib.pyplot as plt

# Parâmetros do modelo
Lx = 100  # Tamanho do domínio em x
Ly = 100  # Tamanho do domínio em y
Q = 9  # Número de direções de velocidade
dx = 1.0  # Intervalo em x na rede
dy = 1.0  # Intervalo em y na rede
dt = 1.0  # Passo de tempo  em unidades de rede
tau = 0.8  # Tempo de relaxação
cs = 1/np.sqrt(3)
g = 0.3 # Parâmetro de força
F = tau*g # Variação de momento

# Condições Iniciais
f = np.zeros((Lx, Ly, Q))
rho = np.ones((Lx, Ly))  # Densidade - uma matriz Lx por Ly cujos elementos valem 1
u = np.zeros((Lx, Ly, 2))  # Velocidade - uma matriz de dimensão Lx por Ly cujos elementos valem 0

# Conjunto de velocidades (D2Q9)
e = np.array([[0, 0], [1, 0], [0, -1], [-1, 0], [0, 1], [1, 1], [1, -1], [-1, -1], [-1, 1]]) # vetores velocidade
w = np.array([4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36]) # pesos da quadratura gaussiana


# Função de equilíbrio
def equilibrium(rho, u):
    """ 
    Função de equilíbrio
    rho: densidade local do fluido
    u: velocidade local do fluido
    returns:
    feq: função de equilíbrio
    """
    eu = np.dot(u, e.T) # Parte de produto escalar entre conjunto de velocidades e média
    uu = np.einsum('...i,...i->...', u, u) # produto escalar entre as médias de velocidades
    feq = np.zeros((Lx, Ly, Q)) # matriz reservatório da função de equilíbrio
    for i in range(Q): 
        feq[:, :, i] = rho * w[i] * (1 + (eu[:, :, i])/cs**2 + (eu[:, :, i]**2)/cs**4 - uu/(2*cs**4)) # função de equilíbrio
    return feq

# Looping sobre os passos de tempo
for t in range(100): # para t de um 0 a 100
    feq = equilibrium(rho, u) # calcula a função de equilíbrio
    
    # Passo de Colisão
    for i in range(Q):
        f[:, :, i] = f[:, :, i] - (dt / tau) * (f[:, :, i] - feq[:, :, i])
        
        
    # Passo de propagação
    for i in range(Q):
        f[:, :, i] = np.roll(np.roll(f[:, :, i], e[i, 0], axis=0), e[i, 1], axis=1)

    # Cálculo da densidade e velocidade média
    rho = np.sum(f, axis=2)
    u = np.dot(f, e) / rho[:, :, None]
    

    # Condições de contorno (paredes fixas)
    u[0, :, :] = 0
    u[-1, :, :] = 0
    u[:, 0, :] = 0
    u[:, -1, :] = 0

    # Força externa (exemplo: força gravitacional)
    u += np.array([F, 0])

 # Criar uma matriz com as colunas a serem salvas
    data = np.column_stack((rho.flatten(), u[:, :, 0].flatten(), u[:, :, 1].flatten()))

    # Salvar em arquivo de texto
    np.savetxt(f"RES-{t}.dat", data, delimiter="\t")


    # Visualização (exemplo: plotar campo de veloc
    