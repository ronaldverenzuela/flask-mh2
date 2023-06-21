from .entities.User import User
class ModelUser():
    
    @classmethod
    def login(self,mysql,user):
        try:
            print('user = ',user)
            cur=mysql.connection.cursor()
            sql="SELECT id,username,password,fullname,permiso,solicitud,nivel FROM user WHERE username = '{}'".format(user.username)
            cur.execute(sql)
            row=cur.fetchone()
            if row != None:
                user=User(row[0],row[1],User.check_password(row[2],user.password),row[3],row[4],row[5],row[6])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
      
    @classmethod
    def get_by_id(self,mysql,id):
        try:
           
            cur=mysql.connection.cursor()
            sql="SELECT id,username,fullname,permiso,solicitud,nivel FROM user WHERE id = {}".format(id)
            cur.execute(sql)
            row=cur.fetchone()
            if row != None:
               return User(row[0],row[1],None,row[2],row[3],row[4],row[5])
                
            else:
                return None
        except Exception as ex:
            raise Exception(ex)