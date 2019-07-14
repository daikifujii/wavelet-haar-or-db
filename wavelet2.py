import wave
import matplotlib.pyplot as plt
import numpy as np
import pywt   
import scipy.signal as sig
import array 
import math

def get_noiz():
    path = './twincle-noise.wav'
    #path ='./output.wav'
    wf = wave.open(path, 'r')
    num_frame = wf.getnframes()
    temp = wf.readframes(num_frame)
    #print(temp)
    temp = np.frombuffer(temp,'int16')
    data = temp/(2**15)
    print('num frame noiz' ,num_frame )
    return data

def get_origin():
    path = './twincle.wav'
    wf = wave.open(path, 'r')
    num_frame = wf.getnframes()
    temp = wf.readframes(num_frame)
    temp = np.frombuffer(temp,'int16')
    data = temp/(2**15)

    return data

def get_noiz_out():
    path = './output-noise.wav'
    wf = wave.open(path, 'r')
    num_frame = wf.getnframes()
    temp = wf.readframes(num_frame)
    temp = np.frombuffer(temp,'int16')
    data = temp/(2**15)
    
    return data


def get_SN(noiz, noiz_transformed):
    num_frame = 187600

    chil = par = 0.0
    for i in range(num_frame):
        chil += noiz[i]
        par += noiz[i] - noiz_transformed[i]
    
    a  = chil**2 / par**2
    sn = math.log10(a)
    print( 'sn',sn)
    return sn


def wavelet_transform(wave, level, wavelet):
    wavelet_data = pywt.wavedec(wave, wavelet, level=level)
    return wavelet_data

def iwavelet_transform(coef, wavelet):
    iwavelet_data = pywt.waverec(coef, wavelet)
    return iwavelet_data

def filt(coef, t):
    for i in range(len(coef)):
        for j in range(len(coef[i])):
            if np.abs(coef[i][j]) <= t:
                coef[i][j] = 0
    return coef

def output_wav(buf):
    int16amp = 32768
    y = np.array([buf * int16amp],dtype="int16")

    w = wave.Wave_write("output-noise.wav")
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(22050)

    w.setnframes(len(buf))
    #w.writeframes(array.array('h',y).tostring())
    w.writeframes(y)
    w.close()



if __name__ == '__main__':
    #w = pywt.Wavelet('haar')
    w = pywt.Wavelet('db4') #chose mother wablet

    print(w)

    '''get_data'''
    noiz = get_noiz()
    org = get_origin()
    
    '''for wavelet'''
    max_level = pywt.dwt_max_level(data_len=len(noiz), filter_len=w.dec_len) 
    print('max level',max_level)
    lev = max_level     #chose under max_level 
    level = int(input('choose lebvel'))
    coef = wavelet_transform(noiz, level, w)   
    sn_list =[]
    for i in range(20):
        threshold = (i +1)/10     #chose threshold to filt 
        print('threshold',threshold)
        filt_coef = filt(coef, threshold)
        aft_wave = iwavelet_transform(filt_coef, w)
        sn = get_SN(noiz,aft_wave)
        sn_list.append (sn)
    
    print(sn_list)

    '''display'''
    #print('len_coef',len(coef),'len_coef[0]',len(coef[0]))
    #plt.plot(noiz)
    #plt.plot(org)
    #plt.plot(aft_wave)
    plt.plot(np.linspace(0.1,2.1,20) ,sn_list)
    plt.xlabel('threshold')
    plt.ylabel('SN rate')
    plt.show()
    
    '''save filted wave'''
    #print(aft_wave)
    #print(org)
    output_wav(aft_wave)

    '''get SN rate'''
    #sn = get_SN(noiz, aft_wave)
