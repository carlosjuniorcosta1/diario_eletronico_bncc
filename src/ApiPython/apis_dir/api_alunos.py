from flask import Flask, jsonify, request
import pyodbc
from flask_pydantic_spec import FlaskPydanticSpec
from pydantic import BaseModel


app = Flask(__name__)
spec = FlaskPydanticSpec('flask', title = "Endpoints da api para inserir alunos")
spec.register(app)


data_for_connection = (
    "Driver={SQL Server Native Client RDA 11.0};"
    "Server=DESKTOP-1698A6Q\SQLEXPRESS;"
    "Database=bncc;"  
    "Trusted_connection=YES;"
)

connection = pyodbc.connect(data_for_connection)
cursor = connection.cursor()

@app.route('/diario', methods = ['GET'])
#@spec.validate(resp=Response(HTTP_200=Student))
def list_all_students():
    """Lista todos os estudantes da escola """
    db = cursor.execute(f"SELECT * FROM tabela_alunos ORDER BY id_aluno DESC")
    query_st = db.fetchall()
    all_st = []
    for x in query_st:
        all_st.append({
            "nome": x[0],
            "sobrenome": x[1],
            "nome_completo": x[2],
            "ano": x[3],
            "nivel_ensino": x[4],
            "idade": x[5], 
            "cpf": x[6],
            "turma": x[7],
            "id_aluno" : x[8],
            "status_aluno": x[9]


        })
    return jsonify(message = "Lista de todos os alunos", lista_total = all_st)

@app.route('/diario/aluno/<id_student>', methods=['GET'])
def list_student_by_id(id_student):
    "Lista os dados de um estudante pelo id"
    db = cursor.execute(f"SELECT * FROM tabela_alunos where id_aluno = ?", (id_student,))
    query_data = db.fetchone()  # Use fetchone() to retrieve a single row

    if query_data is not None:
        student_data = {
            "nome": query_data[0],
            "sobrenome": query_data[1],
            "nome_completo": query_data[2],
            "ano": query_data[3],
            "nivel_ensino": query_data[4],
            "idade": query_data[5],
            "cpf": query_data[6],
            "turma": query_data[7],
            "id_aluno": query_data[8],
            "status_aluno": query_data[9]
        }
        return jsonify(data=student_data, message="Aluno solicitado")
    else:
        return jsonify(message="Aluno não encontrado"), 404 
 
@app.route('/diario/', methods = ['GET'])
def list_filters():
    """Lista por filtros - id, ano, nivel, nome, sobrenome, nome_c, cpf, idade """
    filter_y = request.values.get('ano')
    filter_y2 = request.values.getlist('ano')
    filter_level = request.values.getlist('nivel')    
    filter_full_name = request.values.get('nome_c')
    filter_surname = request.values.get('sobrenome')
    filter_name = request.values.get('nome')
    filter_cpf = request.values.get('cpf')
    filter_age = request.values.get('idade')
    filter_id = request.values.get('id')  
   
    if filter_y2 is not None:
        if len(filter_y2) == 1:        
            query_l = cursor.execute(f"SELECT * FROM tabela_alunos WHERE ano = '{filter_y}'")        
    if filter_y2 is not None:
        if len(filter_y2) >= 2:     
            
            if 'sexto' and 'setimo' in filter_y2:
                #ok
                query_l = cursor.execute(f"SELECT * FROM tabela_alunos WHERE ano = 'sexto' or ano = 'setimo'")
            if 'sexto' and 'oitavo' in filter_y2:
                query_l = cursor.execute(f"SELECT * FROM tabela_alunos WHERE ano = 'sexto' or ano = 'oitavo'")
            if 'sexto' and 'nono' in filter_y2:
                query_l = cursor.execute(f"""SELECT * FROM tabela_alunos WHERE 
                                        ano = 'sexto' or ano = 'nono'""")           
            if 'sexto' and 'setimo' and 'oitavo' in filter_y2:
                query_l = cursor.execute(f"""SELECT * FROM tabela_alunos WHERE ano = 
                                        'sexto' or ano = 'setimo' OR ano = 'oitavo'""")
            if 'sexto' and 'setimo' and 'nono' in filter_y2:
                query_l = cursor.execute(f"""SELECT * FROM tabela_alunos WHERE ano = 
                                        'sexto' or ano = 'setimo' OR ano = 'nono'""")
        
    
            if 'setimo' and 'oitavo' in filter_y2:
                query_l = cursor.execute(f"""SELECT * FROM tabela_alunos WHERE ano = 
                                        'setimo' OR ano = 'oitavo'""")
                
            if 'setimo' and 'oitavo' and 'nono' in filter_y2:
                query_l = cursor.execute(f"""
                                        SELECT * FROM tabela_alunos WHERE ano =
                                        'setimo' OR ano = 'oitavo' OR ano = 'nono'                                     
                                        """)
            if 'oitavo' and 'nono' in filter_y2:
                query_l = cursor.execute(f"""
                                        SELECT * FROM tabela_alunos WHERE ano = 
                                        'oitavo' OR ano = 'nono'                                     
                                        """)
    if filter_level is not None:
        if len(filter_level) > 0:
        
            if 'em' and 'ef' in filter_level:
                query_l= cursor.execute(f""" SELECT * FROM tabela_alunos WHERE nivel_ensino = 'ef' OR 
                                        nivel_ensino = 'em'
                                        """)
            if 'ef' not in filter_level:
                query_l =  cursor.execute(f"""
                                        SELECT * FROM tabela_alunos WHERE nivel_ensino = 'em'                                  
                                        """)
            if 'em' not in filter_level:
                query_l= cursor.execute(f""" SELECT * FROM tabela_alunos WHERE nivel_ensino = 'ef'
                                        """)
    if filter_full_name is not None:
        if len(filter_full_name) > 0:
            query_l = cursor.execute(f"""
                                SELECT * FROM tabela_alunos WHERE nome_completo
                                LIKE ?""", filter_full_name + '%')
    if filter_surname is not None:
        if len(filter_surname) > 0:
            query_l = cursor.execute(f"""
                                SELECT * FROM tabela_alunos WHERE sobrenome
                                LIKE ?""", filter_surname + '%')
            
    if filter_name is not None:
        if len(filter_name) > 0:
            query_l = cursor.execute(f"""
                            SELECT * FROM tabela_alunos WHERE nome
                            LIKE ?""", filter_name + '%')
    if filter_cpf is not None:
        if len(filter_cpf) > 0:
            query_l = cursor.execute(f"""
                        SELECT * FROM tabela_alunos WHERE cpf
                        LIKE ?""", filter_cpf + '%')
    if filter_age is not None:
        if len(filter_age) > 0:
            query_l = cursor.execute(f"""
                                     SELECT * FROM tabela_alunos WHERE idade
                                     = {filter_age}""")
    if filter_id is not None:
        query_l = cursor.execute(f"""
                                 SELECT * FROM tabela_alunos WHERE id_aluno= {filter_id}""")
    

    query_l = query_l.fetchall()
    list_y = []
    
    for x in query_l:
        list_y.append({
            
    "nome": x[0],
    "sobrenome": x[1],
    "nome_completo": x[2],
    "ano": x[3],
    "nivel_ensino": x[4],
    "idade": x[5], 
    "cpf": x[6], 
    "id" : x[7],
    "turma": x[8]

})          
        
    return jsonify(message = "Alunos por ano cursado", data = list_y)                   
           
