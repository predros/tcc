import numpy as np


def Span(start, end, X):
    LX = []
    for i in range(len(start)):
        node1 = start[i]
        node2 = end[i]
        LX.append(X[node2] - X[node1])
    return LX


def Length(LX, LY):
    L = []
    for i in range(len(LX)):
        L.append(np.sqrt(LX[i] * LX[i] + LY[i] * LY[i]))
    return L


def Stiffness(length, elasticity, inertia, area, axial):
    ST = []
    for i in range(len(length)):
        E = elasticity[i]
        A = area[i]
        I = inertia[i]
        L = length[i]
        P = axial[i]
        bL = np.sqrt(np.absolute(P / (E * I)))
        if P == 0:
            C = 4
            S = 2
        elif P > 0:
            c = (bL / np.tanh(bL) - 1) / (bL * bL)
            s = (1 - bL / np.sinh(bL)) / (bL * bL)
            C = c / (c * c - s * s)
            S = s / (c * c - s * s)
        else:
            c = (1 - bL / np.tan(bL)) / (bL * bL)
            s = (bL / np.sin(bL) - 1) / (bL * bL)
            C = c / (c * c - s * s)
            S = s / (c * c - s * s)
        ST.append([[E * A / L, 0, 0, -E * A / L, 0, 0],
                   [0, 2 * E * I * (C + S) / (L * L * L) +
                   P / L, E * I * (C + S) / (L * L), 0, -2
                   * E * I * (C + S) / (L * L * L) - P / L,
                   E * I * (C + S) / (L * L)],
                   [0, E * I * (C + S) / (L * L), E * I * C / L,
                    0, -E * I * (C + S) / (L * L), E * I * S / L],
                   [-E * A / L, 0, 0, E * A / L, 0, 0],
                   [0, -2 * E * I * (C + S) / (L * L * L) - P /
                   L, -E * I * (C + S) / (L * L),
                    0, 2 * E * I * (C + S) / (L * L * L) + P /
                    L, -E * I * (C + S) / (L * L)],
                   [0, E * I * (C + S) / (L * L), E * I * S /
                   L, 0, -E * I * (C + S) / (L * L), E * I * C / L]])
    return ST


def LoadVector(length, elasticity, inertia, area, thermal, Qy, Qx, Tinf, Tsup,
               yinf, ysup, displace, curvature):
    F0 = []
    F0q = []
    F0t = []
    F0s = []
    # Distributed loads
    for i in range(len(length)):
        L = length[i]
        qy = Qy[i]
        qx = Qx[i]
        F0q.append([-qx * L / 2, qy * L / 2, qy * L * L / 12, -
                    qx * L / 2, qy * L / 2, -qy * L * L / 12])
    # Thermal load
    for i in range(len(length)):
        L = length[i]
        T1 = Tinf[i]
        T2 = Tsup[i]
        y1 = yinf[i]
        y2 = ysup[i]
        h = yinf[i] + ysup[i]
        E = elasticity[i]
        A = area[i]
        I = inertia[i]
        alpha = thermal[i]
        T0 = (T1 - T2) * y2 / (y1 + y2)
        F0t.append([E * A * alpha * T0, 0, alpha * E * I * (T1 - T2) /
                    h, -E * A * alpha * T0, 0, -alpha * E * I * (T1 - T2) / h])
    # Prestrain length load
    for i in range(len(length)):
        L = length[i]
        delta = displace[i]
        e = curvature[i]
        E = elasticity[i]
        A = area[i]
        I = inertia[i]
        F0s.append([E * A * delta / L, 0, 8 * E * I * e / (L * L), -
                    E * A * delta / L, 0, -8 * E * I * e / (L * L)])
    # Final vector
    F0 = np.add(F0q, F0t)
    F0 = np.add(F0, F0s)
    return F0

# Calculates every frame's rotation matrix.


def RotationMatrix(L, LX, LY):
    """
    Calculates the degrees of freedom matrix,
    given the number of node displacements and restrictions.
    """
    R = []
    for i in range(0, len(L)):
        cos = LX[i] / L[i]
        sin = LY[i] / L[i]
        R.append([[cos, sin, 0, 0, 0, 0],
                  [-sin, cos, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0],
                  [0, 0, 0, cos, sin, 0],
                  [0, 0, 0, -sin, cos, 0],
                  [0, 0, 0, 0, 0, 1]])
    return R


