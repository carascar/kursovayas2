import random
from collections import defaultdict
from platform import system

import matplotlib.pyplot as plt


class Ochered:
    def __init__(self, dlina):
        self.dlina = dlina


class TwoDeviceSystem:
    def __init__(self, lam, mu1, mu2, d=3, p =0, dlina1=0, dlina2=0, dt=0.00005):
        self.lam = lam  #Интенсивность входящего потока
        self.mu1 = mu1  #Интенсивность обслуживания 1 прибора
        self.mu2 = mu2  #Интенсивность обслуживания 2 прибора
        self.d = d      #Разница в длине очередей при которой осуществляется переход
        self.p=lam/(mu1+mu2)        #Условие стационарности при p<1
        self.ochered1 = Ochered(dlina1) #Очередь перед 1 прибором
        self.ochered2 = Ochered(dlina2) #Очередь перед 2 прибором
        self.dt = dt    #Шаг во времени
        self.counter1 = 0   #Фактическое количество требований прошедших через 1 очередь
        self.counter2 = 0   #Фактическое количество требований прошедших через 2 очередь
        self.counter_prihodov = 0
        self.counter_perehodov = 0

        if(self.p >= 1):
            print("Модель не стационарна! (p>=1)")


    def prihod(self):
        """Одно требование с вероятностью lam*dt приходит в систему"""
        if random.random() < self.lam*self.dt:
            self.napravit_trebovanie()
            self.counter_prihodov += 1


    def napravit_trebovanie(self):
        if self.mu1 > self.mu2:
            self.ochered1.dlina+=1
            self.counter1 += 1
        elif self.mu1 < self.mu2:
            self.ochered2.dlina+=1
            self.counter2 += 1
        elif random.randint(0,1) == 0:
            self.ochered1.dlina += 1
            self.counter1 += 1
        else:
            self.ochered2.dlina += 1
            self.counter2 += 1

    def perehod(self):
        if(self.ochered1.dlina - self.ochered2.dlina > self.d):
            self.ochered1.dlina -= 1
            self.ochered2.dlina += 1
            self.counter2 +=1
            self.counter1 -=1
            self.counter_perehodov +=1
        if(self.ochered2.dlina - self.ochered1.dlina > self.d):
            self.ochered2.dlina -= 1
            self.ochered1.dlina += 1
            self.counter1 +=1
            self.counter2-=1
            self.counter_perehodov +=1

    def pribor_finish(self):
        if self.ochered1.dlina > 0:
            if random.random() < self.mu1*self.dt:
                self.ochered1.dlina -=1
        if self.ochered2.dlina > 0:
            if random.random() < self.mu2*self.dt:
                self.ochered2.dlina -=1


