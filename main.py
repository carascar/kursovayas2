import random
from collections import defaultdict
from platform import system

import matplotlib.pyplot as plt


class Ochered:
    def __init__(self):
        self.spisok = []

class Trebovanie:
    Id = 0
    def __init__(self):
        Trebovanie.Id+=1
        self.id = Trebovanie.Id
        self.Isperehod = False


class TwoDeviceSystem:
    def __init__(self, lam, mu1, mu2, d=3, p =0, dlina1=0, dlina2=0, dt=0.00005):
        self.lam = lam  #Интенсивность входящего потока
        self.mu1 = mu1  #Интенсивность обслуживания 1 прибора
        self.mu2 = mu2  #Интенсивность обслуживания 2 прибора
        self.d = d      #Разница в длине очередей при которой осуществляется переход
        self.p=lam/(mu1+mu2)        #Условие стационарности при p<1
        self.ochered1 = Ochered() #Очередь перед 1 прибором
        self.ochered2 = Ochered() #Очередь перед 2 прибором
        self.dt = dt    #Шаг во времени
        self.counter1 = 0   #Фактическое количество требований прошедших через 1 очередь
        self.counter2 = 0   #Фактическое количество требований прошедших через 2 очередь
        self.counter_prihodov = 0   #количество требований поступивших в систему
        self.counter_perehodov = 0  #количество переходов требований
        self.counter_tr_moved = 0   #количество требований совершивших хотя бы один переход
        self.sum_len_ochered1 = 0   #сумма длин очередей каждого такта
        self.sum_len_ochered2 = 0   #нужна для вычисления средней длины очереди


        if(self.p >= 1):
            print("Модель не стационарна! (p>=1)")


    def prihod(self):
        """Одно требование с вероятностью lam*dt приходит в систему"""
        if random.random() < self.lam*self.dt:
            tr = Trebovanie()
            self.napravit_trebovanie(tr)
            self.counter_prihodov += 1


    def napravit_trebovanie(self, trebovanie):
        if self.mu1 > self.mu2:
            self.counter1 += 1
            self.ochered1.spisok.append(trebovanie)
        elif self.mu1 < self.mu2:
            self.counter2 += 1
            self.ochered2.spisok.append(trebovanie)
        elif random.randint(0,1) == 0:
            self.counter1 += 1
            self.ochered1.spisok.append(trebovanie)
        else:
            self.counter2 += 1
            self.ochered2.spisok.append(trebovanie)


    def perehod(self):
        if(len(self.ochered1.spisok) - len(self.ochered2.spisok) > self.d):
            self.counter2 +=1
            self.counter1 -=1
            self.counter_perehodov += 1

            tr = self.ochered1.spisok.pop(-1)
            if(tr.Isperehod==False):
                tr.Isperehod = True
                self.counter_tr_moved += 1
            self.ochered2.spisok.append(tr)

        elif(len(self.ochered2.spisok) - len(self.ochered1.spisok) > self.d):
            self.counter1 +=1
            self.counter2-=1
            self.counter_perehodov += 1

            tr = self.ochered2.spisok.pop(-1)
            if(tr.Isperehod==False):
                tr.Isperehod = True
                self.counter_tr_moved += 1
            self.ochered1.spisok.append(tr)

    def pribor_finish(self):
        if len(self.ochered1.spisok) > 0:
            if random.random() < self.mu1*self.dt:
                self.ochered1.spisok.pop(0)
        if len(self.ochered2.spisok) > 0:
            if random.random() < self.mu2*self.dt:
                self.ochered2.spisok.pop(0)


def haracteristici(
        system,
        counter,    #Словарь с количеством раз нахождения системы в определенном состоянии
        N,                  #количество шагов имитации
        counter1,           #Фактическое количество прошедших требований через 1 очередь
        counter2,           #Фактическое количество прошедших требований через 2 очередь
):
    lam_fact = system.counter_prihodov/(N*system.dt)
    lam1 = counter1 / (N*system.dt)#Интенсивность потока поступающего в 1 прибор
    lam2 = counter2 / (N*system.dt)#Интенсивность потока поступающего в 1 прибор
    p1 = lam1/system.mu1#коэффициент загрузки 1 канала
    p2 = lam2/system.mu2#коэффициент загрузки 2 канала
    p = system.lam/(system.mu1+system.mu2)#коэффициент загрузки системы

    P = {}#Словарь с вероятностями состояний системы
    P_per = system.counter_tr_moved/system.counter_prihodov#Вероятность перехода требования
    N_per = 0#Среднее число переходов, совершаемых одним требованием за время пребывания в системе
    for state, count in counter.items():
        P[state] = count / N

    L1 = system.sum_len_ochered1/N #Средняя длина 1 очереди
    L2 = system.sum_len_ochered2/N #Средняя длина 2 очереди


    L = L1 + L2     #Общее число требований в системе
    Lq1 = 0 if L1<=p1 else L1- p1    #Среднее число требования ожидающий обслуживание в первой очереди
    Lq2 = 0 if L2<=p2 else L2-p2     #Среднее число требования ожидающий обслуживание в первой очереди
    W1 = 0 if lam1 <= 0 else L1/lam1    #Среднее время пребывания в первой очереди
    W2 = 0 if lam2 <= 0 else L2/lam2    #Среднее время пребывания во второй очереди
    Wq1 = 0 if lam1 <= 0 else Lq1/lam1  #Среднее время ожидания в первой очереди до начала обслуживания
    Wq2 = 0 if lam2 <=0 else Lq2/lam2   #Среднее время ожидания во второй очереди до начала обслуживания
    W = L/lam_fact   #Среднее общее время пребывания требования в системе
    Nper = system.counter_perehodov/system.counter_prihodov #среднее количество переходов одного требования

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
        "prihod": system.counter_prihodov,
    }

    return results

def expirement1(N=100000):

    keys_to_print = ["lam","p", "L", "L1", "L2",
                     "W", "W1", "W2", "P_per"]
    for i in keys_to_print:
        print(f"{i:<10}", end='')
    print()
    for i in range(0, 200, 20):
        system = TwoDeviceSystem(lam=10, mu1=100, mu2=100, dt=0.00005, d=1)
        system.lam += i
        counter = defaultdict(int)
        for step in range(N):
            system.prihod()

            och1 = len(system.ochered1.spisok)
            och2 = len(system.ochered2.spisok)

            counter[(och1, och2)] += 1
            system.sum_len_ochered1 += len(system.ochered1.spisok)
            system.sum_len_ochered2 += len(system.ochered2.spisok)

            system.perehod()
            system.pribor_finish()


        for keys in keys_to_print:
            print(
                f"{haracteristici(system, counter, N, system.counter1, system.counter2)[keys]
                :<10.5f}", end='')
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
