def DOFCalc(RESTRX, RESTRY, RESTRZ, nd):
    """
    Defines the degrees of freedom relative to
    each frame's start and end nodes.
    """
    DOF = []
    i = 0
    n = 0
    for i in range(0, nd):
        if i % 3 == 0:
            a = int(i / 3)
            if RESTRX[a] == 1:
                DOF.append(-1)
            else:
                DOF.append(n)
                n = n + 1

        elif i % 3 == 1:
            a = int((i - 1) / 3)
            if RESTRY[a] == 1:
                DOF.append(-1)
            else:
                DOF.append(n)
                n = n + 1
        else:
            a = int((i - 2) / 3)
            if RESTRZ[a] == 1:
                DOF.append(-1)
            else:
                DOF.append(n)
                n = n + 1
    return DOF


def FrameDOF(START, END, DOF):
    """
    Calculates the prescribed displacement vector with respect to the DOF's.
    """
    FD = []
    for i in range(0, len(START)):
        a = 3 * START[i]
        b = 3 * END[i]
        FD.append([DOF[a], DOF[a + 1], DOF[a + 2],
                   DOF[b], DOF[b + 1], DOF[b + 2]])
    return FD


def PD(PDX, PDY, PDZ):
    """
    Defines the prescribed displacement relative to
    each frame's start and end nodes.
    """
    PD = []
    for i in range(0, len(PDX)):
        PD.append(PDX[i])
        PD.append(PDY[i])
        PD.append(PDZ[i])
    return PD


def FramePD(START, END, PD):
    """
    Calculates the nodal forces vector.
    """
    FramePD = []
    for i in range(0, len(START)):
        a = 3 * START[i]
        b = 3 * END[i]
        FramePD.append([PD[a], PD[a + 1], PD[a + 2],
                        PD[b], PD[b + 1], PD[b + 2]])
    return FramePD


def FN(FX, FY, MZ):
    """
    Adds a single local matrix to the global matrix.
    """
    FN = []
    for i in range(0, len(FX)):
        FN.append(FX[i])
        FN.append(FY[i])
        FN.append(MZ[i])
    return FN


def MatrixOrder(X, DOF, size):
    """
    Adds a scalar to the diagonal of the global matrix.
    """
    row = 0
    col = 0
    A = []
    for i in range(0, size):
        A.append([])
        for j in range(0, size):
            if (i in DOF) and (j in DOF):
                row = DOF.index(i)
                col = DOF.index(j)
                A[i].append(X[row][col])
            else:
                A[i].append(0)
    return A


def ScalarOrder(X, DOF, size):
    """
    Adds a single local vector to the global vector.
    """
    A = np.zeros((size, size))
    A[DOF][DOF] = X
    return A


def VectorOrder(X, DOF, size):
    """
    Divides the nodal displacement matrix into three matrices,
    relative to the three axes.
    """
    row = 0
    A = []
    for i in range(0, size):
        if (i in DOF):
            row = DOF.index(i)
            A.append(X[row])
        else:
            A.append(0)
    return A


def NodeDisplacement(D):
    """
    Run the structural analysis calculations using Galambos' method,
    given an arbitrary vector P.
    """
    DX = []
    DY = []
    RZ = []
    for i in range(0, len(D)):
        if i % 3 == 0:
            DX.append(D[i])
        elif i % 3 == 1:
            DY.append(D[i])
        else:
            RZ.append(D[i])
    return [DX, DY, RZ]


