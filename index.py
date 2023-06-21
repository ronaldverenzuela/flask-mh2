

from datetime import datetime, timedelta,date
import json
import numpy as np
from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager,login_user,logout_user,login_required,current_user
from models.ModelUser import ModelUser
from models.entities.User import User
from werkzeug.security import check_password_hash, generate_password_hash
import re
import os


app = Flask(__name__)
#app = Flask("Web")
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

########### Mysql Clever Cloud #######################
#app.config['MYSQL_HOST']='bywrvr7abbp3kmrjrowf-mysql.services.clever-cloud.com'
#app.config['MYSQL_USER']='ut78srmw5ocilvva'
#app.config['MYSQL_PASSWORD']='7tQQwczWpijptWYA2Ixd'
#app.config['MYSQL_DB']='bywrvr7abbp3kmrjrowf'



############ Mysql Local #######################
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='mh2018'

#pp.config['MYSQL_HOST']='localhost'
#pp.config['MYSQL_USER']='ronald'
#pp.config['MYSQL_PASSWORD']='Ronald1234,'
#pp.config['MYSQL_DB']='piramide'
mysql=MySQL(app)
login_manager_app=LoginManager(app)
#cur = mysql.connection.cursor()
#print('cur = ',cur)
# Creating simple Routes
# 
#

tipo_usuario=['[ SELECCIONE ]','administrador','limitado']

def fecha_hoy():
    hoy = datetime.now()
    hoy=str(hoy)
    hoy=hoy[:11]
    hoy=hoy.strip()
    hoy=datetime.strptime(hoy, "%Y-%m-%d")
    
    #print('fecha = ',hoy)
    hoy=str(hoy)
    i=0
    hoy_f=''
    for j in hoy:
        if i<10:
            hoy_f+=j
           # print(j)
        i=i+1
    #print(hoy_f)
    fecha=hoy_f
    fecha_a=fecha[:4]
    fecha_m=fecha[5:7]
    fecha_d=fecha[8:]
    fecha_t=fecha_a
    fecha_t+=fecha_m
    fecha_t+=fecha_d
    fecha_indice=fecha_t

    fecha_ordenada=''
    fecha_ordenada=fecha_d
    fecha_ordenada+='-'
    fecha_ordenada+=fecha_m
    fecha_ordenada+='-'
    fecha_ordenada+=fecha_a
    #print(fecha_indice)
    return (fecha_indice,fecha,fecha_ordenada)



def calc_costo_mp(dato):

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM inventario_aba WHERE producto = "{dato}" ORDER BY fecha_indice DESC ')
    #cur.execute("CALL ver_precio(1)")
    
    data=cur.fetchall()
    cant_temp=[]
    precio_temp=[]
    for j in data:
        p=devolver_separador_miles(j[3])
        p1=devolver_separador_miles(j[5])
        nombre=j[1]
        p=float(p)
        p1=float(p1)
        cant_temp.append(p)
        precio_temp.append(p1)
    print('')
    print('cantidad temporal')
    print(cant_temp)
    print('')
    print('precio temporal')
    print(precio_temp)
    px=np.multiply(cant_temp,precio_temp)
    print('px = ', px )
    suma_ct=np.sum(cant_temp,axis=0)
    suma_pt=np.sum(px,axis=0)
    print('')
    print('suma cantidad temporal')
    print(suma_ct)
    print('')
    print('suma precio temporal')
    print(suma_pt)
    print('')
    producto=nombre
    costo_total=suma_pt/suma_ct
    print(nombre)
    print('costo total = ', costo_total)
    #mysql.connection.commit()
    #cur=mysql.connection.cursor()
    #cur.execute('INSERT INTO costo_materiaprima (producto,costo,kilos) VALUES(%s,%s,%s)',
    #(producto,costo_total,suma_ct))
    #mysql.connection.commit()

    return 

def ordenar_fecha(fecha):
    fecha_a=fecha[:4]
    fecha_m=fecha[5:7]
    fecha_d=fecha[8:]
    fecha_t=fecha_a
    fecha_t+=fecha_m
    fecha_t+=fecha_d
    fecha_indice=fecha_t
    fecha_a=fecha[:4]
    fecha_m=fecha[5:7]
    fecha_d=fecha[8:]
    fecha_t=fecha_d
    fecha_t+='-'
    fecha_t+=fecha_m
    fecha_t+='-'
    fecha_t+=fecha_a
    fecha_ordenada=fecha_t

    return (fecha_indice,fecha_ordenada)

#@app.route('/borrarmp',methods=['GET','POST'])
#def borrarmp():
#
#    cur=mysql.connection.cursor()
#    cur.execute('SELECT * FROM costo_materiaprima')
#    data=cur.fetchall()
#    cm=[]
#    for j in data:
#        cm.append(j[1])
#    costo='0.0'
#    kilos='0.0'
#    for j in cm:
#        cur=mysql.connection.cursor()
#        cur.execute("""
#            UPDATE costo_materiaprima 
#            SET costo=%s,
#                kilos=%s                           
#            WHERE producto = %s
#        """,(costo,kilos,j))
#    mysql.connection.commit()
#    return 'construccion'



##### crear alimento

@app.route('/crear_alimento_add',methods=['GET','POST'])
def crear_alimento_add():
    if request.method=='POST':
        nombre=request.form['nombre']
        if not nombre:
            flash('Debe Ingresar el Nombre del Alimento','crear_alimento')
            return redirect(url_for('crear_alimento'))
        print(nombre)

        nombre=nombre.upper()

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM tipo_alimento')
        data=cur.fetchall()
        bd_alimento=[]
        for j in data:
            bd_alimento.append(j[1])
        for j in bd_alimento:
            if j == nombre:
                flash(f'El alimento {nombre} ya esta creado en la base de datos ','crear_alimento')
                return redirect(url_for('crear_alimento'))
        cantidad='0'
        costo='0,0'
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO tipo_alimento (alimento,fecha) VALUES(%s,%s)',
        (nombre,cantidad))
        mysql.connection.commit()  

        
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO inventario_alimento (producto,cantidad,costo) VALUES(%s,%s,%s)',
        (nombre,cantidad,costo))
        mysql.connection.commit() 

        flash(f'Alimento {nombre} creada exitosamente','crear_alimento')
        return redirect(url_for('crear_alimento'))




    return 'construccion'



@app.route('/crear_alimento')
def crear_alimento():

    return render_template('crear_alimento.html')




##### crear materiaprima

@app.route('/crear_materiaprima_add',methods=['GET','POST'])
def crear_materia_prima_add():

    if request.method=='POST':
        nombre=request.form['nombre']
        alarma=request.form['alarma']

        if not nombre or not alarma:
            flash('Debe Llenar Todos Los Campos','crear_materiaprima')
            return redirect(url_for('crear_materiaprima'))
        no_numero=0
        for j in alarma:        
            if j=='0' or j=='1' or j=='2' or j=='3' or j== '4' or j=='5' or j=='6' or j=='7' or j=='8' or j=='9':
                None
            else:
                no_numero=1
        if no_numero==1:
            flash('En la cantidad de Kg de ALARMA solo debe indicar numeros enteros, sin "," ni "."','crear_materiaprima')
            return redirect(url_for('crear_materiaprima'))
        
        nombre=nombre.upper()
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto')
        data=cur.fetchall()
        bd_mp=[]
        for j in data:
            bd_mp.append(j[1])
        

        for j in bd_mp:
            if j == nombre:
                flash('El Producto indicado ya existe en la base de datos','crear_materiaprima')
                return redirect(url_for('crear_materiaprima'))

        costo=0.0
        kilos=0.0
        alarma=float(alarma)
        print(nombre, ' ',costo,' ',kilos,' ',alarma)

        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO lista_materiaprima (producto,alarma) VALUES(%s,%s)',
        (nombre,alarma))
        mysql.connection.commit() 

        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO costo_materiaprima (producto,costo,kilos) VALUES(%s,%s,%s)',
        (nombre,costo,kilos))
        mysql.connection.commit() 

        flash(f'MateriaPrima {nombre} creada exitosamente','crear_materiaprima')
        return redirect(url_for('crear_materiaprima'))

        
        

    return 'construccion'


@app.route('/crear_materiaprima')
def crear_materiaprima():

    return render_template('crear_materiaprima.html')


##### mostrar usuarios

@app.route('/mostrar_usuarios')
def mostrar_usuarios():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM user')
    data=cur.fetchall()
    user=[]
    for j in data:
        user.append(j)

    print(user)



    return render_template('usuarios_mostrar.html',user=user)






##### agregar usuarios
@app.route('/agregar_usuarios_add',methods=['GET','POST'])
def agregar_usuarios_add():
    if request.method=='POST':
        username=request.form['username']
        nombre=request.form['nombre']
        password=request.form['password']
        password2=request.form['password2']
        tipo=request.form['tipo']

        if not username or not nombre or not password or not password2:
            print('llenar campos')
            flash('Debe Llenar Todos Los Campos','agregar_usuarios')
            return redirect(url_for('agregar_usuarios'))
        if tipo=='0':
            flash('Debe Seleccionar el Tipo de Usuario','agregar_usuarios')
            return redirect(url_for('agregar_usuarios'))

        if password != password2:
            print('password no coincide')
            flash('El password no coincide con el password de confirmacion','agregar_usuarios')
            return redirect(url_for('agregar_usuarios'))

        print('username = ', username)

        #username=username.upper()
        nombre=nombre.upper()

        clave=generate_password_hash(password)
        print(clave)
        
        tipo=int(tipo)
        print('tipo 1 = ',tipo)
        
        
        nivel_user=tipo_usuario[tipo]
        print(nivel_user)

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM user')
        data=cur.fetchall()
        bd_user=[]
        for j in data:
            bd_user.append(j[1])
        user_existe=0
        for j in bd_user:
            if j == username:
                user_existe=1
        
        if user_existe ==1:
            print('El usuario existe')
            flash('El Usuario existe','agregar_usuarios')
            return redirect(url_for('agregar_usuarios'))
        
        if nivel_user=='administrador':
            user_nivel='admin'
            permiso='1'
            solicitud='0'
        else:
            user_nivel='normal'
            permiso='0'
            solicitud='0'
        

        



        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO user (username,password,fullname,permiso,solicitud,nivel) VALUES(%s,%s,%s,%s,%s,%s)',
        (username,clave,nombre,permiso,solicitud,user_nivel))
        mysql.connection.commit() 

        flash('USUARIO Agregado Exitoso','agregar_usuarios')
        return redirect(url_for('agregar_usuarios'))





        


        
        

    return 'construccion'


@app.route('/agregar_usuarios')
def agregar_usuarios():

    return render_template('usuarios_agregar.html',tipo_usuario=tipo_usuario)








#### agregar granjas externas



@app.route('/clientes_externos_add',methods=['GET','POST'])
def clientes_externos_add():

    if request.method=='POST':
        nombre=request.form['nombre']
        rif=request.form['rif']
        direccion=request.form['direccion']

        if not nombre or not rif or not direccion:
            flash('Debe Llenar Todos Los Campos','add_clientes_externos')
            return redirect(url_for('clientes_externos'))


        nombre=nombre.upper()
        rif=rif.upper()
        direccion=direccion.upper()

        print('nombre = ',nombre)
        print('rif = ',rif)
        print('direccion = ',direccion)

        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO lista_clientes (nombre,direccion,identificacion) VALUES(%s,%s,%s)',
        (nombre,direccion,rif))
        mysql.connection.commit() 

        flash('Cliente Interno Agregado Exitoso','add_clientes_externos')
        return redirect(url_for('clientes_externos'))




    return 'construccion'


@app.route('/clientes_externos')
def clientes_externos():


    return render_template('clientes_externos_agregar.html')







#### agregar granjas internas


@app.route('/clientes_internos_add',methods=['GET','POST'])
def clientes_internos_add():

    if request.method=='POST':
        nombre=request.form['nombre']
        id_socio=request.form['propietario']

        if not nombre:
            flash('debe introducir todos los campos','add_clientes_internos')
            return redirect(url_for('clientes_internos'))
        if id_socio=='0':
            flash('debe introducir todos los campos','add_clientes_internos')
            return redirect(url_for('clientes_internos'))
        
        id_socio=int(id_socio)
        id_socio=id_socio-1

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM propietario ORDER BY propietario')
        data=cur.fetchall()
        socio_id=[]
        for j in data:
            socio_id.append(j[1])
        socio=socio_id[id_socio]
        print('socio = ',socio)
        nombre=nombre.upper()
        print('granja = ', nombre)

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM aba_destinos_internos ORDER BY nombre')
        data=cur.fetchall()
        name_dest=[]
        for j in data:
            name_dest.append(j[1])
        existe=0
        for j in name_dest:
            if j == nombre:
                existe=1
        print('existe = ',existe)
        if existe==1:
            flash(f'error al crear el cliente {nombre} debido a que ya existe en la lista de clientes internos ','add_clientes_internos')
            return redirect(url_for('clientes_internos'))

        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO aba_destinos_internos (nombre,propietario) VALUES(%s,%s)',
        (nombre,socio))
        mysql.connection.commit() 

        flash('Cliente Interno Agregado Exitoso','add_clientes_internos')
        return redirect(url_for('clientes_internos'))
        




        


    return 'construccion'



@app.route('/clientes_internos')
def clientes_internos():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall()
    propietario=['[ SELECCIONE ]']
    for j in data:
        propietario.append(j[1])
    print(propietario)

    return render_template('clientes_internos_agregar.html',propietario=propietario)


###### mostrar proveedores

@app.route('/proveedor_add',methods=['GET','POST'])
def proveedor_add():
    if request.method=='POST':
        nombre=request.form['nombre']
        rif=request.form['rif']
        producto=request.form['producto']
        direccion=request.form['direccion']
        telefono=request.form['telefono']
        contacto=request.form['contacto']

        if not nombre or not rif or not direccion or not telefono or not contacto:
            print('debe introducir todos los campos')
            flash('debe introducir todos los campos','agregar_proveedor')
            return redirect(url_for('proveedores_agregar'))


        nombre=nombre.upper()
        rif=rif.upper()
        direccion=direccion.upper()
        contacto=contacto.upper()
        


        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto')
        data=cur.fetchall()
        mp=[]
        for j in data:
            mp.append(j[1])
        producto=int(producto)
        product_name=mp[producto]
        print('producto seleccionado = ',product_name)

        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO proveedores (proveedor,rif,producto,direccion,telefono,contacto) VALUES(%s,%s,%s,%s,%s,%s)',
        (nombre,rif,product_name,direccion,telefono,contacto))
        mysql.connection.commit() 

        flash('Proveedor Agregado Exitoso','agregar_proveedor')
        return redirect(url_for('proveedores_agregar'))

        


    return redirect(url_for('proveedores_agregar'))




@app.route('/proveedores_agregar')
def proveedores_agregar():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto')
    data=cur.fetchall()
    mp=[]
    for j in data:
        mp.append(j[1])


    return render_template('proveedor_agregar.html',mp=mp)




@app.route('/mostrar_proveedores')
def mostrar_proveedores():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM proveedores ORDER BY proveedor')
    data=cur.fetchall()
    print(data)
    proveedores=[]
    for j in data:
        proveedores.append(j)

    return render_template('mostrar_proveedores.html',proveedores=proveedores)








############## permisos


@app.route('/desactivar_permisos',methods=['GET','POST'])
def desactivar_permisos():

    id_user = current_user.id

    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE user 
        SET permiso=%s                           
        WHERE id = %s
    """,('0',id_user))
    mysql.connection.commit()


    return 'construccion'




@app.route('/aceptar_solicitud_permiso/<id>/<id_solicitud_permiso>',methods=['GET','POST'])
def aceptar_solicitud_permiso(id,id_solicitud_permiso):
    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM user WHERE id = {id}')
    data=cur.fetchall()
    print('usuario que solicita el permiso')
    print(data)
    usuario=[]
    

    print('id = ',id)
    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE user 
        SET permiso=%s                           
        WHERE id = %s
    """,('1',id))
    mysql.connection.commit()




    cur=mysql.connection.cursor()
    cur.execute(f'DELETE FROM solicitud_permiso WHERE id = {id_solicitud_permiso}')
    mysql.connection.commit()

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM solicitud_permiso')
    data=cur.fetchall()
    print(data)
    if (not data):
        solicitud='0'
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM user')
        data=cur.fetchall()
        usuarios=[]
        for j in data:
            usuarios.append(j)
        user_admin=[]
        for j in usuarios:
            if j[6]=='admin':
                user_admin.append(j)
        print('todos los usuarios')
        print(usuarios)
        print('')
        print('usuarios administrador')
        print(user_admin)

        for j in user_admin:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE user 
                SET solicitud=%s                           
                WHERE id = %s
            """,(solicitud,j[0]))
            mysql.connection.commit()







    else:
        solicitud='1'
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM user')
        data=cur.fetchall()
        usuarios=[]
        for j in data:
            usuarios.append(j)
        user_admin=[]
        for j in usuarios:
            if j[6]=='admin':
                user_admin.append(j)
        print('todos los usuarios')
        print(usuarios)
        print('')
        print('usuarios administrador')
        print(user_admin)

        for j in user_admin:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE user 
                SET solicitud=%s                           
                WHERE id = %s
            """,(solicitud,j[0]))
            mysql.connection.commit()
    print('solicitud = ', solicitud)







    return 'construccion'



@app.route('/lista_permisos',methods=['GET','POST'])
def lista_permisos():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM solicitud_permiso')
    data=cur.fetchall()
    print(data)
    list_permisos=[]
    usuario=[]
    for j in data:
        list_permisos.append(j)
        cur=mysql.connection.cursor()
        id_u=j[1]
        cur.execute(f'SELECT * FROM user WHERE id = {id_u}')
        data=cur.fetchall()
        for k in data:
            usuario.append(k)
    fechai,fecha,fechao=fecha_hoy()
    print(list_permisos)
    print(usuario)
    print(fechao)
    return render_template('lista_permisos.html',
                           list_permisos=list_permisos,
                           usuario=usuario,
                           fechao=fechao
                           )

