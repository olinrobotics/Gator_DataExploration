import datetime as dt
import numpy as np
import pylab as plt

class Scan:
    """
    This class creates an object that holds lidar scans from both front lidars and the associated vehicle characteristic
    data.
    """
    def __init__(self, raw_series):
        
        """
        This init function sets up the Scan object by extracting the gps, heading, velocity and date time data. It also
        converts the date time string into an appropriate datetime object for easier future manipulation. Does not return
        anything since this is a class init function.
        
        raw_series: a pandas series
        """
        
        #Vehicle GPS location is contained in the first 2 elements of the series as latitude then longitude
        self.gps=[float(raw_series[0]), float(raw_series[1])] 
        
        #Vehicle heading is contained in the 3rd element of the series, here converted to a float before being stored
        self.heading=float(raw_series[2])
        
        #TODO: I forgot what the 4th element is. Need to check --JP
        
        #Vehicle velocity is contained in the 5th element of the series, here converted to a float before being stored
        self.velocity=float(raw_series[4])
        
        #The date and time that data was collected is contained in the 6th element of the series, here converted to a 
        #datetime object before being stored
        self.datetime=dt.datetime.strptime(raw_series[5].replace(';', ' '), "%m/%d/%Y %I:%M %p")
        
        #Calls the subfunction that creates the left and right lidar data dictionaries
        self.MakeLidarData(raw_series)
        
    def MakeLidarData(self, raw_series):
        
        """
        This function organizes the LIDAR data into dictionaries of data for the left and right LIDARs and adds the data
        to the Scan object. Does not return anything since data is added to the object directly.
        
        raw_series: a pandas series
        """
        
        #These 8 lines create the data dictionaries for the left and right lidar data as well as the relevant x, y and z
        #data lists for the three cartesian coordinates in which data is received.
        self.left=[]
        self.right=[]
        
        left_x=[]
        left_y=[]
        left_z=[]
        
        right_x=[]
        right_y=[]
        right_z=[]
        
        #Iterates through the data corresponding to each angle of the lidar scan to extract the x, y and z data for
        #the left and right lidar for each scan and appends the data to the appropriate list
        for i in range(6,len(raw_series)):
            raw_data=raw_series[i][1:-1].split(';')
            
            left_data=(float(raw_data[0]), float(raw_data[1]), float(raw_data[2]))
            self.left.append(left_data)
            
            right_data=(float(raw_data[3]), float(raw_data[4]), float(raw_data[5]))
            self.right.append(right_data)


    def __string__(self):
        message="This is a scan taken on " + str(self.datetime) + " when vehicle had gps coordinates of latitude " + str(self.gps[0]) + " and longitude " + str(self.gps[1]) +". Vehicle had heading of " + str(self.heading) + " and velocity of " + str(self.velocity) + "."

        return str(message)

    def PlotFFT(self, lidar, axis, Plot):

        if lidar.lower()=='left':

            lidar=self.left
        else:

            lidar=self.right

        L_list=[]
        
        if axis.lower()=='x':

            for scan in lidar:
                L_list.append(scan[0])

        elif axis.lower()=='y':
            for scan in lidar:
                L_list.append(scan[1])

        else:
            for scan in lidar:
                L_list.append(scan[2])
        

        fft_comp=np.fft.fft(L_list)

        frequencies=np.fft.fftfreq(len(fft_comp))

        if Plot==True:
            plt.figure(0)
            plt.plot(frequencies, np.abs(fft_comp))
            plt.show()

        return frequencies, fft_comp