def G_Run(N_X, N_Y, N_PX, N_PY, N_MZ, N_RESTRX, N_RESTRY, N_RESTRZ,
          N_KX, N_KY, N_KZ, N_PDX, N_PDY, N_PDZ, FR_START, FR_END, FR_Qx,
          FR_Qy, FR_Tinf, FR_Tsup, FR_yinf, FR_ysup, FR_tensile,
          FR_curvature, FR_E, FR_I, FR_A, FR_alpha, P
          ):
    # Basic parameters
    nnode = len(N_X)
    nframe = len(FR_START)
    nd = 3 * len(N_X)
    nrestr = sum(N_RESTRX) + sum(N_RESTRY) + sum(N_RESTRZ)
    ndof = nd - nrestr

    # Frame properties
    FR_LX = Span(FR_START, FR_END, N_X)
    FR_LY = Span(FR_START, FR_END, N_Y)
    FR_L = Length(FR_LX, FR_LY)
    FR_SL = Stiffness(FR_L, FR_E, FR_I, FR_A, P)
    FR_R = RotationMatrix(FR_L, FR_LX, FR_LY)
    FR_F0L = LoadVector(FR_L, FR_E, FR_I, FR_A, FR_alpha, FR_Qy, FR_Qx,
                        FR_Tinf, FR_Tsup, FR_yinf, FR_ysup,
                        FR_tensile, FR_curvature)

    # DOF definition
    DOF = DOFCalc(N_RESTRX, N_RESTRY, N_RESTRZ, nd)
    FR_DOF = FrameDOF(FR_START, FR_END, DOF)

    # Prescribed displacements definition
    N_PD = PD(N_PDX, N_PDY, N_PDZ)
    FR_PD = FramePD(FR_START, FR_END, N_PD)

    # Global-coordinates stiffness matrices
    FR_SG = []
    for i in range(nframe):
        a = np.transpose(FR_R[i])
        b = np.dot(a, FR_SL[i])
        c = np.dot(b, FR_R[i])
        FR_SG.append(c)

    # Global-coordinates load vectors
    FR_F0 = []
    for i in range(nframe):
        a = np.transpose(FR_R[i])
        b = np.dot(a, FR_F0L[i])
        FR_F0.append(b)

    # Nodal forces vector
    N_FN = FN(N_PX, N_PY, N_MZ)

    # Prescribed displacement load vectors
    FR_FPD = []
    for i in range(nframe):
        FPD = np.dot(FR_SG[i], FR_PD[i])
        FR_FPD.append(FPD)

    # Global stiffness matrix
    S = np.zeros((ndof, ndof))
    for i in range(nframe):
        X = MatrixOrder(FR_SG[i], FR_DOF[i], ndof)
        S = np.add(S, X)

    # Spring stiffness
    for i in range(nnode):
        X = ScalarOrder(N_KX[i], DOF[3 * i], ndof)
        Y = ScalarOrder(N_KY[i], DOF[3 * i + 1], ndof)
        Z = ScalarOrder(N_KZ[i], DOF[3 * i + 2], ndof)
        S = np.add(S, X)
        S = np.add(S, Y)
        S = np.add(S, Z)

    # Global load vector
    F0G = np.zeros(ndof)  # Frame loads vector
    for i in range(nframe):
        X = VectorOrder(FR_F0[i], FR_DOF[i], ndof)
        F0G = np.add(F0G, X)
    FPDG = np.zeros(ndof)  # Prescribed displacements load vector
    for i in range(nframe):
        X = VectorOrder(FR_FPD[i], FR_DOF[i], ndof)
        FPDG = np.add(FPDG, X)
    FNG = VectorOrder(N_FN, DOF, ndof)  # Nodal forces vector
    FG = np.add(F0G, -FPDG)   # Global load vector
    FG = np.add(FG, FNG)

    # Displacements vector
    S_INV = np.linalg.inv(S)
    d_DOF = np.dot(S_INV, FG)
    d = []
    for i in range(len(DOF)):
        if DOF[i] == -1:
            d.append(N_PD[i])
        else:
            n = DOF[i]
            d.append(d_DOF[n])

    # Internal forces for each frame
    FR_d = []
    for i in range(len(FR_START)):
        a = 3 * FR_START[i]
        b = 3 * FR_END[i]
        FR_d.append([d[a], d[a + 1], d[a + 2], d[b], d[b + 1], d[b + 2]])
    FR_FE = []
    for i in range(len(FR_d)):
        FE = np.dot(FR_SG[i], FR_d[i])
        FE = np.add(FE, -FR_F0[i])
        FR_FE.append(FE)
    FR_FEL = []
    for i in range(len(FR_FE)):
        FEL = np.dot(FR_R[i], FR_FE[i])
        FR_FEL.append(FEL)

    # Normal forces
    PF = []
    for i in range(len(FR_FEL)):
        PF.append(FR_FEL[i][3])

    # Results array
    RESULTS = [d, FR_FEL, PF]
    return RESULTS


def G_Iteration(
    N_X, N_Y, N_PX, N_PY, N_MZ, N_RESTRX, N_RESTRY, N_RESTRZ,
    N_KX, N_KY, N_KZ, N_PDX, N_PDY, N_PDZ, FR_START, FR_END, FR_Qx, FR_Qy,
    FR_Tinf, FR_Tsup, FR_yinf, FR_ysup, FR_tensile, FR_curvature, FR_E, FR_I,
    FR_A, FR_alpha, maxerror, maxiter
):
    P1 = np.zeros(len(FR_START))
    P2 = np.zeros(len(FR_START))
    iterations = 0
    while 1 == 1:
        X = G_Run(
            N_X, N_Y, N_PX, N_PY, N_MZ, N_RESTRX, N_RESTRY, N_RESTRZ,
            N_KX, N_KY, N_KZ, N_PDX, N_PDY, N_PDZ, FR_START,
            FR_END, FR_Qx, FR_Qy, FR_Tinf, FR_Tsup, FR_yinf, FR_ysup,
            FR_tensile, FR_curvature, FR_E, FR_I, FR_A, FR_alpha, P1
        )
        err_vector = []
        for i in range(0, len(P2)):
            P2[i] = X[2][i]
            err_vector.append(np.absolute(P2[i] - P1[i]))
            P1[i] = P2[i]
        error = np.amax(err_vector)
        if iterations >= maxiter or error <= maxerror:
            break
        iterations = iterations + 1
    return X


