from tkinter import *
from tkinter import Text, Button, filedialog, messagebox
import tkinter as tk
import tkinter.ttk as ttk 
import mysql.connector    
    
#sql python connectivity
mydb=mysql.connector.connect(host='localhost',user='root',passwd='abcd4321#',db='HEALTHNU')
sql=mydb.cursor()
sql.execute('use HEALTHNU;')


#Reset the information 
def reset_entry():
    name_e.delete(0,'end')
    age_e.delete(0,'end')
    height_e.delete(0,'end')
    weight_e.delete(0,'end')

#dowload the dietchart
def save_to_file(content, filename="diet_plan.txt"):
    try:
        with open(filename, 'w') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error saving to file: {e}")
        return False

def download_diet_plan(content):
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filename:
        if save_to_file(content, filename):
            print(f"Diet plan saved to {filename}")
        else:
            print("Failed to save diet plan.")
    
#BMI Result Messagebox
def bmi_index(bmi):
    if bmi < 18.5:
        messagebox.showinfo('bmi.result', f'BMI = {bmi} is Underweight\n Please click on ok after viewing your result')
    elif (bmi > 18.5) and (bmi < 24.9):
        messagebox.showinfo('bmi-result', f'BMI = {bmi} is Normalweight\n Please click on ok after viewing your result')
    elif (bmi > 24.9) and (bmi < 29.9):
        messagebox.showinfo('bmi-result', f'BMI = {bmi} is Overweight\n Please click on ok after viewing your result')
    elif (bmi > 29.9):
        messagebox.showinfo('bmi-result', f'BMI = {bmi} is Obese\n Please click on ok after viewing your result') 
    else:
        messagebox.showerror('bmi-result', 'something went wrong!\n Please click on ok after viewing your result')

    
#BMI Calculator
def calculate_bmi():
    global bmi
    name =str(name_e.get())
    age =int(age_e.get())
    kg = int(weight_e.get())
    m = int(height_e.get())/100
    bmi = kg/(m*m)
    bmi = round(bmi, 1)
    bmi_index(bmi)
    sql1()

#destroy the application
def destroy():
    n.destroy()


#fifth window(yes)
def yes():
    global nw
    nw=5
    c.destroy()
    global ye
    ye=Tk()
    ye.title('Diet Chart')
    ye.geometry('800x800')
    ye.config(bg='#97B9CF')
    y1=Label(ye,text='Diet Chart',fg='#14453D', font=40)
    y1.pack()
    frye=Frame(ye,bg='')
    frye.pack(expand=True)
    if bmi < 18.5:
        yee="Diet Chart for Underweight Individuals:"
        dietplan = {"Breakfast": ["Whole grain cereal with milk", "Banana", "A handful of nuts (almonds, walnuts)"],
            "Mid-Morning Snack": ["Greek yogurt with honey and berries", "Whole grain toast with peanut butter"],
            "Lunch": ["Grilled chicken or tofu with quinoa or brown rice", "Steamed vegetables", "Lentil soup or mixed bean salad"],
            "Afternoon Snack": ["Hummus with whole grain pita bread", "Fresh fruit (apple, pear, or grapes)"],
            "Dinner": ["Baked or grilled fish (salmon, mackerel)", "Sweet potato or brown rice", "Mixed vegetable stir-fry with olive oil"],
            "Evening Snack": ["Cottage cheese with pineapple or peach slices"],
            "Bedtime Snack": ["A glass of milk or a small smoothie with banana and yogurt"]}

    elif (bmi > 18.5) and (bmi < 24.9):
        yee="Diet Chart for Normalweight Individuals:"
        dietplan={"Breakfast": ["Whole grain toast with avocado", "Scrambled eggs", "Fresh orange juice"],
            "Mid-Morning Snack": ["Greek yogurt with mixed berries", "Handful of almonds"],
            "Lunch": ["Grilled chicken or chickpea salad with a variety of vegetables", "Quinoa or brown rice", "Vegetable soup"],
            "Afternoon Snack": ["Sliced cucumber and cherry tomatoes with hummus", "Walnut halves"],
            "Dinner": ["Baked or grilled salmon", "Steamed broccoli and carrots", "Quinoa or sweet potato"],
            "Evening Snack": ["Low-fat cottage cheese with pineapple slices"],
            "Bedtime Snack": ["A cup of chamomile tea"]}
        
    elif (bmi > 24.9) and (bmi < 29.9):
        yee="Diet Chart for Overweight Individuals:"
        dietplan={"Breakfast": ["Oatmeal with berries and a sprinkle of chia seeds", "Boiled eggs", "Green tea"],
            "Mid-Morning Snack": ["Greek yogurt with sliced almonds", "Apple slices"],
            "Lunch": ["Grilled chicken or tofu salad with mixed greens", "Quinoa or brown rice", "Vegetable soup"],
            "Afternoon Snack": ["Carrot and cucumber sticks with hummus", "Handful of walnuts"],
            "Dinner": ["Baked or grilled fish (salmon, cod)", "Steamed broccoli and cauliflower", "Sweet potato"],
            "Evening Snack": ["Low-fat cottage cheese with pineapple chunks"],
            "Bedtime Snack": ["A cup of herbal tea"]}

    elif (bmi > 29.9):
        yee="Diet Chart for Obese Individuals:"
        dietplan={'Breakfast':["Steel-cut oats with berries and a sprinkle of flaxseeds", "Boiled eggs", "Green tea"],
            'Mid-Morning Snack':["Low-fat Greek yogurt with sliced almonds", "Apple slices"],
            'Lunch':["Grilled chicken or tofu salad with a variety of colorful vegetables", "Quinoa or brown rice", "Vegetable soup"],
            'Afternoon Snack':["Carrot and celery sticks with hummus","Handful of walnuts"],
            'Dinner':["Baked or grilled fish (salmon, cod)", "Steamed broccoli, cauliflower, and carrots", "Sweet potato or quinoa"],
            'Evening Snack':["Low-fat cottage cheese with cucumber slices"],
            'Bedtime Snack':["A cup of herbal tea or warm water"]}
    else:
        yee="Please! First fill your details and calculate your BMI so that we can suggest a suitable dietchart"
    ye1 =Label(frye, text=yee, font=32)
    ye1.grid(row=1)
    ye2= Text(frye, wrap='word',font=24 ,width=50, height=20)
    ye2.grid(row=2)
    
    for meal, foods in dietplan.items():
        ye2.insert('end', f"{meal}:\n")
        for food in foods:
            ye2.insert('end', f"- {food}\n")

    ye2.config(state='disabled')
    download= Button(frye, text="Download Diet Plan",font=24, command=lambda: download_diet_plan(text_widget.get("1.0", "end-1c")))
    download.grid(row=3)
    yeb=Button(frye, text='NEXT',font=24, command=lambda:Thankyou())
    yeb.grid(row=4)

