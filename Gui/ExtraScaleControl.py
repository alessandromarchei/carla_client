
#===============================================
# ===          CARLA emulator client         ===
# ===   ----------------------------------   ===
# ===     Custom scale control definition    ===
#===============================================

from tkinter import *
from tkinter import ttk
from types import NoneType

class ExtraScaleControlItem(Frame):

    #--------------------------
    #--- Public properties  ---
    #--------------------------

    # --- Control identifier
    identifier = None

    # --- Scale title control object
    scaleTitle = None

    # --- Scale control object
    scaleControl = None

    # --- Panel title main part
    title = None

    # --- Scale trough image
    imageTrough = None
    
    # --- Scale slider image
    imageSlider = None

    # --- Current title text (including value)
    scaleValueText = None

    # --- Scale value divider
    divider: 1

    # --- Currently set scale value
    currentValue = None

    # --- Extra command to be executed
    extraCmd = None

    # --- Custom scale style object
    style = None

    # --- Custom scale style name
    styleName = None

    # --- control background color (unselected)
    unselectedcolor = None

    # --- control background color (selected)
    selectedcolor = None

    # --- control foreground color (selected)
    selectedFgColor = None

    # --- Minimum scale value
    minV: None

    # --- Maximum scale value
    maxV: None

    # --- Used inc/dec keys description label
    labelKeys: None

    #--------------------
    #--- Constructor  ---
    #--------------------

    # --- name: control name
    # --- title: scale' title string
    # --- identifier: parent panel identifier
    # --- imgTrough: image for scale axis
    # --- imgSlider: image for scale slider
    # --- bgcolor: control background color (unselected)
    # --- selectedcolor: control background color (selected)
    # --- minv: minimum scale value
    # --- maxv: maximum scale value
    # --- initv: initial scale value
    # --- keysdesc: used keys description string
    # --- divider: scale value divider
    # --- boldTitle: make control title bold
    # --- cmd: extra command to be executed
    def __init__(self, parent, name, identifier, title,
                 imgTrough, imgSlider, bgcolor, selectedcolor, 
                 selectedFgColor, minv, maxv, initv,  
                 divider, keysdesc, hasReleaseButton = False, 
                 boldTitle = False, cmd = None):

        super().__init__(parent, background=bgcolor)

        self.id = identifier
        self.title = title
        self.divider = divider
        self.extraCmd = cmd
        self.unselectedcolor = bgcolor
        self.selectedcolor = selectedcolor
        self.selectedFgColor = selectedFgColor
        self.minV = minv
        self.maxV = maxv

        self.scaleValueText = StringVar()
        self.scaleValueText.set("{0:.1f}".format(float(initv)))

        # Create required style
        self.imageTrough = PhotoImage(master = self, file=imgTrough)
        self.imageSlider = PhotoImage(master = self, file=imgSlider)

        self.style = ttk.Style(master=parent)
         
        try:
            # create scale elements
            self.style.element_create('{}{}.Scale.trough'.format(identifier, name), 'image', self.imageTrough)
            self.style.element_create('{}{}.Scale.slider'.format(identifier, name), 'image', self.imageSlider)
        
        except Exception as e:

            print("Style is already created")

        self.styleName = "{}{}.Horizontal.TScale".format(identifier, name)
        
        self.style.configure(self.styleName, background='yellow', foreground='yellow')

            # create custom layout
        self.style.layout(self.styleName,
                [('{}{}.Scale.trough'.format(identifier, name), {'sticky': 'we'},),
                    ('{}{}.Scale.slider'.format(identifier, name),
                    {'side': 'left', 'sticky': '',
                        'children': [('{}{}.Horizontal.Scale.label'.format(identifier, name), {'sticky': ''})]
                    })])

        frameTitle = Frame(self, background=bgcolor)

        self.highFrame = Frame(frameTitle, background=bgcolor)
        self.highFrame.columnconfigure(0, weight=1)
        self.highFrame.columnconfigure(1)
        self.highFrame.pack(fill="x")

        if boldTitle == False:
            self.scaleTitle = Label(self.highFrame, text="{}:".format(title), bg=bgcolor, 
                                   font=("Roboto", 10))
        else:
            self.scaleTitle = Label(self.highFrame, text="{}:".format(title), 
                                   font=("Roboto", 10), bg=bgcolor)

        self.scaleTitle.grid(row=0, column=0, sticky='nwse')

        hasReleaseButton = False

        if hasReleaseButton == True:
            button_border = Frame(self.highFrame, highlightbackground = "white", 
                         highlightthickness = 1, bd=0, background='white', width=5, height=2)        
            button_border.grid(row=0, column=1, sticky="w", pady=3, padx=3)
            releaseButton = ttk.Button(button_border, text="Rls", width=3,
                style='W.TButton', command=self.onFastRelease)
            releaseButton.pack(fill='both')

        #self.labelKeys = Label(frameTitle, text=keysdesc, 
        #    wraplength=190, bg=bgcolor, font=("Roboto", 10))
       
        #self.labelKeys.pack(anchor="w", fill="x")

        frameTitle.pack(anchor="w", fill="x")

        self.valueTitle = Label(self, text="0.000", bg=bgcolor, font=("Roboto", 10),
                                textvariable=self.scaleValueText)
        self.valueTitle.pack(anchor="w", padx=5)

        self.currentValue = StringVar()
        self.currentValue.set(str(initv))

        self.scaleControl = Scale(self, from_=minv, to=maxv, 
                         background=self.unselectedcolor,
                         foreground='white', showvalue=False, relief='ridge', sliderrelief='raised',
                         orient="horizontal", 
                         command=self.onScaleChanged,
                         #style=self.styleName, 
                         highlightthickness=0,
                         troughcolor='lavender',
                         variable=self.currentValue)

        self.scaleControl.pack(anchor="w", fill="both")

        self.scaleTitle.bind("<Button-1>", self.onControlSelected)
        #self.labelKeys.bind("<Button-1>", self.onControlSelected)
        self.valueTitle.bind("<Button-1>", self.onControlSelected)
        self.bind("<Button-1>", self.onControlSelected)
        self.scaleControl.bind("<Button-1>", self.onControlSelected)
        self.bind('<FocusOut>', self.onLostFocus)

    # ----------------------
    # --- Public methods 
    # ----------------------

    # --- Set new control title
    # --- title: text to be set
    def setTitle(self, title):
        self.scaleTitle.config(text="{}".format(title))

    # --- Process panel selection actions
    # --- isselected: panel is selected flag
    def processPanelSelection(self, isselected):
        color = self.unselectedcolor
        colorFg = 'gray'
        width = 1
        if isselected == True:
            color = self.selectedcolor
            colorFg = self.selectedFgColor
            width = 2
        self.config(bg=color)
        self.highFrame.config(bg=color)
        self.scaleTitle.config(bg=color, fg=colorFg)
        #self.labelKeys.config(bg=color, fg=colorFg)
        self.valueTitle.config(bg=color, fg=colorFg)
        self.style.configure(self.styleName, background=color)
        self.config(highlightthickness=width)

    # -----------------------
    # --- Controls events 
    # -----------------------

    # --- Scale value is changed event handler
    # --- p: new scale value
    def onScaleChanged(self, p):
        
        text = "{0:.1f}".format(float(p) / self.divider)
        self.scaleValueText.set(text)

        if self.extraCmd is not None:
            self.extraCmd(self.id, p)

    # --- Panel selection is changed event handler
    # --- event: event parameter
    def onControlSelected(self, event):
        
        self.scaleControl.focus_set()
        self.processPanelSelection(True)

    # --- Panel is unselected event handler
    # --- event: event parameter
    def onLostFocus(self, event):
        
        self.processPanelSelection(False)

    # --- Increment / decrement scale control on keyboard events
    # --- event: increment(1) or decrement(2) signature 
    def doKeyboardAction(self, event):

        try:

            sval = self.currentValue.get()

            cval = float(sval)

            nval = cval

            if event != 3:
                if event == 1:
                    nval = cval + 1 
                else:
                    nval = cval - 1

                if float(nval) >= self.maxV:
                    nval = str(self.maxV)
        
                if float(nval) <= self.minV:
                    nval = str(self.minV)
            else:
                nval = 0;

            self.currentValue.set(nval)

            text = "{0:.1f}".format(float(nval) / self.divider)
            self.scaleValueText.set(text)

            if self.extraCmd is not None:
                self.extraCmd(self.id, float(nval) / self.divider)

        except Exception as e:

            print(e)

    # --- Set control value
    # nval: value to be set
    def setValue(self, nval):
        
        self.currentValue.set(nval * 100)

        text = "{0:.1f}".format(float(nval))
        self.scaleValueText.set(text)


    # --- Fast release button is pressed event handler
    def onFastRelease(self):

        print("Fast release")
        self.doKeyboardAction(3)