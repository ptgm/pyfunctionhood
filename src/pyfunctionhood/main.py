import sys

from bitarray import bitarray
from .hassediagram import HasseDiagram
from .function import Function
import re

def signature_to_changed_signs(signature, ndim):
    """ Converts a target signature (a string of ndim bits, 1 = positive and 0 = negative regulator,
    relative to the all-positive reference) into the bitarray of changed signs expected by the
    get_f_*_with_sign_changes methods. Returns None if no sign changes (empty or all 1's).
    Raises ValueError if the signature is invalid. """
    signature = signature.strip()
    if not signature:
        return None
    if len(signature) != ndim or any(c not in ('0', '1') for c in signature):
        raise ValueError('signature must be a string of ' + str(ndim) + ' bits (0/1)!')
    changed_signs = ~bitarray(signature)
    return changed_signs if changed_signs.count() else None

def format_function(f, changed_signs=None):
    """ String of function f, writing variable i as ~i whenever its sign changed. """
    if changed_signs is None:
        return str(f)
    return re.sub(r'\d+', lambda m: ('~' if changed_signs[int(m.group(0)) - 1] else '') + m.group(0), str(f))

def GUI_mode():
    try:
        import tkinter as tk
    except ImportError:
        print("ERROR: tkinter module is not available. GUI mode cannot be started.")
        print("Please install tkinter or run in command line mode.")
        sys.exit(1)
 
    class ToolTip:
        """Small tooltip shown while the mouse is over a widget."""
        def __init__(self, widget, text):
            self.widget, self.text, self.tip = widget, text, None
            widget.bind('<Enter>', self.show)
            widget.bind('<Leave>', self.hide)
            widget.bind('<ButtonPress>', self.hide)

        def show(self, event=None):
            if self.tip is not None:
                return
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
            self.tip = tk.Toplevel(self.widget)
            self.tip.wm_overrideredirect(True)
            self.tip.wm_geometry('+%d+%d' % (x, y))
            tk.Label(self.tip, text=self.text, justify='left', background='#ffffe0',
                     relief='solid', borderwidth=1, padx=6, pady=4).pack()

        def hide(self, event=None):
            if self.tip is not None:
                self.tip.destroy()
                self.tip = None

    def get_changed_signs(idim):
        """ Returns None if no sign changed, otherwise the bitarray of changed signs. """
        return signature_to_changed_signs(varSignature.get(), idim)

    def get_parents():
        try:
            idim = int(varDimension.get())
            hd = HasseDiagram(idim)
            f = Function.fromString(idim, varFunction.get())
            changed_signs = get_changed_signs(idim)
            if changed_signs is None:
                s1Parents, s2Parents, s3Parents = hd.get_f_parents(f)
            else:
                s1Parents, s2Parents, s3Parents = hd.get_f_parents_with_sign_changes(f, changed_signs)
            lParents = ['R1 ' + format_function(f, changed_signs) for f in s1Parents]\
                    + ['R2 ' + format_function(f, changed_signs) for f in s2Parents]\
                    + ['R3 ' + format_function(f, changed_signs) for f in s3Parents]
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
            changed_signs = get_changed_signs(idim)
            if changed_signs is None:
                s1Children, s2Children, s3Children = hd.get_f_children(f)
            else:
                s1Children, s2Children, s3Children = hd.get_f_children_with_sign_changes(f, changed_signs)
            lChildren = ['R1 ' + format_function(f, changed_signs) for f in s1Children]\
                    + ['R2 ' + format_function(f, changed_signs) for f in s2Children]\
                    + ['R3 ' + format_function(f, changed_signs) for f in s3Children]
            output = '** Children(f) ***\n' + '\n'.join(lChildren)
        except ValueError as e:
            output = "ERROR! " + str(e)
        outputText.delete(1.0, "end")  # Clear previous output
        outputText.insert(1.0, output)

    def default_values():
        varFunction.set('{{1,2,3},{1,3,4},{2,3,4}}')
        varDimension.set(4)
        varSignature.set('1' * 4)
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
    labelSignature = tk.Label(root, text="Signature")
    labelSignature.grid(row=row, column=0, sticky='w')
    varSignature = tk.StringVar(value='1' * varDimension.get())  # all 1's: no sign change
    entrySignature = tk.Entry(root, textvariable=varSignature, width=48)
    entrySignature.grid(row=row, column=1, columnspan=2)

    def reset_signature(*args):
        """ Whenever the dimension changes, the signature goes back to all 1's. """
        try:
            varSignature.set('1' * int(varDimension.get()))
        except (ValueError, tk.TclError):  # dimension field empty or not (yet) a number
            pass
    varDimension.trace_add('write', reset_signature)

    signatureHelp = ("Target signature: one bit per variable, 1 = positive and 0 = negative regulator.\n"
                     "All 1's (the default): no sign change. Set a bit to 0 to flip that variable.\n"
                     "\n"
                     "For instance, with 3 variables:\n"
                     "  101  ->  variable 2 is negative\n"
                     "  110  ->  variable 3 is negative\n"
                     "\n"
                     "The function is given in the all-positive signature. In the output,\n"
                     "~i denotes the negated variable i. The signature is reset to all 1's\n"
                     "when the dimension changes.")
    ToolTip(labelSignature, signatureHelp)
    ToolTip(entrySignature, signatureHelp)

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
    print('Usage example:', sys.argv[0], '<type>', '<dimension>', '<function>', '[<signature>]')
    print(' <type>:          [p]arents or [c]hildren')
    print(' <dimension>:     4')
    print(' <function>:      "{{1,2,3},{1,3,4},{2,3,4}}"')
    print(' <signature>:     optional target signature, e.g. "1011" (bit i: 1 = positive, 0 = negative variable i;')
    print('                  all 1\'s or omitted: no sign change). In the output, ~i denotes the negated variable i')
    sys.exit(1)