@app.route('/solicitar_permisos',methods=['GET','POST'])
def solicitar_permisos():

    if request.method=='POST':
        motivo=request.form['motivo']
        id_usuario = request.form['id_usuario']

        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO solicitud_permiso (id_usuario,motivo) VALUES(%s,%s)',
        (id_usuario,motivo))
        mysql.connection.commit() 

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM user')
        data=cur.fetchall()
        usuarios=[]
        for j in data:
            usuarios.append(j)
        user_admin=[]
        for j in usuarios:
            if j[6]=='admin':
                user_admin.append(j)
        print('todos los usuarios')
        print(usuarios)
        print('')
        print('usuarios administrador')
        print(user_admin)

        for j in user_admin:
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE user 
                SET solicitud=%s                           
                WHERE id = %s
            """,('1',j[0]))
            mysql.connection.commit()

        



    return 'construccion'


@app.route('/permisos',methods=['GET','POST'])
def permisos():

    return render_template('permisos.html')







###### balance




@app.route('/balance')
def balance():
    print(current_user.permiso)
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima')
    data=cur.fetchall()
    print(data)
    print(len(data))
    precio_mp=[]
    kilos_mp=[]
    for j in data:
        a=j[2]
        a=float(a)
        precio_mp.append(a)
        a=j[3]
        a=float(a)
        kilos_mp.append(a)
    print('precio = ',precio_mp)
    print('kilos = ',kilos_mp)
    monto_mp=np.multiply(precio_mp,kilos_mp)
    total_mp=np.sum(monto_mp,axis=0)
    print('monto total mp = ',total_mp)
    print('monto materiaprima = ',total_mp)

    # total_mp es el valor de la materiaprima

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento')
    data=cur.fetchall()
    print(data)
    precio_aba=[]
    kilos_aba=[]
    for j in data:
        a=j[2]
        a=devolver_separador_miles(a)
        a=float(a)
        kilos_aba.append(a)
        a=j[8]
        a=devolver_separador_miles(a)
        a=float(a)
        precio_aba.append(a)
    print('kilos aba = ', kilos_aba)
    print('precio aba = ',precio_aba)

    monto_aba=np.multiply(kilos_aba,precio_aba)
    print('monto_aba = ',monto_aba)

    total_aba=np.sum(monto_aba,axis=0)
    print('total aba = ',total_aba)

    #### total_aba es el monto total del inventario de alimento aba

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM ventas_materiaprima')
    data=cur.fetchall()
    print(data)
    fpc=[]
    a_fpc=[]
    for j in data:
        a=j[10]
        a=devolver_separador_miles(a)
        a=float(a)
        fpc.append(a)
        a=j[9]
        a=devolver_separador_miles(a)
        a=float(a)
        a_fpc.append(a)
    print('facturas por cobrar = ',fpc)
    total_fpc=np.sum(fpc,axis=0)

    print('abono facturas por cobrar = ',a_fpc)
    total_a_fpc=np.sum(a_fpc,axis=0)
    print('total abono facturas por cobrar = ', total_a_fpc)

    ### total_fpc es el monto total de facturas por cobrar
    ### total_a_fpc es el monto total de abono de facturas por cobrar

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM compras_materiaprima')
    data=cur.fetchall()
    print(data)
    fpp=[]
    a_fpp=[]
    for j in data:
        a=j[10]
        a=devolver_separador_miles(a)
        a=float(a)
        fpp.append(a)
        a=j[9]
        a=devolver_separador_miles(a)
        a=float(a)
        a_fpp.append(a)
    print('')
    print('faturas por pagar ')
    print(fpp)
    print('abono facturas por pagar')
    print(a_fpp)
    total_fpp=np.sum(fpp,axis=0)
    total_a_fpp=np.sum(a_fpp,axis=0)
    print('')
    print('total faturas por pagar ')
    print(total_fpp)
    print('total abono facturas por pagar')
    print(total_a_fpp)



    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM gastos')
    data=cur.fetchall()
    print(data)
    gastos=[]
    gastos_mh=[]
    gastos_proaba=[]
    for j in data:
        a=j[3]
        a=devolver_separador_miles(a)
        a=float(a)
        gastos.append(a)
        if j[12]=='mh2018':
            gastos_mh.append(a)
        if j[12]=='proaba':
            gastos_proaba.append(a)
    
    print('')
    print('gastos')
    print(gastos)
    print('')
    print('gastos mh ')
    print(gastos_mh)
    print('')
    print('gastos proaba')
    print(gastos_proaba)

    total_gastos=np.sum(gastos,axis=0)
    total_gastos_mh=np.sum(gastos_mh,axis=0)
    total_gastos_proaba=np.sum(gastos_proaba,axis=0)

    print('')
    print('total gastos')
    print(total_gastos)
    print('')
    print('total gastos mh ')
    print(total_gastos_mh)
    print('')
    print('total gastos proaba')
    print(total_gastos_proaba)



    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM saldo_caja')
    data=cur.fetchall()
    print('caja = ', data)
    
    for j in data:
        caja=j[3]



    caja=devolver_separador_miles(caja)
    caja=float(caja)
    total_activos=total_mp+total_aba+total_fpc+caja
    total_pasivos=total_fpp+total_gastos


    total_mp=separador_miles(total_mp)
    total_aba=separador_miles(total_aba)
    total_fpc=separador_miles(total_fpc)
    total_a_fpc=separador_miles(total_a_fpc)
    total_activos=separador_miles(total_activos)
    caja=separador_miles(caja)

    total_fpp=separador_miles(total_fpp)
    
    total_gastos=separador_miles(total_gastos)
    total_a_fpp=separador_miles(total_a_fpp)
    total_pasivos=separador_miles(total_pasivos)

    return render_template('balance.html',
                           total_mp=total_mp,
                           total_aba=total_aba,
                           total_fpc=total_fpc,
                           total_a_fpc=total_a_fpc,
                           total_activos=total_activos,
                           caja=caja,

                           total_fpp=total_fpp,
                           total_a_fpp=total_a_fpp,
                           total_gastos=total_gastos,
                           total_pasivos=total_pasivos
                           )

#### alimento por cobrar
@app.route('/alimento_por_cobrar')
def alimento_por_cobrar():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM despacho_aba_ventas') 
    data=cur.fetchall()
    dav=[]
    fact=[]
    for j in data:
        dav.append(j)
        fact.append(j[1])
    print(dav)

    facturas=[]
    for j in fact:
        a='xz'
        a+=j
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM '+a)
        data=cur.fetchall()
        print(data)
        for k in data:
            monto=k[16]
            monto=devolver_separador_miles(monto)
            monto=float(monto)
            if monto > 0:
                facturas.append(k)
    print('facturas')
    print(facturas)
    return render_template('alimento_por_cobrar.html',facturas=facturas)




#### calculo utilidad
@app.route('/calculo_utilidad',methods=['GET','POST'])

def calculo_utilidad():

    if request.method=='POST':
        fecha1=request.form['fecha1']
        fecha2=request.form['fecha2']
        fecha_indice1,fecha_ordenada1=ordenar_fecha(fecha1)
        fecha_indice2,fecha_ordenada2=ordenar_fecha(fecha2)

        print(fecha_indice1)
        print(fecha_indice2)
        #WHERE fecha_indice BETWEEN {fecha1} AND {fecha2}
        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM despacho_aba_interno WHERE fecha_indice BETWEEN {fecha_indice1} AND {fecha_indice2}')
        data=cur.fetchall()
        cp_dai=[]
        co_dai=[]
        kg_dai=[]
        precio_dai=[]
        factura=[]
        alimento=[]
        cliente=[]
        propietario=[]
        fecha=[]
        print(data)
        for j in data:
            a=j[12]
            a=devolver_separador_miles(a)
            a=float(a)
            cp_dai.append(a)
    
            a=j[13]
            a=devolver_separador_miles(a)
            a=float(a)
            co_dai.append(a)
    
            a=j[5]
            a=devolver_separador_miles(a)
            a=float(a)
            kg_dai.append(a)
    
            a=j[6]
            a=devolver_separador_miles(a)
            a=float(a)
            precio_dai.append(a)

            factura.append(j[1])
            alimento.append(j[2])
            cliente.append(j[3])
            propietario.append(j[4])
            fecha.append(j[10])
    
        print('cp dai')
        print(cp_dai)
        print('co dai')
        print(co_dai)
        print('kg dai')
        print(kg_dai)
        print('precio dai')
        print(precio_dai)
    
        
        costo_final=[]
        i=0
        for j in co_dai:
            a=j
            b=cp_dai[i]
            c=a+b
            costo_final.append(c)
    
        print('costo final')
        print(costo_final)
        
        precio_venta=np.multiply(costo_final,3)
        precio_venta_f=np.divide(precio_venta,100)
        precio_venta_f=np.add(costo_final,precio_venta_f)
    
        print('precio venta')
        print(precio_venta)
    
    
        print('precio venta final')
        print(precio_venta_f)
    
        uti_kg=precio_venta_f-costo_final
    
        print('utilidad por kg')
        print(uti_kg)
    
        uti_total=np.multiply(uti_kg,kg_dai)
        print('utilidad total')
        print(uti_total)
    
        uti_mht=np.multiply(uti_total,60)
        print('utilidad mht')
        print(uti_mht)
        uti_mh=np.divide(uti_mht,100)
        print('utilidad mht')
        print(uti_mh)
    
        uti_proaba=np.multiply(uti_total,40)
        print('utilidad proaba')
        print(uti_proaba)
        uti_proaba=np.divide(uti_proaba,100)
        print('utilidad proaba')
        print(uti_proaba)
    
        print('')
        print('')
        print('')
        print('utilidad mht')
        print(uti_mh)
        print('utilidad proaba')
        print(uti_proaba)
        print('')
        print('')
    
        uti_t_mh=np.sum(uti_mh,axis=0)
        uti_t_proaba=np.sum(uti_proaba,axis=0)
    
        print('suma utilidad mh')
        print(uti_t_mh)
        print('suma utilidad proaba')
        print(uti_t_proaba)

        kg_dai_float=[]
        for j in kg_dai:
            a=j
            a=separador_miles(a)
            kg_dai_float.append(a)
        
        co_dai_float=[]
        for j in co_dai:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            co_dai_float.append(a)

        cp_dai_float=[]
        for j in cp_dai:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            cp_dai_float.append(a)
        
        costo_final_float=[]
        for j in costo_final:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            costo_final_float.append(a)

        precio_venta_f_float=[]
        for j in precio_venta_f:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            precio_venta_f_float.append(a)
        
        uti_kg_float=[]
        for j in uti_kg:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            uti_kg_float.append(a)

        uti_total_float=[]
        for j in uti_total:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            uti_total_float.append(a)
        
        uti_mh_float=[]
        for j in uti_mh:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            uti_mh_float.append(a)
        
        uti_proaba_float=[]
        for j in uti_proaba:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            uti_proaba_float.append(a)
        total_utilidad=uti_t_mh+uti_t_proaba
        total_utilidad=separador_miles(total_utilidad)
        uti_t_mh=separador_miles(uti_t_mh)
        uti_t_proaba=separador_miles(uti_t_proaba)

############ utilidad de ventas de alimento
        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM despacho_aba_ventas WHERE fecha_indice BETWEEN {fecha_indice1} AND {fecha_indice2}')
        data=cur.fetchall()
        vcp_dai=[]
        vco_dai=[]
        vkg_dai=[]
        vprecio_dai=[]
        vfactura=[]
        valimento=[]
        vcliente=[]
        vpropietario=[]
        vfecha=[]
        print(data)
        for j in data:
            a=j[12]
            a=devolver_separador_miles(a)
            a=float(a)
            vcp_dai.append(a)
    
            a=j[13]
            a=devolver_separador_miles(a)
            a=float(a)
            vco_dai.append(a)
    
            a=j[5]
            a=devolver_separador_miles(a)
            a=float(a)
            vkg_dai.append(a)
    
            a=j[6]
            a=devolver_separador_miles(a)
            a=float(a)
            vprecio_dai.append(a)

            vfactura.append(j[1])
            valimento.append(j[2])
            vcliente.append(j[3])
            vpropietario.append(j[4])
            vfecha.append(j[10])
    
        print('vcp dai')
        print(vcp_dai)
        print('vco dai')
        print(vco_dai)
        print('vkg dai')
        print(vkg_dai)
        print('vprecio dai')
        print(vprecio_dai)

        vcosto_final=[]
        i=0
        for j in vco_dai:
            a=j
            b=vcp_dai[i]
            c=a+b
            vcosto_final.append(c)
    
        print('vcosto final')
        print(vcosto_final)
        
        vprecio_venta=np.multiply(vcosto_final,3)
        vprecio_venta_f=np.divide(vprecio_venta,100)
        vprecio_venta_f=np.add(vcosto_final,vprecio_venta_f)
    
        print('vprecio venta')
        print(vprecio_venta)
    
    
        print('vprecio venta final')
        print(vprecio_venta_f)
       

        vuti_kg= np.subtract(vprecio_dai,vcosto_final) 
    
        print('vutilidad por kg')
        print(vuti_kg)
    
        vuti_total=np.multiply(vuti_kg,vkg_dai)
        print('vutilidad total')
        print(vuti_total)
    
        vuti_mht=np.multiply(vuti_total,50)
        print('vutilidad mht')
        print(vuti_mht)
        vuti_mh=np.divide(vuti_mht,100)
        print('vutilidad mht')
        print(vuti_mh)
    
        vuti_proaba=np.multiply(vuti_total,50)
        print('vutilidad proaba')
        print(vuti_proaba)
        vuti_proaba=np.divide(vuti_proaba,100)
        print('vutilidad proaba')
        print(vuti_proaba)
    
        print('')
        print('')
        print('')
        print('vutilidad mht')
        print(vuti_mh)
        print('vutilidad proaba')
        print(vuti_proaba)
        print('')
        print('')
    
        vuti_t_mh=np.sum(vuti_mh,axis=0)
        vuti_t_proaba=np.sum(vuti_proaba,axis=0)
        total_utilidad_ventas=vuti_t_mh + vuti_t_proaba
        total_utilidad_ventas=separador_miles(total_utilidad_ventas)
        print('vsuma utilidad mh')
        print(vuti_t_mh)
        print('vsuma utilidad proaba')
        print(vuti_t_proaba)


        vkg_dai_float=[]
        for j in vkg_dai:
            a=j
            a=separador_miles(a)
            vkg_dai_float.append(a)
        
        vco_dai_float=[]
        for j in vco_dai:
            a=j
            a=separador_miles(a)
            vco_dai_float.append(a)

        vcp_dai_float=[]
        for j in vcp_dai:
            a=j
            a=separador_miles(a)
            vcp_dai_float.append(a)
        
        vcosto_final_float=[]
        for j in vcosto_final:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            vcosto_final_float.append(a)

        vprecio_dai_float=[]
        for j in vprecio_dai:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            vprecio_dai_float.append(a)
        
        vuti_kg_float=[]
        for j in vuti_kg:
            a=j
            a="{:,.3f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            vuti_kg_float.append(a)

        vuti_total_float=[]
        for j in vuti_total:
            a=j
            a="{:,.2f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            vuti_total_float.append(a)
        
        vuti_mh_float=[]
        for j in vuti_mh:
            a=j
            a="{:,.2f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            vuti_mh_float.append(a)
        
        vuti_proaba_float=[]
        for j in vuti_proaba:
            a=j
            a="{:,.2f}".format(a).replace(",","x").replace(".",",").replace("x",".")
            #a=separador_miles(a)
            vuti_proaba_float.append(a)

        vuti_t_mh=separador_miles(vuti_t_mh)
        vuti_t_proaba=separador_miles(vuti_t_proaba)
    return render_template('calculo_utilidad.html',
                           factura=factura,
                           alimento=alimento,
                           cliente=cliente,
                           propietario=propietario,
                           fecha=fecha,
                           kg_dai=kg_dai_float,
                           co_dai=co_dai_float,
                           cp_dai=cp_dai_float,
                           costo_final=costo_final_float,
                           precio_venta=precio_venta_f_float,
                           uti_kg=uti_kg_float,
                           uti_total=uti_total_float,
                           uti_mh=uti_mh_float,
                           uti_proaba=uti_proaba_float,
                           fecha1=fecha_ordenada1,
                           fecha2=fecha_ordenada2,
                           utilidad_mh=uti_t_mh,
                           utilidad_proaba=uti_t_proaba,

                           vfactura=vfactura,
                           valimento=valimento,
                           vcliente=vcliente,
                           vpropietario=vpropietario,
                           vfecha=vfecha,
                           vkg_dai=vkg_dai_float,
                           vco_dai=vco_dai_float,
                           vcp_dai=vcp_dai_float,
                           vcosto_final=vcosto_final_float,
                           vprecio_venta=vprecio_dai_float,
                           vuti_kg=vuti_kg_float,
                           vuti_total=vuti_total_float,
                           vuti_mh=vuti_mh_float,
                           vuti_proaba=vuti_proaba_float,                           
                           vutilidad_mh=vuti_t_mh,
                           vutilidad_proaba=vuti_t_proaba,
                           total_utilidad=total_utilidad,
                           total_utilidad_ventas=total_utilidad_ventas
                           )





@app.route('/calcular_utilidad')
def calcular_utilidad():
    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM despacho_aba_interno')
    data=cur.fetchall()
    cp_dai=[]
    co_dai=[]
    kg_dai=[]
    precio_dai=[]
    
    for j in data:
        a=j[12]
        a=devolver_separador_miles(a)
        a=float(a)
        cp_dai.append(a)

        a=j[13]
        a=devolver_separador_miles(a)
        a=float(a)
        co_dai.append(a)

        a=j[5]
        a=devolver_separador_miles(a)
        a=float(a)
        kg_dai.append(a)

        a=j[6]
        a=devolver_separador_miles(a)
        a=float(a)
        precio_dai.append(a)
    

    print('cp dai')
    print(cp_dai)
    print('co dai')
    print(co_dai)
    print('kg dai')
    print(kg_dai)
    print('precio dai')
    print(precio_dai)

    
    costo_final=[]
    i=0
    for j in co_dai:
        a=j
        b=cp_dai[i]
        c=a+b
        costo_final.append(c)

    print('costo final')
    print(costo_final)
    
    precio_venta=np.multiply(costo_final,3)
    precio_venta_f=np.divide(precio_venta,100)
    precio_venta_f=np.add(costo_final,precio_venta_f)

    print('precio venta')
    print(precio_venta)


    print('precio venta final')
    print(precio_venta_f)

    uti_kg=precio_venta_f-costo_final

    print('utilidad por kg')
    print(uti_kg)

    uti_total=np.multiply(uti_kg,kg_dai)
    print('utilidad total')
    print(uti_total)

    uti_mht=np.multiply(uti_total,60)
    print('utilidad mht')
    print(uti_mht)
    uti_mh=np.divide(uti_mht,100)
    print('utilidad mht')
    print(uti_mh)

    uti_proaba=np.multiply(uti_total,40)
    print('utilidad proaba')
    print(uti_proaba)
    uti_proaba=np.divide(uti_proaba,100)
    print('utilidad proaba')
    print(uti_proaba)

    print('')
    print('')
    print('')
    print('utilidad mht')
    print(uti_mh)
    print('utilidad proaba')
    print(uti_proaba)
    print('')
    print('')

    uti_t_mh=np.sum(uti_mh,axis=0)
    uti_t_proaba=np.sum(uti_proaba,axis=0)

    print('suma utilidad mh')
    print(uti_t_mh)
    print('suma utilidad proaba')
    print(uti_t_proaba)



    

    return 'construccion'


@app.route('/utilidad')
@login_required
def utilidad():

    return render_template('/utilidad.html')
################






### inventario alimento

# alimento externo

@app.route('/confirmacion/salida_alimento/externo',methods=['GET','POST'])
def confirmacion_salida_alimento_externo():
    if request.method=='POST':
        factura=request.form['num_fact']
        fecha=request.form['fecha']
        cliente=request.form['cliente']
        propietario=request.form['propietario']
        producto=request.form['producto']
        cantidad=request.form['cantidad']
        precio=request.form['precio']
        comentario=request.form['comentario']
    
    if (not factura) or (not fecha) or (not cliente) or (not propietario) or (not producto) or (not cantidad) or (not precio):
        print('Debe llenar todos los caqmpos')
        flash('Debe llenar todos los caqmpos','salida_aba_externo')
        return redirect(url_for('salida_alimento_externo'))
    
    if cliente=='0':
        print('Debe llenar todos los caqmpos')
        flash('Debe llenar todos los caqmpos','salida_aba_externo')
        return redirect(url_for('salida_alimento_externo'))

    if propietario=='0':
        print('Debe llenar todos los caqmpos')
        flash('Debe llenar todos los caqmpos','salida_aba_externo')
        return redirect(url_for('salida_alimento_externo'))

    if producto=='0':
        print('Debe llenar todos los caqmpos')
        flash('Debe llenar todos los caqmpos','salida_aba_externo')
        return redirect(url_for('salida_alimento_externo'))

    cliente=int(cliente)
    propietario=int(propietario)
    producto=int(producto)

    cliente=cliente-1
    propietario=propietario-1
    producto=producto-1

    i=0 
    x=0
    for j in cantidad:
        print('j = ',j)
        if j =='.':
            if x ==0:
                print('La cantidad esta mal escrita')
                flash('La cantidad esta mal escrita','salida_aba_externo')
                return redirect(url_for('salida_alimento_externo'))
            i=i+1
            if i>1:
                print('La cantidad esta mal escrita')
                flash('La cantidad esta mal escrita','salida_aba_externo')
                return redirect(url_for('salida_alimento_externo'))
        x=x+1
    i=0 
    x=0
    for j in precio:
        print('j = ',j)
        if j =='.':
            if x ==0:
                print('El precio esta mal escrito')
                flash('El precio esta mal escrito','salida_aba_externo')
                return redirect(url_for('salida_alimento_externo'))
            i=i+1
            if i>1:
                print('EL precio esta mal escrito')
                flash('EL precio esta mal escrito','salida_aba_externo')
                return redirect(url_for('salida_alimento_externo'))
        x=x+1
    
          
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_clientes ORDER BY nombre')
    data=cur.fetchall()
    clientes=[]    
    for j in data:
        clientes.append(j[1])
    id_cliente=int(cliente)  
    cliente=clientes[id_cliente]
    print('cliente = ', cliente)
    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall()
    propietarios=[]
    for j in data:
        propietarios.append(j[1])
    id_propietario=int(propietario)
    propietario=propietarios[id_propietario]
    print(propietario)

    precio=float(precio)
    cantidad=float(cantidad)
    monto=precio*cantidad
    print(monto)
    

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento')
    data=cur.fetchall()
    tipo_alimento=[]
    for j in data:
        tipo_alimento.append(j[1])
    producto=int(producto)
    alimento=tipo_alimento[producto]



    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento ORDER BY producto')
    data=cur.fetchall()
    inv_aba=[]
    id_inv_a=[]
    for j in data:
        id_inv_a.append(j[0])
        inv_aba.append(j[2])
    print(id_inv_a)
    print('producto = ',producto)
    print('inv_aba')
    print(inv_aba)
    id_aba=id_inv_a[producto]
    kg_bd=inv_aba[producto]
    kg_bd=float(kg_bd)
    print('kd bd = ',kg_bd)

    kg_final= kg_bd-cantidad
    print('kd final = ',kg_final)
    if kg_final < 0:
        print('cantidad mayor')            
        flash('la cantidad supera la existencia en inventario','salida_aba_externo')
        return redirect(url_for('salida_alimento_externo'))
    

    #verificar si la factura ya existe
    cur=mysql.connection.cursor()
    cur.execute("SHOW TABLES") 
    mysql.connection.commit()
    
    fact='xz'+factura
    print('cur = ',cur)
    print(fact)
    for j in cur:                      
        print(j[0])
        if(str(j[0]) == str(fact)):
            print('existe')            
            flash('la factura ingresada existe en el sistema','salida_aba_externo')
            return redirect(url_for('salida_alimento_externo'))


    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento')
    data=cur.fetchall()
    print(data)
    cp=[]
    for j in data:
        cp.append(j[8])
    costo_p=cp[producto]
    print(costo_p)

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costos_operativos_actual')
    data=cur.fetchall()
    print(data)
    co=[]
    for j in data:
        c_operativo=j[1]
   

    

    fecha_indice,fecha_ordenada=ordenar_fecha(fecha)
    cantidad=separador_miles(cantidad)
    precio=separador_miles(precio)
    monto=separador_miles(monto)
    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO despacho_aba_ventas (factura,producto,cliente,propietario,cantidad,precio,monto,fecha,fecha_indice,fecha_ordenada,comentario,costo_produccion,costo_operativo) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (factura,alimento,cliente,propietario,cantidad,precio,monto,fecha,fecha_indice,fecha_ordenada,comentario,costo_p,c_operativo))
    mysql.connection.commit()    


    cur = mysql.connection.cursor()    
    cur.execute("CREATE TABLE IF NOT EXISTS " + fact + """ (
      id INT(11) NOT NULL AUTO_INCREMENT,PRIMARY KEY (id),
      propietario TEXT NOT NULL,
      factura TEXT NOT NULL,
      cliente TEXT NOT NULL,
      cantidad TEXT NOT NULL,
      precio TEXT NOT NULL,
      producto TEXT NOT NULL,
      fecha TEXT NOT NULL,
      fecha_indice TEXT NOT NULL,
      dolares TEXT NOT NULL,
      bolivares TEXT NOT NULL,
      banco TEXT NOT NULL,
      referencia TEXT NOT NULL,
      tasa TEXT NOT NULL,
      monto TEXT NOT NULL,
      abono TEXT NOT NULL,
      debe TEXT NOT NULL,
      comentario TEXT NOT NULL,
      fecha_ordenada TEXT NOT NULL)""")
    mysql.connection.commit()
    abono='0,00'
    debe=monto
    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO '+fact+ ' (factura,producto,cliente,propietario,cantidad,precio,monto,fecha,fecha_indice,fecha_ordenada,comentario,abono,debe) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (factura,alimento,cliente,propietario,cantidad,precio,monto,fecha,fecha_indice,fecha_ordenada,comentario,abono,debe))
    mysql.connection.commit()

    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE inventario_alimento 
        SET cantidad=%s                           
        WHERE id = %s
    """,(kg_final,id_aba))
    mysql.connection.commit()
    #return 'construccion'
    return redirect(url_for('planta_aba'))


@app.route('/salida_alimento/externo')
def salida_alimento_externo():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_clientes ORDER BY nombre')
    data=cur.fetchall()
    print(data)
    cliente=['[SELECCIONE]']    
    for j in data:
        cliente.append(j[1])
        
    print('')
    print('cliente')
    print(cliente)
    print('')
    


    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento')
    data=cur.fetchall()
    tipo_alimento=['[SELECCIONE]']
    for j in data:
        tipo_alimento.append(j[1])
    print('')
    print('tipos de alimentos')
    print(tipo_alimento)


    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall()
    propietario=['[SELECCIONE]']
    for j in data:
        propietario.append(j[1])
    return render_template('despacho_aba_externo.html',
                           cliente=cliente,
                           producto=tipo_alimento,
                           propietario=propietario
                           
                           )
# fin alimento externo

#alimento interno 
@app.route('/confirmacion/salida_alimento/interno',methods=['GET','POST'])
def confirmacion_salida_alimento_interno():
    if request.method=='POST':
        factura=request.form['num_fact']
        fecha=request.form['fecha']
        destino=request.form['destino']
        producto=request.form['producto']
        cantidad=request.form['cantidad']
        precio=request.form['precio']
        comentario=request.form['comentario']

    if (not factura) or (not fecha) or (not destino) or (not producto) or (not cantidad) or (not precio):
        print('Debe llenar todos los caqmpos')
        flash('Debe llenar todos los caqmpos','salida_aba_externo')
        return redirect(url_for('salida_alimento_externo'))

    if destino=='0':
        print('Debe llenar todos los caqmpos')
        flash('Debe llenar todos los caqmpos','salida_aba_externo')
        return redirect(url_for('salida_alimento_externo'))
    
    if producto=='0':
        print('Debe llenar todos los caqmpos')
        flash('Debe llenar todos los caqmpos','salida_aba_externo')
        return redirect(url_for('salida_alimento_externo'))

    producto=int(producto)
    producto=producto-1

    destino=int(destino)
    destino=destino-1


    i=0 
    x=0
    for j in cantidad:
        print('j = ',j)
        if j =='.':
            if x ==0:
                print('La cantidad esta mal escrita')
                flash('La cantidad esta mal escrita','salida_aba_interno')
                return redirect(url_for('salida_alimento_interno'))
            i=i+1
            if i>1:
                print('La cantidad esta mal escrita')
                flash('La cantidad esta mal escrita','salida_aba_interno')
                return redirect(url_for('salida_alimento_interno'))
        x=x+1
    i=0 
    x=0
    for j in precio:
        print('j = ',j)
        if j =='.':
            if x ==0:
                print('El precio esta mal escrito')
                flash('El precio esta mal escrito','salida_aba_interno')
                return redirect(url_for('salida_alimento_interno'))
            i=i+1
            if i>1:
                print('EL precio esta mal escrito')
                flash('EL precio esta mal escrito','salida_aba_interno')
                return redirect(url_for('salida_alimento_interno'))
        x=x+1
    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM aba_destinos_internos ORDER BY nombre')
    data=cur.fetchall()
    destinos=[]
    propietarios=[]
    for j in data:
        destinos.append(j[1])
        propietarios.append(j[2])
    destino=int(destino)
    destino_aba=destinos[destino]
    propietario=propietarios[destino]
    print(destino_aba)
    print(propietario)

    precio=float(precio)
    cantidad=float(cantidad)
    monto=precio*cantidad

    
    

    fact='xx'+factura
    print('cur = ',cur)
    print(fact)
    for j in cur:                      
        print(j[0])
        if(str(j[0]) == str(fact)):
            print('existe')            
            flash('la factura ingresada existe en el sistema','salida_aba_interno')
            return redirect(url_for('salida_alimento_interno'))
        
    print(monto)
    

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento')
    data=cur.fetchall()
    tipo_alimento=[]
    for j in data:
        tipo_alimento.append(j[1])
    producto=int(producto)
    alimento=tipo_alimento[producto]

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento ORDER BY producto')
    data=cur.fetchall()
    inv_aba=[]
    id_inv_a=[]
    for j in data:
        id_inv_a.append(j[0])
        inv_aba.append(j[2])
    print(id_inv_a)
    print('producto = ',producto)
    print('inv_aba')
    print(inv_aba)
    id_aba=id_inv_a[producto]
    kg_bd=inv_aba[producto]
    kg_bd=float(kg_bd)
    print('kd bd = ',kg_bd)

    kg_final= kg_bd-cantidad
    print('kd final = ',kg_final)
    if kg_final < 0:
        print('cantidad mayor')            
        flash('la cantidad supera la existencia en inventario','salida_aba_interno')
        return redirect(url_for('salida_alimento_interno'))
    

    fecha_indice,fecha_ordenada=ordenar_fecha(fecha)
    cantidad=separador_miles(cantidad)
    precio=separador_miles(precio)
    monto=separador_miles(monto)

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costos_operativos_actual')
    data=cur.fetchall()
    for j in data:
        costo_op=j[1]
    print('costo op = ',costo_op)

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento')
    data=cur.fetchall()
    print(data)
    cp=[]
    for j in data:
        cp.append(j[8])
    costo_p=cp[producto]
    print(costo_p)

    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE inventario_alimento 
        SET cantidad=%s                           
        WHERE id = %s
    """,(kg_final,id_aba))
    mysql.connection.commit()
    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO despacho_aba_interno (factura,producto,destino,propietario,cantidad,precio,monto,fecha,fecha_indice,fecha_ordenada,comentario,costo_operativo,costo_produccion) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (factura,alimento,destino_aba,propietario,cantidad,precio,monto,fecha,fecha_indice,fecha_ordenada,comentario,costo_op,costo_p))
    mysql.connection.commit()
##
##
    cur = mysql.connection.cursor() 
    
    cur.execute("CREATE TABLE IF NOT EXISTS " + fact + """ (
      id INT(11) NOT NULL AUTO_INCREMENT,PRIMARY KEY (id),
      propietario TEXT NOT NULL,
      factura TEXT NOT NULL,
      destino TEXT NOT NULL,
      cantidad TEXT NOT NULL,
      precio TEXT NOT NULL,
      producto TEXT NOT NULL,
      fecha TEXT NOT NULL,
      fecha_indice TEXT NOT NULL,
      dolares TEXT NOT NULL,
      bolivares TEXT NOT NULL,
      banco TEXT NOT NULL,
      referencia TEXT NOT NULL,
      tasa TEXT NOT NULL,
      monto TEXT NOT NULL,
      abono TEXT NOT NULL,
      debe TEXT NOT NULL,
      comentario TEXT NOT NULL,
      fecha_ordenada TEXT NOT NULL)""")
    mysql.connection.commit()
    abono='0,00'
    debe=monto
    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO '+fact+ ' (factura,producto,destino,propietario,cantidad,precio,monto,fecha,fecha_indice,fecha_ordenada,comentario,abono,debe) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (factura,alimento,destino_aba,propietario,cantidad,precio,monto,fecha,fecha_indice,fecha_ordenada,comentario,abono,debe))
    mysql.connection.commit()

    return 'construccion'
    #return redirect(url_for('planta_aba'))

@app.route('/salida_alimento/interno')
def salida_alimento_interno():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM aba_destinos_internos ORDER BY nombre')
    data=cur.fetchall()
    print(data)
    granja=['[SELECCIONE]']
    propietario=['[SELECCIONE]']
    for j in data:
        a=j[1] 
        a+=' ('
        a+=j[2]
        a+=')'        
        granja.append(a)
        propietario.append(j[2])
    print('')
    print('granjas')
    print(granja)
    print('')
    print('propietario')
    print(propietario)


    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento')
    data=cur.fetchall()
    tipo_alimento=['[SELECCIONE]']
    for j in data:
        tipo_alimento.append(j[1])
    print('')
    print('tipos de alimentos')
    print(tipo_alimento)
    return render_template('despacho_aba_interno.html',
                           granja=granja,
                           producto=tipo_alimento,
                           precio='1'
                           
                           )

# fin alimento interno                           

@app.route('/salida_alimento')
def salida_alimento():
    return render_template('salida_alimento.html')


@app.route('/inventario_alimento')
def inventario_alimento():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento ORDER BY producto')
    data=cur.fetchall()
    inv_aba=[]
    for j in data:
        inv_aba.append(j)
    print(inv_aba)


    return render_template('inventario_alimento.html',
                           inv_aba=inv_aba
                           )



############



# calcular costos oprativos < >

@app.route('/pre_confirmacion_particion_gastos_operativos/<id>/<monto>/<new_monto>/<semanas>',methods=['GET','POST'])
def pre_confirmacion_particion_gastos_operativos(id,monto,new_monto,semanas):

    if request.method=='POST':
        data=request.form
        print('')
        print('data')
        print(data)
        print('len data = ',len(data))
        print('')
        print('new_monto')
        
        monto=float(monto)
        semanas=int(semanas)
        nuevo_m=monto/semanas
        nuevo_m=separador_miles(nuevo_m)
        print(nuevo_m)

        rango=len(data)
        rango=int(rango)

        x=np.asarray(data)
        print('x = ', x)
        array_fecha=[]
        for j in range(rango):
            b=j
            b=str(b)
            a='fecha'+b
            array_fecha.append(request.form[a])
        print(array_fecha)

        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM gastos_particion WHERE id = {id}')
        data=cur.fetchall()
        gp=[]
        for j in data:
            gp.append(j)
        print('')
        print('gastos particion segun id')
        print(gp)

        for j in gp:
            factura=j[1]
            descripcion=j[2]
            nombre=j[8]
            propietario=j[9]
        array_fecha_i=[]
        array_fecha_o=[]
        for j in array_fecha:
            print(j)
            fi,fo=ordenar_fecha(j)
            array_fecha_i.append(fi)
            array_fecha_o.append(fo)
        print('fecha indice = ', array_fecha_i)
        print('fecha ordenada = ', array_fecha_o)

        new_bd=np.zeros((len(array_fecha),9),dtype='<U50' )
        print(new_bd)
        i=0
        x=0
        for j in new_bd:
            x=0
            for k in j:
                if x==0:
                    new_bd[i,x]=factura
                if x==1:
                    new_bd[i,x]=descripcion
                if x==2:
                    new_bd[i,x]=i+1
                if x==3:
                    
                    
                    new_bd[i,x]=nuevo_m
                if x==4:
                    new_bd[i,x]=array_fecha[i]
                if x==5:
                    new_bd[i,x]=array_fecha_i[i]
                if x==6:
                    new_bd[i,x]=array_fecha_o[i]
                if x==7:
                    new_bd[i,x]=nombre
                if x==8:
                    new_bd[i,x]=propietario
                x=x+1
            i=i+1
        print(new_bd)

        for j in range(len(array_fecha)):

            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO gastos_particion (factura,descripcion,cuota,monto,fecha,fecha_indice,fecha_ordenada,nombre,propietario) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (new_bd[j,0],new_bd[j,1],new_bd[j,2],new_bd[j,3],new_bd[j,4],new_bd[j,5],new_bd[j,6],new_bd[j,7],new_bd[j,8]))
            mysql.connection.commit()
        
        cur=mysql.connection.cursor()
        cur.execute(f'DELETE FROM gastos_particion WHERE id = {id}')
        mysql.connection.commit()
        


                    



            
        

    return 'contruccion'



@app.route('/aceptar_pre_particion_gastos_operativos/<id>',methods=['GET','POST'])
def aceptar_pre_particion_gastos_operativos(id):
    if request.method=='POST':
        semanas=request.form['semanas']
        if not semanas:
            return redirect(url_for('pre_particion_gastos_operativos',id=id))
        semanas=int(semanas)
        
        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM gastos_particion WHERE id = {id}')
        data=cur.fetchall()
        print(data)
        
        
        for j in data:
            monto=j[4]
        monto=devolver_separador_miles(monto)
        monto=float(monto)
        new_monto=monto/semanas
        print('monto')
        print(monto)
        print('new monto')
        print(new_monto)

    #return 'construccion'
    return render_template('fecha_particion.html',
                           id=id,
                           monto=monto,
                           new_monto=new_monto,
                           semanas=semanas,

                           )

@app.route('/pre_particion_gastos_operativos/<id>')
def pre_particion_gastos_operativos(id):
    
    return render_template('pre_particion.html',id=id)


@app.route('/aceptar_costos_operativos/<costo>/<fecha1>/<fecha2>/<peso>/<gasto_total>',methods=['GET','POST'])
def aceptar_costos_operativos(costo,fecha1,fecha2,peso,gasto_total):
    print('print costos desde el get = ',costo ,' ',fecha1, ' ',fecha2, ' ',peso,' ',gasto_total)

    fecha=fecha1
    fecha_a=fecha[:4]
    print(fecha_a)
    fecha_m=fecha[4:6]
    print('fecha m = ',fecha_m)
    fecha_d=fecha[6:8]
    print('fecha d = ',fecha_d)
    fecha_t=fecha_a
    fecha_t+='-'
    fecha_t+=fecha_m
    fecha_t+='-'
    fecha_t+=fecha_d
    fecha_normal1=fecha_t
    print(fecha_normal1)

    fecha=fecha1
    fecha_a=fecha[:4]
    print(fecha_a)
    fecha_m=fecha[4:6]
    print('fecha m = ',fecha_m)
    fecha_d=fecha[6:8]
    print('fecha d = ',fecha_d)
    fecha_t=fecha_d
    fecha_t+='-'
    fecha_t+=fecha_m
    fecha_t+='-'
    fecha_t+=fecha_a
    fecha_ordenada1=fecha_t
    print(fecha_ordenada1)




    fecha=fecha2
    fecha_a=fecha[:4]
    print(fecha_a)
    fecha_m=fecha[4:6]
    print('fecha m = ',fecha_m)
    fecha_d=fecha[6:8]
    print('fecha d = ',fecha_d)
    fecha_t=fecha_a
    fecha_t+='-'
    fecha_t+=fecha_m
    fecha_t+='-'
    fecha_t+=fecha_d
    fecha_normal2=fecha_t
    print(fecha_normal2)

    fecha=fecha2
    fecha_a=fecha[:4]
    print(fecha_a)
    fecha_m=fecha[4:6]
    print('fecha m = ',fecha_m)
    fecha_d=fecha[6:8]
    print('fecha d = ',fecha_d)
    fecha_t=fecha_d
    fecha_t+='-'
    fecha_t+=fecha_m
    fecha_t+='-'
    fecha_t+=fecha_a
    fecha_ordenada2=fecha_t
    print(fecha_ordenada2)

    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO costos_operativos (costo,fecha1,fecha1_indice,fecha1_ordenada,fecha2,fecha2_indice,fecha2_ordenada,peso,gastos) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (costo,fecha_normal1,fecha1,fecha_ordenada1,fecha_normal2,fecha2,fecha_ordenada2,peso,gasto_total))
    mysql.connection.commit()
    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costos_operativos_actual')
    data=cur.fetchall()
    for j in data:
        id_costos_act=j[0]

    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE costos_operativos_actual 
        SET costo=%s,
            fecha1=%s,
            fecha2=%s               
        WHERE id = %s
    """,(costo,fecha_normal1,fecha_normal2,id_costos_act))
    mysql.connection.commit() 
    return 'construccion'


