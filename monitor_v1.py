#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'aragonxpd154'
__date__ = '26-09-2018'
__version__ = '1.0.8'

import gpiozero as gpio
import RPi.GPIO as GPIO
import subprocess as sp
import multiprocessing as mp
import sys
import threading as t
import time
import queue as q
# import numpy as np
# import matplotlib.pyplot as plt
# import pandas as pd
from datetime import datetime

if sys.version_info[0] < 3:
    import Tkinter as tk
    from Tkinter import messagebox
else:
    import tkinter as tk
    from tkinter import messagebox


def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)


tk.Canvas.create_circle = _create_circle

# TESTES v
_run = 1
# TESTES ^

class GUI():
    def __init__(self, master):
        self.gui = master
        # self.gui.config(cursor='none')
        # Define a resolução com base na resolução do sistema
        self.gui.geometry('{}x{}'.format(self.gui.winfo_screenwidth(),
                          self.gui.winfo_screenheight()))
        # Define que a janela não terá como redimensionar
        self.gui.resizable(0, 0)
        # Nome da Janela
        self.gui.title('Monitor MKE')
        self.w = self.gui.winfo_screenwidth()
        self.h = self.gui.winfo_screenheight()
        self.pos_x, self.pos_y = (self.w / 6), (self.h - 350)
        # Informa que será fullscreen
        self.gui.attributes('-fullscreen', True)
        self.gui.protocol('WM_DELETE_WINDOW', self.quit)
        
    def quit(self):
        if messagebox.askyesno('Monitor IP', 'Tem certeza que quer sair?'):
            _run = 0
            GPIO.cleanup()
            self.gui.destroy()
            self.gui.quit()
            

