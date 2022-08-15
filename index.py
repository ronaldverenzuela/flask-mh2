#from crypt import methods
#from stringprep import c22_specials
#from time import monotonic
from crypt import methods
from datetime import datetime, timedelta
#import numpy as np
from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for, flash
import re
import os
#app = Flask(__name__)
app = Flask("Web")
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='ronald'
app.config['MYSQL_PASSWORD']='Ronald1234,'
app.config['MYSQL_DB']='piramide'
mysql=MySQL(app)
#cur = mysql.connection.cursor()
#print('cur = ',cur)
# Creating simple Routes 
@app.route('/test')
def test():
    return "Home Page"

@app.route('/abono/factura/add/<cliente2>/<factura2>',methods=['POST']) 
def abono_add(cliente2,factura2):
    if request.method == 'POST':        
        fecha=request.form['fecha']
        abono=request.form['abono']
        print('cliente 2 = ',cliente2)
        print('factura2', factura2)
        cur=mysql.connection.cursor()    
        cur.execute(f"SELECT * FROM " +cliente2+ f" WHERE factura = {factura2}")
        data=cur.fetchall()
        print('>>>>>>>>>>>>>>>>>>> factura >>>>>>>>>>>>>>><')
        print(data[:1])
        for j in data:
            cliente=j[2]
            saldo=j[6]
        saldo=float(saldo)
        #saldo="{:.2f}".format(saldo)
        abono=float(abono)
        #abono="{:.2f}".format(abono)
        saldo=saldo-abono
        saldo=str(saldo)
        abono=str(abono)
        monto=saldo
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        cur=mysql.connection.cursor()            
        cur.execute('INSERT INTO ' +cliente2+ ' (factura,cliente,fecha,monto,abono,saldo) VALUES(%s,%s,%s,%s,%s,%s)',
        (factura2,cliente,fecha,monto,abono,saldo))
        mysql.connection.commit()
        #/relacion/factura/CARNICERIA EL MAUTE DEL LLANO
    #return "Home Page"
    return redirect(url_for('relacion_factura_cliente',factura=factura2))

@app.route('/abono/factura/<factura>/<cliente2>')
def abono_factura(factura,cliente2):  
    print('factura =========> ',factura)
    print('Cliente2 =========> ',cliente2)
    cur=mysql.connection.cursor()    
    cur.execute(f"SELECT * FROM " +cliente2+ f" WHERE factura = {factura}")
    data=cur.fetchall()
    print('Tabla de Facturaaaaaaaaaa = ',data)
    return render_template('abono-factura.html',cliente2=cliente2,factura2=factura)

@app.route('/relacion/factura/<factura>')
def relacion_factura_cliente(factura):
    factura2=factura.lower()    
    factura2=re.sub(r"\s+", "", factura2)
    factura2='f'+factura2
    print('cliente seleccionado = ',factura2)
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM '+factura2)
    data=cur.fetchall()  
    print('Tabla seleccionada = ',data)
    for j in data:
        cliente=j[2]
    cur = mysql.connection.cursor()     
    cur.execute("SHOW TABLES") 
    mysql.connection.commit()
    for x in cur:
      print(x)

    return render_template('relacion-factura.html',data=data,data2=factura,cliente2=factura2,cliente=cliente)


@app.route('/relacion/factura')
def relacion_factura():
    cur = mysql.connection.cursor()     
    cur.execute("SHOW TABLES") 
    mysql.connection.commit()
    for x in cur:
      print(x)

    return render_template('relacion-factura.html')


#CREATE TABLE IF NOT EXISTS `clientes`
@app.route('/factcobrar')
def fact_x_cobrar():
    mycursor = mysql.connection.cursor() 
    mycursor.execute("CREATE TABLE IF NOT EXISTS customers6 (id INT(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (id) ,name TEXT, address VARCHAR(255))")
    mysql.connection.commit()
    mycursor.execute("SHOW TABLES") 
    for x in mycursor:
      print(x)
    return "Home Page"

@app.route('/delete/<string:id>')
def delete_factura(id):
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM tabla1 WHERE id = {0}".format(id))
    mysql.connection.commit()
    flash('Tabla removed susscessfully')
    return redirect(url_for('ventas'))


@app.route('/update/<string:id>',methods=['POST'])
def update_fact(id):
    if request.method == 'POST':
        factura=request.form['factura']
        cliente=request.form['cliente']
        monto=request.form['monto']
        # buscar datos en la tabla por id
        cur=mysql.connection.cursor()    
        cur.execute(f"SELECT * FROM tabla1 WHERE id = {id}")
        data=cur.fetchall()
        print('dataaaaaaaa = ',data)
        print('id = ',id)
        cur=mysql.connection.cursor()
        cliente=cliente.upper() # transformamos a mayusculas
        #cur.execute('SELECT * FROM tabla1 WHERE id = %s',(id))
        cur.execute("""
            UPDATE tabla1
            SET factura = %s,
                cliente = %s,
                monto = %s
            WHERE id = %s
        """,(factura,cliente, monto,id))
        mysql.connection.commit()
        flash('update susscessfully')
        return redirect(url_for('ventas'))


