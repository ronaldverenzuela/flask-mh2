@app.route('/confirmacion_factura_ventas_materiaprima/dolares/<factura>',methods=['GET','POST'])
def confirmacion_facturas_ventas_materiaprima(factura):

    if request.method=='POST':
        abono=request.form['abono']
        fecha=request.form['fecha']
        if (not abono) or (not fecha):
            print('debe llenar todos los campos')
            flash('Debe llenar todos los campos','pago_dolares')
            return render_template('pagar_fvmp_dolares.html',factura=factura)

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
        
        
        
                

    return ('construccion')