from flask import Flask, jsonify, request, render_template, make_response
import pyodbc
from flask_pydantic_spec import FlaskPydanticSpec
import asyncio 

app = Flask(__name__ )
spec = FlaskPydanticSpec('flask', title = "Endpoints da tabela de avaliação")
spec.register(app)      

data_for_connection = (
    "Driver={SQL Server Native Client RDA 11.0};"
    "Server=DESKTOP-1698A6Q\SQLEXPRESS;"
    "Database=bncc;"  
    "Trusted_connection=YES;"
)
connection = pyodbc.connect(data_for_connection)
cursor = connection.cursor()

@app.route('/diario/aula/registrar', methods = ['POST'])
def insert_class():
    obj_cla = request.get_json(force=True)
    id_materia = obj_cla.get('id_materia')
    id_bimestre = obj_cla.get('id_bimestre')
    data_aula = obj_cla.get('data_aula')
    descricao_aula = obj_cla.get('descricao_aula')
    habilidade_bncc = obj_cla.get('habilidade_bncc')
    id_turma = obj_cla.get('id_turma')
    
    cursor.execute(f"""INSERT INTO tabela_aulas (id_materia, id_bimestre, data_aula, 
                   descricao_aula, habilidade_bncc, id_turma) VALUES ({id_materia}, 
                   {id_bimestre}, {data_aula}, '{descricao_aula}', '{habilidade_bncc}', {id_turma})
                   """)
    cursor.execute(f"SELECT SCOPE_IDENTITY() AS last_insert_id")
    id_aula = cursor.fetchone().last_insert_id
    obj_cla.update({'id_aula': id_aula})
    cursor.commit()
    
    return jsonify(data = obj_cla, message = "Aula inserida com sucesso")
    
@app.route('/diario/aula/listar/')
def get_classes():
    id_aula = request.values.get("id_aula")
    id_bimestre = request.values.get("id_bimestre")
    id_materia = request.values.get("id_materia")
    id_turma = request.values.get('id_turma')

    if id_aula == None and id_bimestre == None and id_materia == None and id_turma == None:
       
        db = cursor.execute(f"""SELECT * FROM tabela_aulas""")
        db = db.fetchall()
        db_list = []
        for x in db:
            db_list.append({
                "id_aula": x[0],
                "id_materia": x[1],
                "id_bimestre": x[2],
                "data_aula": x[3],
                "descricao_aula": x[4],
                "habilidade_bncc": x[5]
                
            })
        return jsonify(data = db_list)
    if id_aula is not None:
        db = cursor.execute(f"""SELECT * FROM tabela_aulas WHERE id_aula = {id_aula}
                            """)
        db = db.fetchone()
        if db is not None:
            resultado = {
            "id_aula": db[0],
            "id_materia": db[1],
            "id_bimestre": db[2],
            "data_aula": db[3],
            "descricao_aula": db[4],
            "habilidade_bncc": db[5]
            }
        print(f"esse é o resultado {resultado}")
        
        return jsonify(message = "Dados da aula solicitada", data = resultado)

    if id_aula is None and id_bimestre is not None and id_materia is not None and id_turma is not None:
        db = cursor.execute(f"""SELECT * from tabela_aulas WHERE id_bimestre = {id_bimestre} and 
                            id_materia = {id_materia} and id_turma {id_turma}
                            """)
        db_list = db.fetchall()
        if len(db_list) > 1:
            db_list = []
            for x in db:
                db_list.append({                         
            "id_aula": x[0],
            "id_materia": x[1],
            "id_bimestre": x[2],
            "data_aula": x[3],
            "descricao_aula": x[4],
            "habilidade_bncc": x[5]
            } )
            return jsonify(data = db_list, message = "Todas as aulas retornadas")
        elif len(db_list) == 1:
            resultado = {
            "id_aula": db_list[0][0],
            "id_materia": db_list[0][1],
            "id_bimestre": db_list[0][2],
            "data_aula": db_list[0][3],
            "descricao_aula": db_list[0][4],
            "habilidade_bncc": db_list[0][5]
            }
            return jsonify(data = resultado, message = "Apenas 1 aula retornada")

@app.route('/diario/aula/deletar', methods = ['DELETE'])
def delete_classes():
    id_aula = request.values('id_aula')
    cursor.execute(f""" DELETE FROM tabela_aulas WHERE id_aula = {id_aula}
                        """)
    cursor.commit()
    return jsonify(message = f"Aula {id_aula} deletada com sucesso")