@app.route('/edit/<string:id>')
def edit_fact(id):
    print('id = ',id)
    cur=mysql.connection.cursor()    
    cur.execute(f"SELECT * FROM tabla1 WHERE id = {id}")
    data=cur.fetchall()
    print(data)
    return render_template("edit-factura.html",contact=data[0])

@app.route('/ventas')
def ventas():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tabla1')
    data=cur.fetchall()      
    
    a=0.0   
   # # recorremos la columna MONTO
    for j in data:  
        print(j[6])
        a=float(j[6])+a        
        print('a = ',a)
    a="{:.2f}".format(a)
    a=str(a)
    print('aaaaaaaaaaaa = ',a)     
    return render_template('ventas.html',tabla1=data,dato2=a)


# Routes to Render Something
@app.route('/',methods=['GET', 'POST'])
def home():
    ver_cliente=[]
    if request.method == 'POST':
        factura=request.form['factura']
        cliente=request.form['cliente']
        monto=request.form['monto']  
        fecha=request.form['fecha']
        diascredito=request.form['diascredito']   
        descripcion=request.form['descripcion'] 
        #fecha=request.form['fecha']    
        #print(fecha) 
        monto=float(monto) # monoto como float
        monto="{:.2f}".format(monto)  # formato de 2 decimales
        monto=str(monto)  # devolvemos a string
        cliente=cliente.upper()  # cliente en mayuscula
        if ((not cliente) or (not factura) or (not monto)):        
            print('debe introducir todos los campos')
            return render_template("home.html")
            
        else:
            #cur=mysql.connection.cursor()
            #cur.execute('SELECT * FROM tabla1')
            #data=cur.fetchall()  
            cur = mysql.connection.cursor()     
            cur.execute("SHOW TABLES") 
            mysql.connection.commit()
            factura_existe=0
            fact='f'+factura
            for j in cur:              
                print(j[0])
                if(str(j[0]) == str(fact)):
                    flash('Cliente Existe')
                    print('Cliente existe en la base de datos ') 
                    factura_existe=1
                    return render_template("home.html")
                    break     
            #print('clientes = ',x)
            # recorre todos los clientes existentes en tabla1
            #for j in x:
            #    print(j[2])
            #    ver_cliente.append(j[2])
            #    print('ver_cliente ',ver_cliente) 
            # verifica si exite el cliente en la tabla1
            
            #for j in ver_cliente:
                       

            #datetime.strptime("2021-12-25", "%Y-%m-%d")
            fecha=datetime.strptime(fecha, "%Y-%m-%d")
            fechavencimiento=fecha + timedelta(days=8)
            fecha=str(fecha)
            fecha=fecha[:11]
            print('fecha = ',fecha[:11])
            fechavencimiento=str(fechavencimiento)
            fechavencimiento=fechavencimiento[:11]
            cur=mysql.connection.cursor()
           # cliente=cliente.upper() # transformamos a mayusculas            
            cur.execute('INSERT INTO tabla1 (factura,cliente,monto,fecha,diascredito,descripcion,fechavencimiento) VALUES(%s,%s,%s,%s,%s,%s,%s)',
            (factura,cliente,monto,fecha,diascredito,descripcion,fechavencimiento))
            mysql.connection.commit()
            print('aaaaaaaaa')
            ############ crear bd para cliente
            if(factura_existe==1):
                pass
            else:   ##### crea tabla de relacion abono deuda de clientes
                factura2=factura.lower()
                mycursor = mysql.connection.cursor() 
                factura2='f'+factura2
                factura2=re.sub(r"\s+", "", factura2)
                mycursor.execute("CREATE TABLE IF NOT EXISTS " + factura2 + " (id INT(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (id) ,factura TEXT, cliente TEXT,fecha TEXT,monto TEXT,abono TEXT,saldo TEXT)")
                mysql.connection.commit()
                saldo=monto
                abono='0'
                cur=mysql.connection.cursor()
                cur.execute('INSERT INTO ' + factura2 + ' (factura,cliente,monto,fecha,abono,saldo) VALUES(%s,%s,%s,%s,%s,%s)',
                (factura,cliente,monto,fecha,abono,saldo))
                mysql.connection.commit()
            return redirect(url_for('ventas'))
            #return render_template("ventas.html")
    else:
        return render_template("home.html")
    
    

@app.route('/about', strict_slashes=False)
def about():
    return render_template("about.html")
def run_prog():
    print("runnnnnnn")
# Make sure this we are executing this file
if __name__ == '__main__':
    #app.run(debug=False)
    #app.run(host='192.168.1.102', port=5000,debug=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)



######### calcular fechas dadas
#from datetime import datetime
#date_format = "%m/%d/%Y"
#a = datetime.strptime('8/18/2008', date_format)
#b = datetime.strptime('9/26/2008', date_format)
#delta = b - a
#print delta.days # that's it



####borrar
#DROP TABLE Clientes