class Monitor(GUI):
    def __init__(self, master):
        super().__init__(master)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Pino 38 na Placa
        self.pin_reset = 20
        GPIO.setup(self.pin_reset, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # Variavel de Controle de Erro de Conexão
        self.gui = master
        self.alarm_set = True
        self.flag = False
        # Fila de IPs
        self.my_q = q.Queue()
        # Lista de IPs que falharem
        self.ips_failed = []
        # IPs de TESTE
        # Funciona só no Python 3.6+
        # self.ips = ['204.2.156.127', '8.8.8.8', '127.0.0.1', '216.58.202.3']
        # self.ips = ['10.7.0.85','10.7.0.250','10.7.0.81','127.0.0.1']
        # IPs das MKE
        self.ips = ['10.7.0.74', '10.17.1.4', '10.37.0.24', '10.27.0.6']
        self.servers = ['BKPVIX', 'CAC', 'COL', 'LIN']
        # Objeto circular correspondente a cada placa
        self.server = []
        self.server_name = []
        self.conx_line = []
        self.info = []
        # LEDs de conexão
        for ipq in self.ips:
            self.my_q.put(ipq)
        self.buzz = 26
        GPIO.setup(self.buzz, GPIO.OUT)
        GPIO.output(self.buzz, GPIO.HIGH)
        self.file = None
        self.canvas = tk.Canvas(self.gui, width=self.w, height=self.h, bg='#D6D6D6')
        #self.canvas.grid()
        self.canvas.place(x=0, y=0)
        self.disable_alarm = tk.Button(self.canvas, width=15, text='Desativar Alarme', font=('Arial', 12, 'bold'), command=self.alarm_off)   
        self.disable_alarm.place(x=10, y=1040)
        self.init_server()
        GPIO.add_event_detect(self.pin_reset, GPIO.RISING, callback=self.check_ips_failed, bouncetime=300)
        self.thread_check()
    
    # Cria todos os poligonos que definem as MKE e o Status do Programa
    def init_server(self):
        init_y = (self.pos_y + 150)
        for i in range(len(self.servers)):
            init_x = (self.pos_x) * (1 + i)
            srv = self.canvas.create_circle(150 + init_x, init_y, 100,
                                            fill='gray', outline='black',
                                            width=2)
            self.server.append(srv)
            srv_name = self.canvas.create_text(150 + init_x, init_y,
                                               font=('Arial', 38, 'bold'),
                                               fill='white', text=self.servers[i])
            self.server_name.append(srv_name)
            self.warning = self.canvas.create_rectangle(200, 150, 1680, 500,
                                                        fill='gray',
                                                        outline='gray')
            self.info = self.canvas.create_text(950, 350, text='',
                                                fill='white',
                                                font=('Arial', 88, 'bold'))
            conx = self.canvas.create_line(150 + (self.pos_x * (1 + i)),
                                           self.pos_y, (self.w / 2),
                                           (self.h / 2), dash=(20, 3),
                                           width=4)
            self.conx_line.append(conx)
        self.ledTX = self.canvas.create_circle(150 + self.pos_x * 5, init_y, 50, fill='gray',
                                               outline='black', width=1)
        self.stat = self.canvas.create_text(150 + self.pos_x * 5, init_y, font=('Arial', 12, 'bold'),
                                            fill='black', text='Status OK')

    def check_ping(self, ip):
        stat = None
        passed = False
        while _run:
            if ip not in self.ips_failed:
                cmd = 'ping -c 2 -s 8 -W 5 -q ' + ip
                # print('{} is pinging.'.format(ip))
                try:
                    sp.check_output(cmd.split())
                except sp.CalledProcessError:
                    if self.flag is True:
                        pass
                    else:
                        self.flag = True
                    # Alerta de Erro
                    self.canvas.itemconfigure(self.conx_line[self.ips.index(ip)],
                                              fill='red')
                    self.canvas.itemconfigure(self.server[self.ips.index(ip)],
                                              fill='red')
                    # Cria uma variavel com o index do ip que falhou
                    self.ips_failed.append(ip)
                    d = datetime.now()
                    self.file = open('/home/pi/Monitor/log.txt', 'a')
                    self.file.write('Perda de conectividade em {} às {} \n'.format(self.servers[self.ips.index(ip)], d.strftime('%H:%M:%S - %d-%b-%Y')))
                else:                    
                    # Informa esta tudo OK
                    self.canvas.itemconfigure(self.conx_line[self.ips.index(ip)],
                                              fill='green')
                    self.canvas.itemconfigure(self.server[self.ips.index(ip)],
                                              fill='green')
            if self.flag is True:
                self.call_buzz()
                self.canvas.itemconfigure(self.warning, fill='red')
                self.canvas.itemconfigure(self.info, text='CHECAR GANG')
            # Informa que esta OK
            if not self.ips_failed and self.flag is False:
                self.canvas.itemconfigure(self.warning, fill='green')
                self.canvas.itemconfigure(self.info, text='REMOTE CASTING OK')
            time.sleep(2)
        # self.gui.after(1500, self.check_ping, ip)

    def alarm_off(self):
        if messagebox.askyesno('Alarme', 'Desativar/Ativar Alarme?'):
            if self.alarm_set is True:
                self.alarm_set = False
            else:
                self.alarm_set = True
            alarm_status = self.disable_alarm.cget('text')
        if alarm_status == 'Desativar Alarme':
            self.disable_alarm.config(text='Ativar Alarme')
        else:
            self.disable_alarm.config(text='Desativar Alarme') 

    def thread_check(self):
        while not self.my_q.empty():
            ip_c = self.my_q.get()
            thread = t.Thread(target=self.check_ping, args=(ip_c,))
            thread.daemon = True
            thread.start()
            time.sleep(0.1)
        running = t.Thread(target=self.running)
        running.daemon = True
        running.start()
        buzz = t.Thread(target=self.call_buzz)
        buzz.daemon = True
        buzz.start()

    def call_buzz(self):
        if self.alarm_set is True:
            GPIO.output(self.buzz, GPIO.LOW)
            time.sleep(0.5)
            GPIO.output(self.buzz, GPIO.HIGH)
            time.sleep(0.5)   

    def running(self):
        while _run:
            stc = self.canvas.itemcget(self.ledTX, 'fill')
            st = 'green' if stc == 'orange' else 'orange'
            self.canvas.itemconfigure(self.ledTX, fill=st)
            time.sleep(0.5)
        # self.gui.after(600, self.running)

    def check_ips_failed(self, reset):
        while self.ips_failed:
            for ip_f in self.ips_failed:
                self.ips_failed.remove(ip_f)    
                time.sleep(0.1)
        if not self.ips_failed:
            self.flag = False

def main():
    root = tk.Tk()
    GUI(root)
    Monitor(root)
    root.mainloop()


if __name__ == '__main__':
    main()