@app.route('/diario/inserir', methods = ['POST'])
def insert_student():
    """Insere um novo estudante"""
    
    new_std = request.get_json(force=True)
    new_na = new_std['nome']
    new_su = new_std['sobrenome']
    new_fn = new_std['nome'] + ' ' + new_std['sobrenome']
    new_gr = new_std['ano']
    new_l = new_std['nivel_ensino']
    new_ag = new_std['idade']
    new_c = new_std['cpf']
    new_cl = new_std['id_turma']
    
    cursor.execute(f""" INSERT INTO tabela_alunos (nome, sobrenome, nome_completo,
                   ano, nivel_ensino, idade, cpf, id_turma, status_aluno)
                   VALUES ('{new_na}', '{new_su}', '{new_fn}', '{new_gr}',
                   '{new_l}', {new_ag},
                   '{new_c}', {new_cl}, 'true')
                   """)
    cursor.execute(f"SELECT SCOPE_IDENTITY() AS last_insert_id")
    last_id = cursor.fetchone().last_insert_id
    print(f"o último id inserido foi o {last_id}")
    new_std.update({'id_aluno': last_id})
    cursor.commit()
    return jsonify(message = f"Aluno * {str.upper(new_fn)} * id {last_id}, cadastrado com sucesso", data = new_std)

@app.route('/diario/deletar/<id_student>/<status_aluno>', methods = ['PUT'])
def delete_student(id_student, status_aluno):

    """Altera status do estudante"""    
    cursor.execute(f"""UPDATE tabela_alunos SET status_aluno = {status_aluno}
                    WHERE id_aluno ={id_student}
                """)
    cursor.commit()
    response_data = {"id_aluno": id_student}
    return jsonify(message = "Aluno desativado da lista. ", data=response_data)    
    
    
@app.route('/diario/atualizar/<id_student>', methods = ['PUT'])
def update_std(id_student):
    """Atualiza um estudante da lista"""  
    updated_data = request.get_json(force=True)
    up_na = updated_data['nome']
    up_su = updated_data['sobrenome']
    up_fn =updated_data['nome'] + updated_data['sobrenome']
    up_gr = updated_data['ano']
    up_le = updated_data['nivel_ensino']
    up_ag = updated_data['idade']
    up_cpf = updated_data['cpf']
    up_cl = updated_data['turma']
    
    cursor.execute(f"""UPDATE tabela_alunos SET nome = '{up_na}', 
                   sobrenome = '{up_su}', nome_completo = '{up_fn}',
                   ano = '{up_gr}', nivel_ensino = '{up_le}', 
                   idade = {up_ag}, cpf = '{up_cpf}', turma = {up_cl}
                   WHERE id_aluno ={id_student}
                   """)
    
    cursor.commit()
    updated_data.update({'id_aluno': id_student})
    return(jsonify(message = f"Estudante {up_fn} atualizado", data=updated_data))
    
    
    
app.run(debug=True)