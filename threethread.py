import time
import re
import numpy as np
import random
import threading
import matplotlib.pyplot as plt
import os
beg_time = time.ctime()
beg_time = beg_time.split(' ')[-2]
beg_time = re.sub(r'[^0-9]',"",beg_time)
path = "/Users/wangyiwen/Desktop/lab/"
mili_sec = time.time()
mili_sec = mili_sec % 100000
mili_sec = round(mili_sec,2)
print("beg_time: "+str(beg_time))


def parse_txt(line):
    lst = line.split(' ')
    ang = float(lst[0])
    timestamp = float(lst[1][:-1])
    return ang,timestamp

def bilinear_res(ang1,ang3,t1,t2,t3):
    alpha1 = t2 - t1
    alpha2 = t3 - t2
    return (alpha2*ang1+alpha1*ang3)/(alpha1+alpha2)

def double_array_locate(coordinate1, direction1, angle1, coordinate2, direction2, angle2):
    """
    Get coordinate of sound source. Sound source, array1, array2 must be in `z = 0` plane.

    :param coordinate1: shape = (3,) numpy array. coordinate of 1st car.
    :param direction1: float number. direction of the 1st mic array. top view, anticlockwise is positive.
    :param angle1: float number. angle location result from 1st mic array. top view, anticlockwise is positive.
    :param coordinate2: same as 1st.
    :param direction2: same as 1st.
    :param angle2: same as 1st.
    :return coordinate of sound source.
    """
    # print(angle1,angle2)
    theta1, theta2 = direction1 + angle1, direction2 + angle2
    tan1, tan2 = np.tan(theta1), np.tan(theta2)
    cot1, cot2 = 1 / tan1, 1 / tan2
    x1, y1 = coordinate1[0], coordinate1[1]
    x2, y2 = coordinate2[0], coordinate2[1]
    x = (y2 - y1 + x1 * tan1 - x2 * tan2) / (tan1 - tan2)
    y = (x2 - x1 + y1 * cot1 - y2 * cot2) / (cot1 - cot2)
    return np.asarray([x, y, 0])


class MyThread(threading.Thread):
    def __init__(self,threadid,alpha,name_class):
        threading.Thread.__init__(self) 
        self.id = threadid
        self.alpha = alpha
        self.fst_angle = random.random()*2*np.pi - np.pi
        self.file_path = str(path + beg_time + name_class)
        self.cnt = 0;
        self.mili_sec = round(mili_sec + (random.random()/10+0.02),2)

        
        
    def run(self):
        print("Begin:  id "+str(self.id))
        f = open(self.file_path,'w')
        cnt = 0
        while cnt <= 50:
            f.write(str(self.fst_angle))
            f.write(' ')
            f.write(str(self.mili_sec))
            f.write('\n')
            f.flush()
            self.fst_angle += self.alpha*random.random()/10 - (1-self.alpha)*random.random()/10
            if self.fst_angle > np.pi:
                self.fst_angle -= np.pi*2
            self.mili_sec = round(self.mili_sec + (random.random()/10+0.05),2)
            self.cnt += 1
            cnt += 1
        f.close()
    
    

class DrawPlot(threading.Thread):
    def __init__(self,txt1,txt2):
        threading.Thread.__init__(self)
        self.txt1 = txt1
        self.txt2 = txt2

    def run(self):
        time.sleep(2)
        #wait until it begins to receive the data
        while os.path.isfile(self.txt1) == False or os.path.isfile(self.txt2) == False:
            pass
        #stupid wait until the two documents have been established
        fig,ax=plt.subplots()
        f1 = open(self.txt1,'r')
        f2 = open(self.txt2,'r')
        line1 = f1.readline()
        line2 = f2.readline()
        cnt = 0
        x_axis = []
        y_axis = []
        #x_axis = np.array(x_axis)
        #y_axis = np.array(y_axis)
        ang1 = 0
        ang2 = 0
        ang3 = 0
        tmstp1 = 0
        tmstp2 = 0
        tmstp3 = 0
        bool_cnt = 0
        while bool(line1) and bool(line2):
            time.sleep(0.5) #update the next point after every 0.5 second
            ang1,tmstp1 = parse_txt(line1)
            ang2,tmstp2 = parse_txt(line2)
            if tmstp1 == tmstp2:
                loc = double_array_locate(np.array([0,0,0]),0,np.pi/2+ang2,np.array([3,0,0]),0,np.pi/2+ang1)
                x_axis.append(loc[0])
                y_axis.append(loc[1])
                cnt += 1
                ang3 = ang1
                tmstp3 = tmstp1
                line1 = f1.readline()
                bool_cnt = 1
            elif tmstp1 < tmstp2:
                ang3 = ang1
                tmstp3 = tmstp1
                line1 = f1.readline()
            else:
                if cnt == 0:
                    line2 = f2.readline()
                else:
                    angtemp2=bilinear_res(ang3,ang1,tmstp3,tmstp2,tmstp1)
                    loc = double_array_locate(np.array([0,0,0]),0,np.pi/2+ang2,np.array([3,0,0]),0,np.pi/2+angtemp2)
                    x_axis.append(loc[0])
                    y_axis.append(loc[1])
                    cnt += 1
                    line2 = f2.readline()
                    bool_cnt = 1
            if bool_cnt == 1:
                ax.cla()
                ax.set_title("x-locate")
                ax.set_xlabel("x-locate")
                ax.set_ylabel("y-locate")
                ax.set_xlim(-10,10)
                ax.set_ylim(-5,5)
                ax.grid()
                if cnt > 0 and cnt % 10 == 0:
                 print("iteration: "+str(cnt))
                 fig_t = plt.gcf()
                 file_name = "fig" + str(cnt) + ".png"
                 plt.scatter(x_axis,y_axis,color="red")
                 plt.plot(x_axis,y_axis,label='Label')
                 fig_t.savefig(file_name,dpi=200)
                else:
                 plt.scatter(x_axis,y_axis,color="red")
                 plt.plot(x_axis,y_axis,label='Label')
                plt.xlabel("x-axis")
                plt.ylabel("y-aixs")
                #ax.plot(y1,label='train')
                #ax.plot(y2,label='test')
                ax.legend(loc='best')
                plt.pause(1)
                bool_cnt = 0
        print("Cnt: "+str(cnt))   
        f1.close()
        f2.close()




thread1 = MyThread(1,0.75,"_01.txt")
thread2 = MyThread(2,0.7,"_02.txt")
thread3 = DrawPlot(str(path + beg_time + "_01.txt"),str(path + beg_time + "_02.txt"))
thread1.start()
thread2.start()
thread3.start()
thread1.join()
thread2.join()
thread3.join()