from tkinter import *
from PIL import ImageTk
import tkinter.messagebox
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter.filedialog import *
import os
import glob
try:
    import Image
except ImportError:
    from PIL import Image


class LabelTool:
    def __init__(self, master):
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent, width=1800, height=1800)
        self.frame.pack(fill=BOTH, expand=0)
        # self.parent.resizable(width = False, height =False)
        # initialize global state
        self.List = 0
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = None
        self.imageName = ''
        self.img = None
        self.labelFileName = ''
        self.tkImg = None
        self.tmp = []
        self.currentLabelClass = ''
        self.cla_can_temp = []
        self.classCandidateFileName = 'class.txt'
        # initialize mouse state
        self.STATE = dict()
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0
        # reference to bbox
        self.bboxIdList = []
        self.bboxIdList1 = []
        self.bboxId = None
        self.bboxIdo = None
        self.bboxIdx = None
        self.bboxList = []
        self.bboxList1 = []
        self.hl = None
        self.vl = None
        self.scale = 1
        # ----------------- GUI stuff ---------------------
        self.bun = Button(self.frame, text='OpenDir', command=self.loadDir)
        self.bun.grid(row=0, column=0, sticky=E)
        self.but = Button(self.frame, text='Open', command=self.OpenImg)
        self.but.grid(row=0, column=1, sticky=W)
        self.var = StringVar()
        self.Lab = Label(self.frame, bg='red', width=10, textvariable=self.var)
        self.Lab.grid(row=0, column=2)
        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross', scrollregion=(0, 0, 5000, 5000))
        self.mainPanel.focus_set()
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.mainPanel.bind("<Button-3>", self.number)
        self.parent.bind("<Escape>", self.cancelBBox)
        self.parent.bind("<q>", self.prevImage)
        self.parent.bind("<e>", self.nextImage)
        self.parent.bind("<a>", self.moveoval)
        self.parent.bind("<d>", self.moveoval)
        self.parent.bind("<w>", self.moveoval)
        self.parent.bind("<s>", self.moveoval)
        self.hbar = Scrollbar(self.frame, orient=HORIZONTAL)
        self.hbar.grid(row=5, column=1, sticky=NW+E)
        self.hbar["command"] = self.mainPanel.xview
        self.vbar = Scrollbar(self.frame, orient=VERTICAL)
        self.vbar.grid(row=2, column=1, sticky=NE+S)
        self.vbar["command"] = self.mainPanel.yview
        self.mainPanel.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.mainPanel.grid(row=1, column=1, rowspan=4, sticky=W+N)
        # choose class
        self.className = StringVar()
        self.classCandidate = ttk.Combobox(self.frame, state='readonly', textvariable=self.className)
        self.classCandidate.bind("<<ComboboxSelected>>", self.setClass)
        self.classCandidate.grid(row=1, column=2)
        if os.path.exists(self.classCandidateFileName):
            with open(self.classCandidateFileName) as cf:
                for line in cf.readlines():
                    tmp = line.strip('\n')
                    self.cla_can_temp.append(tmp)
        self.classCandidate['values'] = self.cla_can_temp
        self.classCandidate.current(0)
        self.currentLabelClass = self.classCandidate.get()
        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text='Bounding boxes:')
        self.lb1.grid(row=3, column=2,  sticky=W+N)
        self.listbox = Listbox(self.frame, width=22, height=12)
        self.scrolly = Scrollbar(self.frame)
        self.listbox.configure(yscrollcommand=self.scrolly.set)
        self.scrolly['command'] = self.listbox.yview
        self.scrolly.grid(row=4, column=3, sticky=E+NS)
        self.listbox.grid(row=4, column=2, sticky=N+S)
        self.btnDel = Button(self.frame, text='Delete', command=self.delBBox)
        self.btnDel.grid(row=5, column=2, sticky=W+E+N)
        self.btnClear = Button(self.frame, text='ClearAll', command=self.clearBBox)
        self.btnClear.grid(row=6, column=2, sticky=W+E+N)
        self.btnsave = Button(self.frame, text='Save', command=self.saveImage)
        self.btnsave.grid(row=7, column=2, sticky=W+E+N)
        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row=8, column=1, columnspan=2, sticky=W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width=10, command=self.prevImage)
        self.prevBtn.pack(side=LEFT, padx=5, pady=3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width=10, command=self.nextImage)
        self.nextBtn.pack(side=LEFT, padx=5, pady=3)
        self.progLabel = Label(self.ctrPanel, text="Progress:     /    ")
        self.progLabel.pack(side=LEFT, padx=5)
        self.tmpLabel = Label(self.ctrPanel, text="Go to Image No.")
        self.tmpLabel.pack(side=LEFT, padx=5)
        self.idxEntry = Entry(self.ctrPanel, width=5)
        self.idxEntry.pack(side=LEFT)
        self.goBtn = Button(self.ctrPanel, text='Go', command=self.gotoImage)
        self.goBtn.pack(side=LEFT)
        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side=RIGHT)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(4, weight=1)

    def loadDir(self):
        s = filedialog.askdirectory()
        self.parent.focus()
        self.category = str(s)
        self.imageDir = os.path.join(r'.\Images', '%s' % self.category)
        self.imageList = glob.glob(os.path.join(self.imageDir, "*.jpg"))
        if len(self.imageList) == 0:
            print('No .JPG images found in the specified dir!')
            return
        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)
        # set up output dir
        self.outDir = os.path.join(r'./Labels', '%s' % self.category)
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        self.loadImage()
        print('%d images loaded from %s' % (self.total, s))

    def OpenImg(self):
        default_dir = r'C:\Users\admin\Desktop'
        fns = filedialog.askopenfilenames(filetypes=[('all', '*.*'), ('JPG', '*.jpg')],
                                          title=u'选择图片', initialdir=(os.path.expanduser(default_dir)))
        self.cur = 1
        self.imageList = list(fns)
        category = os.path.split(self.imageList[0])[0]
        self.outDir = os.path.join(r'./Labels', '%s' % category)
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        self.loadImage()

    def loadImage(self):
        # load image
        imagePath = self.imageList[self.cur-1]
        self.img = Image.open(imagePath)
        (width, height) = self.img.size
        if width > 1600 or height > 800:
            self.scale = 800 / height
            width = width * self.scale
            height = height * self.scale
            self.img = self.img.resize((int(width), int(height)), Image.ANTIALIAS)
        else:
            self.scale = 1
        self.tkImg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width=self.tkImg.width(), height=self.tkImg.height())
        self.mainPanel.create_image(0, 0, image=self.tkImg, anchor=NW)
        self.progLabel.config(text="%04d/%04d" % (self.cur, self.total))
        # load labels
        self.clearBBox()
        self.imageName = os.path.split(imagePath)[-1].split('.')[0]
        labelname = self.imageName+'.pts'
        self.labelFileName = os.path.join(self.outDir, labelname)
        if os.path.exists(self.labelFileName):
            self.loadrect_point()
        else:
            for i in range(20):
                labelname = self.imageName + "_" + str(i) + '.pts'
                self.labelFileName = os.path.join(self.outDir, labelname)
                if os.path.exists(self.labelFileName):
                    self.loadrect_point()

    def loadrect_point(self):
        with open(self.labelFileName) as f:
            for (i, line) in enumerate(f):
                tmp2 = [t.strip() for t in line.split()]
                tmp = [t for t in tmp2]
                self.bboxList.append(tuple(tmp))
                if len(tmp) == 4:
                    tmpId = self.mainPanel.create_rectangle(int(tmp[0])*self.scale, int(tmp[1])*self.scale,
                                                            int(tmp[2])*self.scale, int(tmp[3])*self.scale, width=1,
                                                            outline='green')
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '%d %d %d %d' % (int(tmp[0]), int(tmp[1]), int(tmp[2]), int(tmp[3])))
                    self.listbox.itemconfig(len(self.bboxIdList)-1, fg='green')
                if len(tmp) == 2:
                    tmpId = self.mainPanel.create_oval(int(tmp[0])*self.scale - 1, int(tmp[1])*self.scale - 1,
                                                       int(tmp[0])*self.scale + 1, int(tmp[1])*self.scale + 1,
                                                       width=1, outline='red')
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '%d %d' % (int(tmp[0]), int(tmp[1])))
                    self.listbox.itemconfig(len(self.bboxIdList)-1, fg='red')

    def saveImage(self):
        if not self.listbox.get(0, END):
            return
        elif len(self.listbox.get(0, END)) == 6:
            labelname = self.imageName + '.pts'
            self.labelFileName = os.path.join(self.outDir, labelname)
            with open(self.labelFileName, 'w') as f:
                for i in self.listbox.get(0, END):
                    f.write(''.join(map(str, i)) + '\n')
        elif len(self.listbox.get(0, END)) % 6 == 0:
            index = 0
            count = 0
            f_in = open(self.category + '\\' + self.imageName + "_%d.pts" % index, "w")
            for i in self.listbox.get(0, END):
                count += 1
                f_in.write(''.join(map(str, i)) + '\n')
                # 读满6行之后，行计数置零，小文件序号加一，创建一个新的文件写信息
                if count == 6:
                    f_in.close()
                    count = 0
                    index += 1
                    f_in = open(self.category + '\\' + self.imageName + "_%d.pts" % index, "w")
            f_in.close()
            os.remove(self.category + '\\' + self.imageName + "_%d.pts" % index)

        else:
            tkinter.messagebox.showwarning('警告', '标注不完善')
            return False
        print('Image No. %d saved' % self.cur)
        self.bboxList.clear()

    def mouseClick(self, event):
        if self.currentLabelClass == 'Face':
            self.List = 0
            if self.STATE['click'] == 0:
                self.STATE['x'], self.STATE['y'] = event.x, event.y
            else:
                x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
                y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
                self.bboxList.append([x1, y1, x2, y2])
                self.bboxIdList.append(self.bboxId)
                self.bboxId = None
                self.listbox.insert(END, '%d %d %d %d' % (int(x1/self.scale), int(y1/self.scale), int(x2/self.scale),
                                                          int(y2/self.scale)))
                self.listbox.itemconfig(len(self.bboxIdList)-1, fg='green')
                self.classCandidate.current(1)
                self.currentLabelClass = self.classCandidate.get()
            self.STATE['click'] = 1-self.STATE['click']
        elif self.currentLabelClass == 'Point':
            self.bboxIdo = self.mainPanel.create_oval(event.x-1, event.y-1, event.x+1, event.y+1,
                                                      width=1, outline='red')
            self.List += 1
            self.bboxList.append([event.x, event.y])
            self.listbox.insert(END, '%d %d' % (int(event.x/self.scale), int(event.y/self.scale)))
            self.bboxIdList.append(self.bboxIdo)
            self.listbox.itemconfig(len(self.bboxIdList)-1, fg='red')
            if self.List == 5:
                self.classCandidate.current(0)
                self.currentLabelClass = self.classCandidate.get()
                self.List = 0
        elif self.currentLabelClass == 'Change':
            sel = self.listbox.curselection()
            if len(sel) != 1:
                return
            idx = int(sel[0])
            self.mainPanel.delete(self.bboxIdList[idx])
            self.bboxIdList.pop(idx)
            self.bboxList.pop(idx)
            self.listbox.delete(idx)
            self.bboxIdx = self.mainPanel.create_oval(event.x-1, event.y-1, event.x+1, event.y+1,
                                                      width=1, outline='blue')
            self.listbox.insert(idx, '%d %d' % (int(event.x/self.scale), int(event.y/self.scale)))
            self.bboxIdList.insert(idx, self.bboxIdx)
            self.bboxList.insert(idx, [event.x, event.y])

    def moveoval(self, event):
        if event.keysym == "w":
            self.mainPanel.move(self.bboxIdList[-1], 0, -1)
            self.bboxList[-1][1] -= 1
        elif event.keysym == "s":
            self.mainPanel.move(self.bboxIdList[-1], 0, 1)
            self.bboxList[-1][1] += 1
        elif event.keysym == "a":
            self.mainPanel.move(self.bboxIdList[-1], -1, 0)
            self.bboxList[-1][0] -= 1
        elif event.keysym == "d":
            self.mainPanel.move(self.bboxIdList[-1], 1, 0)
            self.bboxList[-1][0] += 1
        self.listbox.delete(END)
        self.listbox.insert(END, '%d %d' % (int(self.bboxList[-1][0]/self.scale), int(self.bboxList[-1][1]/self.scale)))

    def number(self):
        sel = self.listbox.curselection()
        print(sel)
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.var.set(idx)
        for i in range(len(self.bboxIdList)):
            self.mainPanel.itemconfig(self.bboxIdList[i], outline='red')
        self.mainPanel.itemconfig(self.bboxIdList[idx], outline='black')

    def mouseMove(self, event):
        self.disp.config(text='x: %d, y: %d' % (event.x, event.y))
        if self.tkImg:
            if self.currentLabelClass == 'Face':
                if self.STATE['click'] == 1:
                    if self.bboxId:
                        self.mainPanel.delete(self.bboxId)
                    self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], event.x, event.y,
                                                                  width=1, outline ='green')

    def cancelBBox(self):
        if self.STATE['click'] == 1:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1:
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, END)
        self.bboxIdList = []
        self.bboxList = []
        self.classCandidate.current(0)
        self.currentLabelClass = self.classCandidate.get()

    def prevImage(self):
        status = self.saveImage()
        if status:
            if self.cur > 1:
                self.cur -= 1
                self.loadImage()
                self.classCandidate.current(0)
                self.currentLabelClass = self.classCandidate.get()

    def nextImage(self):
        status = self.saveImage()
        if status:
            if self.cur < self.total:
                self.cur += 1
                self.loadImage()
                self.classCandidate.current(0)
                self.currentLabelClass = self.classCandidate.get()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

    def setClass(self):
        self.currentLabelClass = self.classCandidate.get()
        print('set label class to :', self.currentLabelClass)


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width=True, height=True)
    root.mainloop()