# Nodal properties
N_X = [0, 0, 600, 600]  # Nodal X coordinates
N_Y = [0, 400, 400, 0]  # Nodal Y coordinates
N_PX = [0, 50, 0, 0]  # Nodal X-direction forces
N_PY = [0, 0, 0, 0]  # Nodal Y-direction forces
N_MZ = [0, 0, 0, 0]  # Nodal Z-direction torques
# Nodal X-direction displacement restriction (1 = restricted, 0 = unknown)
N_RESTRX = [1, 0, 0, 1]
# Nodal Y-direction displacement restriction (1 = restricted, 0 = unknown)
N_RESTRY = [1, 0, 0, 1]
# Nodal Z-direction rotation restriction (1 = restricted, 0 = unknown)
N_RESTRZ = [1, 0, 0, 1]
# Nodal X-direction spring stiffness (0 = no spring present)
N_KX = [0, 0, 0, 0]
# Nodal Y-direction spring stiffness (0 = no spring present)
N_KY = [0, 0, 0, 0]
# Nodal Z-direction spring stiffness (0 = no spring present)
N_KZ = [0, 0, 0, 0]
# Nodal X-direction prescribed displacement (only usable when RESTRX[i] = 1)
N_PDX = [0, 0, 0, 0]
# Nodal Y-direction prescribed displacement (only usable when RESTRY[i] = 1)
N_PDY = [0, 0, 0, 0]
# Nodal Z-direction prescribed rotation (only usable when RESTRZ[i] = 1)
N_PDZ = [0, 0, 0, 0]

# Frame properties
FR_START = [0, 1, 2]  # Start node for each frame
FR_END = [1, 2, 3]  # End node for each frame
FR_A = [225, 225, 225]  # Cross-sectional area for each frame
FR_I = [4200, 4200, 4200]  # Cross-sectional moment of inertia for each frame
FR_E = [2380, 2380, 2380]  # Elasticity modulus for each frame
# Thermal coefficient for each frame
FR_alpha = [1 / 1000000, 1 / 1000000, 1 / 1000000]
FR_Tinf = [0, 0, 0]  # Temperature difference on inferior side of each frame
FR_Tsup = [0, 0, 0]  # Temperature difference on superior side of each frame
FR_Qx = [0, 0, 0]  # x-direction (local) distributed load for each frame
FR_Qy = [0, -0.15, 0]  # y-direction (local) distributed load for each frame
# y-coordinate (absolute value) of the inferior side of each frame
FR_yinf = [7.5, 7.5, 7.5]
# y-coordinate (absolute value) of the superior side of each frame
FR_ysup = [7.5, 7.5, 7.5]
FR_tensile = [0, 0, 0]  # Tensile pre-displacement of each frame
# Central initial displacement of each frame (circular curvature)
FR_curvature = [0, 0, 0]
P = [0, 0, 0]

# Linear analysis
R1 = G_Run(
    N_X, N_Y, N_PX, N_PY, N_MZ, N_RESTRX, N_RESTRY, N_RESTRZ, N_KX, N_KY, N_KZ,
    N_PDX, N_PDY, N_PDZ, FR_START,
    FR_END, FR_Qx, FR_Qy, FR_Tinf, FR_Tsup, FR_yinf, FR_ysup, FR_tensile,
    FR_curvature, FR_E, FR_I, FR_A, FR_alpha, P
)
print(R1[0][3])

# Non-linear analysis
maxerror = 0.0001
maxiter = 10
R2 = G_Iteration(
    N_X, N_Y, N_PX, N_PY, N_MZ, N_RESTRX, N_RESTRY, N_RESTRZ,
    N_KX, N_KY, N_KZ, N_PDX, N_PDY, N_PDZ, FR_START, FR_END,
    FR_Qx, FR_Qy, FR_Tinf, FR_Tsup, FR_yinf, FR_ysup, FR_tensile,
    FR_curvature, FR_E, FR_I, FR_A, FR_alpha, maxerror, maxiter
)
print(R2[0][3])
