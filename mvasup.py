import math
import numpy

class Norm:
    def __init__(self,name='Support',location='norm/'):
        self.__sig=0
        self.__avg=0
        self.__max_col=0
        self.__min_col=0
        self.__variable_names=0
        self.__read=False
        self.__file_name=location+name+'.csv'

    def Read(self):
        f = open(self.__file_name)
        header = f.readline()
        var = header.split(',')
        for i in range(len(var)):
            var[i] = var[i].replace('\n','')
        data=numpy.loadtxt(self.__file_name,delimiter=',',skiprows=1)
        self.__variable_names=numpy.array(var)
        self.__avg=data[0,:]
        self.__sig=data[1,:]
        self.__read=True
        return var
        
       
    def Standardization(self,X,var=0):
        variable_size=len(X[0])
        sample_size=len(X)
        print ('Detected Variable Size: ',variable_size,'and Sample Size: ', sample_size)
        if self.__read==False:
            sum_col = [0]*variable_size
            sum_square_col = [0]*variable_size
            for i in range(sample_size):
                for j in range(variable_size):
                    sum_col[j]+=X[i][j]
                    sum_square_col[j]+=X[i][j]*X[i][j]
            self.__avg = numpy.array([x / sample_size for x in sum_col])
            self.__sig = numpy.array([math.sqrt(x / sample_size) for x in sum_square_col])
            self.__variable_names = numpy.array(var)
            numpy.savetxt(self.__file_name,(self.__variable_names,self.__avg,self.__sig),delimiter=',', fmt="%s")

        for i in range(sample_size):
            for j in range(variable_size):
                X[i][j] = (X[i][j]-self.__avg[j])/self.__sig[j]
                
        for i in range(variable_size):
            print (self.__variable_names[i],self.__avg[i],self.__sig[i])
            
           
        return X

    def Normalization(self,X,var):
        variable_size=len(X[0])
        sample_size=len(X)
        print ('Detected Variable Size: ',variable_size,'and Sample Size: ', sample_size)
        self.__max_col = numpy.amax(X,axis=0)
        self.__min_col = numpy.amin(X,axis=0)
        self.__variable_names = numpy.array(var)

        for i in range(len(X)):
            for j in range(len(X[i])):
                X[i][j] = (X[i][j]-self.__min_col[j])/(self.__max_col[j]-self.__min_col[j])

            
        for i in range(len(var)):
            print (var[i],self.__max_col[i],self.__min_col[i])

        numpy.savetxt(self.__file_name,(self.__variable_names,self.__avg,self.__sig),delimiter=',', fmt="%s")
        
        return X

def CorrectNames(variable_names):
    for i in range(len(variable_names)):
        variable_names[i]=variable_names[i].replace('(','')
        variable_names[i]=variable_names[i].replace(')','')
        variable_names[i]=variable_names[i].replace('&','')
        variable_names[i]=variable_names[i].replace('$','')
        variable_names[i]=variable_names[i].replace('[','')
        variable_names[i]=variable_names[i].replace(']','')
        variable_names[i]=variable_names[i].replace('-','')
        variable_names[i]=variable_names[i].replace('<','')
        variable_names[i]=variable_names[i].replace('>','')
        variable_names[i]=variable_names[i].replace('*','')

    return variable_names