@app.route('/calcular_costos_opterativos',methods=['GET','POST'])
def calcular_costos_operativos():
    if request.method=='POST':
        print('metodo post')
        fecha1=request.form['fecha1']
        fecha2=request.form['fecha2']
        peso=request.form['kg']
        fecha1,x=ordenar_fecha(fecha1)
        fecha2,y=ordenar_fecha(fecha2)
        #SELECT * FROM orden_produccion WHERE fecha_indice BETWEEN fecha1 AND fecha2
        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM gastos_particion WHERE fecha_indice BETWEEN {fecha1} AND {fecha2}')
        data=cur.fetchall()
        print(data)
        gastos=[]
        suma_gastos=[]
        for j in data:
            gastos.append(j)
            a=j[4]
            a=devolver_separador_miles(a)
            a=float(a)
            suma_gastos.append(a)
        print(suma_gastos)
        gastos_total=np.sum(suma_gastos,axis=0)
        peso=float(peso)
        costo=gastos_total/peso
        print(costo)
        costo="{:,.3f}".format(costo).replace(",","x").replace(".",",").replace("x",".")
        #costo=separador_miles(costo)
        peso=separador_miles(peso)
        gastos_total=separador_miles(gastos_total)
        print('suma total gastos = ',gastos_total)

        

        return render_template('calculo_gastos_operativos.html',
                               gastos=data,
                               gastos_total=gastos_total,
                               costo=costo,
                               peso=peso,
                               fecha1=fecha1,
                               fecha2=fecha2
                            
                               )


    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM gastos')
    data=cur.fetchall()
    print(data)
    gastos=[]
    suma_gastos=[]
    for j in data:
        gastos.append(j)
        a=j[3]
        a=devolver_separador_miles(a)
        a=float(a)
        suma_gastos.append(a)
    print(suma_gastos)
    gastos_total=np.sum(suma_gastos,axis=0)
    gastos_total=separador_miles(gastos_total)
    print('suma total gastos = ',gastos_total)

    return render_template('mostrar_gastos_operativos.html',gastos=gastos,gastos_total=gastos_total)




#   gastos
@app.route('/mostrar_gastos')
def mostrar_gastos():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM gastos')
    data=cur.fetchall()
    print(data)
    gastos=[]
    suma_gastos=[]
    for j in data:
        gastos.append(j)
        a=j[3]
        a=devolver_separador_miles(a)
        a=float(a)
        suma_gastos.append(a)

    gastos_mh=[]
    gastos_proaba=[]
    for j in data:
        if j[12] =='mh2018':            
            a=j[3]
            a=devolver_separador_miles(a)
            a=float(a)
            gastos_mh.append(a)
        
        if j[12] =='proaba':            
            a=j[3]
            a=devolver_separador_miles(a)
            a=float(a)
            gastos_proaba.append(a)
    print('gastos mh ')
    print(gastos_mh)
    print('')
    print('gastos proaba')
    print(gastos_proaba)
    print(suma_gastos)
    gastos_total=np.sum(suma_gastos,axis=0)
    gastos_total=separador_miles(gastos_total)
    print('suma total gastos = ',gastos_total)
    suma_gastos_mh=np.sum(gastos_mh,axis=0)
    suma_gastos_proaba=np.sum(gastos_proaba,axis=0)

    return render_template('mostrar_gastos.html',
                           gastos=gastos,
                           gastos_total=gastos_total,
                           suma_gastos_mh=suma_gastos_mh,
                           suma_gastos_proaba=suma_gastos_proaba
                           )

# gastos varios bolivares
@app.route('/confirmacion_gastos/bolivares',methods=['GET','POST'])
def confirmacion_gastos_bolivares():
    if request.method=='POST':
        nombre=request.form['name']
        descripcion=request.form['descripcion']
        fecha=request.form['fecha']
        abono=request.form['abono']
        tasa=request.form['tasa']
        banco=request.form['banco']
        referencia=request.form['referencia']
        factura=request.form['factura']

        if (not nombre) or (not descripcion) or (not fecha) or (not abono) or (not tasa) or (not banco) or (not referencia):
            print('debe llenar todos los campos')
            flash('debe llenar todos los campos obligatorios (*)','campos_add_gastos_bolivares')
            return redirect(url_for('gastos_varios_bolivares'))

        if (not factura):
            factura = 'S/N'
        print('')
        print('datos del post de gastos bolivares')
        print('nombre = ', nombre)
        print('fecha = ', fecha)
        print('abono = ',abono)
        print('tasa = ', tasa)
        print('banco = ',banco)
        print('referencia = ', referencia)
        print('descripcion = ',descripcion)
        print('factura = ',factura)
        
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM bancos ORDER BY banco')
        data=cur.fetchall()
        bancos=[]
        array_socio=[]
        for j in data:
            bancos.append(j[1])
            array_socio.append(j[3])
        banco=int(banco)
        socio=array_socio[banco]
        socio=socio.lower()
        banco=bancos[banco]
        banco=banco.lower()

        
        

        saldo_banco='saldo_'+banco
       

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM ' +saldo_banco+' ORDER BY banco')
        data=cur.fetchall()
        print(data)
        for j in data:
            id_banco=j[0]
            egreso=j[2]
            saldo=j[3]
        print('egreso = ',egreso, '   saldo = ',saldo)
        egreso=devolver_separador_miles(egreso)
        saldo=devolver_separador_miles(saldo)
        egreso=float(egreso)
        saldo=float(saldo)
        abono=float(abono)
        egreso=egreso+abono
        saldo=saldo-abono
        #if saldo < 0:
        #    print('no dispone de esa cantidad')
        #    flash('El monto supera la cantidad en el Banco','monto_gastos_mayor_bolivares')
        #    return redirect(url_for('gastos_varios_bolivares'))
        tasa=float(tasa)
        dolares = abono/tasa
        egreso=separador_miles(egreso)
        saldo=separador_miles(saldo)
        fecha_indice,fecha_ordenada=ordenar_fecha(fecha)
        print('fecha_indice = ',fecha_indice)
        print('fecha_ordenada = ',fecha_ordenada )

        print('egreso = ',egreso, '   saldo = ',saldo)

        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE """+saldo_banco+""" 
            SET egreso=%s,
                saldo=%s               
            WHERE id = %s
        """,(egreso,saldo,id_banco))
        mysql.connection.commit() 

        banco=banco.upper()
        dolares=separador_miles(dolares)
        tasa=separador_miles(tasa)
        abono=separador_miles(abono)

        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO gastos (descripcion,fecha,fecha_indice,fecha_ordenada,factura,monto,bolivares,tasa,banco,referencia) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (descripcion,fecha,fecha_indice,fecha_ordenada,factura,dolares,abono,tasa,banco,referencia))
        mysql.connection.commit()


        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO gastos_particion (descripcion,fecha,fecha_indice,fecha_ordenada,factura,monto,nombre,propietario) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
            (descripcion,fecha,fecha_indice,fecha_ordenada,factura,dolares,nombre,socio))
        mysql.connection.commit()

        banco=banco.lower()
        ingreso='0,00'
        egreso=abono
        
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO ' +banco+ ' (descripcion,fecha,fecha_indice,fecha_ordenada,referencia,ingreso,egreso,saldo) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
            (descripcion,fecha,fecha_indice,fecha_ordenada,referencia,ingreso,egreso,saldo))
        mysql.connection.commit()



    return ' construccion'


@app.route('/gastos/varios/bolivares')    
def gastos_varios_bolivares():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM bancos ORDER BY banco')
    data=cur.fetchall()
    banco=[]
    for j in data:
        banco.append(j[1])
    


    return render_template('add_gastos_bolivares.html',bancos=banco)
#################

# gastos varios dolares

@app.route('/confirmacion_gastos',methods=['GET','POST'])
def confirmacion_gastos():
    if request.method=='POST':
        fecha=request.form['fecha']
        nombre=request.form['nombre']
        descripcion=request.form['descripcion']
        monto=request.form['monto']
        propietario=request.form['propietario']
    print('fecha = ',fecha)
    print('descripcion = ', descripcion)
    print('monto = ',monto)
    fecha_indice,fecha_ordenada=ordenar_fecha(fecha)
    print(fecha_indice)
    print(fecha_ordenada)
    print(propietario)

    if (not fecha) or (not nombre) or (not descripcion) or (not monto):
        return redirect(url_for('gastos_varios_dolares'))

    if propietario=='0':
        return redirect(url_for('gastos_varios_dolares'))
    propietario=int(propietario)
    propietario=propietario-1

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall()
    array_socio=[]
    for j in data:
        array_socio.append(j[1])
    socio=array_socio[propietario]
    print('socio = ',socio)
    

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM caja')
    data=cur.fetchall()
    caja=[]
    for j in data:
        caja.append(j)

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM saldo_caja')
    data=cur.fetchall()
    saldo_caja=[]
    for j in data:
        saldo_caja.append(j)
        saldo=j[3]
        egreso=j[2]
        id_caja=j[0]
    
    
    monto=float(monto)
    saldo=devolver_separador_miles(saldo)
    saldo=float(saldo)
    saldo=saldo-monto
    

    egreso=devolver_separador_miles(egreso)
    egreso=float(egreso)
    egreso_caja= egreso+monto
    print('egreso = ',egreso)
    print('monto = ',monto)
    egreso=monto
    
    print('')
    print('caja')
    print(caja)
    print('')
    print('saldo caja')
    print(saldo_caja)
    print('')
    print('saldo')
    print(saldo)

    
    ingreso='0,0'
    egreso=separador_miles(egreso)
    monto=separador_miles(monto)
    saldo=separador_miles(saldo)
    egreso_caja=separador_miles(egreso_caja)
    print('egreso_caja = ', egreso_caja)
    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE saldo_caja
        SET egreso=%s,
            saldo=%s               
        WHERE id = %s
    """,(egreso_caja,saldo,id_caja))
    mysql.connection.commit() 

    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO caja (descripcion,fecha,fecha_indice,fecha_ordenada,saldo,ingreso,egreso,propietario) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
        (descripcion,fecha,fecha_indice,fecha_ordenada,saldo,ingreso,egreso,socio))
    mysql.connection.commit()

    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO gastos (descripcion,monto,fecha,fecha_indice,fecha_ordenada,nombre,propietario) VALUES(%s,%s,%s,%s,%s,%s,%s)',
        (descripcion,monto,fecha,fecha_indice,fecha_ordenada,nombre,socio))
    mysql.connection.commit()

    
    cur=mysql.connection.cursor()
    cur.execute('INSERT INTO gastos_particion (descripcion,fecha,fecha_indice,fecha_ordenada,monto,nombre,propietario) VALUES(%s,%s,%s,%s,%s,%s,%s)',
        (descripcion,fecha,fecha_indice,fecha_ordenada,monto,nombre,socio))
    mysql.connection.commit()

    return redirect(url_for('mostrar_gastos'))


@app.route('/gastos/varios/dolares')    
def gastos_varios_dolares():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall()
    propietario=['[ SELECCIONE ]']
    for j in data:
        propietario.append(j[1])

    return render_template('add_gastos.html',
                           propietario=propietario
                           )

####################################

# gastos varios
@app.route('/forma_pago_gastos')    
def forma_pago_gastos():
    return render_template('forma_pago_gastos.html')

@app.route('/add_gastos')    
def add_gastos():
    return render_template('forma_pago_gastos.html')

##################################################


### obtiene el valor de toda la materiaprima
@app.route('/valor_materiaprima',methods=['GET','POST'])
def valor_materiaprima():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto')
    data=cur.fetchall()
    inv_aba=[]
    for j in data:
        inv_aba.append(j)
    print(inv_aba)

    i=0
    costo=[]
    for j in inv_aba:
        a=j[2]
        a=float(a)
        b=j[3]
        b=float(b)
        c=a*b
        costo.append(c)

    print('')  
    print('costo')
    print(costo)
    print('')
    suma_costo=np.sum(costo,axis=0)
    print('suma costo')
    print(suma_costo)
    valor_mp=separador_miles(suma_costo)

    return render_template('valor_materiaprima.html',
                           inv_aba=inv_aba,
                           valor_mp=valor_mp)



@app.route('/cuentas_por_pagar',methods=['GET','POST'])
def cuentas_por_pagar():

    return 'construccion'





@app.route('/facturas_por_pagar',methods=['GET','POST'])
def facturas_por_pagar():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM compras_materiaprima')
    data=cur.fetchall()
    vmp=[]
    monto_fpc=[]
    abono_fpc=[]
    facturado_fpc=[]
    print(data)
    for j in data:
        a=j[9]
        a=devolver_separador_miles(a)
        a=float(a)        
        monto_fpc.append(a)
        b=j[10]
        b=devolver_separador_miles(b)
        b=float(b)        
        abono_fpc.append(b)
        c=j[8]
        c=devolver_separador_miles(c)
        c=float(c)        
        facturado_fpc.append(c)

        if b == 0:
            None
        else:   
            vmp.append(j)
    print(vmp)

    print('monto facturas por cobrar')
    print(monto_fpc)
    monto_fpc=np.sum(monto_fpc,axis=0)
    abono_fpc=np.sum(abono_fpc,axis=0)
    facturado_fpc=np.sum(facturado_fpc,axis=0)

    porc_monto=(monto_fpc*100)/facturado_fpc
    porc_abono=(abono_fpc*100)/facturado_fpc
    print('monto facturas por cobrar despues de la suma')
    print(monto_fpc)
    monto_fpc=separador_miles(monto_fpc)
    abono_fpc=separador_miles(abono_fpc)
    facturado_fpc=separador_miles(facturado_fpc)
    print('monoto fpc')
    print(monto_fpc)
    print('abono fpc')
    print(abono_fpc)
    print('facturado fpc')
    print(facturado_fpc)

    p='10'



    return render_template("facturas_por_pagar.html",
                        vmp=vmp,
                        monto_fpc=monto_fpc,
                        abono_fpc=abono_fpc,
                        facturado_fpc=facturado_fpc,
                        porc_monto=porc_monto,
                        porc_abono=porc_abono,
                        p=p
                        )


@app.route('/facturas_por_cobrar',methods=['GET','POST'])
def facturas_por_cobrar():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM ventas_materiaprima')
    data=cur.fetchall()
    vmp=[]
    monto_fpc=[]
    abono_fpc=[]
    facturado_fpc=[]
    print(data)
    for j in data:
        a=j[9]
        a=devolver_separador_miles(a)
        a=float(a)        
        monto_fpc.append(a)
        b=j[10]
        b=devolver_separador_miles(b)
        b=float(b)        
        abono_fpc.append(b)
        c=j[8]
        c=devolver_separador_miles(c)
        c=float(c)        
        facturado_fpc.append(c)

        if b == 0:
            None
        else:   
            vmp.append(j)
    print(vmp)

    print('monto facturas por cobrar')
    print(monto_fpc)
    monto_fpc=np.sum(monto_fpc,axis=0)
    abono_fpc=np.sum(abono_fpc,axis=0)
    facturado_fpc=np.sum(facturado_fpc,axis=0)

    porc_monto=(monto_fpc*100)/facturado_fpc
    porc_abono=(abono_fpc*100)/facturado_fpc
    print('monto facturas por cobrar despues de la suma')
    print(monto_fpc)
    monto_fpc=separador_miles(monto_fpc)
    abono_fpc=separador_miles(abono_fpc)
    facturado_fpc=separador_miles(facturado_fpc)
    print('monoto fpc')
    print(monto_fpc)
    print('abono fpc')
    print(abono_fpc)
    print('facturado fpc')
    print(facturado_fpc)

    p='10'
    return render_template("facturas_por_cobrar.html",
                           vmp=vmp,
                           monto_fpc=monto_fpc,
                           abono_fpc=abono_fpc,
                           facturado_fpc=facturado_fpc,
                           porc_monto=porc_monto,
                           porc_abono=porc_abono,
                           p=p
                           )

@app.route('/caja/estado/detalle',methods=['GET','POST'])
def caja_estado_detalle():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM caja')
    data=cur.fetchall()
    print('data')
    print(data)
    caja=[]
    for j in data:        
        caja.append(j)
    
    

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM saldo_caja')
    data=cur.fetchall()
    print(data)
    
    for j in data:
        ingresos=j[1]
        egresos=j[2]
        saldo=j[3]
        
    
    ingresos=devolver_separador_miles(ingresos)
    egresos=devolver_separador_miles(egresos)
    saldo=devolver_separador_miles(saldo)
    ingresos=float(ingresos)
    egresos=float(egresos)
    saldo=float(saldo)
    ingresos=separador_miles(ingresos)
    egresos=separador_miles(egresos)
    saldo=separador_miles(saldo)


    return render_template('caja_dolares_detalle.html',
                           caja=caja,
                           ingresos=ingresos,
                           egresos=egresos,
                           saldo=saldo
                           )

@app.route('/caja/estado',methods=['GET','POST'])
def caja_estado():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM saldo_caja')
    data=cur.fetchall()
    print(data)
    caja=[]
    for j in data:
        ingresos=j[1]
        egresos=j[2]
        saldo=j[3]
        caja.append(j)
    
    ingresos=devolver_separador_miles(ingresos)
    egresos=devolver_separador_miles(egresos)
    saldo=devolver_separador_miles(saldo)
    ingresos=float(ingresos)
    egresos=float(egresos)
    saldo=float(saldo)
    ingresos=separador_miles(ingresos)
    egresos=separador_miles(egresos)
    saldo=separador_miles(saldo)

    

    return render_template('caja_dolares.html',
                           caja=caja,
                           ingresos=ingresos,
                           egresos=egresos,
                           saldo=saldo
                           )


##### bancos

@app.route('/retiro_banco',methods=['GET','POST'])
def retiro_banco():


    return 'construccion'



@app.route('/bancos/detalle/<banco>',methods=['GET','POST'])
def bancos_detalle(banco):
    print('llego el nombre del banco')
    print(banco)
    nombre_banco=banco
    banco=banco.lower()
    print(banco)

    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM '+banco)
    data=cur.fetchall()
    detalle_banco=[]
    for j in data:
        detalle_banco.append(j)
    print(detalle_banco)

    return render_template('bancos_detalle.html',bancos=detalle_banco,nombre_banco=nombre_banco)

@app.route('/estado_cuentas_bancos',methods=['GET','POST'])
def estado_cuentas_bancos():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM bancos ORDER BY banco')
    data=cur.fetchall()
    bancos=[]
    for j in data:
        bank=j[1].lower()  
        nombre_banco='saldo_'+bank
        bancos.append(nombre_banco)
    print(bancos)
    ingresos=0.0
    egresos=0.0
    saldo=0.0
    estado_bancos=[]
    for j in bancos:
        print('j = ',j)
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM '+j)
        data=cur.fetchall()
        
        for k in data:
            ingresos_t=k[1]
            ingresos_t=devolver_separador_miles(ingresos_t)
            ingresos_t=float(ingresos_t)
            ingresos=ingresos+ingresos_t

            egresos_t=k[2]
            egresos_t=devolver_separador_miles(egresos_t)
            egresos_t=float(egresos_t)
            egresos=egresos+egresos_t

            saldo_t=k[3]
            saldo_t=devolver_separador_miles(saldo_t)
            saldo_t=float(saldo_t)
            saldo=saldo+saldo_t

            estado_bancos.append(k)

        
        print(' suma de ingresos')
        print(ingresos)
        print(' suma de egresos')
        print(egresos)

        print(' suma de saldo')
        print(saldo)
    ingresos=float(ingresos)
    egresos=float(egresos)
    saldo=float(saldo)
    ingresos=separador_miles(ingresos)
    egresos=separador_miles(egresos)
    saldo=separador_miles(saldo)
    print('estado bancos = ', estado_bancos)


    return render_template('bancos.html',
                           bancos=estado_bancos,
                           ingresos=ingresos,
                           egresos=egresos,
                           saldo=saldo
                           )