#updating feedback data in sql relation    
def sql2():
    global l1, mydb
    l1=mydb.cursor()
    Name=str(name_n.get())
    Feedback=str(msg_n.get())
    query='INSERT INTO Feedback_and_Suggestions (Name, Feedback) VALUES(%s,%s);'
    values = (Name, Feedback)
    l1.execute(query,values)
    mydb.commit()

#Last window
def Thankyou():
    ye.destroy()
    global n,name_n,msg_n
    n=Tk()
    n.title('Thankyou')
    n.geometry('660x400')
    n.config(bg='#E0EAF0')
    nn='''Dear user,\n
    Thank you for using our application.\n Hope it was a successful experience for you and your health.
    We appreciate your trust and hope our application meets your expectations.
    If you have any feedback or suggestions, feel free to let us know.\n
    Best regards,\n
    HEALTHNU'''
    n1=Label(n,text=nn, font='Calibri',fg='#121E26',bg='#E0EAF0')
    n1.pack()
    framen=Frame(n,bg='#E0EAF0')
    framen.pack(expand=True)
    namen=Label(framen,text='Enter name',font=20)
    namen.grid(row=1, column=1)
    name_n=Entry(framen,)
    name_n.grid(row=1,column=2,pady=5)
    message=Label(framen, text='Feedback or suggestions',font=20)
    message.grid(row=2,column=1)
    msg_n=Entry(framen,)
    msg_n.grid(row=2,column=2,pady=10)
    r1=Label(framen, text='Review',font=20)
    r1.grid(row=3,column=1)
    global rv
    rv=tk.StringVar()
    review=ttk.Combobox(framen, textvariable=rv)
    review['values'] = ('Very good', 'Good', 'Average', 'Poor')
    review.grid(row=3,column=2,padx=10, pady=10)
    nb=Button(framen, text="SUBMIT",bg='#97B9CF',fg='#FFFFFF',font=(20,'bold'),command=lambda:destroy())
    nb.grid(row=4,column=3)
    sql2()

