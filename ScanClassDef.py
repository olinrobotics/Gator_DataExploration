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
        
        #Iterates through the data corresponding to each angle of the lidar scan to extract the x, y and z data for
        #the left and right lidar for each scan, puts them together into a tuple and appends the tuple to the appropriate list
        for i in range(6,len(raw_series)):

            #Splits up the original string from the raw data that contains the six numbers that make up x, y and z for the left and right lidar
            raw_data=raw_series[i][1:-1].split(';')
            
            #Creates tuple of x, y and z for the particular left lidar scan 
            left_data=(float(raw_data[0]), float(raw_data[1]), float(raw_data[2]))
            self.left.append(left_data)
            
            #Creates tuple of x, y and z for the particular right lidar scan 
            right_data=(float(raw_data[3]), float(raw_data[4]), float(raw_data[5]))
            self.right.append(right_data)

        #Sends the data to the ThresholdPoints function to remove lidar data outside the range of the camera
        self.ThresholdPoints(thresholds)


    def __string__(self):

        #TODO: This function doesn't actually work the way I intended it. Since it is not crucial, I have left it alone but it DOES NOT WORK

        message="This is a scan taken on " + str(self.datetime) + " when vehicle had gps coordinates of latitude " + str(self.gps[0]) + " and longitude " + str(self.gps[1]) +". Vehicle had heading of " + str(self.heading) + " and velocity of " + str(self.velocity) + "."

        return str(message)

    def GetLidarData(self, lidar, axis):
        """
        This function takes in the lidar and cartesian axis (e.g. x-axis data, y-axis data) for the data that is desired and retrieves the appropriate data.

        lidar: String that indicates the lidar that is desired; Should only be either 'left' or 'right'; Case does not matter
        axis: String that indicates the cartesian axis for the desired data; Should only be 'x', 'y' or 'z'. Case again does not matter

        Returns: A list of float numbers that are the position between the particular lidar scan and the rear axle of the vehicle.
        """
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

        return L_list

    def PlotFFT(self, lidar, axis, Plot):
        """
        This function plots the dFFT of the lidar data using numpy's np.fft.fft. 

        lidar: Desired lidar from which the data will be analyzed (either 'left' or 'right')
        axis: Desired cartesian axis of the data (either 'x', 'y' or 'z')
        Plot: Boolean True or False value that indicates whether you want the function to also plot the fft for you.

        Returns a list of sampled frequencies and the results of the dfft.
        """

        #Uses the existing GetLidarData points method to grab the list of appropriate lidar data
        L_list=self.GetLidarData(lidar, axis)

        #Computes the dfft
        fft_comp=np.fft.fft(L_list)

        #Retrieves data on the frequencies at which were sampled
        frequencies=np.fft.fftfreq(len(fft_comp))

        #If the Plot variable is True, plot the data
        if Plot==True:
            plt.figure(0)
            plt.plot(frequencies, np.abs(fft_comp))
            plt.show()

        #Returns the sampled frequencies as real numbers and the fourier transforms in complex numbers.
        return frequencies, fft_comp

    def ThresholdPoints(self, thresholds):

        """
        This function uses provided thresholds to directly modify self.left and self.right in order to remove any lidar scan points not within the desired range. 

        thresholds: List of thresholding values in the following order: minimum value of x, maximum value of x, minimum value of y, maximum value of y.

        Does not return anything since the function is directly modifying the Scan class attributes
        """

        #Assigns the various threshold values to appropriately named holders for easier reading
        x_min=thresholds[0]
        x_max=thresholds[1]
        y_min=thresholds[2]
        y_max=thresholds[3]

        #Iterates through every point in self.left
        for point_L in self.left:

            #If the x, or y value falls outside the desired range (i.e. either too high or too low for x or y), remove the point entirely
            if point_L.x<x_min or point_L.x>x_max or point_L.y<y_min or point_L.y>y_max:
                self.left.remove(point_L)

        #Does the same thing for self.right
        for point_R in self.right:
            if point_R.x<x_min or point_R.x>x_max or point_R.y<y_min or point_R.y>y_max:
                self.right.remove(point_R)