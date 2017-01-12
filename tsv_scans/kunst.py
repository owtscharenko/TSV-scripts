'''

@author: Wilhelm Linac
'''

import time
import logging
import csv
import matplotlib.pyplot as plt
import multiprocessing
import progressbar
import os.path
import numpy as np

from basil.dut import Dut


class Plot(object):
    
    def Readout(self,Vin, Iin, Vout1, *file):
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        z = [[] for z in range(0, nf)]
        v = [[] for v in range(0, nf)]
        w = [[] for w in range(0, nf)]
        csvfilearray = [[] for csvfilearray in range(0, nf)]
        csvfile = [None] * nf
        plots = [None] * nf
        label = []
        color = []
        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
            
        for i in range(0,nf):
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                for row in plots[i]:
                    csvfilearray[i].append(row)
                    if 'Regulator 2 output voltage[V]' in csvfilearray[0] and 'Regulator 1 load current [A]' in csvfilearray[0]:
                        Iload1 = 3
                        Vout2 = 4
                        x[i].append(row[Vin])
                        y[i].append(row[Iin])
                        z[i].append(row[Vout1])
                        v[i].append(row[Iload1])
                        w[i].append(row[Vout2])
                    elif 'Regulator 1 load current [A]' in csvfilearray[0] and 'Regulator 2 output voltage[V]' not in csvfilearray[0]:
                        Iload1 = 3
                        x[i].append(row[Vin])
                        y[i].append(row[Iin])
                        z[i].append(row[Vout1])
                        v[i].append(row[Iload1])
                    elif 'Regulator 1 load current [A]' not in csvfilearray[0] and 'Regulator 2 output voltage[V]' in csvfilearray[0]:
                        Vout2 = 3
                        x[i].append(row[Vin])
                        y[i].append(row[Iin])
                        z[i].append(row[Vout1])
                        w[i].append(row[Vout2])                    
                    elif 'Regulator 1 load current [A]' not in csvfilearray[0] and 'Regulator 2 output voltage[V]' not in csvfilearray[0]:
                        x[i].append(row[Vin])
                        y[i].append(row[Iin])
                        z[i].append(row[Vout1])
                    else:
                        raise RuntimeError('Error occured')
        for i in range(0, nf):
            print csvfilearray[i]
                    
            
        
    
    
    
    
    def VrefVout(self, pfad, *file):
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Current Supply Mode', 'Voltage Supply Mode']
        color = ['r', 'b']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        
        path = os.getcwd()
        if pfad not in path:
            path = os.getcwd() + r'\Messungen' + pfad
        os.chdir(path)
        print os.getcwd()
        print nf
        for i in range(0, nf):
            print os.getcwd()
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                for row in plots[i]:
                    #print row
                    x[i].append(row[0])
                    y[i].append(row[1])
 
        #print plots
         
            #plt.figure(z)
            #ax = plt.subplot(111)
            plt.plot(x[i], y[i], color[i], label = label[i])
          #  plt.plot(x[i], v[i], color[i] + '--', label = '2, ' + label[i])
             
        #plt.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.legend(loc='lower right')
        plt.xlabel('Reference voltage [V]')
        plt.ylabel('Output voltage [V]')
        plt.title('Vref vs Vout')
        plt.grid()
        plt.axis([0.4,0.66,0.8,1.32])
        plt.tight_layout()
        plt.savefig('VrefVout.pdf')
            
    
    def Lineregulation_CURR(self, Vref, Iin, Vin, Vout, Vout2, *file):
        
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        v = [[] for v in range(0, nf)]
        w = [[] for w in range(0, nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Vref = 600 mV', 'Vref = 500 mV']
        color = ['r', 'b', 'g']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        
        #=======================================================================
        # path = os.getcwd()
        # if pfad not in path:
        #     path = os.getcwd() + r'\Messungen' + pfad
        # os.chdir(path)
        # print os.getcwd()
        # print nf
        #=======================================================================
        for i in range(0, nf):
            print os.getcwd()
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                next(plots[i], None)
                for row in plots[i]:
                    #print row
                    x[i].append(row[Iin])
                    y[i].append(row[Vout])
                    v[i].append(row[Vin])
                    #w[i].append(row[Vout2])
 
        #print plots
         
            #plt.figure(z)
            #ax = plt.subplot(111)
        plt.plot(x[0], y[0], color[0], label = 'Iin vs Vout, ' + label[0])
        plt.plot(x[0], v[0], color[1] + '--', label = 'Iin vs Vin' + label[0])
        #plt.plot(x[0], w[0], color[1], label = 'Iin vs Vout, ' + label[1])
             
        #plt.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.legend(loc='lower right')
        plt.xlabel('Input current [A]')
        plt.ylabel('Voltage [V]')
        plt.title('Line Regulation, two parallel ShuLDOs')
        plt.grid()
        plt.axis()#    [0,0.95,0,2])
        plt.tight_layout()
        #plt.show()
        plt.savefig('CMode_LineReg_Vref_500mV.pdf')
        
        
    
    
    def Lineregulation_VOLT(self, pfad, Vref, z, *file):
        
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Iload = 0 mA', 'Iload = 250 mA', 'Iload = 500 mA']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        print csvfile
        
        path = os.getcwd()
        if pfad not in path:
            path = os.getcwd() + r'\Messungen' + pfad
        os.chdir(path)
        print os.getcwd()
        
        for i in range(0, nf):
            print file[i]
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                for row in plots[i]:
                    #print row
                    x[i].append(row[0])
                    y[i].append(row[2])
                print x[i]
                print y[i]

        #print plots
        
            plt.figure(z)
            #ax = plt.subplot(111)
            plt.plot(x[i], y[i], label = label[i])
            
        #plt.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.legend(loc='lower right')
        plt.xlabel('Input voltage [V]')
        plt.ylabel('Output voltage [V]')
        plt.title('Line Regulation, Vref = ' + str(Vref) + ' mV')
        plt.grid()
        plt.axis([1.2,2,0.7,1.4])
        plt.tight_layout()
        #plt.show()
        plt.savefig('VMode_LineReg_Vref' + str(Vref) +'mV.pdf')
        
        
    def Loadregulation_CURR(self, pfad, z, *file):
        
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        v = [[] for v in range(0,nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Vref = 500 mV', 'Vref = 600 mV', 'Vref = 660 mV']
        color = ['r', 'b', 'g']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        print csvfile
        
        path = os.getcwd()
        if pfad not in path:
            path = os.getcwd() + r'\Messungen' + pfad
        os.chdir(path)
        print os.getcwd()
        
        for i in range(0, nf):
            print file[i]
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                next(plots[i], None)
                for row in plots[i]:
                    #print row
                    x[i].append(row[3])
                    y[i].append(row[2])
                    v[i].append(row[0])
                    #v[i].append(row[1])

        #print plots
        
            plt.figure(z)
            #ax = plt.subplot(111)
            plt.plot(x[i], y[i], color[i], label = 'ILoad vs Vout, ' + label[i])
            plt.plot(x[i], v[i], color[i] + '--', label = 'Iload vs Vin, ' + label[i])
            
        #plt.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.legend(loc='best')
        plt.xlabel('Load current [A]')
        plt.ylabel('Output voltage [V]')
        plt.title('Iin = 0.5 A, Iload vs. Vout & Iload vs. Vin')
        plt.grid()
        plt.axis([0,-0.45, 0.6, 1.6])
        #plt.tight_layout()
        #plt.show()
        #plt.gca().invert_xaxis()
        plt.savefig('CMode_LoadReg.pdf')
        
    def Loadregulation_CURR_parallel(self, pfad, z, *file):
        
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        v = [[] for v in range(0,nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Vref = 500 mV', 'Vref = 600 mV', 'Vref = 660 mV']
        color = ['r', 'b', 'g']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        print csvfile
        
        path = os.getcwd()
        if pfad not in path:
            path = os.getcwd() + r'\Messungen' + pfad
        os.chdir(path)
        print os.getcwd()
        
        for i in range(0, nf):
            print file[i]
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                next(plots[i], None)
                for row in plots[i]:
                    #print row
                    x[i].append(row[3])
                    y[i].append(row[2])
                    v[i].append(row[0])
                    #v[i].append(row[1])

        #print plots
        
            plt.figure(z)
            #ax = plt.subplot(111)
            plt.plot(x[i], y[i], color[i], label = 'ILoad vs Vout, ' + label[i])
            plt.plot(x[i], v[i], color[i] + '--', label = 'Iload vs Vin, ' + label[i])
            
        #plt.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.legend(loc='best')
        plt.xlabel('Load current [A]')
        plt.ylabel('Output voltage [V]')
        plt.title('Iin = 1 A, Iload vs. Vout & Iload vs. Vin')
        plt.grid()
        plt.axis([0,-0.45, 0.6, 1.6])
        #plt.tight_layout()
        #plt.show()
        #plt.gca().invert_xaxis()
        plt.savefig('CMode_LoadReg_parallel.pdf')    
    
    def Loadregulation_VOLT(self, pfad, Vref, z, *file):
        
        nf = len(file)
        x = [[] for x in range(0, nf)]
        y = [[] for y in range(0, nf)]
        csvfile = [None]*len(file)
        plots = [None]*len(file)
        label = ['Vref = 500 mV', 'Vref = 600 mV', 'Vref = 660 mV']

        
        for i in range(0, nf):
            csvfile[i] = 'csvfile' + str(i)
        print csvfile
        
        path = os.getcwd()
        if pfad not in path:
            path = os.getcwd() + r'\Messungen' + pfad
        os.chdir(path)
        print os.getcwd()
        
        for i in range(0, nf):
            print file[i]
            with open(file[i], 'rb') as csvfile[i]:
                plots[i] = csv.reader(csvfile[i], delimiter=',')
                next(plots[i], None)
                for row in plots[i]:
                    x[i].append(row[3])
                    y[i].append(row[2])

        
            plt.figure(z)
            plt.plot(x[i], y[i], label = label[i])
            
        plt.legend(loc='best')
        plt.xlabel('Load current [A]')
        plt.ylabel('Output voltage [V]')
        plt.title('Vin = 1.5 V, Iload vs. Vout')
        plt.grid()
        plt.axis([0, -0.45, 0.85, 1.4])
        plt.tight_layout()
        #plt.show()
        #plt.gca().invert_xaxis()
        plt.savefig('VMode_LoadReg.pdf')
        
if __name__ == '__main__':
    plot = Plot()
    
    plot.Readout(0, 1, 2, 'CMode_500_mV_LineReg.csv', 'CMode_600_mV_LineReg.csv', 'CMode_660_mV_LineReg.csv', 'CMode_600_500_mV_LoadReg.csv') 
    #plot.Lineregulation_CURR(660, 1, 0, 2, 3, 'CMode_500_mV_LineReg.csv')
    #plot.Loadregulation_VOLT('\Load Regulation\Voltage Supply', 500, 1, 'VMode_500_mV_LoadReg.csv', 'VMode_600_mV_LoadReg.csv', 'VMode_660_mV_LoadReg.csv')
    #plot.Loadregulation_CURR('\Load Regulation\Current Supply', 1, 'CMode_500_mV_LoadReg.csv', 'CMode_600_mV_LoadReg.csv', 'CMode_660_mV_LoadReg.csv')
    #plot.Loadregulation_CURR_parallel('\Load Regulation\Current Supply', 1, 'CMode_600_500_mV_LoadReg_parallel2.csv', 'CMode_500_600_mV_LoadReg_parallel2.csv')
    #plot.Readout(r'\Messungen\Line Regulation\Current Supply', 'CMode_600_mV_LineReg.csv', 'CMode_500_mV_LineReg.csv', 'CMode_600_500_mV_LineReg_parallel.csv')
    #plot.VrefVout('\VrefVout', 'VrefVout_Curr.csv', 'VrefVout_Volt.csv')