def command_line_mode():
    if len(sys.argv) not in (4, 5):
        print('ERROR: invalid number of arguments!')
        usage()
    if sys.argv[1] not in ('p','parents','c','children'):
        print('ERROR: invalid <type>')
        usage()

    ndim = int(sys.argv[2])
    hd = HasseDiagram(ndim)
    f = Function.fromString(ndim, sys.argv[3])

    changed_signs = None
    if len(sys.argv) == 5:
        try:
            changed_signs = signature_to_changed_signs(sys.argv[4], ndim)
        except ValueError:
            print('ERROR: invalid <signature>')
            usage()

    if sys.argv[1] in ('p','parents'):
        if changed_signs is None:
            s1Parents, s2Parents, s3Parents = hd.get_f_parents(f)
        else:
            s1Parents, s2Parents, s3Parents = hd.get_f_parents_with_sign_changes(f, changed_signs)
        lParents = ['R1 ' + format_function(f, changed_signs) for f in s1Parents]\
                 + ['R2 ' + format_function(f, changed_signs) for f in s2Parents]\
                 + ['R3 ' + format_function(f, changed_signs) for f in s3Parents]
        print('\n'.join(lParents))
    else:
        if changed_signs is None:
            s1Children, s2Children, s3Children = hd.get_f_children(f)
        else:
            s1Children, s2Children, s3Children = hd.get_f_children_with_sign_changes(f, changed_signs)
        lChildren = ['R1 ' + format_function(f, changed_signs) for f in s1Children]\
                  + ['R2 ' + format_function(f, changed_signs) for f in s2Children]\
                  + ['R3 ' + format_function(f, changed_signs) for f in s3Children]
        print('\n'.join(lChildren))

    


#--------------------------------------------------------------------
def main():
    if len(sys.argv) == 1: 
        GUI_mode()
    else:
        command_line_mode()

if __name__ == '__main__':
    main()