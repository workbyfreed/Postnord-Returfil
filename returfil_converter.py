import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from csv import reader
import pandas as pd
from datetime import date
import webbrowser
# Icon path
from pathlib import Path
bundle_dir = Path(__file__).parent
path_to_ico = Path.cwd() / bundle_dir / 'convert-file.ico'

# Base window
window = tk.Tk()
window.title('Returfil manager')

window.rowconfigure(0, minsize=200, weight=1)
window.columnconfigure(1, minsize=400, weight=1)
window.configure(bg='lightblue')

window.wm_iconbitmap(path_to_ico)

# Open file and add to list
returlist = []
def open_file():
    # Delete old field data if new file is searched for
    text_open.delete('1.0', 'end')
    text_run.delete('1.0', 'end')
    url = askopenfilename(
        filetypes=[('Text Files', ['*.txt', '*.csv']), ("All Files", "*.*")]
        )
    print(url)
    if not url:
        return
    # Create a list of list from file, each cohesive record starts with 20 which is our mark to start a new sublist
    sublist = []
    with open(url, 'r') as file:
        returfil = reader(file)
        for row in returfil:
            prefix = int(row[0][:2])
            value = row[0][2:].strip()
            tolist = [prefix, value]
            if prefix == 20:
                returlist.append(sublist)
                sublist = []
            # We are only interested of prefixes between 20 and 50
            if prefix >= 20 and prefix <= 50:
                sublist.append(tolist)
    # save filename for output file
    global filename
    filename = url.split('/')[-1].split('.')[-3]
    input_file = url.split('/')[-1]
    text_open.insert('1.0', input_file)
    # Save path for output file
    global filepath
    filepath = url.rpartition('/')[0]

# Map from Postnord Fillayout for renaming columns
dictmap = {
1:'Postföretag'
,2:'Skapad datum'
,3:'Kundidentitet'
,4:'Kundnamn'
,5:'Filuppdateringsidentitet'
,20:'UppdateringsTyp'
,21:'Registreringsdatum'
,22:'Kontrollnummer'
,23:'Mottagaridentitet'
,24:'Förnamn'
,25:'Efternamn/Företagsnamn'
,26:'Från c/o adress'
,27:'Från Gatunamn'
,28:'Från Gatunummer'
,29:'Från Litterabeteckning'
,30:'Från Gatubeskrivning'
,31:'Från Extra Adressinformation'
,32:'Från Postnummer'
,33:'Från Postort'
,34:'Till c/o adress'
,35:'Till Gatunamn'
,36:'Till Gatunummer'
,37:'Till litterabeteckning'
,38:'Till Gatubeskrivning'
,39:'Till Extra Adressinformation'
,40:'Till Postnummer'
,41:'Till Postort'
,42:'Till Land'
,50:'Obeställbar_Anledning'
,90:'UppdateringsTyp'
,91:'Antal per uppdateringsTyp'
,99:'Totalt antal transaktioner i fil'
}

# Process file with Run button
def process_file():
    # Create empty dataframe with some example columns, missing columns will be added when concat
    rcdf = pd.DataFrame(columns=[20, 21, 22, 23])
    # Loop through returlist, skipping first empty sublist and create a dataframe per sublist with prefix as column name
    # Then concatenate each temp dataframe to rcdf dataframe, creating a full dataframe with all rows from returlist
    for i in returlist[1:]:
        temp = pd.DataFrame(i, columns=['Prefix', 'Value'])
        temp = temp.set_index('Prefix').T
        frames = [rcdf, temp]
        rcdf = pd.concat(frames)
    
    # Reorder columns in nummeric order
    rcdf = rcdf.reindex(sorted(rcdf.columns), axis=1)
    # Rename columns according to map
    rcdf = rcdf.rename(columns=dictmap)
    # Date for file name
    today = date.today().isoformat()
    # Save to spreadsheet using source path
    rcdf.to_excel(filepath + '/' + filename + '_' + today +'.xlsx', index=False)
    # Print file name to input field
    text_run.insert('1.0', filename + '_' + today + '.xlsx')
    # Create a link to open directory
    global path_print
    path_print = ('file://' + filepath)
    path_label = tk.Label(frm_buttons, text='Open Directory', bg='lightblue', fg='blue', cursor='hand2', font=('Arial', 10, 'underline'))
    path_label.grid(row=4, column=1, sticky='sw', padx=5)
    path_label.bind('<Button-1>', lambda e: openlink(path_print))

# Function to open directory from app link
def openlink(path_print):
    webbrowser.open(path_print)

# Create a working frame
frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=0, bg='lightblue')

# Buttons
btn_open = tk.Button(frm_buttons, text='Open', command=open_file)
btn_run = tk.Button(frm_buttons, text='Run', command=process_file)

btn_open.grid(row=1, column=0, sticky='ew', padx=5)
btn_run.grid(row=3, column=0, sticky='ew', padx=5)

frm_buttons.grid(row=0, column=1, sticky='ns')

# Text fields
text_open = tk.Text(frm_buttons, height=1, width=25)
text_run = tk.Text(frm_buttons, height=1, width=25)

text_open.grid(row=1, column=1, sticky='ew', padx=5)
text_run.grid(row=3, column=1, sticky='ew', padx=5)

# Labels
open_label = tk.Label(frm_buttons, text='Input file:', bg='lightblue', font=('Arial', 10))
run_label = tk.Label(frm_buttons, text='Output file:', bg='lightblue', font=('Arial', 10))

open_label.grid(row=0, column=1, sticky='sw', padx=5, pady=(10,0))
run_label.grid(row=2, column=1, sticky='sw', padx=5)

window.mainloop()