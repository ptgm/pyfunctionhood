import tkinter as tk
from hassediagram import *
import sys


def GUI_mode():

    def get_parents():
        try:
            idim = int(varDimension.get())
            hd = HasseDiagram(idim)
            f = Function.fromString(idim, varFunction.get())
            s1Parents, s2Parents, s3Parents = hd.get_f_parents(f)
            lParents = ['R1 ' + str(f) for f in s1Parents]\
                    + ['R2 ' + str(f) for f in s2Parents]\
                    + ['R3 ' + str(f) for f in s3Parents]
            output = '** Parents(f) ***\n' + '\n'.join(lParents)
        except ValueError as e:
            output = "ERROR! " + str(e)
        outputText.delete(1.0, "end")  # Clear previous output
        outputText.insert(1.0, output)

    def get_children():
        try:
            idim = int(varDimension.get())
            hd = HasseDiagram(idim)
            f = Function.fromString(idim, varFunction.get())
            s1Children, s2Children, s3Children = hd.get_f_children(f)
            lChildren = ['R1 ' + str(f) for f in s1Children]\
                    + ['R2 ' + str(f) for f in s2Children]\
                    + ['R3 ' + str(f) for f in s3Children]
            output = '** Children(f) ***\n' + '\n'.join(lChildren)
        except ValueError as e:
            output = "ERROR! " + str(e)
        outputText.delete(1.0, "end")  # Clear previous output
        outputText.insert(1.0, output)

    def default_values():
        varFunction.set('{{1,2,3},{1,3,4},{2,3,4}}')
        varDimension.set('4')
        outputText.delete(1.0, "end")  # Clear previous output
        outputText.insert(1.0, '')

    def set_infimum():
        try:
            idim = int(varDimension.get())
            hd = HasseDiagram(idim)
            f = hd.get_infimum()
            varFunction.set(str(f))
        except ValueError as e:
            output = "ERROR! " + str(e)

    def set_supremum():
        try:
            idim = int(varDimension.get())
            hd = HasseDiagram(idim)
            f = hd.get_supremum()
            varFunction.set(str(f))
        except ValueError as e:
            output = "ERROR! " + str(e)

    def close_window():
        """
        Close the main window (exits the interface).
        """
        root.destroy()

    # Create the main window
    root = tk.Tk()
    root.title("pyFunctionHood GUI")

    root.grid_columnconfigure(0, minsize=1, weight=0)
    root.grid_columnconfigure(1, minsize=1, weight=1)
    root.grid_columnconfigure(2, minsize=1, weight=1)

    row = 0
    # Entry field for user function
    labelDimension = tk.Label(root, text="Dimension")
    labelDimension.grid(row=row, column=0, sticky='w')
    labelFunction = tk.Label(root, text="Monotone Boolean Function")
    labelFunction.grid(row=row, column=1, columnspan=2)

    row += 1
    # Spinbox with Dimension
    varDimension = tk.IntVar(value=4) # default dimension
    spinboxDimension = tk.Spinbox(root, from_=2, to=14, textvariable=varDimension, width=6)
    spinboxDimension.grid(row=row, column=0, sticky='w')
    varFunction = tk.StringVar(value='{{1,2,3},{1,3,4},{2,3,4}}')
    entryFunction = tk.Entry(root, textvariable=varFunction, width=48)
    entryFunction.grid(row=row, column=1, columnspan=2)

    row += 1
    bottomFrame = tk.Frame(root, padx=5, pady=5)
    bottomFrame.grid(row=row, columnspan=2)

    row = 0
    # Buttons for Infimum/Supremum
    buttonInfimum = tk.Button(bottomFrame, text="Set Infimum", command=set_infimum)
    buttonInfimum.grid(row=row, column=0)
    buttonSupremum = tk.Button(bottomFrame, text="Set Supremum", command=set_supremum)
    buttonSupremum.grid(row=row, column=1)

    row += 1
    canvas = tk.Canvas(bottomFrame, height=2, bg="darkgray")  # Adjust height and color
    canvas.grid(row=row, columnspan=3, sticky="ew", pady=10)

    row += 1
    # Buttons to call parents/children methods
    buttonParents = tk.Button(bottomFrame, text="Generate Parents", command=get_parents)
    buttonParents.grid(row=row, column=0)
    buttonChildren = tk.Button(bottomFrame, text="Generate Children", command=get_children)
    buttonChildren.grid(row=row, column=1)

    row += 1
    # Text area with grid placement and set state to disabled
    outputText = tk.Text(bottomFrame, width=60, height=10)#, state="disabled")
    outputText.grid(row=row, columnspan=2)  # Span across two columns
#    scrollbar = tk.Scrollbar(bottomFrame)
#    outputText.config(yscrollcommand=scrollbar.set)
#    scrollbar.config(command=outputText.yview)

    row += 1
    # Default values
    buttonDefault = tk.Button(bottomFrame, text="Default values", command=default_values)
    buttonDefault.grid(row=row, column=0)
    # Close button
    buttonClose = tk.Button(bottomFrame, text="Close", command=close_window)
    buttonClose.grid(row=row, column=1)

    # Run the main loop
    root.mainloop()

#--------------------------------------------------------------------

def usage():
    print('\nFor graphical mode, run without arguments: python', sys.argv[0])
    print('\nFor command line mode, use the following arguments:')
    print('Usage example: python', sys.argv[0], '<type>', '<dimension>', '<function>')
    print(' <type>:      [p]arents or [c]hildren')
    print(' <dimension>: 4')
    print(' <function>:  "{{1,2,3},{1,3,4},{2,3,4}}"')
    sys.exit(1)

def command_line_mode():
    if len(sys.argv) != 4:
        print('ERROR: invalid number of arguments!')
        usage()
    if sys.argv[1] not in ('p','parents','c','children'):
        print('ERROR: invalid <type>')
        usage()

    ndim = int(sys.argv[2])
    hd = HasseDiagram(ndim)
    f = Function.fromString(ndim, sys.argv[3])
    if sys.argv[1] in ('p','parents'):
        s1Parents, s2Parents, s3Parents = hd.get_f_parents(f)
        lParents = ['R1 ' + str(f) for f in s1Parents]\
                 + ['R2 ' + str(f) for f in s2Parents]\
                 + ['R3 ' + str(f) for f in s3Parents]
        print('\n'.join(lParents))
    else:
        s1Children, s2Children, s3Children = hd.get_f_children(f)
        lChildren = ['R1 ' + str(f) for f in s1Children]\
                  + ['R2 ' + str(f) for f in s2Children]\
                  + ['R3 ' + str(f) for f in s3Children]
        print('\n'.join(lChildren))

    


#--------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) == 1: 
        GUI_mode()
    else:
        command_line_mode()
