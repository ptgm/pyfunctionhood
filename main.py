from tkinter import Tk, Label, Entry, Text, Button, Spinbox, StringVar, IntVar
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

    def close_window():
        """
        Close the main window (exits the interface).
        """
        root.destroy()

    # Create the main window
    root = Tk()
    root.title("pyFunctionHood GUI")

    row = 0
    # Entry field for user function
    labelFunction = Label(root, text="Function:")
    labelFunction.grid(row=row, column=0, sticky="W") # Align left
    varFunction = StringVar(value='{{1,2,3},{1,3,4},{2,3,4}}')
    entryFunction = Entry(root, textvariable=varFunction)
    entryFunction.grid(row=row, column=1)

    row += 1
    # Spinbox with Dimension
    labelDimension = Label(root, text="Dimension:")
    labelDimension.grid(row=row, column=0, sticky="W") # Align left
    varDimension = IntVar(value=4) # default dimension
    spinboxDimension = Spinbox(root, from_=2, to=20, textvariable=varDimension)
    spinboxDimension.grid(row=row, column=1)

    row +=1
    # Buttons to call parents/children methods
    buttonParents = Button(root, text="Parents", command=get_parents)
    buttonParents.grid(row=row, column=0)
    buttonChildren = Button(root, text="Children", command=get_children)
    buttonChildren.grid(row=row, column=1)

    row += 1
    # Text area with grid placement and set state to disabled
    outputText = Text(root, width=50, height=10)#, state="disabled")
    outputText.grid(row=row, columnspan=2)  # Span across two columns

    row += 1
    # Reset default values
    buttonDefault = Button(root, text="Reset", command=default_values)
    buttonDefault.grid(row=row, column=0)
    # Close button
    buttonClose = Button(root, text="Close", command=close_window)
    buttonClose.grid(row=row, column=1)

    # Run the main loop
    root.mainloop()

#--------------------------------------------------------------------

def usage():
    print('Usage example: python', sys.argv[0], '<type>', '<dimension>', '<function>')
    print(' <type>:      [p]arents or [c]hildren')
    print(' <dimension>: 4')
    print(' <function>:  "{{1,2,3},{1,3,4},{2,3,4}}"')

def command_line_mode():
    if len(sys.argv) != 4:
        print('ERROR: invalid number of arguments!')
        usage()
    elif sys.argv[1] not in ('p','parents','c','children'):
        print('ERROR: invalid <type>')
        usage()
    else:
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
