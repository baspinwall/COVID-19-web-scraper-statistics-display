#Brian Aspinwall, lab 3
#frontend file with ui
import tkinter as tk
import sqlite3
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import lab3back

class MainWindow(tk.Tk):
    def __init__(self, cur):
        super().__init__()
        self.title('Covid-19 Cases')
        self.geometry('350x125')
        self.cur = cur
    
        cur.execute("SELECT COUNT(id) FROM CoronaDB")
        numCountries = str(cur.fetchone()[0])
        cur.execute("SELECT SUM(totalCases) *1000000.0 / SUM(population) FROM CoronaDB")
        casesPerM = str(int(cur.fetchone()[0]))
        cur.execute("SELECT SUM(totalDeaths) *1000000.0 / SUM(population) FROM CoronaDB")
        deathsPerM = str(round(cur.fetchone()[0],1))
        
        l1 = tk.Label(self, text="Worldwide: "+numCountries+" countries")
        l2 = tk.Label(self, text="Worldwide: "+casesPerM+" cases per 1M people")
        l3 = tk.Label(self, text="Worldwide: "+deathsPerM+" deaths per 1M people")
        l1.grid(sticky=tk.W, columnspan=5)
        l2.grid(sticky=tk.W, columnspan=7)
        l3.grid(sticky=tk.W, columnspan=8)
        
        tk.Label(self, text="").grid(row=3)#spacer label
            
        tk.Button(self, text="New Cases", command=self.newCases).grid(row = 4, column = 1, columnspan = 3)
        tk.Button(self, text="Top 20 Cases", command=self.topTwenty).grid(row = 4, column = 4, columnspan = 3)
        tk.Button(self, text="Compare Countries", command=self.compare).grid(row = 4, column = 8, columnspan = 3)
        
    def newCases(self):
        self.cur.execute("SELECT country, newCases, newDeaths, continent FROM CoronaDB WHERE newCases IS NOT NULL ORDER BY newCases DESC")
        DisplayWindow(self, 1, *self.cur.fetchall())
    def topTwenty(self):
        self.cur.execute("SELECT country, casesPer1M, deathsPer1M, testsPer1M FROM CoronaDB ORDER BY casesPer1M DESC LIMIT 20")
        DisplayWindow(self, 2, *self.cur.fetchall())
    def compare(self):
        self.cur.execute("SELECT country FROM CoronaDB ORDER BY country")
        DialogueWindow(self, *self.cur.fetchall())
    def plot(self, *args):
        countriesData = []
        for a in args:
            self.cur.execute("SELECT country, casesPer1M FROM CoronaDB WHERE country = ?", a)
            countriesData.append(self.cur.fetchone())
        PlotWindow(self, *countriesData)        

class DisplayWindow(tk.Toplevel):
    def __init__(self, master, winType, *args):
        super().__init__(master)
        self.transient(master)
        self.focus_set() 
        
        #pass in args to avoid taking memory with instance attributes
        if winType == 1 :
            self.newCases(*args)
        elif winType == 2 :
            self.topTwenty(*args)
    def topTwenty(self, *args):
        self.title('Top Twenty')
        self.geometry('450x350')       

        L = tk.Listbox(self, height=21, width=72)
        
        L.insert(tk.END, "Country Cases / 1 million people Deaths / 1 million people Tests / 1 million people")
        L.insert(tk.END, *[' '.join(map(str, a)) for a in args])
        
        L.grid(column=0)

    def newCases(self, *args):
        self.title('New Cases')
        self.geometry('300x190')       
        
        data = {'North America' : 0, 'South America' : 0, 'Europe' : 0, 'Asia' : 0, 'Africa' : 0, 'Australia/Oceania' : 0}
        for country in args:
            data[country[3]] += country[1]
        maxCont = max(data, key = data.get)
        
        S = tk.Scrollbar(self)
        L = tk.Listbox(self, height=10, width=45, yscrollcommand=S.set)
        l1 = tk.Label(self, text="Highest: " + str(data[maxCont]) + " new cases in " + maxCont)
        
        L.insert(tk.END, "Country New Cases New Deaths")
        L.insert(tk.END, *[' '.join(map(str, a)) for a in args])
        
        L.grid(column=0)
        S.grid(row=0, column=1, sticky ='ns')
        l1.grid()
        S.config(command=L.yview)                

class DialogueWindow(tk.Toplevel):
    def __init__(self, master, *args):
        super().__init__(master)
        self.master = master
        self.args = args
        
        self.title('Choose Countries')
        self.geometry('300x190')
        self.transient(master)
        self.focus_set()        
        
        S = tk.Scrollbar(self)
        self.L = tk.Listbox(self, height=10, width=45, selectmode="multiple", yscrollcommand=S.set)
        B = tk.Button(self, text="OK", command = self.closePrompt)
        
        self.L.insert(tk.END, *[a.replace('{','').replace('}','') for b in args for a in b])
        
        self.L.grid(column=0)
        S.grid(row=0, column=1, sticky ='ns')
        B.grid(row=1)
        S.config(command=self.L.yview)        
    def closePrompt(self):
        selections = self.L.curselection()
        if len(selections) > 0:
            self.master.plot(*[self.args[i] for i in selections])        
        self.destroy()

class PlotWindow(tk.Toplevel):
    def __init__(self, master, *args):     
        super().__init__(master)
        self.title('Covid-19 Cases')
        self.geometry('400x500')
        self.transient(master)  
        self.focus_set()       
        
        fig = plt.figure(figsize=(4,4.9))
        plt.bar([i[0] for i in args], [i[1] for i in args])
        plt.xticks(rotation='vertical')
        plt.ylabel("Number of Cases Per 1M People")
        plt.title("Number of Cases for Chosen Countries")
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self)     
        canvas.get_tk_widget().grid()
        canvas.draw()        

def main():
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()   
    app = MainWindow(cur)
    app.mainloop()
    conn.close()
    

main()
