import time
from BMPFrameBuffer import *

#from memory_profiler import profile #ADD @profile BEFORE FUNCTION NAME TO ANALYSE IT

def img128x160():
    data = BMPFrameBuffer(128,160,16) #FOR MY TFT SCREEN 160x128

    start_time = time.time()

    data = BMPFrameBuffer(128,160,16)

    data.setThikness(0)

    data.setColor(0,0,0,True)
    data.setWindow(0,128,0,160,False)

    data.drawLineH(10,10,50)

    data.setColor(255,0,0)
    data.drawLineH(40,100,100)
    data.restoreColor(True)

    data.setColor(255,255,255)
    data.setColor(0,255,0,True)
    data.drawCircle(100,100,25,True)
    data.restoreColor(True)
    
    data.setColor(127,127,127)
    data.drawLine(10,90,10,80)

    data.setColor(255,0,0,True)
    data.setColor(255,255,0)
    data.drawSquare(60,50,-40,True)


    data.setColor(255,0,255,True)
    data.setColor(200,255,255)
    data.setRotation(45,64,80)
    data.drawRectangle(64-20,80-25,40,50,True)
    data.setRotation()
    data.restoreColor(True)


    data.flush()

    data.loadFont('font16bits-20X5.bmp')
    data.setColor(0,0,255,True) 
    data.setColor(255,0,0)
    data.setWindow(1,300,1,16,False)
    data.printChars(1,1,b'HEllo World!')
    data.flush()

    data.saveBitmap('output-128x160.bmp')

    end_time = time.time()

    print("TIME ", (end_time-start_time))


img128x160()    