# pyMonitorSOCKET

Este código é uma aplicação GUI para o Raspberry Pi que monitora as conexões com servidores especificados. O objetivo é verificar se cada servidor está online ou não, e exibir o status na interface gráfica. A aplicação utiliza bibliotecas como gpiozero, RPi.GPIO, subprocess, multiprocessing, threading, time, queue e tkinter. Ela também contém métodos para criar círculos no canvas da tela, verificar se a versão do Python é 3.x, encerrar a aplicação com mensagem de confirmação, limpar o GPIO e controlar o buzzer do Raspberry Pi.

A função GUI é responsável por criar a interface gráfica do programa. Ela inicializa a janela, define sua resolução, tamanho, se pode ser redimensionada, nome e se é fullscreen. A função também contém um método "quit" que é chamado ao clicar no botão de sair da janela.

A classe Monitor estende a classe GUI e adiciona informações e comportamentos relacionados ao monitoramento de conexões. Ele inicializa e configura os pinos do Raspberry Pi para o uso como entradas ou saídas. Ele também define variáveis e estruturas de dados para armazenar informações sobre as conexões e desenha elementos na interface gráfica (circulos, linhas de conexão, informações de status, etc.). Além disso, a classe contém uma fila de endereços IPs a serem monitorados e informações adicionais sobre os servidores que estão sendo monitorados.

A função "\_create_circle" adiciona um método "create_circle" ao objeto Canvas do Tkinter, permitindo que sejam desenhados círculos na interface gráfica.

    #!/usr/bin/python3: é o caminho para o interpretador Python 3.
    # -*- coding: utf-8 -*-: especifica que o código está escrito em utf-8.
    __author__ = '+', __date__ = '26-09-2018' e __version__ = '1.0.8': informações sobre o autor, data e versão do código.
    import gpiozero as gpio, import RPi.GPIO as GPIO, import subprocess as sp, import multiprocessing as mp, import sys, import threading as t, import time, import queue as q: importação de bibliotecas necessárias para o funcionamento do código.
    if sys.version_info[0] < 3: e import Tkinter as tk: verifica a versão do Python e importa a biblioteca Tkinter, se a versão for menor que 3.
    def _create_circle(self, x, y, r, **kwargs):: define uma função para criar um círculo no canvas.
    tk.Canvas.create_circle = _create_circle: adiciona a função _create_circle ao método create_circle do Canvas.
    class GUI():: define a classe GUI que será usada como base para a classe Monitor.
    class Monitor(GUI):: define a classe Monitor que herda da classe GUI.
    self.pin_reset = 20: define o pino de reset como 20.
    GPIO.setup(self.pin_reset, GPIO.IN, pull_up_down=GPIO.PUD_UP): configura o pino de reset como entrada e com pull-up.
    self.ips = ['10.7.0.74', '10.17.1.4', '10.37.0.24', '10.27.0.6']: define uma lista de IPs que serão monitorados.
    self.servers = ['BKPVIX', 'CAC', 'COL', 'LIN']: define uma lista de nomes de servidores que correspondem a cada IP na lista anterior.
    self.buzz = 26: define o pino do buzzer como 26.
    GPIO.setup(self.buzz, GPIO.OUT): configura o pino do buzzer