#################################
# recibe el pago en dolares
@app.route('/confirmacion_factura_compras_materiaprima/bolivares/<factura>',methods=['GET','POST'])
def confirmacion_facturas_compras_materiaprima_bolivares(factura):

    if request.method=='POST':
        abono=request.form['abono']
        fecha=request.form['fecha']
        banco=request.form['banco']
        tasa=request.form['tasa']
        referencia=request.form['referencia']

        if (not abono) or (not fecha) or (not banco) or (not tasa) or (not referencia):
           print('debe llenar todos los campos')
           flash('Debe llenar todos los campos','pago_bolivares')
           return redirect(url_for('pagar_facturas_compras_materiaprima_bolivares',factura=factura))
           #return render_template('pagar_fvmp_dolares.html',factura=factura)aqui
        if banco=='0':
           print('debe llenar todos los campos')
           flash('Debe llenar todos los campos','pago_bolivares')
           return redirect(url_for('pagar_facturas_compras_materiaprima_bolivares',factura=factura))
        banco=int(banco)
        banco=banco-1

        print('banco = ', banco)
        print(abono)
        print(fecha)
        print(factura)

        # buscar el banco seleccionado

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM bancos ORDER BY banco')
        data=cur.fetchall()
        
        bancos=[]
        for j in data:
            bancos.append(j)
        i=0
        #banco=int(banco)
        for j in bancos:
            if i==banco:
                banco_seleccionado=j[1]
                socio=j[3]
            i=i+1
        print('socio titular del banco es = ', socio)
        print('banco seleccionado es = ',banco_seleccionado)
        # fin buscar el banco seleccionado

        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM compras_materiaprima WHERE factura = "{factura}"')
        data=cur.fetchall()
        
        vm=[]
        for j in data:
            vm.append(j)
        print('vm')
        print(vm)

        for j in vm:
            abono_f=(j[9])
            monto_f=(j[8])
            saldo_f=(j[10])
            cliente_f=j[3]
            propietario_f=j[4]
            producto_f=j[5]
        abono_f=devolver_separador_miles(abono_f)
        monto_f=devolver_separador_miles(monto_f)
        saldo_f=devolver_separador_miles(saldo_f)
        abono_f=float(abono_f)
        monto_f=float(monto_f)
        saldo_f=float(saldo_f)
        print('')
        print('')
        print('abono de factura')
        print(abono_f)
        print('')
        print('monto de factura')
        print(monto_f)
        print('')
        print('saldo de factura')
        print(saldo_f)
        print('')
        print('')
        print('')

        abono_cliente=float(abono)
        tasa=float(tasa)
        abono_cliente=abono_cliente/tasa

        print('')
        print('la conversion en dolares es = ',abono_cliente)

        saldo_final=saldo_f-abono_cliente
        if saldo_final < 0.0:
            print('este monto es mayor a la deuda')
            flash('el pago supera el monto de la deuda','monto_mayor_bolivares')
            return redirect(url_for('pagar_facturas_compras_materiaprima_bolivares',factura=factura))
        print('')
        print('saldo final del abono')
        print(saldo_final)
        print('')

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_a
        fecha_t+=fecha_m
        fecha_t+=fecha_d
        fecha_indice=fecha_t

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_d
        fecha_t+='-'
        fecha_t+=fecha_m
        fecha_t+='-'
        fecha_t+=fecha_a
        fecha_ordenada=fecha_t
        abono=float(abono)
        abono=separador_miles(abono)
        abono_cliente=separador_miles(abono_cliente)
        tasa=separador_miles(tasa)
        saldo_final=separador_miles(saldo_final)
        factura2='x'+factura
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO '+factura2+' (factura,producto,abono,fecha,bolivares,tasa,banco,referencia,debe,fecha_indice,fecha_ordenada) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (factura,producto_f,abono_cliente,fecha,abono,tasa,banco_seleccionado,referencia,saldo_final,fecha_indice,fecha_ordenada))
        mysql.connection.commit()
        
        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM compras_materiaprima WHERE factura= {factura}')
        data=cur.fetchall()
        
        for j in data:
            abono_anterior=(j[9])
        
        abono_anterior=devolver_separador_miles(abono_anterior)
        abono_cliente=devolver_separador_miles(abono_cliente)
        abono_cliente=float(abono_cliente)
        abono_anterior=float(abono_anterior)

        abono_vmp=abono_cliente+abono_anterior

        abono_vmp=separador_miles(abono_vmp)


        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE compras_materiaprima
            SET abono=%s,
                debe=%s               
            WHERE factura = %s
        """,(abono_vmp,saldo_final,factura))
        mysql.connection.commit() 

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM '+banco_seleccionado)
        data=cur.fetchall()
        print('banco')
        print(data)
        if (not data):
            print('dato vacio')
            descripcion='descuento factura Nª '
            descripcion+=factura
            descripcion+=' de '
            descripcion+=producto_f
            descripcion+=' proveedor '
            descripcion+=cliente_f
            ingreso='0,0'
            
            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO '+banco_seleccionado+' (descripcion,referencia,ingreso,saldo,fecha,fecha_indice,fecha_ordenada,egreso) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
            (descripcion,referencia,ingreso,abono,fecha,fecha_indice,fecha_ordenada,abono))
            mysql.connection.commit()

            estado_banco='saldo_'+banco_seleccionado

            cur.execute('INSERT INTO '+estado_banco+' (ingreso,egreso,saldo) VALUES(%s,%s,%s)',
            (ingreso,abono,ingreso))
            mysql.connection.commit()

        else:
            estado_banco='saldo_'+banco_seleccionado
            cur=mysql.connection.cursor()
            cur.execute('SELECT * FROM '+estado_banco)
            data=cur.fetchall()
            print('dato lleno')
            datos_banco=[]
            for j in data:
                datos_banco.append(j)

            print('')
            print('')
            print('')
            print('datos banco')
            print(datos_banco)
            print('')
            print('')
            print('')
            print('')

            
            for j in datos_banco:
                a=devolver_separador_miles(j[3])
                a=float(a)
                saldo_banco=a
                b=devolver_separador_miles(j[2])
                b=float(b)
                egreso_banco=b
                id_banco=j[0]
            print('saldo banco')
            print(saldo_banco)
            print('')
            print('ingreso banco')
            print(egreso_banco)
            print('id banco ',id_banco)
            
            abono=devolver_separador_miles(abono)
            abono=float(abono)
            saldo_banco=saldo_banco-abono
            egreso_banco=egreso_banco+abono


            

            print('saldo banco final')
            print(saldo_banco)
            abono=separador_miles(abono)
            saldo_banco=separador_miles(saldo_banco)
            egreso_banco=separador_miles(egreso_banco)
            descripcion='descuento factura Nª '
            descripcion+=factura
            descripcion+=' de '
            descripcion+=producto_f
            descripcion+=' proveedor '
            descripcion+=cliente_f
            ingreso='0,0'
            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO '+banco_seleccionado+' (descripcion,referencia,ingreso,saldo,fecha,fecha_indice,fecha_ordenada,egreso) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
            (descripcion,referencia,ingreso,saldo_banco,fecha,fecha_indice,fecha_ordenada,egreso_banco))
            mysql.connection.commit()


            cur=mysql.connection.cursor()
            cur.execute("UPDATE " +estado_banco+ " SET egreso=%s,saldo=%s  WHERE id = %s",(egreso_banco,saldo_banco,id_banco))
            mysql.connection.commit() 
        #
        #afvmp=[]
        #for j in data:
        #    afvmp.append(j)
        #print('afvmp')
        #print(afvmp)
#
        #print('')
        #print('cliente')
        #print(cliente)
#
        #print('')
        #print('producto')
        #print(producto)
#
        #if not afvmp:
        #    cur=mysql.connection.cursor()
        #    cur.execute('INSERT INTO abono_factura_venta_materiaprima (factura,producto,abono,fecha,efectivo) VALUES(%s,%s,%s,%s,%s)',
        #    (factura,producto,abono,fecha,abono))
        #    mysql.connection.commit()
        
                

    return ('construccion')










@app.route('/confirmacion_factura_compras_materiaprima/dolares/<factura>',methods=['GET','POST'])
def confirmacion_facturas_compras_materiaprima(factura):

    if request.method=='POST':
        abono=request.form['abono']
        fecha=request.form['fecha']
        socio=request.form['propietario']
        if (not abono) or (not fecha):
            print('debe llenar todos los campos')
            flash('Debe llenar todos los campos','pago_dolares')
            return render_template('pagar_fcmp_dolares.html',factura=factura)
        if socio=='0':
            print('debe llenar todos los campos')
            flash('Debe llenar todos los campos','pago_dolares')
            return render_template('pagar_fcmp_dolares.html',factura=factura)
        socio=int(socio)
        socio=socio-1
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM propietario ORDER BY propietario')
        data=cur.fetchall()
        data_socio=[]
        for j in data:
            data_socio.append(j[1])
        name_socio=data_socio[socio]
        print('')
        print('socio = ', name_socio)
        print('')
        print(abono)
        print(fecha)
        print(factura)

        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM compras_materiaprima WHERE factura = "{factura}"')
        data=cur.fetchall()
        
        vm=[]
        for j in data:
            vm.append(j)
        print('vm')
        print(vm)

        for j in vm:
            abono_f=(j[9])
            monto_f=(j[8])
            saldo_f=(j[10])
            cliente_f=j[3]
            propietario_f=j[4]
            producto_f=j[5]
        abono_f=devolver_separador_miles(abono_f)
        monto_f=devolver_separador_miles(monto_f)
        saldo_f=devolver_separador_miles(saldo_f)
        abono_f=float(abono_f)
        monto_f=float(monto_f)
        saldo_f=float(saldo_f)
        print('')
        print('')
        print('abono de factura')
        print(abono_f)
        print('')
        print('monto de factura')
        print(monto_f)
        print('')
        print('saldo de factura')
        print(saldo_f)
        print('')
        print('')
        print('')

        abono_cliente=float(abono)



        saldo_final=saldo_f-abono_cliente

        if saldo_final < 0.0:
            print('este monto es mayor a la deuda')
            flash('el pago supera el monto de la deuda','monto_mayor_dolares')
            return redirect(url_for('pagar_facturas_compras_materiaprima',factura=factura))
#
        ####### dinero existente en caja
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM saldo_caja')
        data=cur.fetchall()
        caja=[]
        for j in data:
            caja.append(j)
        for j in caja:
            ingreso_caja=j[1]
            egreso_caja=j[2]
            saldo_caja=j[3]
            id_caja=j[0]
        saldo_caja=devolver_separador_miles(saldo_caja)
        saldo_caja=float(saldo_caja)
        ingreso_caja=devolver_separador_miles(ingreso_caja)
        ingreso_caja=float(ingreso_caja)
        egreso_caja=devolver_separador_miles(egreso_caja)
        egreso_caja=float(egreso_caja)



        abono=float(abono)
        saldo_caja=saldo_caja-abono
        egreso_caja=egreso_caja+abono

        ##  ######### confirma monto que existe en el caja
        #if saldo_caja < 0.0:
        #    print('no se dispone de es cantidad en caja')
        #    flash('no se dispone de esa cantidad en caja','monto_mayor_dolares')
        #    return redirect(url_for('pagar_facturas_compras_materiaprima',factura=factura))

        print('')
        print('saldo final del abono')
        print(saldo_final)
        print('')

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_a
        fecha_t+=fecha_m
        fecha_t+=fecha_d
        fecha_indice=fecha_t

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_d
        fecha_t+='-'
        fecha_t+=fecha_m
        fecha_t+='-'
        fecha_t+=fecha_a
        fecha_ordenada=fecha_t
        abono=float(abono)
        abono=separador_miles(abono)
        saldo_final=separador_miles(saldo_final)
        factura2='x'+factura

        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO '+factura2+' (factura,producto,abono,fecha,dolares,debe,fecha_indice,fecha_ordenada) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
        (factura,producto_f,abono,fecha,abono,saldo_final,fecha_indice,fecha_ordenada))
        mysql.connection.commit()






        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM compras_materiaprima WHERE factura= {factura}')
        data=cur.fetchall()
        
        for j in data:
            abono_anterior=(j[9])
        abono_egreso=abono
        abono_anterior=devolver_separador_miles(abono_anterior)
        abono=devolver_separador_miles(abono)
        abono=float(abono)
        abono_anterior=float(abono_anterior)

        abono_vmp=abono+abono_anterior

        abono_vmp=separador_miles(abono_vmp)


        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE compras_materiaprima
            SET abono=%s,
                debe=%s               
            WHERE factura = %s
        """,(abono_vmp,saldo_final,factura))
        mysql.connection.commit()
        egreso_caja=separador_miles(egreso_caja)
        saldo_caja=separador_miles(saldo_caja)
        ingreso_caja='0,0'
        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE saldo_caja
            SET egreso=%s,
                saldo=%s               
            WHERE id = %s
        """,(egreso_caja,saldo_caja,id_caja))
        mysql.connection.commit() 

        descripcion='pago factura '+factura+' de '+producto_f
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO caja (descripcion,ingreso,egreso,saldo,fecha,fecha_indice,fecha_ordenada,propietario) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
        (descripcion,ingreso_caja,abono_egreso,saldo_caja,fecha,fecha_indice,fecha_ordenada,name_socio))
        mysql.connection.commit()       
    
        
                

    return ('construccion')



@app.route('/pagar_factura_compras_materiaprima/bolivares/<factura>',methods=['GET','POST'])
def pagar_facturas_compras_materiaprima_bolivares(factura):
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM bancos ORDER BY banco')
    data=cur.fetchall()
    array_bancos=[]
    for j in data:
        array_bancos.append(j)
    print('data')
    print(data)
    bancos=['[ SELECCIONE ]']
    for j in array_bancos:
        bancos.append(j[1])
    print('')
    print('array_bancos')
    print(array_bancos)
    print('')
    print('bancos')
    print(bancos)

    return render_template('pagar_fcmp_bolivares.html',
                           factura=factura,
                           bancos=bancos)

@app.route('/pagar_factura_compras_materiaprima/dolares/<factura>',methods=['GET','POST'])
def pagar_facturas_compras_materiaprima(factura):

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario ')
    data=cur.fetchall()
    propietario=['[ SELECCIONE ]']
    for j in data:
        propietario.append(j[1])
    return render_template('pagar_fcmp_dolares.html',
                           factura=factura,
                           propietario=propietario
                           )

@app.route('/prepagar_factura_compras_materiaprima/<factura>',methods=['GET','POST'])
def prepagar_facturas_compras_materiaprima(factura):


    return render_template('prepagar_fcmp.html',factura=factura)


@app.route('/abonar_factura_compras_materiaprima/<factura>',methods=['GET','POST'])
def abonar_facturas_compras_materiaprima(factura):

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM compras_materiaprima WHERE factura = "{factura}"')
    data=cur.fetchall()
    factura2='x'+factura
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM '+factura2)
    data=cur.fetchall()  
    print('Tabla seleccionada = ',data)
    print('data de abono')
    print(data)
    fv=[]
    cliente=''
    for j in data:
        
        fv.append(j)
    
    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM compras_materiaprima WHERE factura = "{factura}"')
    data=cur.fetchall()
    afv=[]
    
    for j in data:        
        afv.append(j)
    
    for j in afv:
        cliente=j[3]
        producto=j[5]
        m_total=j[8]

    

    print('no existe abono')
    return render_template('abonar_fcmp.html',
                               fv=fv,
                               cliente=cliente,
                               factura=factura,
                               producto=producto,
                               monto=m_total
                               )



@app.route('/facturas_compras_materiaprima',methods=['GET','POST'])
def facturas_compras_materiaprima():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM compras_materiaprima ORDER BY fecha DESC')
    data=cur.fetchall()
    array_fv=[]
    for j in data:
        array_fv.append(j)
    print('')
    print('')
    print('array_fv')
    print(array_fv)
    print('')

    return render_template('facturas_compras_materiaprima.html',array_fv=array_fv)
##############
##############


##############
@app.route('/facturas_ventas_materiaprima',methods=['GET','POST'])
def facturas_ventas_materiaprima():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM ventas_materiaprima ORDER BY fecha DESC')
    data=cur.fetchall()
    array_fv=[]
    for j in data:
        array_fv.append(j)
    print('')
    print('')
    print('array_fv')
    print(array_fv)
    print('')

    return render_template('facturas_ventas_materiaprima.html',array_fv=array_fv)




##############################
@app.route('/confirmacion_factura_ventas_materiaprima/bolivares/<factura>',methods=['GET','POST'])
def confirmacion_facturas_ventas_materiaprima_bolivares(factura):

    if request.method=='POST':
        abono=request.form['abono']
        fecha=request.form['fecha']
        banco=request.form['banco']
        tasa=request.form['tasa']
        referencia=request.form['referencia']

        if (not abono) or (not fecha) or (not banco) or (not tasa) or (not referencia):
           print('debe llenar todos los campos')
           flash('Debe llenar todos los campos','pago_bolivares')
           return redirect(url_for('pagar_facturas_ventas_materiaprima_bolivares',factura=factura))
           #return render_template('pagar_fvmp_dolares.html',factura=factura)aqui
        
        print('banco = ', banco)
        print(abono)
        print(fecha)
        print(factura)

        # buscar el banco seleccionado

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM bancos ORDER BY banco')
        data=cur.fetchall()
        bancos=[]
        for j in data:
            bancos.append(j)
        i=0
        banco=float(banco)
        for j in bancos:
            if i==banco:
                banco_seleccionado=j[1]
            i=i+1

        print('banco seleccionado es = ',banco_seleccionado)
        # fin buscar el banco seleccionado

        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM ventas_materiaprima WHERE factura = "{factura}"')
        data=cur.fetchall()
        
        vm=[]
        for j in data:
            vm.append(j)
        print('vm')
        print(vm)

        for j in vm:
            abono_f=(j[9])
            monto_f=(j[8])
            saldo_f=(j[10])
            cliente_f=j[3]
            propietario_f=j[4]
            producto_f=j[5]
        abono_f=devolver_separador_miles(abono_f)
        monto_f=devolver_separador_miles(monto_f)
        saldo_f=devolver_separador_miles(saldo_f)
        abono_f=float(abono_f)
        monto_f=float(monto_f)
        saldo_f=float(saldo_f)
        print('')
        print('')
        print('abono de factura')
        print(abono_f)
        print('')
        print('monto de factura')
        print(monto_f)
        print('')
        print('saldo de factura')
        print(saldo_f)
        print('')
        print('')
        print('')

        abono_cliente=float(abono)
        tasa=float(tasa)
        abono_cliente=abono_cliente/tasa

        print('')
        print('la conversion en dolares es = ',abono_cliente)

        saldo_final=saldo_f-abono_cliente
        if saldo_final < 0.0:
            print('este monto es mayor a la deuda')
            flash('el pago supera el monto de la deuda','monto_mayor_bolivares')
            return redirect(url_for('pagar_facturas_ventas_materiaprima_bolivares',factura=factura))
        print('')
        print('saldo final del abono')
        print(saldo_final)
        print('')

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_a
        fecha_t+=fecha_m
        fecha_t+=fecha_d
        fecha_indice=fecha_t

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_d
        fecha_t+='-'
        fecha_t+=fecha_m
        fecha_t+='-'
        fecha_t+=fecha_a
        fecha_ordenada=fecha_t
        abono=float(abono)
        abono=separador_miles(abono)
        abono_cliente=separador_miles(abono_cliente)
        tasa=separador_miles(tasa)
        saldo_final=separador_miles(saldo_final)
        factura2='z'+factura
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO '+factura2+' (factura,producto,abono,fecha,bolivares,tasa,banco,referencia,debe,fecha_indice,fecha_ordenada) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (factura,producto_f,abono_cliente,fecha,abono,tasa,banco_seleccionado,referencia,saldo_final,fecha_indice,fecha_ordenada))
        mysql.connection.commit()
        
        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM ventas_materiaprima WHERE factura= {factura}')
        data=cur.fetchall()
        
        for j in data:
            abono_anterior=(j[9])
        
        abono_anterior=devolver_separador_miles(abono_anterior)
        abono_cliente=devolver_separador_miles(abono_cliente)
        abono_cliente=float(abono_cliente)
        abono_anterior=float(abono_anterior)

        abono_vmp=abono_cliente+abono_anterior

        abono_vmp=separador_miles(abono_vmp)


        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE ventas_materiaprima
            SET abono=%s,
                debe=%s               
            WHERE factura = %s
        """,(abono_vmp,saldo_final,factura))
        mysql.connection.commit() 

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM '+banco_seleccionado)
        data=cur.fetchall()
        print('banco')
        print(data)
        if (not data):
            print('dato vacio')
            descripcion='abono factura Nª '
            descripcion+=factura
            descripcion+=' de '
            descripcion+=producto_f
            descripcion+=' cliente '
            descripcion+=cliente_f
            egreso='0,0'

            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO '+banco_seleccionado+' (descripcion,referencia,ingreso,saldo,fecha,fecha_indice,fecha_ordenada,egreso) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
            (descripcion,referencia,abono,abono,fecha,fecha_indice,fecha_ordenada,egreso))
            mysql.connection.commit()

            estado_banco='saldo_'+banco_seleccionado

            cur.execute('INSERT INTO '+estado_banco+' (ingreso,egreso,saldo) VALUES(%s,%s,%s)',
            (abono,egreso,abono))
            mysql.connection.commit()

        else:
            estado_banco='saldo_'+banco_seleccionado
            cur=mysql.connection.cursor()
            cur.execute('SELECT * FROM '+estado_banco)
            data=cur.fetchall()
            print('dato lleno')
            datos_banco=[]
            for j in data:
                datos_banco.append(j)

            print('')
            print('')
            print('')
            print('datos banco')
            print(datos_banco)
            print('')
            print('')
            print('')
            print('')

            
            for j in datos_banco:
                a=devolver_separador_miles(j[3])
                a=float(a)
                saldo_banco=a
                b=devolver_separador_miles(j[1])
                b=float(b)
                ingreso_banco=b
                id_banco=j[0]
            print('saldo banco')
            print(saldo_banco)
            print('')
            print('ingreso banco')
            print(ingreso_banco)
            print('id banco ',id_banco)
            
            abono=devolver_separador_miles(abono)
            abono=float(abono)
            saldo_banco=saldo_banco+abono
            ingreso_banco=ingreso_banco+abono
            print('saldo banco final')
            print(saldo_banco)
            abono=separador_miles(abono)
            saldo_banco=separador_miles(saldo_banco)
            ingreso_banco=separador_miles(ingreso_banco)
            descripcion='abono factura Nª '
            descripcion+=factura
            descripcion+=' de '
            descripcion+=producto_f
            descripcion+=' cliente '
            descripcion+=cliente_f
            egreso='0,0'
            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO '+banco_seleccionado+' (descripcion,referencia,ingreso,saldo,fecha,fecha_indice,fecha_ordenada,egreso) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
            (descripcion,referencia,abono,saldo_banco,fecha,fecha_indice,fecha_ordenada,egreso))
            mysql.connection.commit()


            cur=mysql.connection.cursor()
            cur.execute("UPDATE " +estado_banco+ " SET ingreso=%s,saldo=%s  WHERE id = %s",(ingreso_banco,saldo_banco,id_banco))
            mysql.connection.commit() 
      
        
                

    return ('construccion')

##############################
@app.route('/confirmacion_factura_ventas_materiaprima/dolares/<factura>',methods=['GET','POST'])
def confirmacion_facturas_ventas_materiaprima(factura):

    if request.method=='POST':
        abono=request.form['abono']
        fecha=request.form['fecha']
        socio=request.form['propietario']
        if (not abono) or (not fecha):
            print('debe llenar todos los campos')
            flash('Debe llenar todos los campos','pago_dolares')
            return render_template('pagar_fvmp_dolares.html',factura=factura)
        if socio=='0':
            print('debe llenar todos los campos')
            flash('Debe llenar todos los campos','pago_dolares')
            return render_template('pagar_fvmp_dolares.html',factura=factura)
        socio=int(socio)
        socio=socio-1
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM propietario ORDER BY propietario')
        data=cur.fetchall()
        array_socio=[]
        for j in data:
            array_socio.append(j[1])
        name_socio=array_socio[socio]
        print('socio = ',name_socio)
        print(abono)
        print(fecha)
        print(factura)

        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM ventas_materiaprima WHERE factura = "{factura}"')
        data=cur.fetchall()
        
        vm=[]
        for j in data:
            vm.append(j)
        print('vm')
        print(vm)

        for j in vm:
            abono_f=(j[9])
            monto_f=(j[8])
            saldo_f=(j[10])
            cliente_f=j[3]
            propietario_f=j[4]
            producto_f=j[5]
        abono_f=devolver_separador_miles(abono_f)
        monto_f=devolver_separador_miles(monto_f)
        saldo_f=devolver_separador_miles(saldo_f)
        abono_f=float(abono_f)
        monto_f=float(monto_f)
        saldo_f=float(saldo_f)
        print('')
        print('')
        print('abono de factura')
        print(abono_f)
        print('')
        print('monto de factura')
        print(monto_f)
        print('')
        print('saldo de factura')
        print(saldo_f)
        print('')
        print('')
        print('')

        

        abono_cliente=float(abono)



        saldo_final=saldo_f-abono_cliente

        if saldo_final < 0.0:
            print('este monto es mayor a la deuda')
            flash('el pago supera el monto de la deuda','monto_mayor_dolares')
            return redirect(url_for('pagar_facturas_ventas_materiaprima',factura=factura))



        ####### dinero existente en caja
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM saldo_caja')
        data=cur.fetchall()
        caja=[]
        for j in data:
            caja.append(j)
        for j in caja:
            ingreso_caja=j[1]
            egreso_caja=j[2]
            saldo_caja=j[3]
            id_caja=j[0]
        saldo_caja=devolver_separador_miles(saldo_caja)
        saldo_caja=float(saldo_caja)
        ingreso_caja=devolver_separador_miles(ingreso_caja)
        ingreso_caja=float(ingreso_caja)
        egreso_caja=devolver_separador_miles(egreso_caja)
        egreso_caja=float(egreso_caja)

        ingreso_caja=ingreso_caja+abono_cliente
        saldo_caja=saldo_caja+abono_cliente
        

        print('')
        print('saldo final del abono')
        print(saldo_final)
        print('')

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_a
        fecha_t+=fecha_m
        fecha_t+=fecha_d
        fecha_indice=fecha_t

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_d
        fecha_t+='-'
        fecha_t+=fecha_m
        fecha_t+='-'
        fecha_t+=fecha_a
        fecha_ordenada=fecha_t
        abono=float(abono)
        abono=separador_miles(abono)
        saldo_final=separador_miles(saldo_final)
        factura2='z'+factura
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO '+factura2+' (factura,producto,abono,fecha,dolares,debe,fecha_indice,fecha_ordenada) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
        (factura,producto_f,abono,fecha,abono,saldo_final,fecha_indice,fecha_ordenada))
        mysql.connection.commit()






        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM ventas_materiaprima WHERE factura= {factura}')
        data=cur.fetchall()
        
        for j in data:
            abono_anterior=(j[9])
        
        abono_anterior=devolver_separador_miles(abono_anterior)
        abono=devolver_separador_miles(abono)
        abono=float(abono)
        abono_anterior=float(abono_anterior)

        abono_vmp=abono+abono_anterior

        abono_vmp=separador_miles(abono_vmp)


        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE ventas_materiaprima
            SET abono=%s,
                debe=%s               
            WHERE factura = %s
        """,(abono_vmp,saldo_final,factura))
        mysql.connection.commit() 
        



        ingreso_caja=separador_miles(ingreso_caja)
        saldo_caja=separador_miles(saldo_caja)
        egreso_caja='0,0'
        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE saldo_caja
            SET ingreso=%s,
                saldo=%s               
            WHERE id = %s
        """,(ingreso_caja,saldo_caja,id_caja))
        mysql.connection.commit() 

        descripcion='abono factura '+factura+' de '+producto_f
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO caja (descripcion,ingreso,egreso,saldo,fecha,fecha_indice,fecha_ordenada,propietario) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
        (descripcion,abono,egreso_caja,saldo_caja,fecha,fecha_indice,fecha_ordenada,name_socio))
        mysql.connection.commit()
        
        
                

    return ('construccion')





@app.route('/pagar_factura_ventas_materiaprima/bolivares/<factura>',methods=['GET','POST'])
def pagar_facturas_ventas_materiaprima_bolivares(factura):
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM bancos ORDER BY banco')
    data=cur.fetchall()
    array_bancos=[]
    for j in data:
        array_bancos.append(j)
    print('data')
    print(data)
    bancos=[]
    for j in array_bancos:
        bancos.append(j[1])
    print('')
    print('array_bancos')
    print(array_bancos)
    print('')
    print('bancos')
    print(bancos)

    return render_template('pagar_fvmp_bolivares.html',
                           factura=factura,
                           bancos=bancos)

@app.route('/pagar_factura_ventas_materiaprima/dolares/<factura>',methods=['GET','POST'])
def pagar_facturas_ventas_materiaprima(factura):

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall()
    propietario=['[ SELECCIONE ]']
    for j in data:
        propietario.append(j[1])
    return render_template('pagar_fvmp_dolares.html',
                           factura=factura,
                           propietario=propietario
                           )

@app.route('/prepagar_factura_ventas_materiaprima/<factura>',methods=['GET','POST'])
def prepagar_facturas_ventas_materiaprima(factura):
    

    return render_template('prepagar_fvmp.html',factura=factura)


@app.route('/abonar_factura_ventas_materiaprima/<factura>',methods=['GET','POST'])
def abonar_facturas_ventas_materiaprima(factura):

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM ventas_materiaprima WHERE factura = "{factura}"')
    data=cur.fetchall()
    factura2='z'+factura
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM '+factura2)
    data=cur.fetchall()  
    print('Tabla seleccionada = ',data)
    print('data de abono')
    print(data)
    fv=[]
    cliente=''
    for j in data:
        
        fv.append(j)
    
    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM ventas_materiaprima WHERE factura = "{factura}"')
    data=cur.fetchall()
    afv=[]
    
    for j in data:        
        afv.append(j)
    
    for j in afv:
        cliente=j[3]
        producto=j[5]
        m_total=j[8]

    

    print('no existe abono')
    return render_template('abonar_fvmp.html',
                               fv=fv,
                               cliente=cliente,
                               factura=factura,
                               producto=producto,
                               monto=m_total
                               )
    


    




@app.route('/add_ventas_materiaprima',methods=['GET','POST'])
def add_ventas_materiaprima():
    
    if request.method=='POST':
        num_factura=request.form['num_fact']
        fecha=request.form['fecha']
        cliente=request.form['cliente']
        propietario=request.form['propietario']
        producto=request.form['producto']
        kilos=request.form['cantidad']
        precio=request.form['precio']
        comentario=request.form['comentario']

        factura2=num_factura
        factura=num_factura
        if ((not num_factura) or (not fecha) or (not cliente) or (not propietario) or (not producto) or (not kilos) or (not precio)):        
            print('debe introducir todos los campos')
            flash('Debe Introducir Todos Los Campos','todosloscampos')
            return redirect(url_for('ventas_materiaprima'))
        if cliente=='0':
            print('debe introducir todos los campos')
            flash('Debe Introducir Todos Los Campos','todosloscampos')
            return redirect(url_for('ventas_materiaprima'))
        if propietario=='0':
            print('debe introducir todos los campos')
            flash('Debe Introducir Todos Los Campos','todosloscampos')
            return redirect(url_for('ventas_materiaprima'))
        if producto=='0':
            print('debe introducir todos los campos')
            flash('Debe Introducir Todos Los Campos','todosloscampos')
            return redirect(url_for('ventas_materiaprima'))
        cliente=int(cliente)
        propietario=int(propietario)
        producto=int(producto)
        cliente=cliente-1
        propietario=propietario-1
        producto=producto-1
        total=float(precio)*float(kilos)

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM propietario ORDER BY propietario')
        data=cur.fetchall()

        buscar_propietario=[]       
        for j in data:
            buscar_propietario.append(j[1])
        propietario=buscar_propietario[int(propietario)]

        cur=mysql.connection.cursor()
        cur.execute('SELECT *FROM lista_materiaprima ORDER BY producto')
        data=cur.fetchall()
        buscar_producto=[]
        for j in data:
            buscar_producto.append(j[1])
        producto=buscar_producto[int(producto)]


        cur=mysql.connection.cursor()
        cur.execute('SELECT *FROM lista_clientes ORDER BY nombre')
        data=cur.fetchall()
        buscar_cliente=[]
        for j in data:
            buscar_cliente.append(j[1])
        cliente=buscar_cliente[int(cliente)]

        
        
        



        


        print(producto)
        # buscar en bd costo_materiaprima la cantidad almacenada en el inventario

        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM costo_materiaprima WHERE producto = "{producto}"')
        data=cur.fetchall()
        for j in  data:
            kilos_bd=j[3]

        kilos_bd=float(kilos_bd)
        kilos=float(kilos)
        print(kilos_bd)
        print(kilos)

        kilo_nuevo=kilos_bd-kilos
                                        #<div class="form-group titulo-inv">   
        if kilo_nuevo < 0.0:
            print('no se dispone de es cantidad de kilos, quedan en inventario ',kilos_bd)
            flash(f'no se dispone de {kilos} kilos de {producto}. Hay en existencia {kilos_bd} Kg','inventariobajo')
            return redirect(url_for('ventas_materiaprima'))   

        else:
            
            cur=mysql.connection.cursor()
            cur.execute("""
                UPDATE costo_materiaprima
                SET kilos=%s                
                WHERE producto = %s
            """,(kilo_nuevo,producto))
            mysql.connection.commit() 

            # arreglar fecha
            

            cur = mysql.connection.cursor()     
            cur.execute("SHOW TABLES") 
            mysql.connection.commit()
            factura_existe=0
            fact='z'+factura2
            print('cur = ',cur)

            for j in cur: 
                             
                print(j[0])
                if(str(j[0]) == str(fact)):
                    flash('Cliente Existe')
                    print('Cliente existe en la base de datos ') 
                    factura_existe=1
                    return "existe"
                    break     
            cur = mysql.connection.cursor() 
            factura2='z'+factura2
            factura2=re.sub(r"\s+", "", factura2)
            cur.execute("CREATE TABLE IF NOT EXISTS " + factura2 + " (id INT(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (id),propietario TEXT NOT NULL,factura TEXT NOT NULL, cliente TEXT NOT NULL,producto TEXT NOT NULL,fecha TEXT NOT NULL,fecha_indice TEXT NOT NULL,dolares TEXT NOT NULL,bolivares TEXT NOT NULL,banco TEXT NOT NULL,referencia TEXT NOT NULL,tasa TEXT NOT NULL,monto TEXT NOT NULL,abono TEXT NOT NULL,debe TEXT NOT NULL,comentario TEXT NOT NULL,fecha_ordenada TEXT NOT NULL)")
            mysql.connection.commit()
            


            
            # ordenar fecha
            fecha_a=fecha[:4]
            fecha_m=fecha[5:7]
            fecha_d=fecha[8:]
            fecha_t=fecha_a
            fecha_t+=fecha_m
            fecha_t+=fecha_d
            fecha_indice=fecha_t

            fecha_a=fecha[:4]
            fecha_m=fecha[5:7]
            fecha_d=fecha[8:]
            fecha_t=fecha_d
            fecha_t+='-'
            fecha_t+=fecha_m
            fecha_t+='-'
            fecha_t+=fecha_a
            fecha_ordenada=fecha_t
            # fin ordenar fecha
            abono=0.0
            monto=total
            debe=total
            
            monto=float(monto)
            debe=float(debe)
            kilos=float(kilos)
            precio=float(precio)
            monto=separador_miles(monto)
            debe=separador_miles(debe)
            abono=separador_miles(abono)
            kilos=separador_miles(kilos)
            precio=separador_miles(precio)
            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO ' + factura2 + ' (propietario,factura,cliente,producto,fecha,monto,abono,debe,comentario,fecha_indice,fecha_ordenada) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (propietario,factura,cliente,producto,fecha,monto,abono,debe,comentario,fecha_indice,fecha_ordenada))
            mysql.connection.commit()

            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO ventas_materiaprima (propietario,factura,cliente,producto,fecha,monto,abono,debe,comentario,cantidad,precio,fecha_indice,fecha_ordenada) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (propietario,factura,cliente,producto,fecha,monto,abono,debe,comentario,kilos,precio,fecha_indice,fecha_ordenada))
            mysql.connection.commit()

    return redirect(url_for('planta_aba'))
