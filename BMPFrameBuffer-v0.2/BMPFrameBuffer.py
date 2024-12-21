import struct
import random
import math

class MemoryWindow:

    def __init__(self):

        self._bits = 0
        self._bytes = 0

        self._buffer = None
        self._windowBuffer = None

        self._columns = 0
        self._rows = 0

        self._windowColumnStart = 0
        self._windowColumnEnd = 0
        self._windowRowStart = 0
        self._windowRowEnd = 0
        self._windowColumns = 0
        self._windowRows = 0

    def setWindow(self,columnStart,columnEnd,rowStart,rowEnd,copy=True):
        
        if columnStart < 0: columnStart *= -1
        if rowStart < 0: rowStart *= -1
    
        if columnStart > columnEnd:
            tmp = columnEnd
            columnEnd = columnStart
            columnStart = tmp
        
        if rowStart > rowEnd:
            tmp = rowEnd
            rowEnd = rowStart
            rowStart = tmp

        if columnEnd > self._columns: columnEnd = self._columns
        if rowEnd > self._rows: rowEnd = self._rows

        self._windowColumnStart = columnStart
        self._windowColumnEnd = columnEnd
        self._windowRowStart = rowStart
        self._windowRowEnd = rowEnd
        self._windowColumns = self._windowColumnEnd - self._windowColumnStart
        self._windowRows = self._windowRowEnd - self._windowRowStart
        self._windowColumnSize = self._bytes
        self._windowRowSize = self._windowColumns * self._bytes
        
        if self._buffer == None:
            self._buffer = bytearray(self._columns*self._rows*self._bytes)

        self._windowBuffer = bytearray(self._windowColumns*self._windowRows*self._bytes)
        
        if copy == False: return

        nByte = 0
        R = self._windowRowStart * (self._columns*self._bytes)
        for r in range(self._windowRows):            
            C = self._windowColumnStart * self._bytes
            for c in range(self._windowColumns):
                for b in range(self._bytes):
                    self._windowBuffer[nByte] = self._buffer[R+C+b]
                    nByte += 1
                C += self._bytes
            R +=  self._columns*self._bytes

    def flush(self):
        nByte = 0
        R = self._windowRowStart * (self._columns*self._bytes)
        for r in range(self._windowRows):            
            C = self._windowColumnStart * self._bytes
            for c in range(self._windowColumns):
                for b in range(self._bytes):
                    self._buffer[R+C+b] = self._windowBuffer[nByte]
                    nByte += 1
                C += self._bytes
            R +=  self._columns*self._bytes