def haracteristici(
        system,
        counter,    #Словарь с количеством раз нахождения системы в определенном состоянии
        N,                  #количество шагов имитации
        counter1,           #Фактическое количество прошедших требований через 1 очередь
        counter2,           #Фактическое количество прошедших требований через 2 очередь
):
    lam1 = counter1 / (N*system.dt)#Интенсивность потока поступающего в 1 прибор
    lam2 = counter2 / (N*system.dt)#Интенсивность потока поступающего в 1 прибор
    p1 = lam1/system.mu1#коэффициент загрузки 1 канала
    p2 = lam2/system.mu2#коэффициент загрузки 2 канала
    p = system.lam/(system.mu1+system.mu2)#коэффициент загрузки системы
    P = {}#Словарь с вероятностями состояний системы
    P_per = 0#Вероятность перехода требования
    N_per = 0#Среднее число переходов, совершаемых одним требованием за время пребывания в системе
    for state, count in counter.items():
        P[state] = count / N

    L1 = 0#Средняя длина 1 очереди
    L2 = 0#Средняя длина 2 очереди
    for (i, j), k in P.items():
        '''через фор перебирается состояние и количество раз этого состояния
        затем вычленяется длина 1 очереди и умножается на количество раз этого
         сотояния'''
        L1 += i * k
        L2 += j * k
        '''если разница в очередях больше чем d то здесь должен совершится
         переход поэтому плюсуем все вероятности где должен совершится переход'''
        if abs(i-j) > system.d:
            P_per += k
    L = L1 + L2#Общее число требований в системе
    Lq1 = lam1**2/(system.mu1*(system.mu1-lam1))#Среднее число требования ожидающий обслуживание в первой очереди
    Lq2 = lam2**2/(system.mu2*(system.mu2-lam2))#Среднее число требования ожидающий обслуживание в первой очереди
    W1 = L1/lam1#Среднее время пребывания в первой очереди
    W2 = L2/lam2#Среднее время пребывания во второй очереди
    Wq1 = Lq1/lam1  #Среднее время ожидания в первой очереди до начала обслуживания
    Wq2 = Lq2/lam2  #Среднее время ожидания во второй очереди до начала обслуживания
    W = L/system.lam#Среднее общее время пребывания требования в системе
    Nper = system.counter_perehodov/system.counter_prihodov

    results = {
        "lam":system.lam,
        "lam1": lam1,
        "lam2": lam2,
        "p1": p1,
        "p2": p2,
        "p": p,
        "P": P,
        "P_per": P_per,
        "L1": L1,
        "L2": L2,
        "L": L,
        "Lq1": Lq1,
        "Lq2": Lq2,
        "W1": W1,
        "W2": W2,
        "Wq1": Wq1,
        "Wq2": Wq2,
        "W": W,
        "Nper": Nper,
    }

    return results

def expirement1(N=100000):

    keys_to_print = ["lam","lam1", "lam2", "p", "L", "Lq1", "Lq2", "W", "Wq1", "Wq2", "P_per"]
    for i in keys_to_print:
        print(f"{i:<10}", end='')
    print()
    for i in range(0, 100, 10):
        system = TwoDeviceSystem(lam=50, mu1=100, mu2=100, dt=0.00005, d=1)
        system.lam += i
        counter = defaultdict(int)
        for step in range(N):
            system.prihod()
            system.perehod()
            system.pribor_finish()
            och1 = system.ochered1.dlina
            och2 = system.ochered2.dlina
            counter[(och1, och2)] += 1


        for keys in keys_to_print:
            print(f"{haracteristici(system, counter, N, system.counter1, system.counter2)[keys]:<10.4f}", end='')
        print()


def main():
    plt.ion()  # включаем интерактивный режим

    fig, ax = plt.subplots(figsize=(10, 4))
    line1, = ax.plot([], [], label="Очередь 1")
    line2, = ax.plot([], [], label="Очередь 2")
    ax.set_xlabel("Шаг")
    ax.set_ylabel("Длина очереди")
    ax.set_title("Динамика очередей")
    ax.legend()
    ax.grid(True, alpha=0.3)

    system = TwoDeviceSystem(lam=1.8, mu1=1, mu2=1, dt=0.00005, d=1)

    history_L1 = []
    history_L2 = []

    N = 100000
    update_every = 1000

    counter = defaultdict(int)#Словарь с количеством раз нахождения системы в определенном состоянии

    """for step in range(N):
        system.prihod()
        system.perehod()
        system.pribor_finish()

        '''Расчет вероятности состояний системы'''
        i = system.ochered1.dlina
        j = system.ochered2.dlina
        counter[(i,j)] += 1

        history_L1.append(system.ochered1.dlina)
        history_L2.append(system.ochered2.dlina)

        if step % update_every == 0:
            skip = 10
            x_vis = list(range(0, len(history_L1), skip))
            line1.set_data(x_vis, history_L1[::skip])
            line2.set_data(x_vis, history_L2[::skip])
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.001)  # пауза между кадрами
    haracteristici(system, counter, N, system.counter1, system.counter2)
    plt.ioff()
    plt.show()  # в конце оставляем окно открытым"""

    expirement1()

if __name__ == "__main__":
    main()
