####### ventas materia prima 

@app.route('/ventas_materiaprima', methods=['GET','POST'])
def ventas_materiaprima():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_clientes ORDER BY nombre')
    data=cur.fetchall()
    print('data = ',data)
    cliente=['[SELECCIONE]']
    for j in  data:
        cliente.append(j[1])

    data=bd_lista_materiaprima()
    producto=['[SELECCIONE]']
    for j in data:
        producto.append(j[1])
    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall()
    propietario=['[SELECCIONE]']
    for j in data:
        propietario.append(j[1])




    return render_template('ventas_materiaprima.html',
                           cliente=cliente,
                           producto=producto,
                           propietario=propietario
                           )


####### fin ventas materia prima

@app.route('/psql', methods=['GET','POST'])
def psql():
       
    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM orden_produccion WHERE estado = "producido" and baches = "10" and alimento="POLLITA"')
    #cur.execute("CALL ver_precio(1)")
    
    data=cur.fetchall()
    print('--------------------------') 
    #print(data)
    #print('longitud = ',len(data))


    

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM inventario_aba WHERE producto = "AFRECHO DE TRIGO" ORDER BY fecha_indice DESC ')
    #cur.execute("CALL ver_precio(1)")
    
    data=cur.fetchall()
    print('--------------------------') 
    
    print(' ') 
    print('lafrecho = ',data)

    calc_costo_mp('MAIZ AMARILLO')

   
    return render_template('psql.html')

