from tkinter import *
from tkinter import ttk

root = Tk()

# content = ttk.Frame(root, padding=(3,3,12,12))
# frame = ttk.Frame(content, borderwidth=5, relief="sunken", width=200, height=100)
# namelbl = ttk.Label(content, text="Name")
# name = ttk.Entry(content)

# onevar = BooleanVar()
# # twovar = BooleanVar()
# threevar = BooleanVar()
# 
# # onevar.set(True)
# twovar.set(False)
# threevar.set(True)
# 
# one = ttk.Checkbutton(content, text="One", variable=onevar, onvalue=True)
# two = ttk.Checkbutton(content, text="Two", variable=twovar, onvalue=True)
# three = ttk.Checkbutton(content, text="Three", variable=threevar, onvalue=True)
# ok = ttk.Button(content, text="Okay")
# cancel = ttk.Button(content, text="Cancel")
# 
# content.grid(column=0, row=0, sticky=(N, S, E, W))
# frame.grid(column=0, row=0, columnspan=3, rowspan=2, sticky=(N, S, E, W))
# namelbl.grid(column=3, row=0, columnspan=2, sticky=(N, W), padx=5)
# name.grid(column=3, row=1, columnspan=2, sticky=(N, E, W), pady=5, padx=5)
# one.grid(column=0, row=3)
# two.grid(column=1, row=3)
# three.grid(column=2, row=3)
# ok.grid(column=3, row=3)
# cancel.grid(column=4, row=3)


def borderFrame(parent, bg='#ff4095', border='#66cdaa', 
        padx_bg=5, pady_bg=5, padx_b=0.2, pady_b=0.2):
    """When creating a subframe, center it with frame.grid(row=2, column=2)"""

    canvas = Frame(parent, bg=bg)
    
    # fill border sides
    blank_frame1 = Frame(canvas, bg=border)
    blank_frame2 = Frame(canvas, bg=border)
    blank_frame3 = Frame(canvas, bg=border)
    blank_frame4 = Frame(canvas, bg=border)
    blank_frame1.grid(row=2, column=1, ipadx=padx_b, sticky=N+S)
    blank_frame2.grid(row=2, column=3, ipadx=padx_b, sticky=N+S)
    blank_frame3.grid(row=1, column=2, ipady=pady_b, sticky=W+E)
    blank_frame4.grid(row=3, column=2, ipady=pady_b, sticky=W+E)

    
    # fill background sides
    blank_frame5 = Frame(canvas, bg=bg)
    blank_frame6 = Frame(canvas, bg=bg)
    blank_frame7 = Frame(canvas, bg=bg)
    blank_frame8 = Frame(canvas, bg=bg)
    blank_frame5.grid(row=2, column=0, padx=padx_bg)
    blank_frame6.grid(row=2, column=4, padx=padx_bg)
    blank_frame7.grid(row=0, column=2, pady=pady_bg)
    blank_frame8.grid(row=4, column=2, pady=pady_bg)

    # fill border corners
    blank_frame9 = Frame(canvas, bg=border)
    blank_frame10 = Frame(canvas, bg=border)
    blank_frame11 = Frame(canvas, bg=border)
    blank_frame12 = Frame(canvas, bg=border)
    blank_frame9.grid(row=1, column=1, ipadx=padx_b/3, ipady=pady_b/3, sticky=S+E)
    blank_frame10.grid(row=1, column=3, ipadx=padx_b/3, ipady=pady_b/3, sticky=S+W)
    blank_frame11.grid(row=3, column=1, ipadx=padx_b/3, ipady=pady_b/3, sticky=N+E)
    blank_frame12.grid(row=3, column=3, ipadx=padx_b/3, ipady=pady_b/3, sticky=N+W)

    return canvas

# have borderFrame do all the work of maintaining a border and background
mode_frame = borderFrame(root, bg="#4C4C4C", border='#C9C9C9',
        padx_bg=2, pady_bg=2)

message = StringVar()
mode_label = Label(mode_frame, textvariable=message)
mode_label.config(width=18)
message.set("Mode")
mode_label.grid(row=2, column=2)
mode_frame.grid(sticky=W+E)

recent_frame = borderFrame(root, bg="#4C4C4C", border='#C9C9C9',
        padx_bg=4, pady_bg=4)
recent_wrapper = Frame(recent_frame)

for i in range(3):
    recentCmd = StringVar()
    label = Label(recent_wrapper, textvariable=recentCmd)
    label.config(width=17)
    recentCmd.set("Recent cmd " + str(i))
    label.grid(row=i)
recent_frame.grid(row=1, sticky=W+E)
recent_wrapper.grid(row=2, column=2)

status_frame = borderFrame(root, bg="#4C4C4C", border='#C9C9C9',
        padx_bg=4, pady_bg=4)

status = StringVar()
status_label = Label(status_frame, textvariable=status)
status_label.config(width=18)
status.set("Processing...")
status_label.grid(row=2, column=2)
status_frame.grid(row=2, sticky=W+E)





# recent_frame = Frame(root, bg='#4C4C4C')
# status_frame = Frame(root, bg='#4C4C4C')



# hello = StringVar()
# mode_label = Label(back, textvariable=hello)
# hello.set("Hello World")
# mode_comp = Frame(back, bg='k)
# mode_label.config(width=15)
# mode_label.grid(row=0, column=0, pady=10)

# back.pack()

root.mainloop()
