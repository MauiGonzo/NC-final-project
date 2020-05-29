import numpy as np
import matplotlib.pyplot as plt

def SIR(N, R_0, infectious, I_0, t, model='SIR', incubation=5.2, alpha = 0.05, death = 6):

    check1 = False
    check2 = False

    if model == 'SEIR':
        check1 = True
    elif model == 'SEIRD':
        check1 = True
        check2 = True
    elif model != "SIR":
        print("ERROR!, choose valid model (SIR, SEIR, or SEIRD)")
        return()

    gamma = 1/infectious
    beta = R_0 * gamma
    delta = 1/incubation
    rho = 1/death

    S = N - I_0
    E = 0
    I = I_0
    R = 0
    D = 0

    def deltaS():
        return -beta * I * S/N

    def deltaE():
        return beta * I * S/N - delta * E

    def deltaI():
        if check2:
            return delta * E - (1 - alpha) * gamma * I - alpha * rho * I
        elif check1:
            return delta * E - gamma * I
        else:
            return beta * I * S/N - gamma * I

    def deltaR():
        if check2:
            return (1 - alpha) * gamma * I
        else:
            return gamma * I

    def deltaD():
        if check2:
            return alpha * rho * I
        else:
            return 0

    S_array = [S]
    E_array = [E]
    I_array = [I]
    R_array = [R]
    D_array = [D]

    for j in range(t):

        s = deltaS()
        e = deltaE()
        i = deltaI()
        r = deltaR()
        d = deltaD()

        S += s
        E += e
        I += i
        R += r
        D += d

        S_array.append(S)
        E_array.append(E)
        I_array.append(I)
        R_array.append(R)
        D_array.append(D)

    X = np.arange(len(S_array))

    plt.plot(X, S_array, label='Susceptible')
    if check1:
        plt.plot(X, E_array, label='Exposed')
    plt.plot(X, I_array, label='Infected')
    plt.plot(X, R_array, label='Recovered')
    if check2:
        plt.plot(X, D_array, label='Deceased')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    SIR(51*51, 2.2, 2.9, 1, 150, 'SIR')