@app.route('/estado_produccion/<id>', methods=['GET','POST'])
def estado_produccion(id):
    print('')
    print('')
    print('')
    print('-------------------------------------------------')
    print('-------------------------------------------------')
    print('-------------------------------------------------')
    print('')
    print('INICIO DE ESTADO DE PRODUCCION')
    print('')
    print('el id de la tabla estado_produccion es  = ',id)

    cur=mysql.connection.cursor()
    #cur.execute('SELECT * FROM orden_produccion ORDER BY id ')
    cur.execute(f"SELECT * FROM orden_produccion" + f" WHERE id = {id}")
    
    data=cur.fetchall() 


    print('id buscado en la BD = ',data)
    
    estado='producido'

    cur=mysql.connection.cursor()
    #cliente=cliente.upper() # transformamos a mayusculas
    cur.execute("""
        UPDATE orden_produccion
        SET estado=%s                
        WHERE id = %s
    """,(estado,id))
    mysql.connection.commit()  

    #return redirect(url_for('ordenes_produccion'))   

    ##############

    # materia prima
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_materiaprima=[] 
    for j in data:
        array_materiaprima.append((j))
    print('materia prima = ',array_materiaprima)
    # fin materia prima
    print('')
    # formula
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formula ORDER BY alimento ')
    data=cur.fetchall() 
    array_formula=[] 
    for j in data:
        array_formula.append((j))
    
    print('formula = ',array_formula)
    # fin formula

    print('')
    # tipos de alimento

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_tipo_alimento=[] 
    for j in data:
        array_tipo_alimento.append((j))
    
    print('tipo alimento = ',array_tipo_alimento)

    # fin tipos de alimentos

    print('')

    # orden produccion
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM orden_produccion ORDER BY alimento ')
    data=cur.fetchall() 
    array_orden_produccion=[] 
    for j in data:
        array_orden_produccion.append((j))
    
    print('orden pruduccion = ',array_orden_produccion)

    # fin orden produccion

    
     
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_aba ORDER BY producto ')
    data=cur.fetchall() 
    array_inventario=[] 
    for j in data:
        array_inventario.append((j))
    
    print('inventario = ',array_inventario)

    # fin inventario aba materia prima


   
    i=0
    #inventario_productos=[]
    inventario_kilos=np.zeros(len(array_materiaprima),dtype='<U50' )
    inventario_kilos_f=np.zeros(len(array_materiaprima) )
    
    suma=0.0
    for j in array_materiaprima:
        suma=0.0
        for k in array_inventario:

            if j[1]==k[1]:

                suma_t=k[3]
                suma_t=devolver_separador_miles(suma_t)
                suma_t=float(suma_t)
                suma=suma+suma_t
                inventario_kilos[i]=suma
                inventario_kilos_f[i]=suma
                
                
        i=i+1    
                
    print('inventario_kilos = ',inventario_kilos)

   

    print('')
    print('')
    print('formula', array_formula)
    print('')
    print('')


    print('')
    print('')
    print('orden produccion', array_orden_produccion)
    print('')
    print('')
    suma=0.0
    array_baches=np.zeros(len(array_tipo_alimento),dtype='<U50' )
    array_baches_float=np.zeros(len(array_tipo_alimento) )
    
    
    i =0
    q=0
    y=0
    array_kilos_np =np.zeros((len(array_materiaprima),len(array_tipo_alimento)) )#,dtype='<U50'
    for j in array_tipo_alimento:
        

        for k in array_formula:

            if j[1] == k[1]:
                y=0
                for h in array_materiaprima:
                    
                    if h[1]==k[2]:
                        #print(k[2],' ', k[1],' ',j[1], '    y= ',y)
                        array_kilos_np[y,q]=k[3]
                    y=y+1
                
        q=q+1
                
                
    
    i=i+1
    print('array_kilos_np = ', array_kilos_np)
    
    cur=mysql.connection.cursor()
    cur.execute(f"SELECT * FROM orden_produccion" + f" WHERE id = {id}")
    data=cur.fetchall() 

    buzon_op=[]
    for j in data:          
        buzon_op.append(j)  
                            
    print ('buzon_op = ', buzon_op)

    for j in buzon_op:      

        baches=j[4]
        nombre_buzon=j[1]
    print('baches = ',baches)
    print('nombre buzon = ',nombre_buzon)

    baches=float(baches)
    i=0
    indice_m=0
    for j in array_tipo_alimento:
        if j[1]==nombre_buzon:
            indice_m=i


        i=i+1

    print('indice = ', indice_m)

    mp_consumida=[]
    for j in array_kilos_np:
        mp_consumida.append(j[indice_m])
    
    print('materia prima consumida = ',mp_consumida)

    alimento_elaborado=np.sum(mp_consumida)
    print('alimento elaborado suma =  ',alimento_elaborado)
    alimento_elaborado=alimento_elaborado*baches
    print('')
    print('alimento elaborado final =  ',alimento_elaborado)

    mp_consumida_final=np.multiply(mp_consumida,baches)
    print(' materia prima consumida final')
    print(mp_consumida_final)



    cur=mysql.connection.cursor()
    cur.execute(f"SELECT * FROM inventario_alimento WHERE producto = '{nombre_buzon}'")
    data=cur.fetchall() 
    print ('data ',data)

    
    for j in data:
        kilos_i_a=j[2]
    kilos_i_a=float(kilos_i_a)
    kilos_i_a=alimento_elaborado+kilos_i_a  # suma los kilos de alimento existente en el inventario de alimento

    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE inventario_alimento
        SET cantidad=%s              
        WHERE producto = %s
    """,(kilos_i_a,nombre_buzon))
    mysql.connection.commit()

    data=bd_lista_materiaprima()
    b_mp=[]
    for j in data:
        b_mp.append(j[1])

    print('b_mp = ',b_mp)


    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    print ('data ',data) 
    
    b_kilos_mp=[]
    for j in data:
        b_kilos_mp.append(float(j[3]))
    
    print('')
    print('mp_consumida_final')
    print(mp_consumida_final)
    print('')
    print('kilos mp en inventario')
    print(b_kilos_mp)

    mp_consumida_final2=[]
    for j in mp_consumida_final:
        p=float(j)
        mp_consumida_final2.append(p)

    kilos_inventario=np.subtract(b_kilos_mp,mp_consumida_final2) 
    print(kilos_inventario)

    
    
    # podemos agregar aqui deficit de materia prima

    i=0
    for j in b_mp:
        cur=mysql.connection.cursor()
        cur.execute("""
        UPDATE costo_materiaprima
        SET kilos=%s              
        WHERE producto = %s
        """,(kilos_inventario[i],j))
        mysql.connection.commit()
        i=i+1



    print('')
    print('')
    print('')
    print('-------------------------------------------------')
    print('-------------------------------------------------')
    print('-------------------------------------------------')
    print('')
    print('FIN DE ESTADO DE PRODUCCION')
    print('')

    return render_template('estado_produccion.html',id=id)



@app.route('/ordenes_produccion', methods=['GET','POST'])
def ordenes_produccion():

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM orden_produccion ORDER BY fecha_indice ASC')
    data=cur.fetchall() 
    print(data)
    array_data=[]
    fecha=fecha_hoy()
    hoy=fecha[0]
    print('hoy = ', hoy)
    aba_ok=[]
    aba_nook=[]
    for j in data:
        if j[5]=='producido':
            aba_ok.append(j)
        else:
            aba_nook.append(j)

        array_data.append(j)
    print(array_data)




    


    return render_template('ordenes_produccion.html',array_data=array_data,aba_ok=aba_ok,aba_nook=aba_nook)






@app.route('/add_producir/<id>/<costo>', methods=['GET', 'POST'])
def add_producir(id,costo):
    
    b=fecha_hoy()
    print('b = ',b)
    array_alimento=[]
    indice_alimento=int(id)
    fecha=b[2]
    fecha_indice=b[0]
    print('fecha = ',fecha)

    if request.method=='POST':

        baches=request.form['cantidad']
        if ((not baches)):
            flash('debe ingresar la cantidad de baches','baches_nulo')
            return redirect(url_for('generar_produccion'))

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
        data=cur.fetchall() 
        
        for j in data:
            array_alimento.append(j[1])
        estado='pendiente'
        alimento=array_alimento[indice_alimento]
        print('Alimento = ',alimento)

        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM formula WHERE alimento = "{alimento}"')
        data=cur.fetchall()
        formula=[]
        for j in data:
            formula.append(j)

        print('')
        print('data formula')
        print(formula)
        print('')

        data=bd_lista_materiaprima()
        lista_mp=[]
        for j in data:
            lista_mp.append(j[1])
        
        print('')
        print('')
        print('lista mp')
        print(lista_mp)
        print('')
        print('')
        array_mp=np.zeros((len(lista_mp)))
        i=0
        x=[]
        for j in lista_mp:
            for k in formula:
                if j == k[2]:
                    array_mp[i]=k[3]
                    x.append(i)
            i=i+1
        n_baches=float(baches)
        array_mp=np.multiply(array_mp,n_baches)
        print('')
        print('')
        print('array_mp')
        print(array_mp)
        print('')
        print('')

        cur=mysql.connection.cursor()
        cur.execute(f'SELECT * FROM costo_materiaprima ORDER BY producto')
        data=cur.fetchall()
        array_cm=[]
        for j in data:
            a=float(j[3])
            array_cm.append(a)
        print('')
        print('')
        print('array_cm')
        print(array_cm)
        print('x = ',x)
        print('')
        permiso=0
        array_validacion=[]
        for j in x:
            validacion=array_cm[j]-array_mp[j]
            print('array_csoto mp ', array_cm[j], ' array_mp ',array_mp[j],' validacion ',validacion)
            array_validacion.append(validacion)
            if validacion<0:
                permiso=1

        print('')
        print('')
        print('array_validacion')
        print(array_validacion)
        print('')
        print('')
        print('validacion')
        print(validacion)
        print('')
        print('')
        print('permiso')
        print(permiso)
        print('')
        print('')

        if permiso == 1:
            flash('no hay suficiente inventario para producir esta cantidad de alimento','inventario_insuficiente')
            return redirect(url_for('generar_produccion'))
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO orden_produccion (alimento,fecha,fecha_indice,baches,estado,costo) VALUES(%s,%s,%s,%s,%s,%s)',
        (alimento,fecha,fecha_indice,baches,estado,costo))
        mysql.connection.commit()


    print('id de alimento = ',id)
    
    print('Numero de Baches = ',baches)

    #return render_template('planta_aba.html')
    return redirect(url_for('planta_aba'))










@app.route('/producir/<id>/<costo>')
def producir(id,costo):
    print('llego id =',id,costo)

      # rutina buscar tipo de alimento
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_alimento=[]
    indice_alimento=int(id)
    for j in data:
        array_alimento.append((j[1]))
    print(array_alimento)

    print('El alimento seleccionado es = ',array_alimento[indice_alimento])
    alimento=array_alimento[indice_alimento]
    # fin rutina buscar tipo de alimento
    return render_template('pre_produccion.html',
                           indice_alimento=indice_alimento,
                           alimento=alimento,
                           costo=costo)








@app.route('/generar_produccion',methods=['GET', 'POST'])
def generar_produccion():
       # rutina buscar tipo de alimento
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_alimento=[]
    for j in data:
        array_alimento.append((j[1]))
    
    # fin rutina buscar tipo de alimento


     # rutina buscar formula
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formula ORDER BY alimento ')
    data=cur.fetchall() 
    array_formula_alimento=[]
    array_formula_materia=[]
    array_formula_cantidad=[]



    for j in data:
        array_formula_alimento.append((j[1]))
        array_formula_materia.append((j[2]))
        array_formula_cantidad.append((j[3]))

    
    
    # fin rutina buscar formula

     # rutina buscar lista_materiaprima
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_materiaprima=[] 
    for j in data:
        array_materiaprima.append((j[1]))

    # fin rutina buscar lista_materiaprima

    print('')
    print('alimentos en bd tipo alimento',array_alimento)
    print('')
    print('tipos de alimentos en bd de formula',array_formula_alimento)
    print('')
    print('tipos de materia en bd de formula',array_formula_materia)
    print('')
    print('cantidad materia en bd de formula',array_formula_cantidad)
    print('')
    print('tipos de materia prima',array_materiaprima)
    print('')
    
    matriz=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50' )
    matriz_kilos=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50' )
    print(matriz)
    print(matriz.shape)
    print('matriz_kilos = ',matriz_kilos)
    
    print(matriz.shape)
    longitud_matriz=0
    for j in matriz.shape:
        print(j)

    longitud_matriz=len(array_materiaprima)
    print('longitud matriz = ', longitud_matriz)
    i=0

    array_temporal=[]
    
    array_kilos_temporal=[]
    array_alimento_utilizado=[]
    array_materia_utizado=[]
    array_cantidad_utizado=[]
    array_validacion=[]
    i=0
    z=0
    cont=0
    r=0
    validacion=0
    for j in array_alimento:
        validacion=0
        z=0
        try:
            cur=mysql.connection.cursor()
            cur.execute(f"SELECT * FROM formula WHERE alimento = '{j}'") 
            alim=j
            data=cur.fetchall() 
            print('data = ',data)
            validacion=0
            for k in data:
                
                array_temporal.append(k[2])
                array_kilos_temporal.append(k[3])
                
            
        except:
            print('no existe')
            

        finally:
            print('error')
            validacion=1
        
        if array_temporal==[]:
            array_validacion.append(0)
        else:
            array_validacion.append(1)

        print('******************************************') 
        print('alimento  = ',alim)
        print('materia prima usada en el alimento = ',array_temporal)
        print('i= ',i) 
       
        print('******************************************') 
        r=0
        u=0
        for g in array_temporal :
                for h in array_materiaprima :
                    if g ==h:                        
                        matriz[r,i]=g
                        matriz_kilos[r,i]=array_kilos_temporal[u]
                        
                        r=0
                        break
                        
                    r=r+1
                u=u+1
        alim=''
        array_temporal=[]
        array_kilos_temporal=[]
        print('array_temporal = ',array_temporal) 
        print(matriz)
        print('') 
        print(matriz_kilos)
        print('r',r)
        print('len materia =',len(array_materiaprima))
        print(matriz.shape)
        print('matriz validacion alimento = ', array_validacion)
        i=i+1
       
        #####
    i=0
    x=0
    m_kilos_f=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype=float)
    for j in matriz_kilos:
        x=0
        for k in j:
            if k=='':
                m_kilos_f[i,x]=0.0
            else:
                m_kilos_f[i,x]=k

            print(k,' i= ', i, ' x= ',x)
            x=x+1
        i=i+1
    print(m_kilos_f)      

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto')
    data=cur.fetchall()
    valor_costo=[]
    for j in data:
        a=j[2]
        
        valor_costo.append(a)
    print(valor_costo)
    print(len(valor_costo))
    print(len(array_materiaprima))

    costo=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype=float)
    i=0
    x=0
    print('costo')
    print(costo.shape)
    print(costo)
    a,b=costo.shape
    print(b)
    for j in valor_costo:
        x=0
        
        for k in range(b):
            print('j = ',j,' i = ',i,' x = ',x)
            costo[i,x]=j
            x=x+1    
        i=i+1
    print(costo)
    i=0
    x=0

    costo_final=np.multiply(costo,m_kilos_f)
    i=0
    x=0
    costo_final=np.around(costo_final,decimals=4)
    suma_costo=np.sum(costo_final,axis=0)
    costo_kg=np.divide(suma_costo,250)
    costo_saco=np.multiply(costo_kg,40)
    print(costo_final)
    print('suma costo')
    suma_costo=np.around(suma_costo,decimals=3)
    print(suma_costo)

    print('costo kg')
    print(costo_kg)
    costo_kg=np.round(costo_kg,decimals=4)
    costo_saco=np.round(costo_saco,decimals=2)

    print('costo saco')
    print(costo_saco)
    
    return render_template('generar_produccion.html',
                           materia_prima=matriz,
                           kilos=matriz_kilos,
                           alimento=array_alimento,
                           validacion=array_validacion,
                           inventario_materia=array_materiaprima,
                           longitud_matriz=longitud_matriz,
                           costo_final=costo_final,
                           suma_costo=suma_costo,
                           costo_kg=costo_kg,
                           costo_saco=costo_saco
                           )


@app.route('/mostrar_formulas',methods=['GET', 'POST'])
def mostrar_formulas():
     # rutina buscar tipo de alimento
    print(' ********* Mostrar Formulas ********')
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_alimento=[]
    for j in data:
        array_alimento.append((j[1]))
    
    # fin rutina buscar tipo de alimento


     
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formula ORDER BY alimento ')
    data=cur.fetchall() 
    array_formula_alimento=[]
    array_formula_materia=[]
    array_formula_cantidad=[]


    print('')
    print('')
    print('data')
    print(data)
    print('')
    print('')
    print('')
    for j in data:
        array_formula_alimento.append((j[1]))
        array_formula_materia.append((j[2]))
        array_formula_cantidad.append((j[3]))

    
    
    # fin rutina buscar formula

     # rutina buscar lista_materiaprima
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_materiaprima=[] 
    for j in data:
        array_materiaprima.append((j[1]))

    # fin rutina buscar lista_materiaprima

    print('')
    print('alimentos en bd tipo alimento',array_alimento)
    print('')
    print('tipos de alimentos en bd de formula',array_formula_alimento)
    print('')
    print('tipos de materia en bd de formula',array_formula_materia)
    print('')
    print('cantidad materia en bd de formula',array_formula_cantidad)
    print('')
    print('tipos de materia prima',array_materiaprima)
    print('')
    
    matriz=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50' )
    matriz_kilos=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50' )
    print(matriz)
    print(matriz.shape)
    print('matriz_kilos = ',matriz_kilos)
    
    print(matriz.shape)
    longitud_matriz=0
    for j in matriz.shape:
        print(j)

    longitud_matriz=len(array_materiaprima)
    print('longitud matriz = ', longitud_matriz)
    i=0

    array_temporal=[]
    
    array_kilos_temporal=[]
    array_alimento_utilizado=[]
    array_materia_utizado=[]
    array_cantidad_utizado=[]
    array_validacion=[]
    i=0
    z=0
    cont=0
    r=0
    validacion=0
    for j in array_alimento:
        validacion=0
        z=0
        try:
            cur=mysql.connection.cursor()
            cur.execute(f"SELECT * FROM formula WHERE alimento = '{j}'") 
            alim=j
            data=cur.fetchall() 
            print('data = ',data)
            validacion=0
            for k in data:
                
                array_temporal.append(k[2])
                array_kilos_temporal.append(k[3])
                
            
        except:
            print('no existe')
            

        finally:
            print('error')
            validacion=1
        
        if array_temporal==[]:
            array_validacion.append(0)
        else:
            array_validacion.append(1)

        print('******************************************') 
        print('alimento  = ',alim)
        print('materia prima usada en el alimento = ',array_temporal)
        print('i= ',i) 
       
        print('******************************************') 
        r=0
        u=0
        for g in array_temporal :
                for h in array_materiaprima :
                    if g ==h:                        
                        matriz[r,i]=g
                        matriz_kilos[r,i]=array_kilos_temporal[u]
                        
                        r=0
                        break
                        
                    r=r+1
                u=u+1
        alim=''
        array_temporal=[]
        array_kilos_temporal=[]
        print('array_temporal = ',array_temporal) 
        print(matriz)
        print('') 
        print(matriz_kilos)
        print('r',r)
        print('len materia =',len(array_materiaprima))
        print(matriz.shape)
        print('matriz validacion alimento = ', array_validacion)
        i=i+1
        
        s_m_kilos=np.asarray(array_formula_cantidad, float)
        #s_m_kilos=np.sum(s_m_kilos,axis=0)
        a=0.0
        for j in s_m_kilos:
            a=a+j
        print(s_m_kilos)
        print(a)

        print(matriz_kilos)
        print('')
        print('')
        print('')

    
    print(matriz_kilos)
    print(array_materiaprima)
    i=0
    x=0
    m_kilos_f=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype=float)
    for j in matriz_kilos:
        x=0
        for k in j:
            if k=='':
                m_kilos_f[i,x]=0.0
            else:
                m_kilos_f[i,x]=k

            #print(k,' i= ', i, ' x= ',x)
            x=x+1
        i=i+1
    print(m_kilos_f)      

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto')
    data=cur.fetchall()
    valor_costo=[]
    for j in data:
        a=j[2]
        
        valor_costo.append(a)
    print(valor_costo)
    print(len(valor_costo))
    print(len(array_materiaprima))

    costo2=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50')
    costo=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype=float)
    i=0
    x=0
    print('costo')
    print(costo.shape)
    print(costo)
    a,b=costo.shape
    print(b)
    for j in valor_costo:
        x=0
        
        for k in range(b):
            #print('j = ',j,' i = ',i,' x = ',x)
            costo[i,x]=j
            x=x+1    
        i=i+1
    print(costo)
    i=0
    x=0

    costo_final=np.multiply(costo,m_kilos_f)
    i=0
    x=0
    costo_final=np.around(costo_final,decimals=4)
    suma_costo=np.sum(costo_final,axis=0)
    costo_kg=np.divide(suma_costo,250)
    costo_saco=np.multiply(costo_kg,40)
    print(costo_final)
    print('suma costo')
    suma_costo=np.around(suma_costo,decimals=3)
    print(suma_costo)

    print('costo kg')
    print(costo_kg)
    costo_kg=np.round(costo_kg,decimals=4)
    costo_saco=np.round(costo_saco,decimals=2)

    print('costo saco')
    print(costo_saco)
    return render_template('mostrar_formulas.html',
                           materia_prima=matriz,
                           kilos=matriz_kilos,
                           alimento=array_alimento,
                           validacion=array_validacion,
                           inventario_materia=array_materiaprima,
                           longitud_matriz=longitud_matriz,
                           costo_final=costo_final,
                           suma_costo=suma_costo,
                           costo_kg=costo_kg,
                           costo_saco=costo_saco
                           )




@app.route('/pruebadiv')
def pruebadiv():


    return render_template('pruebadiv.html')

@app.route('/prueba', methods=['GET','POST'])
def prueba():
    if request.method=='POST':
        indice=request.form['producto']
        print(indice)
        #return render_template('prueba.html')
        inv_mp2=bd_inventario_aba()
        inv_mp=[]
        inv_mp_entero=[]
        for j in inv_mp2:
            inv_mp.append(j)

        p=bd_proveedor()
        proveedor=[]
        for j in p:
            proveedor.append(j[1])

        
        lista_mp=bd_lista_materiaprima()
        array_lista_mp=[]
        for j in lista_mp:
            array_lista_mp.append(j[1])
        
        mp_nombre=array_lista_mp[int(indice)]
        print(inv_mp)
        print('')
        print('materia prima seleccionada es = ', array_lista_mp[int(indice)])
        materiaprima=[]
        for j in lista_mp:
            materiaprima.append(j[1])
        matriz_precio=np.zeros((1,len(inv_mp)))
        
        print(matriz_precio)

        a_proveedor=[]
        a_costo=np.zeros((0,0))
        
        print('ccccccccccccccc')
        print(a_costo)

        
        
        for j in inv_mp:
            if j[1]==mp_nombre:
                a_proveedor.append(j[4])
                d=devolver_separador_miles(j[5])
                a_costo=np.append(a_costo,d)

            else:
                a_proveedor.append(j[4])
                a_costo=np.append(a_costo,0.0)

        print(a_proveedor)
        print('a costo es = ',a_costo)

        indicador=0
        for j in a_costo:
            print('j en a_costo = ',j)
            if j != 0:
                indicador=1

        
        print('indicador = ',indicador)   

        if indicador==0:
            flash(f'No se encontro proveedor para {mp_nombre}','buscar_proveedor')
            return redirect(url_for('prueba'))    

        
        id_precio=np.where(a_costo > '0.0')[0] 
        print(id_precio)

        nombre_p=np.zeros((0,0))
        monto_prod=np.zeros((0,0))
        print('id len = ', len(id_precio))
        
        a_precio=[]

        for j in id_precio:
            a_precio.append(j)
        print('a precio = ',a_precio)
        print('array=',a_precio)
        for j in a_precio:
            nombre_p=np.append(nombre_p,a_proveedor[j])
            monto_prod=np.append(monto_prod,a_costo[j])
            print(j)
        print('')
        print('nobres')
        print(nombre_p)
        print('')
        print('costo')
        print(monto_prod)

        print('min = ',monto_prod.argmin())
        mp_final=np.zeros((0,0))
        n_final=np.zeros((0,0))
        variable=len(monto_prod)
        i_monto=0
        for j in range(variable):
            i_monto=monto_prod.argmin()
            print('i_monto = ',i_monto)
            mp_final=np.append(mp_final,monto_prod[i_monto])
            n_final=np.append(n_final,nombre_p[i_monto])
            monto_prod=np.delete(monto_prod,i_monto,0)
            nombre_p=np.delete(nombre_p,i_monto)
            print('')            
            print(monto_prod)
            print(nombre_p)
        print('')            
        print(mp_final)
        print(n_final)
        return render_template('prueba.html',
                               array_productos=materiaprima,
                               mp_final=mp_final,
                               n_final=n_final,
                               producto=mp_nombre
                               )




    else:
        inv_mp=bd_inventario_aba()
        p=bd_proveedor()
        proveedor=[]
        for j in p:
            proveedor.append(j[1])

        print(len(proveedor))
        print(proveedor)
        print('')
        lista_mp=bd_lista_materiaprima()
        print(len(lista_mp))
        materiaprima=[]
        for j in lista_mp:
            materiaprima.append(j[1])
        matriz_precio=np.zeros((len(proveedor),len(lista_mp)))
        matriz_precio[1,2]=20
        print(matriz_precio)
    
    return render_template('prueba.html',array_productos=materiaprima)



@app.route('/consumo_interno')
def consumo_interno():
    
    return render_template('consumo_interno.html')

@app.route('/confirmar_consumo_interno',methods=['GET', 'POST'])
def confirmar_consumo_interno():
    return render_template('consumo_interno.html')

@app.route('/confirmar_formula',methods=['GET', 'POST'])
def confirmar_formula():

    hoy = datetime.now()
    hoy=str(hoy)
    hoy=hoy[:11]
    hoy=hoy.strip()
    hoy=datetime.strptime(hoy, "%Y-%m-%d")
    
    #print('fecha = ',hoy)
    hoy=str(hoy)
    i=0
    hoy_f=''
    for j in hoy:
        if i<10:
            hoy_f+=j
            print(j)
        i=i+1
    #print(hoy_f)
    fecha=hoy_f
    fecha_a=fecha[:4]
    fecha_m=fecha[5:7]
    fecha_d=fecha[8:]
    fecha_t=fecha_a
    fecha_t+=fecha_m
    fecha_t+=fecha_d
    fecha_indice=fecha_t
    #print(fecha_indice)

   


    # rutina buscar numero de reporte 
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM consumo_interno ORDER BY reporte ')
    data=cur.fetchall() 
    array_reporte=[]
    for j in data:
        array_reporte.append(int(j[3]))
    print('reporte')
    print(array_reporte)

    reporte=0
    y=0
    for j in array_reporte:
        if j > y:
            reporte=j 
        y=j
    reporte=reporte+1
    reporte=str(reporte)
    #print("reporte = ",reporte)


    # fin rutina buscar numero de reporte

    if request.method=='POST':
        hoy = datetime.now()
        hoy=str(hoy)
        hoy=hoy[:11]
        hoy=hoy.strip()
        hoy=datetime.strptime(hoy, "%Y-%m-%d")

        #print('fecha = ',hoy)
        hoy=str(hoy)
        i=0
        hoy_f=''
        for j in hoy:
            if i<10:
                hoy_f+=j
                print(j)
            i=i+1
        #print(hoy_f)
        fecha=hoy_f
        print('Llego el dato de confirmacion por el metodo POST')
        #producto=request.form
        #recibe el numero de tamaño del array que envia el post
        rango=request.form['b']
        datospost=request.form
        print('datos post',datospost)
        indice=request.form['indice']
        alimentoseleccionado=request.form['alimentoseleccionado']
        #print('Indice Alimento = ',indice)

        #print('este es el POST = ',producto)

        rango=int(rango)
        array_materia=[]
        array_cantidad=[]
        q=0
        array_p_int=[]
        array_k_int=[]
        alimento=0
        #verificar la longitud del dato enviado en el post para crear un array 
        #donde se almacena la entrada de productos y materia prima del post
        for j in range(rango):
            x='a'
            c='c'
            p=str(q)
            x+=p
            c+=p
            array_materia.append(x)
            array_cantidad.append(c)
            array_p_int.append(request.form[array_materia[q]])
            array_k_int.append(request.form[array_cantidad[q]])
            producto=array_p_int[q]
            cantidad=array_k_int[q]

            cur=mysql.connection.cursor()
            cur.execute('INSERT INTO formula (alimento,producto,cantidad,fecha,fecha_indice) VALUES(%s,%s,%s,%s,%s)',
            (alimentoseleccionado,producto,cantidad,fecha,fecha_indice))
            mysql.connection.commit() 

            
            

            alimento_t=array_k_int[q]
            alimento_t=float(alimento_t)
            alimento=alimento + alimento_t

            
            q=q+1
        cantidad_alimento=alimento
        procedencia='INTERNO'
        
        producto=array_p_int
        cantidad=array_k_int
    #return 'construccion'    
    return redirect(url_for('planta_aba'))
    


@app.route('/crear_formula',methods=['GET', 'POST'])
def crear_formula():

    ##### metodo post
    
        
     # rutina buscar lista de tipo de alimentos
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_tipo_alimento=[]
    for j in data:
        array_tipo_alimento.append(j[1])
    
    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_productos=[]
    for j in data:
        array_productos.append(j[1])
    
    
    
    array_proveedores=[]
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM proveedores ORDER BY proveedor')
    data=cur.fetchall() 
    array_proveedores=[]
    for j in data:
        array_proveedores.append(j[1])
    
    

    # fin rutina lista de proveedores

     # rutina para lista de propietario
    array_propietario=[]
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall() 
    
    for j in data:
        array_propietario.append(j[1])
    
    

    # fin rutina de lista de propietario
    #
    # rutina buscar lista de productos agregados
    array_consumo=[]
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM consumo_interno ORDER BY producto')
    data=cur.fetchall() 
    array_consumo=[]
    for j in data:
        array_consumo.append(j[1])
    
   

    # fin rutina lista de productos agregados
    if request.method=='POST':
        
        print("llego el metodo post")
        producto=request.form['productoadd']
        alimento=request.form['alimento']
        #print('alimento seleccionado = ', alimento)
        alimento=int(alimento)
        indice_alimento=str(alimento)
        alimento_seleccionado=array_tipo_alimento[alimento]

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM formula')
        data=cur.fetchall()
        t_aba=[]
        for j in data:
            t_aba.append(j[1])
        print('')
        print('tipos de alimentos en formulas')
        print(t_aba)
        for j in t_aba:
            if j == alimento_seleccionado:
                print('el alimento seleccionado ya existe')
                flash('Este Alimento ya tiene una formula creada', 'puntos')
                return redirect(url_for('crear_formula'))
        
        
        longitud=len(array_productos)
        #print(longitud)
        array_variable=[]
        q=0
        array_data=[]
        # obtener el post de variable
        for j in array_productos:
            x='a'
            p=str(q)
            x+=p
            
            array_variable.append(x)
            a=request.form[array_variable[q]]
           
            for j in a:
                if j=='0' or j=='1' or j=='2' or j=='3' or j== '4' or j=='5' or j=='6' or j=='7' or j=='8' or j=='9' or j=='.':
                    print('normal')
                else:
                    print('error')
                    if j==',':
                        flash('no se aceptan "," debe colocar "." para decimales', 'puntos')
                        return redirect(url_for('crear_formula'))
                    else:
                        flash('no debe ingresar letras u otros caracteres, solo se aceptan numeros y puntos para decimales','puntos2')
                        return redirect(url_for('crear_formula'))


            array_data.append(a)
            print(array_data)
            q=q+1
        #print(array_variable)
        #print(array_data)

        array_kilos=[]
        array_productos_add=[]
        contador=0
        for j in array_data:
            #print(j)
            if j=='':
                None
                
            else:
                array_productos_add.append(array_productos[contador])
                array_kilos.append(j)
                
            contador=contador+1
        
        return render_template('confirmar_formula.html',array_productos_add=array_productos_add,
                               array_kilos=array_kilos,indice_alimento=indice_alimento,
                               alimento_seleccionado=alimento_seleccionado)
        




    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_aba ORDER BY fecha_indice DESC')
    data=cur.fetchall() 
    
    productos_inv=[]
    productos_suma=[]
    
    for j in array_productos:
        prod=j
        productos_inv.append(prod)
        suma_t=0.0
        i=0
        # comparamos productos array con bd y guardamos en productos_inv y productos_suma
        for k in data:
            if j == k[1]:
                
                suma=k[3]
                
                suma=devolver_separador_miles(suma)
                suma=float(suma)
                suma_t=suma+suma_t
                
            
            i=i+1
            
            if i==len(data):
                suma_t=separador_miles(suma_t)
                productos_suma.append(suma_t)
            
       

       
    return render_template('crear_formula.html',tabla1=data,array_productos=array_productos,
                           productos_inv=productos_inv,productos_suma=productos_suma,
                           array_consumo=array_consumo,array_tipo_alimento=array_tipo_alimento                         
                           )



@app.route('/agregar_inventario',methods=['GET', 'POST'])
def agregar_inventario():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_productos=['']
    for j in data:
        array_productos.append(j[1])
    
    #print('lista materia prima = ', array_productos)

    # rutina para lista de proveedores
    array_proveedores=[]
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM proveedores ORDER BY proveedor')
    data=cur.fetchall() 
    array_proveedores=['']
    for j in data:
        array_proveedores.append(j[1])
    
    
    array_propietario=['']
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall() 
    
    for j in data:
        array_propietario.append(j[1])
    
    print('lista propietario = ', array_propietario)


    # fin rutina de lista de propietario
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_aba ORDER BY fecha_indice DESC')
    data=cur.fetchall() 
    
    productos_inv=[]
    productos_suma=[]
    
    for j in array_productos:
        prod=j
        productos_inv.append(prod)
        suma_t=0.0
        i=0
        for k in data:
            if j == k[1]:
                
                suma=k[3]
                
                suma=devolver_separador_miles(suma)
                suma=float(suma)
                suma_t=suma+suma_t
                
            
            i=i+1
            
            if i==len(data):
                suma_t=separador_miles(suma_t)
                productos_suma.append(suma_t)
            
        #print("inventario = ",productos_inv)
        #print("suma       = ", productos_suma)

    return render_template('agregar_inventario.html',
                           tabla1=data,array_productos=array_productos,array_proveedores=array_proveedores,
                           array_propietario=array_propietario,
                           productos_inv=productos_inv,productos_suma=productos_suma)





@app.route('/planta_aba',methods=['GET', 'POST'])
def planta_aba():

    print('')
    print('')
    print('************************** INCICIO PLANTA ABA **************************************')
    print('')
    print('')
    # rutina buscar lista de productos
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_productos=[]
    
    for j in data:
        array_productos.append(j[1])
    
    array_proveedores=[]
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM proveedores ORDER BY proveedor')
    data=cur.fetchall() 
    array_proveedores=[]
    for j in data:
        array_proveedores.append(j[1])
    
    
    array_propietario=[]
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM propietario ORDER BY propietario')
    data=cur.fetchall() 
    
    for j in data:
        array_propietario.append(j[1])
    
    #print('lista propietario = ', array_propietario)


    # fin rutina de lista de propietario
    # post planta_aba
    if request.method=='POST':
        #print('post')
        producto=request.form['producto']
        fecha=request.form['fecha']
        cantidad=request.form['cantidad']  
        proveedor=request.form['proveedor']
        precio=request.form['precio']   
        propietario=request.form['propietario']
        factura=request.form['num_fact']
        comentario=request.form['comentario']
        if ((not producto) or (not fecha) or (not cantidad) or (not propietario) or (not proveedor) or (not precio) or (not factura)):        
           print('debe introducir todos los campos')
           flash('Debe Introducir Todos Los Campos','todosloscampos')           
           return redirect(url_for('agregar_inventario'))
        if producto=='0':
            print('debe introducir todos los campos')
            flash('Debe Introducir Todos Los Campos','todosloscampos')           
            return redirect(url_for('agregar_inventario'))
        if propietario=='0':
            print('debe introducir todos los campos')
            flash('Debe Introducir Todos Los Campos','todosloscampos')           
            return redirect(url_for('agregar_inventario'))
        if proveedor=='0':
            print('debe introducir todos los campos')
            flash('Debe Introducir Todos Los Campos','todosloscampos')           
            return redirect(url_for('agregar_inventario'))
        
        cur.execute("SHOW TABLES") 
        mysql.connection.commit()
        factura_existe=0
        fact='x'+factura
        print('cur = ',cur)
        for j in cur: 
                         
            print(j[0])
            if(str(j[0]) == str(fact)):
                
                flash('Cliente Existe')
                print('Esta factura ya existe en la base de datos ','factura_compra_existe')                
                factura_existe=1
                return redirect(url_for('agregar_inventario'))
                break
        #print('numero de proveedor = ',proveedor)
        proveedor=int(proveedor)
        proveedor=proveedor-1
        proveedor=array_proveedores[proveedor]
        
        
        propietario=int(propietario)
        propietario=propietario-1
        propietario=array_propietario[propietario]
        
        producto=int(producto)
        producto=producto-1
        producto=array_productos[producto]
        
        precio=float(precio)
        cantidad=float(cantidad)
        costo=precio*cantidad
        
        costo=float(costo)
        costo=separador_miles(costo)
        total=costo
        # calculamos total costo



        #fin calculo total costo
        
        precio=separador_miles(precio)
        precio=str(precio)
        
        cantidad=separador_miles(cantidad)
        cantidad=str(cantidad)
        # metodo para crear fecha indice
        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_a
        fecha_t+=fecha_m
        fecha_t+=fecha_d
        
        fecha_indice=fecha_t
        # fin fecha indice
        #
        # ingresamos datos a la bd
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO inventario_aba (producto,fecha,cantidad,proveedor,precio,propietario,fecha_indice,total,factura,comentario) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (producto,fecha,cantidad,proveedor,precio,propietario,fecha_indice,total,factura,comentario))
        mysql.connection.commit()
        # fin ingreso bd

        # llamada bd por fecha indice
        i=0
        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM inventario_aba ORDER BY fecha_indice DESC')
        data=cur.fetchall()
       
        
        
        ##### llamar a funcion para calcular costo total de materia prima #####
        
        
        cur=mysql.connection.cursor()
        cur.execute(f"SELECT * FROM costo_materiaprima WHERE producto = '{producto}'")
        data=cur.fetchall() 
        print('')
        print('DATA')
        print ('data ',data)
        print('')
        
        for j in data:
            costo_bd=float(j[2])
            kilos_bd=float(j[3])
        print('')
        print('costo_bd')
        print (costo_bd)
        print('')
        print('kilos_bd')
        print(kilos_bd)
        print('')

        total_bd=costo_bd*kilos_bd
        print('')
        print('total_base de datos = ',total_bd)

        cantidad=devolver_separador_miles(cantidad)
        cantidad=float(cantidad)
        costo=devolver_separador_miles(costo)
        costo=float(costo)

        nuevo_costo=costo+total_bd
        nuevo_kilos=cantidad+kilos_bd

        nuevo_costo_final=nuevo_costo/nuevo_kilos

        print('')
        print(' imprimiendo costos de la nueva materia prima')
        print('')
        print('la materia prima nueva --- costo = ', costo, ' kilos = ',cantidad)
        print('')
        print('la materia prima de bd ----costo = ', total_bd,'kilos = ', kilos_bd)
        print('')
        print('el nuevo costo de la materia prima es = ', nuevo_costo_final, ' y los nuevos kilos son = ',nuevo_kilos)

        # ingresar nuevo inventario en la base de dato
        
        ##### calcular montos para la factura
        precio_factura=devolver_separador_miles(precio)
        precio_factura=float(precio_factura)
        total_fact=cantidad*precio_factura
        print('')
        print('')
        print('total factura')
        print(total_fact)
        print('')
        print('')
        abono_fact=0.0
        saldo_fact=total_fact
        cur=mysql.connection.cursor() 
        cur.execute('INSERT INTO facturas_compras_materiaprima (factura,producto,cantidad,precio,total,abono,saldo,fecha,propietario) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (factura,producto,cantidad,precio,total_fact,abono_fact,saldo_fact,fecha,propietario))
        mysql.connection.commit()


        cur=mysql.connection.cursor()
        cur.execute("""
        UPDATE costo_materiaprima
        SET kilos=%s,
            costo=%s              
        WHERE producto = %s
        """,(nuevo_kilos,nuevo_costo_final,producto))
        mysql.connection.commit()



        flash('Nueva Materia prima Agregado')


        
        ## fin dellamar a funcion para calcular costo total de materia prima ##
        


        
        ## llenar base de datos de compras materiaprima #######################
        
        

        
            
        precio_cmp=devolver_separador_miles(precio)
        precio_cmp=float(precio_cmp)
        monto_cmp=precio_cmp*cantidad

        print('**********************************')
        print('')
        print('datos para llenar bd de compras materia prima')
        print('')
        print('prducto = ',producto)
        print('fecha = ',fecha)
        print('cantidad = ',cantidad)
        print('proveedor = ', proveedor)
        print('precio = ', precio)
        print('propietario = ', propietario)
        print('factura = ',factura)
        print('comentario = ',comentario)
        print('monto_cmp = ',monto_cmp)
        print('******************************')
        print('')
        print('')

        cantidad_cmp=cantidad
        cantidad_cmp=separador_miles(cantidad_cmp)
        precio_cmp=separador_miles(precio_cmp)
        monto_cmp=separador_miles(monto_cmp)
        abono_cmp='0,0'

        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_a
        fecha_t+=fecha_m
        fecha_t+=fecha_d
        fecha_indice=fecha_t
        fecha_a=fecha[:4]
        fecha_m=fecha[5:7]
        fecha_d=fecha[8:]
        fecha_t=fecha_d
        fecha_t+='-'
        fecha_t+=fecha_m
        fecha_t+='-'
        fecha_t+=fecha_a
        fecha_ordenada=fecha_t

        cur=mysql.connection.cursor() 
        cur.execute('INSERT INTO compras_materiaprima (factura,fecha,proveedor,propietario,producto,cantidad,precio,monto,abono,debe,comentario,fecha_indice,fecha_ordenada) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (factura,fecha,proveedor,propietario,producto,cantidad_cmp,precio_cmp,monto_cmp,abono_cmp,monto_cmp,comentario,fecha_indice,fecha_ordenada))
        mysql.connection.commit()


        cur = mysql.connection.cursor() 
        factura2='x'+factura
        factura2=re.sub(r"\s+", "", factura2)
        cur.execute("CREATE TABLE IF NOT EXISTS " + factura2 + " (id INT(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (id),propietario TEXT NOT NULL,factura TEXT NOT NULL, cliente TEXT NOT NULL,producto TEXT NOT NULL,fecha TEXT NOT NULL,fecha_indice TEXT NOT NULL,dolares TEXT NOT NULL,bolivares TEXT NOT NULL,banco TEXT NOT NULL,referencia TEXT NOT NULL,tasa TEXT NOT NULL,monto TEXT NOT NULL,abono TEXT NOT NULL,debe TEXT NOT NULL,comentario TEXT NOT NULL,fecha_ordenada TEXT NOT NULL)")
        mysql.connection.commit()
        
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO ' + factura2 + ' (propietario,factura,cliente,producto,fecha,monto,abono,debe,comentario,fecha_indice,fecha_ordenada) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (propietario,factura,proveedor,producto,fecha,monto_cmp,abono_cmp,monto_cmp,comentario,fecha_indice,fecha_ordenada))
        mysql.connection.commit()

        # fin post
        
            
        
        
    # llamada bd por fecha indice
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_aba ORDER BY fecha_indice DESC')
    data=cur.fetchall() 
    tabla_1=data
    productos_inv=[]
    productos_suma=[]
    
    



    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto')
    data=cur.fetchall() 
    costo_mp=[]
    for j in data:
        productos_suma.append(j[3])
        productos_inv.append(j[1])
        costo_mp.append(j[2])

    costo_mp_string=[]
    for j in costo_mp:
        j=separador_miles(float(j))
        costo_mp_string.append(j)
    
    print('')
    print('')
    print('producto suma')
    print(productos_suma)    ####                               suma todo el inventario en catidad de kilos string
    print('')
    print('')
    print('')
    # rutina buscar tipos de alimentos
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_alimento=[]
    for j in data:
        array_alimento.append(j[1])
    
    # fin rutina buscar tipos de alimentos

    # rutina buscar inventario de alimento
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento ORDER BY producto ')
    data=cur.fetchall() 
    array_kilos_aba=[]
    alimento_inv=[]
    alimento_suma=[]
    for j in data:
        array_kilos_aba.append(float(j[2]))
        alimento_inv.append(j[1])
    # fin rutina buscar inventario de alimento

    
    # rutina para sumar la cantidad de alimentos por tipo   
    
    aliment=j
    #alimento_inv.append(aliment)
    suma_a=0.0
    i=0
    
    


    print('')
    print('--- alimento suma -------')
    print(alimento_suma)                             ##### todos los alimentos realizados por tipo de alimentos
    print('')
            
    

    kilos_final=[]
    for j in productos_suma:
        j=float(j)
        kilos_final.append(j)
    print('kilos final')
    print(kilos_final)
    print('')
    print('array kilos aba')
    print(array_kilos_aba)
    i=0

    k_aba=np.divide(array_kilos_aba,40)

    #### kilos en sacos
    kilos_total_sacos=np.divide(kilos_final,40)
    print('kilos total en sacos')
    print(kilos_total_sacos)
    #fin kilos en sacos
    
    kilos_total=np.zeros(len(kilos_final),dtype='<U50')
    for j in range(len(kilos_final)):
        #print('kilos final = ',kilos_final[i])
        kilos_total[i]=separador_miles(kilos_final[i])
        i=i+1
    i=0
    kilos_aba=np.zeros(len(array_kilos_aba),dtype='<U50')
    for j in range(len(array_kilos_aba)):
        kilos_aba[i]=separador_miles(array_kilos_aba[i])
        i=i+1
    
    # kilos en sacos a string con dos decimales######################
    k_t_sacos=np.zeros(len(kilos_total_sacos),dtype='<U50')          #
    i=0                                                              #
    for j in range(len(kilos_total_sacos)):                          #           
        k_t_sacos[i]=separador_miles(kilos_total_sacos[i])           #          
        i=i+1                                                        #     
    # fin kilos en sacos a string####################################

    # kilos en alimento sacos a string con dos decimales #############
    k_aba_final=np.zeros(len(k_aba),dtype='<U50')                    #
    i=0                                                              #
    for j in range(len(k_aba)):                                      #           
        k_aba_final[i]=separador_miles(k_aba[i])                     #          
        i=i+1                                                        #     
    # fin kilos aliemnto en sacos a string ###########################

    print('kilos total = ',kilos_total)
    print('kilos en sacos = ',k_t_sacos)
    

    
    print('--------------------------------')
    print('--------------------------------')
    print('--------------------------------')
    print('alerta inventario')
    alerta,porcentaje = alerta_inventario()
    print('desde planta aba emitimos alerta')
    print(alerta)

    print(array_kilos_aba)
    print(k_aba_final)
    print(porcentaje)

    
    # 
    #       Calcular dias de consumo segun formula de ponedora
    
    print('buscando formula //////////////////////')
    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM formula WHERE alimento = "PONEDORA 1 REF (52622)(2% PROD. A 60 SEM)" ')
    #cur.execute("CALL ver_precio(1)")
    
    data=cur.fetchall()
    formula=np.array(data)
    print(formula)
    print(len(formula))

    index_mp=np.array(bd_lista_materiaprima())

    print('index = ', index_mp)
    i=0
    buzon_mp=np.array([])
    buzon_matriz_mp=np.zeros((len(index_mp)),dtype='<U50')
    print(buzon_matriz_mp)
    print('kilos final',kilos_final[0])
    for j in index_mp :
        
        print(j[1])
        for k in formula:
            
            if j[1]==k[2]:
                p=k[3]
                #p=devolver_separador_miles(p)
                print('p = ',p)
                p1=kilos_final[i]/float(p)
                p1=p1/40
                p1=separador_miles(p1)
                #print(p1)
                buzon_matriz_mp[i]=p1
                #print(j[1], ' son iguales con i = ',i)
            #else:
            #    buzon_matriz_mp[i]='N/A'
        i=i+1

    print('buzon matriz materia prima')
    print(buzon_matriz_mp)
    print(kilos_final)
    print('')
    #buzon_mp_final=np.array((kilos_final/buzon_matriz_mp))
                             
    #print((kilos_final/buzon_matriz_mp)/40)
    print('')
    #print(buzon_mp_final)
    
    #</tr>
   
    ############  calcular costo de produccion de alimento  
    costo_p=[]
    costo_p.append(calcular_costo_produccion2())
    print(costo_p)
    costo_p_final=[]
    print('for de costo p')
    for j in costo_p:
        for k in j:
            print(k)
            costo_p_final.append(k)
    print('')
    print('')
    print('************************** FIN PLANTA ABA **************************************')
    print('')
    print('')

    print('array_alimento')
    print(array_alimento)
    print('')
    
    print('alimento_inv')
    print(alimento_inv)
    print('')
    print('array_kilos_aba')
    print(array_kilos_aba)
    print('')
    
    dias_p2=[] 
    dias_p2.append(dias_ponedora2())
    print(dias_p2)
    dias_p2_final=[]
    for j in dias_p2:
        for k in j:
           
            dias_p2_final.append(k)
    print(dias_p2_final)
    return render_template('planta_aba.html',
                           tabla1=tabla_1,
                           array_productos=array_productos,
                           productos_inv=productos_inv,
                           productos_suma=kilos_total,
                           alimento_inv=alimento_inv,
                           alimento_suma=kilos_aba,
                           alerta=alerta,
                           sacos_aba=k_aba_final,
                           porcentaje=porcentaje,
                           buzon_matriz_mp=buzon_matriz_mp,
                           costo_mp=costo_mp_string,
                           costo_p=costo_p_final,

                           dias_p2=dias_p2_final


                           )
 



@app.route('/imprimir_inv/<producto>/<kilos>/<costo>')
def imprimir_inv(producto,kilos,costo,matriz):
    print('')
    print('producto imprimir')
    print(producto)


    return 'construccion'





@app.route('/barra')
def barra():
    return render_template('barra.html')

@app.route('/t')
def tablero():
    return render_template('tablero.html')

@app.route('/panelgrafico')
def panelgrafico():
    return render_template('panelgrafico.html')

@app.route('/test2')
def test2():
    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tabla1 ORDER BY fecha ASC ')
    data=cur.fetchall()      
    #print("data")
    #print(data)
    #print("************")
    fechatemporal='0'
    a=0.0
    arrayfecha=[]
    arrayfechafinal=[] 
    arraymonto=[]
    arraymontofinal=[]
    indice_fecha=[]
    indice_temp="0"
    indice_n=0
    for j in data: # recorre las fechas y las guarda en array
        #print(j[3])
        arrayfecha.append(j[3])
        montox=devolver_separador_miles(j[6])
        montox=float(montox)
        arraymonto.append(montox)
       
        #print("arrayfecha = ",arrayfecha)
        #print("rraymonto = ",arraymonto)
        #print("montox = ", montox)
    variable_incremento=0
    print("longitud = ",len(arrayfecha)) 
    print("arrayfecha = ",arrayfecha) 
    for j in arrayfecha:
        print("var incremento = ",variable_incremento)
        print("arraymonto = ",arraymontofinal)        
        if j==fechatemporal: # fecha temporal es para guardar fecha anterior del array
            
            x=(arraymontofinal[variable_incremento-1]) # x es valor anterior del array
            #print("x i -1 = ", x)
            x=x+(arraymonto[variable_incremento]) # x es la suma del array anterior y el actual
            #print("x + montox = ", x)
            arraymontofinal[variable_incremento-1]=(x) # agregamos el array con el valor sumado
            #print("amfinal = ",arraymontofinal[variable_incremento-1])
            
        else:
            arraymontofinal.append((arraymonto[variable_incremento]))
            arrayfechafinal.append(j)
            variable_incremento=variable_incremento+1
        fechatemporal=j
        #variable_incremento=variable_incremento+1
        #print(j)
    
    for j in arrayfechafinal:  

        indice_fecha.append(str(indice_n))
        indice_n=indice_n+1
    arraymontofinal2=[]
    for j in arraymontofinal:
        arraymontofinal2.append(int(j))
    #print(arrayfecha)
    #print("fecha = ",arrayfechafinal)
    #print("monto = ",arraymontofinal)
    arrayfechafinal2=[]
    xa='0'
    za=0
    arrayfechafinal3=[]
    for j in arrayfechafinal:   
        xa=''         
        xa+=j[0]
        xa+=j[1]
        xa+=j[2]
        xa+=j[3]
        xa+=j[5]
        xa+=j[6]
        xa+=j[8]
        xa+=j[9]
        za=int(xa)
        arrayfechafinal2.append(xa)
        arrayfechafinal3.append(za)
        #print("arrayfechafinal2 = ",arrayfechafinal2)
        #print("arrayfechafinal3 = ",arrayfechafinal3)
    
    #print("arrayfechafinal2 = ",arrayfechafinal3)
    #print(indice_fecha)
    #print(arraymontofinal2)
   # # recorremos la columna MONTO 
    
    filename="src/static/js/datosgrafico.json"
    
    with open(filename,"w") as file:
        json.dump(arraymontofinal2,file)
    #print(archivo)

    with open(filename,"r+") as file:
        archivo=json.load(file)
       # archivo.append(xyz)
        file.seek(0)
        json.dump(archivo,file)
    #print(archivo)    



    filename="src/static/js/datosgraficox.json"
     
    with open(filename,"w") as file:
        json.dump(arrayfechafinal,file)
    #print(archivo)

    with open(filename,"r+") as file:
        archivo2=json.load(file)
       # archivo.append(xyz)
        file.seek(0)
        json.dump(archivo2,file)
    #print(archivo2)


     ###### entrar en egresos
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM egresos ORDER BY fecha ASC ')
    data=cur.fetchall()      
    #print("data")
    #print(data)
    #print("************")

    e_fechatemporal='0'
    a=0.0
    e_arrayfecha=[]
    e_arrayfechafinal=[] 
    e_arraymonto=[]
    e_arraymontofinal=[]
    e_indice_fecha=[]
    e_indice_temp="0"
    e_indice_n=0
    for j in data: # recorre las fechas y las guarda en array
        #print(j[3])
        e_arrayfecha.append(j[3])
        e_montox=devolver_separador_miles(j[4])
        e_montox=float(e_montox)
        e_arraymonto.append(e_montox)
       
        #print("arrayfecha = ",arrayfecha)
        #print("rraymonto = ",arraymonto)
        #print("montox = ", montox)
    e_variable_incremento=0

    for j in e_arrayfecha:        
        if j==e_fechatemporal: # fecha temporal es para guardar fecha anterior del array
            
            x=(e_arraymontofinal[e_variable_incremento-1]) # x es valor anterior del array
            #print("x i -1 = ", x)
            x=x+(e_arraymonto[e_variable_incremento]) # x es la suma del array anterior y el actual
            #print("x + montox = ", x)
            e_arraymontofinal[e_variable_incremento-1]=(x) # agregamos el array con el valor sumado
            #print("amfinal = ",arraymontofinal[variable_incremento-1])
            None
        else:
            e_arraymontofinal.append((e_arraymonto[e_variable_incremento]))
            e_arrayfechafinal.append(j)
        e_fechatemporal=j
        e_variable_incremento=e_variable_incremento+1
        #print(j)
    
    for j in e_arrayfechafinal:  

        e_indice_fecha.append(str(e_indice_n))
        e_indice_n=e_indice_n+1
    e_arraymontofinal2=[]
    for j in e_arraymontofinal:
        e_arraymontofinal2.append(int(j))
    #print(arrayfecha)
    #print("fecha = ",arrayfechafinal)
    #print("monto = ",arraymontofinal)
    e_arrayfechafinal2=[]
    e_xa='0'
    e_za=0
    e_arrayfechafinal3=[]
    for j in e_arrayfechafinal:   
        e_xa=''         
        e_xa+=j[0]
        e_xa+=j[1]
        e_xa+=j[2]
        e_xa+=j[3]
        e_xa+=j[5]
        e_xa+=j[6]
        e_xa+=j[8]
        e_xa+=j[9]
        e_za=int(xa)
        e_arrayfechafinal2.append(e_xa)
        e_arrayfechafinal3.append(e_za)

    print("fecha = ",arrayfechafinal3)
    print("monto = ",arraymontofinal)
    print("longitud = ", len(arrayfechafinal3))
    print("************************")
    
    print("fecha = ",e_arrayfechafinal3)
    print("monto = ",e_arraymontofinal)
    print("longitud e_ = ", len(e_arrayfechafinal3))

    
    



    return render_template('grafico.html',x=archivo2,y=archivo)


@app.route('/test')
def test():
    
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tabla1 ORDER BY fecha ASC ')
    data=cur.fetchall()      
    print("data")
    print(data)
    print("************")
    fechatemporal='0'
    a=0.0
    arrayfecha=[]
    arrayfechafinal=[] 
    arraymonto=[]
    arraymontofinal=[]
    indice_fecha=[]
    indice_temp="0"
    indice_n=0
    for j in data: # recorre las fechas y las guarda en array
        print(j[3])
        arrayfecha.append(j[3])
        montox=devolver_separador_miles(j[6])
        montox=float(montox)
        arraymonto.append(montox)
        print(arrayfecha)
        print(arraymonto)
        print("montox = ", montox)
    variable_incremento=0

    for j in arrayfecha:        
        if j==fechatemporal:
            
            x=(arraymontofinal[variable_incremento-1])
            print("x i -1 = ", x)
            x=x+(arraymonto[variable_incremento])
            print("x + montox = ", x)
            arraymontofinal[variable_incremento-1]=(x)
            print("amfinal = ",arraymontofinal[variable_incremento-1])
            None
        else:
            arraymontofinal.append((arraymonto[variable_incremento]))
            arrayfechafinal.append(j)
        fechatemporal=j
        variable_incremento=variable_incremento+1
        print(j)
    
    for j in arrayfechafinal:  

        indice_fecha.append(str(indice_n))
        indice_n=indice_n+1
    arraymontofinal2=[]
    for j in arraymontofinal:
        arraymontofinal2.append(int(j))
    print(arrayfecha)
    print(arrayfechafinal)
    print(arraymontofinal)
    print(indice_fecha)
    print(arraymontofinal2)
   # # recorremos la columna MONTO 
   
    filename="src/static/js/datosgrafico.json"
     
    with open(filename,"w") as file:
        json.dump(arraymontofinal2,file)
    #print(archivo)

    with open(filename,"r+") as file:
        archivo=json.load(file)
       # archivo.append(xyz)
        file.seek(0)
        json.dump(archivo,file)
    print(archivo)    



    filename="src/static/js/datosgraficox.json"
     
    with open(filename,"w") as file:
        json.dump(arrayfechafinal,file)
    #print(archivo)

    with open(filename,"r+") as file:
        archivo2=json.load(file)
       # archivo.append(xyz)
        file.seek(0)
        json.dump(archivo2,file)
    print(archivo2)


     ###### entrar en egresos
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM egresos ORDER BY fecha ASC ')
    data=cur.fetchall()      
    print("data")
    print(data)
    print("************")

    fechaegreso=[]
    arrayfechaegreso=[]
    fechaegresofinal=[]
    for j in data:
        fechaegreso.append(j[3])
        print(fechaegreso)
    fechaetemp='0'
    for j in fechaegreso:
        if j==fechaetemp:
            None
        else:
            fechaegresofinal.append(j)
        fechaetemp=j
        a=""
        for i in j:
            
            a+=j[0]
            a+=j[1]
            a+=j[2]
            a+=j[3]
            a+=j[5]
            a+=j[6]
            a+=j[8]
            a+=j[9]
            a+="-"
            print("a = ",a)
        
    print(fechaegresofinal)
    return render_template('grafico.html',x=archivo2,y=archivo)


@app.route('/caja',methods=['GET','POST'])
def caja():
    if request.method == 'POST':
        titulo=request.form['titulo']
        descripcion=request.form['descripcion']
        fecha=request.form['fecha']  
        monto=request.form['monto'] 
        if ((not titulo) or (not descripcion) or (not fecha) or (not monto)): ##### verifica que todos los campos esten llenos     
            print('debe introducir todos los campos') 
            return redirect(url_for('caja'))

        else:
            monto=float(monto) # monoto como float
            monto=separador_miles(monto)
           # monto="{:.2f}".format(monto)  # formato de 2 decimales
            #monto=montodec
            #print('monto separador = ',montodec)

            
            
            monto=str(monto)  # devolvemos a string      
            cur=mysql.connection.cursor() 
            cur.execute('INSERT INTO egresos (titulo,descripcion,fecha,monto) VALUES(%s,%s,%s,%s)',
                (titulo,descripcion,fecha,monto))
            mysql.connection.commit()
            print('GUARDADOOOOOOO')

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tabla1')
    data=cur.fetchall()      
    caja=0.0
    
    a=0.0   
   # # recorremos la columna ABONO
    for j in data:  
        #abono=j[8]
        abono=devolver_separador_miles(j[8]) 
        abono=float(abono)
        
        caja=caja+abono  
    caja2=caja   
    
    #caja="{:.2f}".format(caja)   
    caja=separador_miles(caja)
   
    caja=str(caja)
    #print('Caja = ',caja)
    #adec="{:,.2f}".format(a).replace(",","x").replace(".",",").replace("x",".")
    a="{:.2f}".format(a)
    #a=adec
    a=str(a)
    #print('aaaaaaaaaaaa = ',a)   
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM egresos ORDER BY id DESC')
    data=cur.fetchall() 
    gastos='0.0' 
    gastos2=0.0
#######
    for j in data:  
        gastos=j[4]
        gastos=devolver_separador_miles(gastos)
        gastos=float(gastos)
        gastos2=gastos2+gastos

    #print('Suma de Gastos = ',gastos2)  
    gastos=gastos2  
    gastos2=caja2-gastos2  
   # print('gastos = ',gastos) 
    #gastos2="{:.2f}".format(gastos2)
    #gastos2=str(gastos2)
    #gastos="{:.2f}".format(gastos)
    #gastos=str(gastos)
    #print('gastos = ',gastos2) 
    gastos=separador_miles(gastos)
    gastos2=separador_miles(gastos2)
    
   
    return render_template('caja.html',gastos=gastos,gastos2=gastos2,caja=caja,tabla1=data)


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
        print('dataaaaaaa ',data)
        print('>>>>>>>>>>>>>>>>>>> factura >>>>>>>>>>>>>>><')
        print(data[:1])
        
        total_abono=0.0
        for j in data:
            cliente=j[2]
            saldo=j[6]
            factura=j[1]
            abono2=j[5]
            abono2=devolver_separador_miles(abono2)
            abono2=float(abono2)
            total_abono=total_abono + abono2
        print("saldoooo == ", saldo)
        saldo=devolver_separador_miles(saldo)
        saldo=float(saldo)
        abono=float(abono)
        total_abono=total_abono+abono
        saldo=saldo-abono
        #saldo="{:.2f}".format(saldo)
        #abono="{:.2f}".format(abono)        
        saldo=separador_miles(saldo)
        abono=separador_miles(abono)
        saldo=str(saldo)
        abono=str(abono)

        monto=saldo
        #total_abono="{:.2f}".format(total_abono)
        total_abono=separador_miles(total_abono)
        print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        cur=mysql.connection.cursor()            
        cur.execute('INSERT INTO ' +cliente2+ ' (factura,cliente,fecha,monto,abono,saldo) VALUES(%s,%s,%s,%s,%s,%s)',
        (factura2,cliente,fecha,monto,abono,saldo))
        mysql.connection.commit()


        cur=mysql.connection.cursor()    
        cur.execute(f"SELECT * FROM tabla1 WHERE factura = {factura}")
        data=cur.fetchall()
        print('vvvvvvvvvvvvvvvvvvvvvvvv')
        print(data)
        print('vvvvvvvvvvvvvvvvvvvvvvvvvv')
        cur=mysql.connection.cursor()
        cliente=cliente.upper() # transformamos a mayusculas
        cur.execute("""
            UPDATE tabla1
            SET abono=%s,
                saldo=%s
            WHERE factura = %s
        """,(total_abono,saldo,factura))
        mysql.connection.commit()        
        
    return redirect(url_for('relacion_factura_cliente',factura=factura2))



@app.route('/abono/factura/<factura>/<cliente2>')
def abono_factura(factura,cliente2):  
    print('factura =========> ',factura)
    print('Cliente2 =========> ',cliente2)
    cur=mysql.connection.cursor()    
    cur.execute(f"SELECT * FROM " +cliente2+ f" WHERE factura = {factura}")
    data=cur.fetchall()
    print('Tabla de Facturaaaaaaaaaa = ',data)
    for j in data:
        debe=j[6]
    print('debe ==> ',debe)
    return render_template('abono-factura.html',cliente2=cliente2,factura2=factura,debe=debe)

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

######### facturas vencidas
@app.route('/facturas_vencidas')
def facturas_vencidas():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tabla1')
    data=cur.fetchall()      
    hoy = datetime.now()
    hoy=str(hoy)
    hoy=hoy[:11]
    hoy=hoy.strip()
    hoy=datetime.strptime(hoy, "%Y-%m-%d")
    #hoy=str(hoy)
    #hoy=hoy[:11]
    fact_venc=[]
    fact_sin_pagar=[]
    j1=[]
    j2=[]
    j3=[]
    j4=[]
    #j8=[]
    j8=np.array([])
    jx=np.array([])
    #j2=np.array([])
    n_fact_venc=0
    a=0.0   
    facturado=0.0
   # # recorremos la columna MONTO
    for j in data:  
        print(j[6])
        saldo=j[9]
        saldo=devolver_separador_miles(saldo)
        saldo=float(saldo)
        if saldo == 0.00:
            pass
        else:            
            fact_sin_pagar.append(j)
            fecha=j[5] 
            fecha=str(fecha)    
            fecha=fecha.strip()
            fecha=datetime.strptime(fecha, "%Y-%m-%d")
            dias=(hoy-fecha).days
            
            
            if dias >=0:
                n_fact_venc=n_fact_venc + 1
                print("j9=====",j[9])
                b=devolver_separador_miles(j[9])
                b=float(b)
                a=b+a
                np.append(jx,j,axis=0)
                j2.append(dias)
                j1.append(dias)                
                fact_venc.append(j)
                # tomar valor del monto facturado
                facturado_t=devolver_separador_miles(j[6])
                facturado_t=float(facturado_t)
                facturado=facturado + facturado_t
                
    #a="{:.2f}".format(a)
    
    
    #np.vsplit(j2)
    #
    array_vencida=[]
    abono_vencido_s=""
    abono_vencido_t=0.0
    abono_vencido=0.0
    for j in fact_venc:
        array_vencida.append(j[8])
        abono_vencido_s=j[8]
        abono_vencido_s=devolver_separador_miles(abono_vencido_s)
        abono_vencido_t=float(abono_vencido_s)
        abono_vencido=abono_vencido+abono_vencido_t
    print("ABONO VENCIDO = ",abono_vencido)
    print("array_vencida = ",array_vencida)
    #abono_vencido_s=str(abono_vencido)
    abono_vencido_s=separador_miles(abono_vencido)    
    print(abono_vencido_s)
    j2=np.transpose(j2)
   
    j4.append(fact_venc)
   
    por_cobrar=a
    a=separador_miles(a)
    a=str(a)
    print('por_cobrar = ',por_cobrar)    
    print("facturado ",facturado)
    print("abono vencido ",abono_vencido) 
    porcentaje_abono=(abono_vencido*100)/facturado
    porcentaje_por_cobrar=(por_cobrar*100)/facturado

    abono_int=int(porcentaje_abono)
    cobrar_int=int(porcentaje_por_cobrar)

    barra_cobrar=calcular_porcentaje(cobrar_int)
    barra_abono=calcular_porcentaje(abono_int)

    print("vc = ",barra_cobrar)
    print("va = ",barra_abono)
    porcentaje_abono="{:.1f}".format(porcentaje_abono)
    porcentaje_por_cobrar="{:.1f}".format(porcentaje_por_cobrar)
    
    print("porcentaje abono  ",porcentaje_abono)
    print("porcentaje cobrar ",porcentaje_por_cobrar)
    print("n_fact_venc = ",n_fact_venc)
    return render_template('facturas_vencidas.html',
                           tabla1=fact_venc,
                           dato2=a,
                           dia=j2,
                           abono_vencido=abono_vencido_s,
                           porcentaje_abono=porcentaje_abono,
                           barra_abono=barra_abono,
                           porcentaje_por_cobrar=porcentaje_por_cobrar,
                           barra_cobrar=barra_cobrar,
                           n_fact_venc=n_fact_venc)

# Funcion Calcular Porcentaje de ProgressBar
def calcular_porcentaje(valor):
    porcentaje=0
    if valor==0:
        porcentaje=0
        return porcentaje
    elif valor >0 and valor <= 10:
        porcentaje=10
        return porcentaje
    elif valor >10 and valor <= 20:
        porcentaje=20
        return porcentaje
    elif valor >20 and valor <= 30:
        porcentaje=30
        return porcentaje
    elif valor >30 and valor <= 40:
        porcentaje=40
        return porcentaje
    elif valor >40 and valor <= 50:
        porcentaje=50
        return porcentaje
    elif valor >50 and valor <= 60:
        porcentaje=60
        return porcentaje
    elif valor >60 and valor <= 70:
        porcentaje=70
        return porcentaje
    elif valor >70 and valor <= 80:
        porcentaje=80
        return porcentaje
    elif valor >80 and valor <= 90:
        porcentaje=90
        return porcentaje
    elif valor >90 and valor <= 95:
        porcentaje=95
        return porcentaje
    elif valor >95 :
        porcentaje=100
        return porcentaje
#
################ Facturas por Cobrar
@app.route('/factcobrar')
def fact_x_cobrar():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tabla1')
    data=cur.fetchall()      
    print('######################################################')
    print(data)
    print('######################################################')
    hoy = datetime.now()
    hoy=str(hoy)
    hoy=hoy[:11]
    hoy=hoy.strip()
    print('hoy 1 =',hoy)
    hoy=datetime.strptime(hoy, "%Y-%m-%d")    
    fact_venc=[]
    fact_sin_pagar=[]
    a=0.0 
    monto_abonado=0.0  
   # # recorremos la columna MONTO
    for j in data:  
        print(j[6])
        
        saldo=j[9]
        print('saldo ====>',saldo)
        saldo=devolver_separador_miles(saldo)
        saldo=float(saldo)
        if saldo == 0.00:
            pass
        else:
            b=devolver_separador_miles(j[9])
            
            b=float(b)
            a=b+a
            #a=float(j[9])+a  
            print('a = ',a)
            fact_sin_pagar.append(j)

            monto_abonado_t=devolver_separador_miles(j[8])
            monto_abonado_t=float(monto_abonado_t)
            monto_abonado=monto_abonado + monto_abonado_t

        fecha=j[5]         
   # a="{:.2f}".format(a)
    monto_cobrar=a
    a=separador_miles(a)
    a=str(a)
    print('aaaaaaaaaaaa = ',a)    
    print("monto_abonado = ", monto_abonado)
    porcentaje_monto_abonado=(monto_abonado*100)/monto_cobrar
    print(porcentaje_monto_abonado) 
    progressbar_abonado=int(porcentaje_monto_abonado)
    progressbar_abonado=calcular_porcentaje(progressbar_abonado)
    print(progressbar_abonado)
    porc_m_abonado="{:.1f}".format(porcentaje_monto_abonado)
    print(porc_m_abonado)
    monto_abonado=separador_miles(monto_abonado)
    return render_template('factura_por_cobrar.html',
                           tabla1=fact_sin_pagar,
                           dato2=a,
                           progressbar_abonado=progressbar_abonado,
                           porc_m_abonado=porc_m_abonado,
                           monto_abonado=monto_abonado)
    

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

# funcion ventas
@app.route('/ventas')
def ventas():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tabla1 ORDER BY fecha DESC')
    data=cur.fetchall()      
    
    a=0.0 
   # # recorremos la columna MONTO
    for j in data:  
        print(j[6])
        
        #a=devolver_separador_miles(float(j[6])) +a 
        
        b=devolver_separador_miles((j[6]))
        b=float(b)
        a=a+b 
             
        print('a = ',a)
    
    #a="{:.2f}".format(a)
    memoria_ventas=int(a)
    a=separador_miles(a)
    a=str(a)
    print('aaaaaaaaaaaa = ',a)  
    abono=0
    for j in data:  
        print(j[8])
        
        #a=devolver_separador_miles(float(j[6])) +a 
        
        b=devolver_separador_miles((j[8]))
        b=float(b)
        abono=abono+b 
             
        print('abono = ',abono)
    
    #a="{:.2f}".format(a)
    memoria_abono=abono
    abono=separador_miles(abono)
    abono=str(abono)
    print('abono = ',abono)

    saldo=0
    for j in data:  
        print(j[9])
        
        #a=devolver_separador_miles(float(j[6])) +a 
        
        b=devolver_separador_miles((j[9]))
        b=float(b)
        saldo=saldo+b 
             
        print('saldoo = ',saldo)
    
    #a="{:.2f}".format(a)
    memoria_saldo=int(saldo)
    saldo=separador_miles(saldo)
    saldo=str(saldo)
    print('saldo = ',saldo) 
    p_x_cobrar=  (memoria_saldo*100)/memoria_ventas 
    #p_x_cobrar=100-p_x_cobrar
    p_x_cobrar_f=p_x_cobrar
    p_x_cobrar_f="{:.1f}".format(p_x_cobrar_f)
    p_x_cobrar = int(p_x_cobrar)
    x_cobrar_final=0
    if p_x_cobrar==0:
        x_cobrar_final=0
    elif p_x_cobrar >0 and p_x_cobrar <= 10:
        x_cobrar_final=10
    elif p_x_cobrar >10 and p_x_cobrar <= 20:
        x_cobrar_final=20
    elif p_x_cobrar >20 and p_x_cobrar <= 30:
        x_cobrar_final=30
    elif p_x_cobrar >30 and p_x_cobrar <= 40:
        x_cobrar_final=40
    elif p_x_cobrar >40 and p_x_cobrar <= 50:
        x_cobrar_final=50
    elif p_x_cobrar >50 and p_x_cobrar <= 60:
        x_cobrar_final=60
    elif p_x_cobrar >60 and p_x_cobrar <= 70:
        x_cobrar_final=70
    elif p_x_cobrar >70 and p_x_cobrar <= 80:
        x_cobrar_final=80
    elif p_x_cobrar >80 and p_x_cobrar <= 90:
        x_cobrar_final=90
    elif p_x_cobrar >90 and p_x_cobrar <= 95:
        x_cobrar_final=95
    elif p_x_cobrar >95 :
        x_cobrar_final=100

    #"{:.2f}".format(a)
    print("p_x_cobrar = ",int(p_x_cobrar))
    p_x_cobrar2=str(p_x_cobrar)
    x_cobrar="width:"
    x_cobrar+=p_x_cobrar2
    x_cobrar+="%"

    x_abono_final=0
    memoria_abono=(memoria_abono*100)/memoria_ventas
    #memoria_abono=100-memoria_abono
    memoria_abono2=int(memoria_abono) 
    memoria_abono=float(memoria_abono)
    
    memoria_abono="{:.1f}".format(memoria_abono)
    
    
    #memoria_abono=int(memoria_abono)
    #print("memoria_abono = ",int(memoria_abono))
    print("memoria_abono = ",memoria_abono)
    print("p_x_cobrar_f = ",p_x_cobrar_f)
    if memoria_abono2==0:
        x_abono_final=0
    elif memoria_abono2 >0 and memoria_abono2 <= 10:
        x_abono_final=10
    elif memoria_abono2 >10 and memoria_abono2 <= 20:
        x_abono_final=20
    elif memoria_abono2 >20 and memoria_abono2 <= 30:
        x_abono_final=30
    elif memoria_abono2 >30 and memoria_abono2 <= 40:
        x_abono_final=40
    elif memoria_abono2 >40 and memoria_abono2 <= 50:
        x_abono_final=50
    elif memoria_abono2 >50 and memoria_abono2 <= 60:
        x_abono_final=60
    elif memoria_abono2 >60 and memoria_abono2 <= 70:
        x_abono_final=70
    elif memoria_abono2 >70 and memoria_abono2 <= 80:
        x_abono_final=80
    elif memoria_abono2 >80 and memoria_abono2 <= 90:
        x_abono_final=90
    elif memoria_abono2 >90 and memoria_abono2 <= 95:
        x_abono_final=95
    elif memoria_abono2 >95 :
        x_abono_final=100
    
    ##### tomar cuantas facturas vencidas existen 
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tabla1')
    data=cur.fetchall()      
    
    cantidad_vencidas=0
    hoy = datetime.now()
    hoy=str(hoy)
   
    hoy=hoy[:11]
    
    hoy=hoy.strip()
    
    hoy=datetime.strptime(hoy, "%Y-%m-%d")
    #hoy=str(hoy)
    #hoy=hoy[:11]
    fact_venc=[]
    fact_sin_pagar=[]
    j1=[]
    j2=[]
    j3=[]
    j4=[]
    #j8=[]
    j8=np.array([])
    jx=np.array([])
    #j2=np.array([])

   
   # # recorremos la columna MONTO
    for j in data:  
        
        
        saldo2=j[9]
       
        saldo2=devolver_separador_miles(saldo2)
        saldo2=float(saldo2)
        if saldo2 == 0.00:
            pass
        else:            
            fact_sin_pagar.append(j)
            fecha=j[5] 
            fecha=str(fecha)    
                  
            fecha=fecha.strip()
            
            fecha=datetime.strptime(fecha, "%Y-%m-%d")
            
            dias=(hoy-fecha).days
            
            
            if dias >=0:
                cantidad_vencidas=cantidad_vencidas+1
                
    print("cantidad vencidas = ",cantidad_vencidas)  
    return render_template('ventas.html',tabla1=data,dato2=a,abono=abono,saldo=saldo,x_cobrar_final=x_cobrar_final,p_x_cobrar=p_x_cobrar_f,x_abono_final=x_abono_final,memoria_abono=memoria_abono,cantidad_vencidas=cantidad_vencidas)








@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql,id)

@app.route('/salir')
def salir():
    print('cerrando sesion')

    if current_user.nivel != 'admin':
        id_user=current_user.id
        cur=mysql.connection.cursor()
        cur.execute("""
        UPDATE user 
        SET permiso=%s                           
        WHERE id = %s
        """,('0',id_user))
        mysql.connection.commit()
    logout_user()
    return redirect(url_for('login'))

# ruta principal
@app.route('/',methods=['GET', 'POST'])
def login():
    
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        print('username = ',username)
        print('password = ',password)
        user=User(0,username,password)
        logged_user=ModelUser.login(mysql,user)
        print('logged user')
        print(logged_user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                print('entro')
                print(login_user(logged_user))
                return redirect(url_for('planta_aba'))
            else:
                flash('USUARIO o PASSWORD Incorrecto','home')
                return render_template("home.html")        
        else:
            flash('USUARIO o PASSWORD Incorrecto','home')
            return render_template("home.html")
        #return render_template("planta_aba.html")
        flash('USUARIO o PASSWORD Incorrecto','home')
        return render_template("home.html")
    else:
        return render_template("home.html")
    
    

@app.route('/about', strict_slashes=False)
def about():
    print('password')
    print(current_user.fullname)
    

    return render_template("about.html")
def run_prog():
    print("runnnnnnn")
########################################
def separador_miles(monto):
     monto="{:,.2f}".format(monto).replace(",","x").replace(".",",").replace("x",".")
     #print('monto separador de miles = ',monto)
     return monto

def devolver_separador_miles(monto):
     monto=format(monto).replace(".","x").replace(",",".").replace("x","")
     #print('monto separador de miles devuelto= ',monto)
     return monto
#########################################
def calcular_inventario():
    

    

    #return redirect(url_for('ordenes_produccion'))   

    ##############

    # materia prima
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_materiaprima=[] 
    for j in data:
        array_materiaprima.append((j))
    
    # fin materia prima
    
    # formula
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formula ORDER BY alimento ')
    data=cur.fetchall() 
    array_formula=[] 
    for j in data:
        array_formula.append((j))
    
    
    # fin formula

    
    # tipos de alimento

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_tipo_alimento=[] 
    for j in data:
        array_tipo_alimento.append((j))
    
    

    # fin tipos de alimentos

    

    # orden produccion
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM orden_produccion ORDER BY alimento ')
    data=cur.fetchall() 
    array_orden_produccion=[] 
    for j in data:
        array_orden_produccion.append((j))
    
    

    # fin orden produccion

    # inventario aba materia prima
     
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_aba ORDER BY producto ')
    data=cur.fetchall() 
    array_inventario=[] 
    for j in data:
        array_inventario.append((j))
    
    

    # fin inventario aba materia prima


    #
    # agrupar y sumar todas las materias primas del inventario
    #
    i=0
    #inventario_productos=[]
    inventario_kilos=np.zeros(len(array_materiaprima),dtype='<U50' )
    inventario_kilos_f=np.zeros(len(array_materiaprima) )
    
    suma=0.0
    for j in array_materiaprima:
        suma=0.0
        for k in array_inventario:

            if j[1]==k[1]:

                suma_t=k[3]
                suma_t=devolver_separador_miles(suma_t)
                suma_t=float(suma_t)
                suma=suma+suma_t
                inventario_kilos[i]=suma
                inventario_kilos_f[i]=suma
                
                
        i=i+1    
                
    

    #
    # fin de la suma de todas las materias primas del inventario
    # donde inventario_kilos[] es la suma de kilos de las materias primas por tipo
    #

    # 
    # calcular kilos de materia prima utilizado en cada bache segun la formula
    # 

    
    suma=0.0
    array_baches=np.zeros(len(array_tipo_alimento),dtype='<U50' )
    array_baches_float=np.zeros(len(array_tipo_alimento) )
    
    i=0
    for j in array_tipo_alimento:
        suma=0.0
        for k in array_orden_produccion:

            if j[1]==k[1]:
                if k[5]=='producido':
                    suma_t=k[4]
                    suma_t=devolver_separador_miles(suma_t)
                    suma_t=float(suma_t)
                    suma=suma+suma_t
                    array_baches[i]=suma
                    array_baches_float[i]=suma
        i=i+1
        print('baches = ', array_baches)
    i =0
    q=0
    y=0
    array_kilos_np =np.zeros((len(array_materiaprima),len(array_tipo_alimento)) )#,dtype='<U50'
    for j in array_tipo_alimento:
        

        for k in array_formula:

            if j[1] == k[1]:
                y=0
                for h in array_materiaprima:
                    
                    if h[1]==k[2]:
                        #print(k[2],' ', k[1],' ',j[1], '    y= ',y)
                        array_kilos_np[y,q]=k[3]
                    y=y+1
                #print('j = ',j)
                #print('k = ',k , '  i = ', i , '  q = ',q)
        q=q+1
                
                
    
    i=i+1
    #
    # fin calcula de kilos de materia prima utilizado en cada bache segun la formula
    #donde array_kilos_np es igual a una matriz con kilos y materia prima
    i=0
    q=0
    kilos_t =np.zeros((len(array_materiaprima),len(array_tipo_alimento)) )
    for j in array_tipo_alimento:
        q=0
        for k in array_materiaprima:
            kilos_t=array_kilos_np
            array_kilos_np[q,i]=np.multiply(array_kilos_np[q,i], array_baches_float[i] )
            
            q=q+1 
            
        i=i+1 
    print(array_kilos_np)  
    print(inventario_kilos)  

    #kilos_t =np.zeros((len(array_materiaprima),len(array_tipo_alimento)) )
    a = np.zeros((len(array_tipo_alimento),len(array_materiaprima)) )
    s = np.sum(array_kilos_np, axis=1)
    alimento_final=np.sum(array_kilos_np,axis=0)
    print(alimento_final)
    ##############
    print(len(inventario_kilos), ' ',len(s))

    #inventario_kilos =  np.asarray(inventario_kilos, dtype=float)
    inventario_final=inventario_kilos_f-s
    print('##############')
    print('##############')
    print('##############')
    print(alimento_final)
    print('##############')
    print('##############')
    print('##############')
    print(inventario_final)
    
    return(inventario_final,alimento_final)






def alerta_inventario():
    print('alerta')
    array_materiaprima=[]
    inventario2,alimento=calcular_inventario()

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto')
    data=cur.fetchall()
    i_mp=[]
    inventario=[]
    for j in data:
        a=j[3]
        a=float(a)
        i_mp.append(a)
        inventario.append(a)

    print('')
    print('')
    print('inventario de materia prima desde costo_mp')
    print(i_mp)
    print('')
    print('')
    print('')
    print('')
    print('')
    print('')
    print('-------- inventario -------')
    print(inventario)
    print('---------------------------')
    print('-------- alimento -------')
    print(alimento)
    print('---------------------------')
    materiaprima=bd_lista_materiaprima()
    print ('lista materia prima ',materiaprima)

    print ('lista materia prima len ',len(materiaprima))
    mp=np.zeros(len(materiaprima))
    r_mp=np.zeros(len(materiaprima))
    i=0
    for j in materiaprima:
        mp[i]=j[2]
        i=i+1
    #r_mp=inventario-mp
    print('mp = ',mp) 
    print('r_mp = ',r_mp)   
    #</tr>
    condiciones=[(inventario > mp),(inventario <= mp)]
    
    resultados=['normal','alerta']
    
    s=np.select(condiciones,resultados)
    print('s = ',s)

    #porcentaje=(inventario*50)/mp
    porcentaje=np.multiply(inventario,50)
    print('')
    print('mulplicacion de porct * 50 = ',porcentaje)
    porcentaje=np.divide(porcentaje,mp)
    print('')
    print('division de porct / mp = ',porcentaje)
    cond_porcentaje=[(porcentaje>=100),((porcentaje>=0) & (porcentaje<=100)),(porcentaje<0)]
    res_porcentaje=[100,porcentaje,0]
    p_final=np.select(cond_porcentaje,res_porcentaje)
    print('++++++++++++++++++++++++++++++')
    print('')
    print(p_final)
    print('')
    print(porcentaje)
    
    print('++++++++++++++++++++++++++++++')
    print('')
    return  (s,p_final)


def bd_proveedor():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM proveedores ORDER BY proveedor ')
    data=cur.fetchall() 
    
    return(data)

def bd_lista_materiaprima():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    
    return(data)

def bd_formula():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formula ORDER BY alimento ')
    data=cur.fetchall()
    return data

def bd_tipo_alimento():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall()
    return data

def bd_orden_produccion():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM orden_produccion ORDER BY alimento ')
    data=cur.fetchall() 
    return data

def bd_inventario_aba():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_aba ORDER BY producto ')
    data=cur.fetchall() 
    return data
######################################

######################################
     
@app.route('/confirmacion_final_planta_aba/inventario/delete/<string:id>/<string:c_bd>/<string:k_bd>')
def confirmacion_final_delete_inventario_general(id,c_bd,k_bd):


    print('los datos son id = ',id, ' k_bd = ',k_bd, ' c_bd = ',c_bd )

    #########
    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM inventario_aba WHERE id = {id}')
    data=cur.fetchall()
    print('data de inventario aba')
    print(data)
    for j in data:
        producto=j[1]

    


    ###########

    producto=str(producto)

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM costo_materiaprima WHERE producto = "{producto}"')
    data=cur.fetchall() 
    
    
    for j in data:
        costo_ci=(float(j[2]))
        producto_ci=(j[1])
        kilos_ci=(float(j[3]))
    print('')
    print('')
    print('')
    print('LISTA OBTENIDA DE LA BASE DE DATOS COSTO INVENTARIO')
    print(costo_ci)
    print(producto_ci)
    print(kilos_ci)
    print('')
    print('')
    print('')

    k_bd=devolver_separador_miles(k_bd)
    c_bd=devolver_separador_miles(c_bd)
    k_bd=float(k_bd)
    c_bd=float(c_bd)

    cu_bd=c_bd/k_bd
    nuevo_ci= costo_ci*kilos_ci
    nuevo_costo=abs(c_bd-nuevo_ci)
    print('')
    print('')
    print('NUEVO COSTO')
    print(nuevo_costo)

    nuevo_kilos=abs(k_bd-kilos_ci)
    print('')
    print('NUEVOS KILOS')
    print(nuevo_kilos)

    if nuevo_costo==0 and nuevo_kilos==0:
        costo_final=0.0

    else:
        costo_final=nuevo_costo/nuevo_kilos
    
    
    print('')
    print('COSTO FINAL')
    print(costo_final)
    print('')
    print('')
    print('')
    print('')
    print('')

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM inventario_aba WHERE id = {id}')
    data=cur.fetchall()
    print('datos desde inventario aba')
    print(data)
    for j in data:
        fact=j[9]
    print('factura = ',fact)
    factura='x'+fact

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM compras_materiaprima WHERE factura = {fact} ')
    data=cur.fetchall()
    print('la factura es')
    print(data)
    for j in data:
        abono_fact=j[9]
    
    print('abono = ',abono_fact)
    abono=devolver_separador_miles(abono_fact)
    abono=float(abono)
    abono_existe=0
    if abono > 0:
        abono_existe=1
    print('abono existe = ',abono_existe)

    



    
    cur=mysql.connection.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {factura}')
    mysql.connection.commit()
    #IF NOT EXISTS
    #DROP TABLE `f100`;

    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE costo_materiaprima
        SET costo=%s,
            kilos=%s                
        WHERE producto = %s
    """,(costo_final,nuevo_kilos,producto))
    mysql.connection.commit()







    cur=mysql.connection.cursor()
    cur.execute(f"DELETE FROM inventario_aba WHERE id = '{id}'".format(id))
    mysql.connection.commit()
    kilos_ci=separador_miles(kilos_ci)