#fifth window(no)
def no():
    c.destroy()
    global n,name_n,msg_n
    n=Tk()
    n.title('Thankyou')
    n.geometry('660x400')
    n.config(bg='#E0EAF0')
    nn='''Dear user,\n
    Thank you for using our application.\n Hope it was a successful experience for you and your health.
    We appreciate your trust and hope our application meets your expectations.
    If you have any feedback or suggestions, feel free to let us know.\n
    Best regards,\n
    HEALTHNU'''
    n1=Label(n,text=nn, font='Calibri',fg='#121E26',bg='#E0EAF0')
    n1.pack()
    framen=Frame(n,bg='#E0EAF0')
    framen.pack(expand=True)
    namen=Label(framen,text='Enter name',font=20)
    namen.grid(row=1, column=1)
    name_n=Entry(framen,)
    name_n.grid(row=1,column=2,pady=5)
    message=Label(framen, text='Feedback or suggestions',font=20)
    message.grid(row=2,column=1)
    msg_n=Entry(framen,)
    msg_n.grid(row=2,column=2,pady=10)
    r1=Label(framen, text='Review',font=20)
    r1.grid(row=3,column=1)
    global rv
    rv=tk.StringVar()
    review=ttk.Combobox(framen, textvariable=rv)
    review['values'] = ('Very good', 'Good', 'Average', 'Poor')
    review.grid(row=3,column=2,padx=10, pady=10)
    nb=Button(framen, text="SUBMIT",fg='black',font=20,command=lambda:destroy())
    nb.grid(row=4,column=3)
    sql2()
                
#fourth window
def window4():
    x.destroy()
    global c
    c=Tk()
    c.title('HEALTHNU')
    c.geometry('500x300')
    c.config(bg='#B8D8D8')
    cl=Label(c,text='Do you want a Diet Chart?', font='algerian')
    cc='''HEALTHNU assists you in selecting the proper
    foods and diet, enabling you to live a better
    lifestyle. It gives you a diet that is calorie-
    conscious and well-balanced based on your age,
    gender, and body mass index. So, are you interested
    in using HEALTHNU to begin a better lifestyle?'''
    framec=Frame(c, padx=10, pady=10,bg='#7A9E9F')
    framec.pack(expand=True)
    c1=Label(framec,text=cc,font='calibri')
    c1.grid(row=1)
    framec1=Frame(framec,bg='red')
    framec1.grid(row=4)
    c11=Button(framec1,text='YES',bg='#E0EAF0',fg='#14453D',width=25,command=lambda:yes())
    c11.grid(row=1,column=1)
    c12=Button(framec1, text='NO',bg='#E0EAF0',fg='#14453D',width=25,command=lambda:no())
    c12.grid(row=1, column=2)

    
#third window (bmi calculator)
def window3():
    s.destroy()
    global x, height_e, weight_e, name_e,g
    x=Tk()
    x.title('HEALTHNU')
    x.geometry('500x400')
    x.config(bg='#949494')
    var= IntVar()
    l2=Label(x,text='BMI CALCULATOR',fg='#4F6367',font=('Algerian',34,'underline','bold'))
    l2.pack()
    frame = Frame(x, padx=10, pady=10)
    frame.pack(expand=True)
    name=Label(frame,text='Enter name')
    name.grid(row=1, column=1)
    name_e=Entry(frame,)
    name_e.grid(row=1,column=2,pady=5)
    global age_e
    age = Label(frame, text="Enter Age")
    age.grid(row=2, column=1)
    age_e = Entry(frame,)
    age_e.grid(row=2, column=2, pady=5)

    gender = Label(frame,text='Select Gender')
    gender.grid(row=3, column=1)

    frame2 = Frame(frame)
    frame2.grid(row=3, column=2, pady=5)
    g=tk.StringVar()
    gender=ttk.Combobox(frame2, textvariable=g)
    gender['values'] = ('Male','Female','Other')
    gender.grid(row=1,padx=10, pady=10)
    
    height= Label(frame,text="Enter Height (cm)  ")
    height.grid(row=4, column=1)
    height_e = Entry(frame,)
    height_e.grid(row=4, column=2, pady=5)

    weight = Label(frame,text="Enter Weight (kg)  ")
    weight.grid(row=5, column=1)
    weight_e = Entry(frame,)
    weight_e.grid(row=5, column=2, pady=5)

    frame3 = Frame(frame,)
    frame3.grid(row=6, columnspan=3, pady=10)
    #button to calculate bmi
    calculate = Button(frame3,text='Calculate',bg='#D3D3D3',fg='black',command=(lambda:calculate_bmi()))
    calculate.grid(row=1,column=1)

    #button to reset the details
    reset = Button(frame3,text='Reset',bg='#D3D3D3',fg='black',command=lambda:reset_entry())
    reset.grid(row=1,column=2)

    #button to go to the next window
    next=Button(frame3,text='Next',bg='#D3D3D3',fg='black',command=lambda:window4())
    next.grid(row=1,column=3)

    frame4=Frame(x)
    frame4.pack(expand=True)
    msg=Label(frame4, text='Please click on next to proceed further',font=15)
    msg.grid(row=1)    