@app.route('/diario/frequencia/atualizaraula/', methods = ["GET", "PUT"])
def update_class():
    id_aula = request.values.get('id_aula')
    try:
        up_obj = request.get_json(force=True)
        up_id_materia = up_obj.get('id_materia')
        up_id_bimestre = up_obj.get('id_bimestre')
        up_data_aula = up_obj.get('data_aula')
        up_descricao_aula = up_obj.get('descricao_aula')
        up_habilidade_bncc = up_obj.get('habilidade_bncc')
        up_id_turma = up_obj.get('id_turma')
    except:
        pass 
    cursor.execute(f"""UPDATE tabela_aulas SET id_materia = {up_id_materia},
                   id_bimestre = {up_id_bimestre}, data_aula = '{up_data_aula}',
                   descricao_aula = '{up_descricao_aula}', 
                   habilidade_bncc ='{up_habilidade_bncc}', id_turma = {up_id_turma}
                   WHERE id_aula = {id_aula}
                   """)
    up_obj.update({'id_aula': id_aula})
    cursor.commit()
    return jsonify(message= f"Aula de id = {id_aula} atualizada com sucesso", data = up_obj)

#inserção de frequência na tabela_frequencia a partir daqui
@app.route('/diario/frequencia/inserir', methods = ["POST"])
def insert_freq():
    """insere presença para todos de uma turma"""
    payload = request.get_json(force=True)
    id_aula = payload.get('id_aula')
    presente = payload.get('presente')
    db_turma = cursor.execute(f"SELECT id_turma from tabela_aulas WHERE id_aula = {id_aula}")
    db_turma = db_turma.fetchall()
    id_turma = db_turma[0][0]
    db_ids = cursor.execute(f"""SELECT id_aluno FROM tabela_alunos WHERE id_turma = {id_turma}""")
    list_ids = db_ids.fetchall()
    dic_ids = []
    for x in list_ids:
        for y in x:
            dic_ids.append({
                "id_aluno": y
            })
    print(f"esses são os alunos  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% {dic_ids}")
    result = []
    
    id_alunos_adicionados = set()
    
    for id_aluno in dic_ids:
        if id_aluno["id_aluno"] not in id_alunos_adicionados:
            result.append({
                "id_aluno": id_aluno["id_aluno"],
                "id_aula": id_aula,
                "presente": presente  
            })
            id_alunos_adicionados.add(id_aluno["id_aluno"])    
 
    print(f"esse é o result final %%%%%%%%%%$$$$$$$$$$$$$$$$$$$$$$$$$$$$ {result}")   
    id_freq_list = []
    for x in result:
        cursor.execute(f"""INSERT INTO tabela_frequencia (id_aluno, id_aula, presente) VALUES (
                           {x['id_aluno']}, {x['id_aula']}, {x['presente']}       
                       ) """)
        cursor.commit()
        cursor.execute(f"SELECT SCOPE_IDENTITY() AS last_insert_id")
        id_freq = cursor.fetchone().last_insert_id
        id_freq_list.append(id_freq)
    id_freq_f = []
    for x in id_freq_list:
        id_freq_f.append({
            "id_frequencia": int(x)
        })        
    for i, x in enumerate(result):
        x['id_frequencia'] = id_freq_f[i]['id_frequencia']
        print(f"printando a chave i {i} printando o valor x {x}")       
        
    
    return jsonify(message= "está funcionando", data = result) 
    
@app.route('/diario/frequencia/listar/', methods = ['GET'])
def get_frequency():
    id_aula = request.values.get('id_aula')
    db = cursor.execute(f"""SELECT * FROM tabela_frequencia where id_aula = {id_aula}""")
    db = db.fetchall()
    db_list = []
    for x in db:
        db_list.append(
            {
                "id_frequencia": x[0],
                "id_aluno": x[1],
                "id_aula": x[2],
                "presente": x[3]
            }
        )
    return jsonify(data = db_list, message = f"Listagem de frequência da aula de id = {id_aula}")

@app.route('/diario/frequencia/deletar/', methods = ['DELETE'])
def delete_frequency():
    id_aula = request.values.get('id_aula')
    cursor.execute(f"""
                   DELETE FROM tabela_frequencia WHERE id_aula = {id_aula}
                   """)
    cursor.commit()
    
@app.route('/diario/frequencia/atualizar/', methods = ['PUT'])
def update_frequency():
    id_aula = request.values.get('id_aula')
    up_obj = request.get_json(force=True)
    up_presente = up_obj.get('presente')
    id_aluno = up_obj.get('id_aluno')
    
    cursor.execute(f"""UPDATE tabela_frequencia SET presente = {up_presente}
                       WHERE id_aula = {id_aula} and id_aluno = {id_aluno}
                       """)
    cursor.commit()    
    
    return jsonify(message = "Tabela frequência atualizada", data = up_obj)

    
app.run(debug=True)