#
    flash(f"{kilos_ci} Kg de {producto_ci} ha sido borrado del inventario junto con la factura Nº {fact}",'borrar_inventario_mp')

    return 'construccion' 

######## el original   
#@app.route('/planta_aba/inventario/delete/<string:id>/<string:c_bd>/<string:k_bd>/<string:producto>')
@app.route('/planta_aba/inventario/delete/<string:id>/<string:c_bd>/<string:k_bd>')
def delete_inventario_general(id,c_bd,k_bd):


    print('los datos son id = ',id, ' k_bd = ',k_bd, ' c_bd = ',c_bd )

    #########
    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM inventario_aba WHERE id = {id}')
    data=cur.fetchall()
    print('data de inventario aba')
    print(data)
    for j in data:
        producto=j[1]

    


    ###########

    producto=str(producto)

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM costo_materiaprima WHERE producto = "{producto}"')
    data=cur.fetchall() 
    
    
    for j in data:
        costo_ci=(float(j[2]))
        producto_ci=(j[1])
        kilos_ci=(float(j[3]))
    print('')
    print('')
    print('')
    print('LISTA OBTENIDA DE LA BASE DE DATOS COSTO INVENTARIO')
    print(costo_ci)
    print(producto_ci)
    print(kilos_ci)
    print('')
    print('')
    print('')

    k_bd=devolver_separador_miles(k_bd)
    c_bd=devolver_separador_miles(c_bd)
    k_bd=float(k_bd)
    c_bd=float(c_bd)

    cu_bd=c_bd/k_bd
    nuevo_ci= costo_ci*kilos_ci
    nuevo_costo=abs(c_bd-nuevo_ci)
    print('')
    print('')
    print('NUEVO COSTO')
    print(nuevo_costo)

    nuevo_kilos=abs(k_bd-kilos_ci)
    print('')
    print('NUEVOS KILOS')
    print(nuevo_kilos)

    if nuevo_costo==0 and nuevo_kilos==0:
        costo_final=0.0

    else:
        costo_final=nuevo_costo/nuevo_kilos
    
    
    print('')
    print('COSTO FINAL')
    print(costo_final)
    print('')
    print('')
    print('')
    print('')
    print('')

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM inventario_aba WHERE id = {id}')
    data=cur.fetchall()
    print('datos desde inventario aba')
    print(data)
    for j in data:
        fact=j[9]
    print('factura = ',fact)
    factura='x'+fact

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM compras_materiaprima WHERE factura = {fact} ')
    data=cur.fetchall()
    print('la factura es')
    print(data)
    for j in data:
        abono_fact=j[9]
    
    print('abono = ',abono_fact)
    abono=devolver_separador_miles(abono_fact)
    abono=float(abono)
    abono_existe=0
    if abono > 0:
        abono_existe=1
    print('abono existe = ',abono_existe)

    if abono_existe==1:
        print('no se puede borrar porque la factura tiene abonos y existe relacion de pagos')
        return render_template('notificacion_borrar.html',
                               factura=fact,
                               abono=abono_fact,
                               id=id,
                               k_bd=k_bd,
                               c_bd=c_bd,
                               
                               )



    
    cur=mysql.connection.cursor()
    cur.execute(f'DROP TABLE IF EXISTS {factura}')
    mysql.connection.commit()
    #IF NOT EXISTS
    #DROP TABLE `f100`;

    cur=mysql.connection.cursor()
    cur.execute("""
        UPDATE costo_materiaprima
        SET costo=%s,
            kilos=%s                
        WHERE producto = %s
    """,(costo_final,nuevo_kilos,producto))
    mysql.connection.commit()
    cur=mysql.connection.cursor()
    cur.execute(f"DELETE FROM inventario_aba WHERE id = '{id}'".format(id))
    mysql.connection.commit()
    kilos_ci=separador_miles(kilos_ci)