#updating the details in the sql relation
def sql1():
    global l, mydb, c
    l=mydb.cursor()
    name=str(name_e.get())
    age=int(age_e.get())
    weight=int(weight_e.get())
    height=int(height_e.get())
    if bmi < 18.5:
        result='Underweight'
        l.execute("select Calories from Calories where Result='Underweight';")
    elif (bmi > 18.5) and (bmi < 24.9):
        result='Normalweight'
        l.execute('select Calories from Calories where Result="Normalweight";')
    elif (bmi > 24.9) and (bmi < 29.9):
        result='Overweight'
        l.execute('select Calories from Calories where Result="Overweight";')
    elif (bmi > 29.9):
        result='Obese'
        l.execute('select Calories from Calories where Result="Obese";')
    cee=l.fetchone()
    cee=str(cee)
    ce = {'name': name,
        'age': age,
        'height': height,
        'weight': weight,
        'bmi': bmi,
        'result': result,
        'calories': cee}
    le='INSERT INTO Details VALUES (%(name)s, %(age)s, %(height)s, %(weight)s, %(bmi)s, %(result)s, %(calories)s);'
    
    l.execute(le,ce)
    mydb.commit()


#progressing bar in first window   
def bar(): 
    global p
    p1=Label(y,text='Progressing...')
    p1.pack()
    p= ttk.Progressbar(y,orient=HORIZONTAL,length =500, mode = 'determinate')
    p.pack()
    import time 
    p['value'] = 20
    y.update_idletasks() 
    time.sleep(1) 
  
    p['value'] = 40
    y.update_idletasks() 
    time.sleep(1) 
  
    p['value'] = 50
    y.update_idletasks() 
    time.sleep(1) 
  
    p['value'] = 60
    y.update_idletasks() 
    time.sleep(1) 
  
    p['value'] = 80
    y.update_idletasks() 
    time.sleep(1) 
    p['value'] = 100
    window2()

    
#second window
def window2():
    y.destroy()
    global s
    s=Tk()
    s.title('BMI')
    s.geometry('600x400')
    s.config(bg='#7A9E9F')
    ls=Label(s,text='BMI(Body Mass Index)',fg='#14453D',font=('Algerian',36,'bold'))
    ls.pack()
    w1='''The body mass index (BMI) is a measure that uses your 
    height and weight to work out if your weight is healthy.
    If your BMI is:
    -below 18.5, you're in the underweight range
    -between 18.5 and 24.9, you're in the healthy weight range
    -between 25 and 29.9, you're in the overweight range
    -30 or over, you're in the obese range
    BMI takes into account natural variations in body shape,
    giving a healthy weight range for a particular height.
    healthcare professionals may take other factors into 
    account when assessing if you're a healthy weight.
    '''
    ls1=Label(s,text=w1,bg='#E0EAF0',fg='#14453D',font='Futura')
    ls1.pack()
    sframe = Frame(s, padx=10, pady=10)
    sframe.pack(expand=True)
    #button to go to the next window 
    b1=Button(sframe,text='Calculate BMI',bg='#B8D8D8',font='Georgia',command=lambda:window3())
    b1.grid(row=1)
    
   

#First Window (introduction of HEATHNU)
y =Tk()
y.title('HEALTHNU')
y.geometry('600x400')
y.config(bg='#B8D8D8')
l1=Label(y,text='WELCOME TO HEALTHNU',fg='#14453D',font=('Algerian',40))
l1.pack()
framey = Frame(y, padx=10, pady=10, bg='#7A9E9F')
framey.pack(expand=True)

w='''HEALTHNU is an application for calculating your BMI.
Body Mass Index is widely used as a general indicator
of whether a person has a healthy body weight for their
height. Specifically, the value obtained from the calculation
of BMI is used to categorize whether a person is underweight,
normal weight, overweight, or obese depending on what range 
the value falls between. This appliaction also provides you with
a suitable dietchart according to your bmi to ensure a more healthy
lifestyle for you.'''

l11=Label(framey,text=w,font='Calibri')
l11.grid(row=1)
#button to go to the next window
b=Button(framey,text='NEXT',width=15,bg='#FFFFFF', fg='#4F6367',font=('Artemis',18,'bold'),command=lambda:bar())
b.grid(row=2)
y.mainloop()

#closing the connectivity with sql
mydb.commit()
