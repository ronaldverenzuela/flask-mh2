     # rutina buscar tipo de alimento
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