#
    flash(f"{kilos_ci} Kg de {producto_ci} ha sido borrado del inventario junto con la factura Nº {fact}",'borrar_inventario_mp')

    #return 'construccion' 
    return redirect(url_for('planta_aba'))  
   
def calcular_costo_produccion():
    print('')
    print('')
    print('')
    print('***************************************************')
    print('INICIO DE CALCULAR PRODUCCION')
    print('')
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_alimento=[]
    for j in data:
        array_alimento.append((j[1]))

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formula ORDER BY alimento ')
    data=cur.fetchall() 
    print(data)
    array_formula_alimento=[]
    array_formula_materia=[]
    array_formula_cantidad=[]
    
    for j in data:
        array_formula_alimento.append((j[1]))
        array_formula_materia.append((j[2]))
        array_formula_cantidad.append((j[3]))
    print('array formula alimento')
    print(array_formula_alimento)
    print('')
    print('array formula materiprima')
    print(array_formula_materia)
    print('')
    print('array formula cantidad')
    print(array_formula_cantidad)

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_materiaprima=[] 
    for j in data:
        array_materiaprima.append((j[1]))

    # fin rutina buscar lista_materiaprima

    print('')
    print('alimentos en bd tipo alimento',array_alimento)
    print('')
    print('tipos de alimentos en bd de formula',array_formula_alimento)
    print('')
    print('tipos de materia en bd de formula',array_formula_materia)
    print('')
    print('cantidad materia en bd de formula',array_formula_cantidad)
    print('')
    print('tipos de materia prima',array_materiaprima)

    matriz=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50' )
    matriz_kilos=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50' )
    print(matriz)
    print(matriz.shape)
    print('matriz_kilos = ',matriz_kilos)


    print(matriz.shape)
    longitud_matriz=0
    for j in matriz.shape:
        print(j)

    longitud_matriz=len(array_materiaprima)
    print('longitud matriz = ', longitud_matriz)
    i=0

    array_temporal=[]
    
    array_kilos_temporal=[]
    array_alimento_utilizado=[]
    array_materia_utizado=[]
    array_cantidad_utizado=[]
    array_validacion=[]
    i=0
    z=0
    cont=0
    r=0
    validacion=0
    for j in array_alimento:
        validacion=0
        z=0
        try:
            cur=mysql.connection.cursor()
            cur.execute(f"SELECT * FROM formula WHERE alimento = '{j}'") 
            alim=j
            data=cur.fetchall() 
            print('data = ',data)
            validacion=0
            for k in data:
                
                array_temporal.append(k[2])
                array_kilos_temporal.append(k[3])
                
            
        except:
            print('no existe')
            

        finally:
            print('error')
            validacion=1
        
        if array_temporal==[]:
            array_validacion.append(0)
        else:
            array_validacion.append(1)

        print('******************************************') 
        print('alimento  = ',alim)
        print('materia prima usada en el alimento = ',array_temporal)
        print('i= ',i) 
       
        print('******************************************') 
        r=0
        u=0
        for g in array_temporal :
                for h in array_materiaprima :
                    if g ==h:                        
                        matriz[r,i]=g
                        matriz_kilos[r,i]=array_kilos_temporal[u]
                        
                        r=0
                        break
                        
                    r=r+1
                u=u+1
        alim=''
        array_temporal=[]
        array_kilos_temporal=[]
        print('array_temporal = ',array_temporal) 
        print(matriz)
        print('') 
        print(matriz_kilos)
        print('r',r)
        print('len materia =',len(array_materiaprima))
        print(matriz.shape)
        print('matriz validacion alimento = ', array_validacion)
        i=i+1
        
        s_m_kilos=np.asarray(array_formula_cantidad, float)
        #s_m_kilos=np.sum(s_m_kilos,axis=0)
        a=0.0
        for j in s_m_kilos:
            a=a+j
        print(s_m_kilos)
        print(a)

        print(matriz_kilos)
        print('')
        print('')
        print('')

    
    print(matriz_kilos)
    print(array_materiaprima)
    i=0
    x=0
    m_kilos_f=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype=float)
    for j in matriz_kilos:
        x=0
        for k in j:
            if k=='':
                m_kilos_f[i,x]=0.0
            else:
                m_kilos_f[i,x]=k

            print(k,' i= ', i, ' x= ',x)
            x=x+1
        i=i+1
    print(m_kilos_f)      

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima')
    data=cur.fetchall()
    valor_costo=[]
    for j in data:
        a=j[2]
        
        valor_costo.append(a)
    print(valor_costo)
    print(len(valor_costo))
    print(len(array_materiaprima))

    
    costo=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype=float)
    i=0
    x=0
    print('costo')
    print(costo.shape)
    print(costo)
    a,b=costo.shape
    print(b)
    for j in valor_costo:
        x=0
        
        for k in range(b):
            print('j = ',j,' i = ',i,' x = ',x)
            costo[i,x]=j
            x=x+1    
        i=i+1
    print(costo)
    i=0
    x=0

    costo_final=np.multiply(costo,m_kilos_f)
    i=0
    x=0
    costo_final=np.around(costo_final,decimals=4)
    suma_costo=np.sum(costo_final,axis=0)
    costo_kg=np.divide(suma_costo,250)
    costo_saco=np.multiply(costo_kg,40)
    print(costo_final)
    print('suma costo')
    suma_costo=np.around(suma_costo,decimals=3)
    print(suma_costo)

    print('costo kg')
    print(costo_kg)
    costo_kg=np.round(costo_kg,decimals=4)
    costo_saco=np.round(costo_saco,decimals=2)

    print('costo saco')
    print(costo_saco)
    costo2=np.zeros((len(costo_kg)),dtype='<U50')
    i=0
    for j in costo_kg:
        if j ==0:
            costo2[i]='0,0'
        else:
            a=j
            a=separador_miles(a)
            costo2[i]=a
        i=i+1
    print('costo 2')
    print(costo2)


    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento ORDER BY producto')
    data=cur.fetchall()
    i_alimento=[]
    for j in data:
        i_alimento.append(j[1])
    print('i_alimento')
    print(i_alimento)
    i=0
    for j in i_alimento:
        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE inventario_alimento 
            SET costo=%s                           
            WHERE producto = %s
        """,(costo2[i],j))
        mysql.connection.commit()
        i=i+1

    







    print('')
    print('')
    print('')
    print('')
    print('FIN DE CALCULAR PRODUCCION')
    print('***************************************************')
    return (costo2)

def status_401(error):
    return redirect(url_for('login'))



@app.route('/c')
def calcular_costo_produccion2():
    print('')
    print('')
    print('')
    print('***************************************************')
    print('INICIO DE CALCULAR PRODUCCION')
    print('')
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_alimento=[]
    for j in data:
        array_alimento.append((j[1]))

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM formula ORDER BY alimento ')
    data=cur.fetchall() 
    print(data)
    array_formula_alimento=[]
    array_formula_materia=[]
    array_formula_cantidad=[]
    
    for j in data:
        array_formula_alimento.append((j[1]))
        array_formula_materia.append((j[2]))
        array_formula_cantidad.append((j[3]))
    print('array formula alimento')
    print(array_formula_alimento)
    print('')
    print('array formula materiprima')
    print(array_formula_materia)
    print('')
    print('array formula cantidad')
    print(array_formula_cantidad)

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM lista_materiaprima ORDER BY producto ')
    data=cur.fetchall() 
    array_materiaprima=[] 
    for j in data:
        array_materiaprima.append((j[1]))

    # fin rutina buscar lista_materiaprima

    print('')
    print('alimentos en bd tipo alimento',array_alimento)
    print('')
    print('tipos de alimentos en bd de formula',array_formula_alimento)
    print('')
    print('tipos de materia en bd de formula',array_formula_materia)
    print('')
    print('cantidad materia en bd de formula',array_formula_cantidad)
    print('')
    print('tipos de materia prima',array_materiaprima)

    matriz=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50' )
    matriz_kilos=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype='<U50' )
    print(matriz)
    print(matriz.shape)
    print('matriz_kilos = ',matriz_kilos)


    print(matriz.shape)
    longitud_matriz=0
    for j in matriz.shape:
        print(j)

    longitud_matriz=len(array_materiaprima)
    print('longitud matriz = ', longitud_matriz)
    i=0

    array_temporal=[]
    
    array_kilos_temporal=[]
    array_alimento_utilizado=[]
    array_materia_utizado=[]
    array_cantidad_utizado=[]
    array_validacion=[]
    i=0
    z=0
    cont=0
    r=0
    validacion=0
    for j in array_alimento:
        validacion=0
        z=0
        try:
            cur=mysql.connection.cursor()
            cur.execute(f"SELECT * FROM formula WHERE alimento = '{j}'") 
            alim=j
            data=cur.fetchall() 
            #print('data = ',data)
            validacion=0
            for k in data:
                
                array_temporal.append(k[2])
                array_kilos_temporal.append(k[3])
                
            
        except:
            print('no existe')
            

        finally:
            print('error')
            validacion=1
        
        if array_temporal==[]:
            array_validacion.append(0)
        else:
            array_validacion.append(1)

        print('******************************************') 
        print('alimento  = ',alim)
        print('materia prima usada en el alimento = ',array_temporal)
        print('i= ',i) 
       
        print('******************************************') 
        r=0
        u=0
        for g in array_temporal :
                for h in array_materiaprima :
                    if g ==h:                        
                        matriz[r,i]=g
                        matriz_kilos[r,i]=array_kilos_temporal[u]
                        
                        r=0
                        break
                        
                    r=r+1
                u=u+1
        alim=''
        array_temporal=[]
        array_kilos_temporal=[]
        print('array_temporal = ',array_temporal) 
        print(matriz)
        print('') 
        print(matriz_kilos)
        print('r',r)
        print('len materia =',len(array_materiaprima))
        print(matriz.shape)
        print('matriz validacion alimento = ', array_validacion)
        i=i+1
        
        s_m_kilos=np.asarray(array_formula_cantidad, float)
        #s_m_kilos=np.sum(s_m_kilos,axis=0)
        a=0.0
        for j in s_m_kilos:
            a=a+j
        print(s_m_kilos)
        print(a)

        print(matriz_kilos)
        print('')
        print('')
        print('')

    
    print(matriz_kilos)
    print(array_materiaprima)
    i=0
    x=0
    m_kilos_f=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype=float)
    for j in matriz_kilos:
        x=0
        for k in j:
            if k=='':
                m_kilos_f[i,x]=0.0
            else:
                m_kilos_f[i,x]=k

            #print(k,' i= ', i, ' x= ',x)
            x=x+1
        i=i+1
    print(m_kilos_f)      

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto')
    data=cur.fetchall()
    valor_costo=[]
    for j in data:
        a=j[2]
        
        valor_costo.append(a)
    print(valor_costo)
    print(len(valor_costo))
    print(len(array_materiaprima))

    
    costo=np.zeros((len(array_materiaprima)+1,len(array_alimento)),dtype=float)
    i=0
    x=0
    print('costo')
    print(costo.shape)
    print(costo)
    a,b=costo.shape
    print(b)
    for j in valor_costo:
        x=0
        
        for k in range(b):
            #print('j = ',j,' i = ',i,' x = ',x)
            costo[i,x]=j
            x=x+1    
        i=i+1
    print(costo)
    i=0
    x=0

    costo_final=np.multiply(costo,m_kilos_f)
    i=0
    x=0
    costo_final=np.around(costo_final,decimals=4)
    suma_costo=np.sum(costo_final,axis=0)
    costo_kg=np.divide(suma_costo,250)
    costo_saco=np.multiply(costo_kg,40)
    print(costo_final)
    print('suma costo')
    suma_costo=np.around(suma_costo,decimals=3)
    print(suma_costo)

    print('costo kg')
    print(costo_kg)
    costo_kg=np.round(costo_kg,decimals=4)
    costo_saco=np.round(costo_saco,decimals=2)

    print('costo saco')
    print(costo_saco)
    costo2=np.zeros((len(costo_kg)),dtype='<U50')
    i=0
    for j in costo_kg:
        if j ==0:
            costo2[i]='0,0'
        else:
            a=j
            a=separador_miles(a)
            costo2[i]=a
        i=i+1
    print('costo 2')
    print(costo2)


    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento ORDER BY producto')
    data=cur.fetchall()
    i_alimento=[]
    for j in data:
        i_alimento.append(j[1])
    print('i_alimento')
    print(i_alimento)
    i=0
    for j in i_alimento:
        cur=mysql.connection.cursor()
        cur.execute("""
            UPDATE inventario_alimento 
            SET costo=%s                           
            WHERE producto = %s
        """,(costo2[i],j))
        mysql.connection.commit()
        i=i+1

    

    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto')
    data=cur.fetchall()
    v=[]
    for j in data:
        v.append(j)
    print('')
    print('costo mp')
    print(v)
    print('lista mp ')
    print(array_materiaprima)


    print('')
    print('')
    print('')
    print('')
    print('FIN DE CALCULAR PRODUCCION')
    print('***************************************************')
    return costo2


#@app.route('/dias')
def dias_ponedora2():
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_aba ORDER BY fecha_indice DESC')
    data=cur.fetchall() 
    tabla_1=data
    productos_inv=[]
    productos_suma=[]
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM costo_materiaprima ORDER BY producto')
    data=cur.fetchall() 
    costo_mp=[]
    for j in data:
        productos_suma.append(j[3])
        productos_inv.append(j[1])
        costo_mp.append(j[2])

    costo_mp_string=[]
    for j in costo_mp:
        j=separador_miles(float(j))
        costo_mp_string.append(j)
    
    print('')
    print('')
    print('producto suma')
    print(productos_suma)    ####                               suma todo el inventario en catidad de kilos string
    print('')
    print('')
    print('')
    # rutina buscar tipos de alimentos
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM tipo_alimento ORDER BY alimento ')
    data=cur.fetchall() 
    array_alimento=[]
    for j in data:
        array_alimento.append(j[1])
    
    # fin rutina buscar tipos de alimentos

    # rutina buscar inventario de alimento
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario_alimento ORDER BY producto ')
    data=cur.fetchall() 
    array_kilos_aba=[]
    alimento_inv=[]
    alimento_suma=[]
    for j in data:
        array_kilos_aba.append(float(j[2]))
        alimento_inv.append(j[1])
    # fin rutina buscar inventario de alimento

    
    # rutina para sumar la cantidad de alimentos por tipo   
    
    aliment=j
    #alimento_inv.append(aliment)
    suma_a=0.0
    i=0
    
    


    print('')
    print('--- alimento suma -------')
    print(alimento_suma)                             ##### todos los alimentos realizados por tipo de alimentos
    print('')
            
    

    kilos_final=[]
    for j in productos_suma:
        j=float(j)
        kilos_final.append(j)
    print('kilos final')
    print(kilos_final)
    print('')
    print('array kilos aba')
    print(array_kilos_aba)
    i=0

    k_aba=np.divide(array_kilos_aba,40)

    #### kilos en sacos
    kilos_total_sacos=np.divide(kilos_final,40)
    print('kilos total en sacos')
    print(kilos_total_sacos)
    #fin kilos en sacos
    
    kilos_total=np.zeros(len(kilos_final),dtype='<U50')
    for j in range(len(kilos_final)):
        #print('kilos final = ',kilos_final[i])
        kilos_total[i]=separador_miles(kilos_final[i])
        i=i+1
    i=0
    kilos_aba=np.zeros(len(array_kilos_aba),dtype='<U50')
    for j in range(len(array_kilos_aba)):
        kilos_aba[i]=separador_miles(array_kilos_aba[i])
        i=i+1
    
    # kilos en sacos a string con dos decimales######################
    k_t_sacos=np.zeros(len(kilos_total_sacos),dtype='<U50')          #
    i=0                                                              #
    for j in range(len(kilos_total_sacos)):                          #           
        k_t_sacos[i]=separador_miles(kilos_total_sacos[i])           #          
        i=i+1                                                        #     
    # fin kilos en sacos a string####################################

    # kilos en alimento sacos a string con dos decimales #############
    k_aba_final=np.zeros(len(k_aba),dtype='<U50')                    #
    i=0                                                              #
    for j in range(len(k_aba)):                                      #           
        k_aba_final[i]=separador_miles(k_aba[i])                     #          
        i=i+1                                                        #     
    # fin kilos aliemnto en sacos a string ###########################

    print('kilos total = ',kilos_total)
    print('kilos en sacos = ',k_t_sacos)
    

    
    print('--------------------------------')
    print('--------------------------------')
    print('--------------------------------')
    print('alerta inventario')
    alerta,porcentaje = alerta_inventario()
    print('desde planta aba emitimos alerta')
    print(alerta)

    print(array_kilos_aba)
    print(k_aba_final)
    print(porcentaje)

    cur=mysql.connection.cursor()
    cur.execute(f'SELECT * FROM formula WHERE alimento = "PONEDORA 2 REF (52627) (60 SEM A FIN)" ')
    #cur.execute("CALL ver_precio(1)")
    
    data=cur.fetchall()
    formula=np.array(data)
    print(formula)
    print(len(formula))

    index_mp=np.array(bd_lista_materiaprima())

    print('index = ', index_mp)
    i=0
    buzon_mp=np.array([])
    buzon_matriz_mp=np.zeros((len(index_mp)),dtype='<U50')
    print(buzon_matriz_mp)
    print('kilos final',kilos_final[0])
    for j in index_mp :
        
        print(j[1])
        for k in formula:
            
            if j[1]==k[2]:
                p=k[3]
                #p=devolver_separador_miles(p)
                print('p = ',p)
                p1=kilos_final[i]/float(p)
                p1=p1/40
                p1=separador_miles(p1)
                #print(p1)
                buzon_matriz_mp[i]=p1
                #print(j[1], ' son iguales con i = ',i)
            #else:
            #    buzon_matriz_mp[i]='N/A'
        i=i+1
    print(buzon_matriz_mp)
    return (buzon_matriz_mp)

# Main Principal
if __name__ == '__main__':
    #app.run(debug=False)
    #app.run(host='192.168.1.102', port=5000,debug=True)
    app.register_error_handler(401,status_401)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='192.168.254.237', port=port, debug=True)
    #app.run(host='localhost', port=port, debug=True)

    
   


