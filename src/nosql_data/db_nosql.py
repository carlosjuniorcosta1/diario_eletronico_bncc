import pymongo

client = pymongo.MongoClient("mongodb://localhost", 27017)

#acessa o db al_db, que foi feito no mongodbCompass, importando um json feito no python
db = client["al_db"] 

collection = db["dados"]

def list_all_students():
        all_students = []
        for x in collection.find():
                all_students.append(x)
        
        return all_students, print(all_students)
#list_all_students()

def list_student_by_name(name: str):
        name_st = name
        query1 = {"nome": name_st }
        q1 = collection.find(query1)
        name_st_l = []               
        for x in q1:
                name_st_l.append(x)
        return name_st_l, print(name_st_l)
        
#list_student_by_name('Kristian')
                

def insert_new_student(new_st):
        add_new = collection.insert_one(new_st)
        new_ = collection.find(new_st)
        for x in new_:
                print(x)
        return print(add_new.inserted_id)

new_st = {"nome": "aluno_inserido_para_exemplo", 'turma': 'nono_ef', 'sobrenome': 'sobrenome do aluno'}
        
insert_new_student(new_st)
client.close()