class BMPFrameBuffer:

    def __init__(self,columns,rows,bits=32,window=None):

        self._window = window
        if self._window == None: self._window = MemoryWindow()
        self._window._columns = columns
        self._window._rows = rows
        self._window._bits = bits
        self._window._bytes = math.ceil(self._window._bits/8)
        self._window._buffer = None 

        self._flipV = -1
        self._flipH = 1

        self._rotation = 0
        self._xOrigin = 0
        self._yOrigin = 0

        self._color =  None
        self._tmpColor = None

        self._fillColor = None
        self._tmpFillColor = None

        self._thikness = 0
        self._tmpThikness = 0

        self._roundConers = True

        self._charTable = None

    def setWindow(self,startX,endX,startY,endY,copy=True):
        self._window.setWindow(startX,endX,startY,endY,copy)

        if self._fillColor != None and copy == False:
            self.setThikness(0)
            tmpColor = self._color
            self._color = self._fillColor
            for r in range(self._window._windowRows):
                for c in range(self._window._windowColumns):
                    self.setPixel(c,r)
            self._color = tmpColor
            self.restoreThikness()
            return

        if self._fillColor == None and copy == False:

            for nByte in range(len(self._window._windowBuffer)):
                self._window._windowBuffer[nByte] = random.randbytes(1)[0]
            return


    def setColor(self,R,G,B,isFillColor=False):
        
        color = None

        if self._window._bits == 8: #--- ? ATENÇÃO AS CORES ESTÃO ERRADAS
            encodedData = ((R<<5)&0xE0 | (G<<2)&0X1C | (B>>5)&0x3 )&0xFF
            color = int(encodedData).to_bytes(1,'big')

        if self._window._bits == 16: #OK
            color = int(((R&0xF8)<<8) | ((G&0xFC)<<3) | (B>>3)).to_bytes(2,'little')
            
        if self._window._bits == 24: #OK
            color = int( R<<16 | G<<8 | B ).to_bytes(3,'little')

        if self._window._bits == 32: #OK
            color = int( (0xFF<<24|R<<16|G<<8|B) ).to_bytes(4,'little')

        if isFillColor == False:
            self._color = bytearray(color)
        else:
            self._fillColor = bytearray(color)

    def restoreColor(self,isFillColor=False):
        if isFillColor == False:
            self._color = self._tmpColor
        else:
            self._fillColor = self._tmpFillColor

    def setThikness(self,thikness):
        self._tmpThikness = self._thikness
        if thikness == 1: thikness=2
        self._thikness = thikness

    def restoreThikness(self):
        self._thikness = self._tmpThikness

    def setRotation(self,degress=0,xOrigin=0,yOrigin=0):
            self._rotation = degress
            self._xOrigin = xOrigin
            self._yOrigin = yOrigin

    def setPixel(self,xPos,yPos):
        if self._color == None: return

        if self._rotation > 0:

            cos = math.cos(self._rotation*math.pi/180)
            sin = math.sin(self._rotation*math.pi/180)            
            
            cosX = cos*(xPos-self._xOrigin)
            sinX = sin*(xPos-self._xOrigin)
            cosY = cos*(yPos-self._yOrigin)
            sinY = sin*(yPos-self._yOrigin)

            xPos = int( cosX - sinY ) + self._xOrigin 
            yPos = int( sinX + cosY ) + self._yOrigin

        if xPos < 0 or xPos > self._window._windowColumns-1 - self._thikness: return
        if yPos < 0 or yPos > self._window._windowRows-1 - self._thikness: return

        
        xPos *= self._window._windowColumnSize
        yPos *= self._window._windowRowSize

        for nByte in range(self._window._bytes):
            self._window._windowBuffer[int(self._flipH*(xPos))+int(self._flipV*(yPos))+nByte] = self._color[nByte]

        tR = 0
        while tR < self._thikness:
            tC = 0
            while tC < self._thikness:
                for nByte in range(self._window._bytes):
                    self._window._windowBuffer[int(self._flipV*(yPos-(tR*self._window._windowRowSize)))+int(self._flipH*(xPos-(tC*self._window._windowColumnSize)))+nByte] = self._color[nByte]
                tC += 1
            tR += 1
        return

    def drawLine(self,startX,endX,startY,endY):
        width = (endX-startX)
        height = (endY-startY)

        len = math.sqrt(math.pow(width,2) + math.pow(height,2))
        rowInc = height/len
        rowStep = 1
        colInc = width/len
        colStep = 1

        for _ in range(int(len)):
            self.setPixel(startX+int(colStep),startY+int(rowStep)) 
            rowStep += rowInc
            colStep += colInc


    def drawLineH(self,xPos,yPos,size):
        rangeStep = int(self._thikness/2)
        if self._thikness == 0: rangeStep = 1
        if size < 0: rangeStep *= -1

        for step in range(0,size,rangeStep):
            self.setPixel(xPos+step,yPos)
    
    def drawLineV(self,xPos,yPos,size):
        rangeStep = int(self._thikness/2)
        if self._thikness == 0: rangeStep = 1
        if size < 0: rangeStep *= -1

        for step in range(0,size,rangeStep):
            self.setPixel(xPos,yPos+step)

    def drawRectangle(self,xPos,yPos,width,height,fill=False):
        if fill == True:
            tmpColor = self._color
            self._color = self._fillColor
            rangeStep = self._thikness
            if self._thikness == 0: rangeStep = 1
            if height < 0: rangeStep *= -1            

            for step in range(0,height,rangeStep):
                self.drawLineH(xPos,yPos+step,width)
            self._color = tmpColor

        incW = 1
        incH = 1
        if width < 0: incW *= -1
        if height < 0: incH *= -1

        self.drawLineH(xPos,yPos,width)
        self.drawLineH(xPos,yPos+height,width+incW)
        self.drawLineV(xPos,yPos,height)
        self.drawLineV(xPos+width,yPos,height+incH)


    def drawSquare(self,xPos,yPos,size,fill=False):
        self.drawRectangle(xPos,yPos,size,size,fill)
 

    def drawCircle(self,xPos,yPos,radius,fill=False):
        angle = 0
        while angle <= 360:
            x = math.ceil(radius * math.cos(angle))
            y = math.ceil(radius * math.sin(angle))
            
            if fill == True:
                tmpColor = self._color
                self._color = self._fillColor
                self.setThikness(0)
                n = 0
                while n < radius:
                    x = math.floor(n * math.cos(angle))
                    y = math.floor(n * math.sin(angle))
                    self.setPixel(xPos+x,yPos+y)
                    n += 1
                self.restoreThikness()
                self._color = tmpColor
            
            self.setPixel(xPos+x,yPos+y)
            
            angle += 0.2


    def loadFont(self,file,debug=False):
        self._charTable = open(file,'rb')
        
        self._charTableMatrix = file[file.rfind('-')+1:file.rfind('.bmp')].split('X')
        self._charTableMatrix[0] = int(self._charTableMatrix[0])
        self._charTableMatrix[1] = int(self._charTableMatrix[1])

        self._charTable.seek(14) #jump to dib header
        dib_header = struct.unpack_from('<I I I H H I I I I I I',self._charTable.read(40))

        if dib_header[4] != self._window._bits:
            self._charTable.close()
            self._charTable = None
            print("loadFont() WARNING: charTable not same Bit depth !!!")
            return

        self._charTable = self._charTable.read()
        self._charTableWidth = dib_header[1]
        self._charTableHeight = dib_header[2]
        self._charTableCharWidth = int(self._charTableWidth/self._charTableMatrix[0])
        self._charTableCharHeight = int(self._charTableHeight/self._charTableMatrix[1])

        if debug == True:
            for nByte in range(self._charTableWidth*self._charTableHeight*self._window._bytes):
                self._window._windowBuffer[nByte] = self._charTable[nByte]

    def printChar(self,xPos,yPos,char):
        if self._charTable == None: return

        charIndexs = b' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
        charIndex = charIndexs.find(char)
 
        atRow =  math.floor(charIndex/self._charTableMatrix[0])
        atCol = charIndex - self._charTableMatrix[0]*atRow

        tmpColor = self._color
        self.setThikness(0)
        sRow = atRow * self._charTableCharWidth * self._charTableWidth * self._window._bytes        
        for r in range(self._charTableCharHeight):
            sCol = atCol * self._charTableCharHeight * self._window._bytes
            sRow += self._charTableWidth * self._window._bytes
            for c in range(self._charTableCharWidth):
                if self._charTable[-(sRow)+sCol] != 0x00:
                    self.setPixel(xPos+c-1,yPos+r)
                sCol += self._window._bytes
        self.restoreThikness()
        self._color = tmpColor


    def printChars(self,xPos,yPos,chars):
        if self._charTable == None: return

        for char in chars:
            self.printChar(xPos,yPos,char)
            xPos += self._charTableCharWidth

    def flush(self):
        self._window.flush()

    def saveBitmap(self,file):
        raw_size = self._window._columns*self._window._rows*self._window._bytes

        out_file = open(file,'wb')
        # --- THE BITMAP HEADER ---
        #--BMP HEADER 14 bytes
        bmp_header = struct.pack('<2s I 2s 2s I',
            b'BM',       #BmDescription
            14 + 40,      #FileSize #THE SISZE OF THE HEADER
            b'\x00\x00',  #ApplicationSpecific_1
            b'\x00\x00',  #ApplicationSpecific_2
            14+40        #PixelArrayOffset
        )
        #--DIB HEADER 40 bytes
        dib_header = struct.pack('<I I I H H I I I I I I',
            40,                             #DibHeaderBytes
            self._window._columns,          #ImageWidth
            self._window._rows,             #ImageHeight
            1,                              #ColorPlanes
            self._window._bits,             #BitsPerPixel
            0,                              #BiRGB
            0,                       #RawBitmapSize
            self._window._columns,          #PrintResolutionH
            self._window._rows,             #PrintResolutionV
            256,                              #NumberOfColorsInPallet
            256                               #ImportantColors
        )

        #WRITE TO FILE
        out_file.write(bmp_header)
        out_file.write(dib_header)

        if self._window._bits == 8:
            out_file.write(self.pallet_8bits_color())

        out_file.write(self._window._buffer)

        out_file.close

    def pallet_8bits_color(self):
        paleta = bytearray()
        for i in range(256):
            R = (i>>5) * 36
            G = ((i>>2)& 0x7) * 36
            B = (i&0x3) * 85
            paleta.append(B&0XFF) #RED
            paleta.append(G&0xFF) #GREEN
            paleta.append(R&0xFF) #BLUE
            paleta.append(0) #?
        return paleta
    
    def pallet_8bits_grey(self):
        paleta = bytearray()
        for i in range(256):
            paleta.append(i) #RED
            paleta.append(i) #GREEN
            paleta.append(i) #BLUE
            paleta.append(0) #?
        return paleta
    




