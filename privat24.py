# PART 1 'import'
import hashlib   #hashlib - бібліотека для шифрування
import requests   #бібліотека для створення різного роду запитів
import xml.etree.ElementTree as ET   #бібліотека для парсення XML
import matplotlib.pyplot as plt   #Matplotlib - бібліотека для роботи з графіками
import numpy as np   #Numpy



#PART 2 'main'


#Privat definition
def privat_bank(d1,d2):

    #формулюємо тіло запиту
    url = "https://api.privatbank.ua/p24api/rest_fiz"   #змінна в яку записано посилання до сайту
 
    password = "arI8058XKQjeiiZ562p7b8mGTofRFapK"   #змінна в яку записано пароль 

    #складається тіло запиту
    head = """<?xml version="1.0" encoding="UTF-8"?>
        <request version="1.0">
        <merchant>
        <id>207902</id>   
        <signature>"""
    data = f"""<oper>cmt</oper>
                    <wait>0</wait>
                    <test>0</test>
                    <payment id="">
                        <prop name="sd" value="{d1}" />
                        <prop name="ed" value="{d2}" />
                        <prop name="card" value="4149439001234339" />
                    </payment>"""
    end_head = """</signature>
            </merchant>
            <data>
                """
    footer = """
    </data>
    </request>"""


    #шифруємо пароль
    signature_md5 = hashlib.md5((data+password).encode('utf-8')).hexdigest()
    signature_done = hashlib.sha1(signature_md5.encode('utf-8')).hexdigest()

    #складаємо тіло запиту
    data_done = head + signature_done + end_head + data + footer  

    #робимо пост запист
    res = requests.post(url, data=data_done, headers={'Content-Type': 'application/xml; charset=UTF-8'})
    root = ET.fromstring(res.text)   
    statements = root.find('data/info/statements')
    


 
    arr=[]   #створюємо масив arr
    for statement in statements:
        arr.append(statement.get('cardamount')[:-4])   #записуємо в масив cardamount
        print(res.text)   #виводим відповідь сайту в консоль
    suma=0
    minus=0
    plus=0
    for i in arr:
        suma = suma+float(i)   #додаємо всі елементи масиву arr
        if float(i)<0:
            minus=minus+float(i)   #додаємо всі від'ємні елементи масиву
        else:
            plus=plus+float(i)   #додаємо всі додатні елементи масиву   
    
    #Обраховуємо передбачення на наступний місяць
    predict= 0
    for i in arr:
        predict=predict+float(i)
    if predict>0:
        predict=plus-predict
    else:
        predict=plus+predict
        
    general_title="ArtLab Transactions"   #ств змінну яку передамо в функцію PrintMatplotlib, для виводу конкретного тексту на графіку
    a1_titel="Income"   #ств змінну яку передамо в функцію PrintMatplotlib, для виводу конкретного тексту на графіку
    a2_titel="Outcome"   #ств змінну яку передамо в функцію PrintMatplotlib, для виводу конкретного тексту на графіку
    plus,minus=PrintMatplotlib(plus,minus,general_title,a1_titel,a2_titel)   #записуємо результат роботи функції PrintMatplotlib в дві змінні (plus,minus)

    return arr, predict, plus, minus   #повертаємо 4 змінні(arr, predict, plus, minus)






#MATPLOTLIB definithion
def PrintMatplotlib(plus,minus,general_title,a1_titel,a2_titel):

    y=[]
    minus=round(abs(minus),2)   #округляємо змінну minus до сотих і перезапису
    plus=round(abs(plus),2)    #округляємо змінну plus до сотих
    
    plus_100 = round(plus/(plus+minus)*100,2)   #переводимо в проценти значення і округляємо до сотих
    y.append(plus_100)   #записуємо в масив y, як перший елемент
    y.append(100-y[0])   #записуємо в масив y, як другий елемент


    fig, ax = plt.subplots()
    recipe = [f"{a1_titel}\n({plus})",   #даємо назву частинам графіку
            f"{a2_titel}\n({minus})"]   #даємо назву частинам графіку
    colors = ['#0057b8', '#ffd700']   #задаємо колір графіка
    wedges, texts = ax.pie(y, wedgeprops=dict(width=0.5), startangle=-40,)
    ax.pie(y, autopct='%.2f%%',colors=colors,)   #робить графік


    #настройки графіка
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
            bbox=bbox_props, zorder=0, va="center")
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(recipe[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title(f"{general_title}")   #даємо назву графіку
    plt.savefig('tmp\grath.png')   #зберігаємо графік локально в папці tmp з назвою grath.png

    return plus, minus   #повертаємо 2 змінні(plus, minus)
    




    

   
    