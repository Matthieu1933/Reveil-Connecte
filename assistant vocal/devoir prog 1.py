#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 10:25:48 2019

@author: arthur
"""

def matrixproduct(A, B):
    m = len(A)
    n = len(A[0])
    if n != len(B):
        raise Exception("Incompatible dimensions")
    p = len(B[0])
    M = matrix.init(m, p, 0)
    for i in range(m):
        for j in range(p):
            for k in range(n):
                M[i][j] = M[i][j] + A[i][k] * B[k][j]
    return M