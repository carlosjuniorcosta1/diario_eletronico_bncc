from flask import Flask, jsonify, request
import pyodbc
import pandas as pd
from flask_pydantic_spec import FlaskPydanticSpec


app = Flask(__name__ )
spec = FlaskPydanticSpec(title = "Endpoints da tabela de avaliação", \
    description = "Documentação da api")
spec.register(app)

app.config['id_for_grades'] = None

data_for_connection = (
    "Driver={SQL Server Native Client RDA 11.0};"
    "Server=DESKTOP-1698A6Q\SQLEXPRESS;"
    "Database=bncc;"  
    "Trusted_connection=YES;"
)
connection = pyodbc.connect(data_for_connection)
cursor = connection.cursor()

cursor.commit()

#funcionando
@app.route('/diario/atividades', methods = ['GET'])
def get_all_act():
    """Lista todas as atividades de todos os alunos de todas as turmas"""

    db = cursor.execute(f"""SELECT * from tabela_atividade
                        """)
    db = db.fetchall()
    db_l = []
    for x in db:
        db_l.append({
            'id_materia': x[0],
            'id_bimestre': x[1],
            'descricao_at':x[2],
            'id_turma': x[3],
            'id_atividade':x[4],
            'data_cadastro_atv': x[5]
        })
    return jsonify(message = "Todas as atividades", data = db_l)

#funcionando
@app.route('/diario/atividade/<int:id_atividade>', methods = ['GET'])
def get_act_by_id(id_atividade):
    db = cursor.execute(f"""SELECT * FROM tabela_atividade WHERE id_atividade = {id_atividade}
                       """)
    db = db.fetchone()
    db_l = [{
            'id_materia': db[0],
            'id_bimestre': db[1],
            'descricao_at':db[2],
            'id_turma': db[3],
            'id_atividade':db[4],
            'data_cadastro_atv': db[5]
        }]
    return jsonify(message = f"Atividade solicitada", data = db_l)

#funcionando
   
@app.route('/diario/inserir/atividades', methods=['POST'])
def insert_act():
    """Insere uma nova atividade"""
    
    act_obj = request.get_json(force=True)    
    id_materia = act_obj.get('id_materia')
    id_bimestre = act_obj.get('id_bimestre')
    turma = act_obj.get('id_turma')
    act_des = act_obj.get('descricao_at')
    data_cadastro_atv = act_obj.get('data_cadastro_atv')
    
    if id_materia is None or id_bimestre is None or turma is None:
        return jsonify(message="Certifique-se de fornecer id_materia, id_bimestre, id_turma e data_cadastro_atv no corpo da solicitação."), 400
    
    cursor.execute(f"""INSERT INTO tabela_atividade (id_materia, id_bimestre, 
                   id_turma, descricao_at, data_cadastro_atv)
                   VALUES ({id_materia}, {id_bimestre}, {turma},
                   '{act_des}', '{data_cadastro_atv}')""")
    
    cursor.execute(f"SELECT SCOPE_IDENTITY() AS last_insert_id")
    last_id_act = cursor.fetchone().last_insert_id
    
    act_obj.update({'id_atividade': last_id_act})
    
    cursor.commit()
    
    return jsonify(message=f"Atividade inserida com sucesso e o id inserido é {last_id_act}", data=act_obj)


@app.route('/diario/notas/', methods = ['GET'])
def get_list_filters():
    """1) materia=MATERIA(str)&bimestre=BIMESTRE(int) => gera todos os
    boletins para todas as turmas do bimestre de 1 matéria \n
    2) materia=MATERIA(str)&bimestre=BIMESTRE(int)&turma=TURMA(int)=> gera todos os boletins 
    de uma matéria, de 1 bimestre para 1 turma \n
    3) materia=MATERIA(str)&ano=ANO(str)&bimestre=BIMESTRE(int) => gera todos os boletins
    de uma matéria para uma série/ano específico, baseado em um bimestre.
    4) materia=MATERIA(str)&ano=ANO(str)&bimestre=BIMESTRE(int)&turma=TURMA(int) => gera os boletins
    de uma matéria, de 1 bimestre, de 1 série específica, de 1 turma.
    5) materia=MATERIA(str) = > gera todas as notas de uma matéria, independente do ano
    6) materia=MATERIA(str)&turma=TURMA(int) => gera todas as notas de uma matéria, de uma turma 
    """
    filter_sub = request.args.get('materia')
    filter_cla = request.args.get('turma')
    filter_yea = request.args.get('ano')
    filter_per = request.args.get('bimestre')
    filter_gra = request.args.get('total')
    filter_avg = request.args.get('media')
    
    #matéria e bimestre
    if filter_sub is not None and filter_per is not None and filter_cla is None:
        query_l = cursor.execute(f"""
                                 SELECT nome_completo, ano, materia, id_turma, 
                                 tabela_bimestre.id_bimestre, total, id_avaliacao, id_atividade
                                 FROM tabela_alunos INNER JOIN tabela_avaliacao
                                 ON tabela_alunos.id_aluno = tabela_avaliacao.id_aluno
                                 INNER JOIN tabela_materias ON 
                                 tabela_avaliacao.id_materia = tabela_materias.id_materia 
                                 INNER JOIN tabela_bimestre ON 
                                 tabela_avaliacao.id_bimestre = tabela_materias.id_materia
                                 WHERE materia ='{filter_sub}' and tabela_avaliacao.id_bimestre = {filter_per}
                                 
                             """)
    #matéria, ano
    if filter_sub is not None and filter_yea is not None and filter_per is None:
        query_l = cursor.execute(f"""
                                  SELECT nome_completo, ano, materia, tabela_alunos.id_turma, 
                                  tabela_bimestre.id_bimestre, total, id_avaliacao, id_atividade
                                    FROM tabela_alunos INNER JOIN tabela_avaliacao
                                 ON tabela_alunos.id_aluno = tabela_avaliacao.id_aluno
                                 INNER JOIN tabela_materias ON 
                                 tabela_avaliacao.id_materia = tabela_materias.id_materia 
                                 INNER JOIN tabela_bimestre ON 
                                 tabela_avaliacao.id_bimestre = tabela_materias.id_materia
                                 WHERE tabela_materias.materia ='{filter_sub}' and tabela_alunos.ano = '{filter_yea}'
                                 """)
    
    #matéria, bimestre e turma
    if filter_sub is not None and filter_per is not None and filter_cla is not None:
         query_l = cursor.execute(f"""
                                 SELECT nome_completo, ano, 
                                 materia, tabela_alunos.id_turma, id_bimestre, total
                                 FROM tabela_alunos INNER JOIN tabela_avaliacao , 
                                 id_avaliacao, id_atividade
                                 ON tabela_alunos.id_aluno = tabela_avaliacao.id_aluno
                                 INNER JOIN tabela_materias ON 
                                 tabela_avaliacao.id_materia = tabela_materias.id_materia
                                 WHERE materia ='{filter_sub}' and tabela_avaliacao.id_bimestre = {filter_per}
                                 AND tabela_alunos.id_turma = {filter_cla}                                 
                                 """)
    #materia, bimestre, ano e turma
    if filter_sub is not None and filter_per is not None and filter_cla is not None and filter_yea is not None:
        query_l = cursor.execute(f"""
                                SELECT nome_completo,  
                                ano, materia, tabela_alunos.id_turma, 
                                id_bimestre, total , id_avaliacao, id_atividade
                                FROM tabela_alunos INNER JOIN tabela_avaliacao
                                ON tabela_alunos.id_aluno = tabela_avaliacao.id_aluno
                                INNER JOIN tabela_materias ON 
                                tabela_avaliacao.id_materia = tabela_materias.id_materia
                                WHERE materia ='{filter_sub}' and tabela_avaliacao.id_bimestre = {filter_per}
                                AND tabela_alunos.id_turma = {filter_cla} AND tabela_alunos.ano = '{filter_yea}'                                
                                """)
    #matéria e turma 
    if filter_sub is not None and filter_cla is not None and \
        filter_per is None and filter_gra is None and filter_yea is None:
        query_l = cursor.execute(f"""
                                SELECT nome_completo,  
                                ano, materia, tabela_alunos.id_turma,
                                id_bimestre, total, id_avaliacao, id_atividade
                                FROM tabela_alunos INNER JOIN tabela_avaliacao
                                ON tabela_alunos.id_aluno = tabela_avaliacao.id_aluno
                                INNER JOIN tabela_materias ON 
                                tabela_avaliacao.id_materia = tabela_materias.id_materia
                                WHERE tabela_materias.materia ='{filter_sub}' and tabela_alunos.id_turma = {filter_cla}
                                """)   

       
    query_l = query_l.fetchall()
    print(query_l)
    list_l = []
    for x in query_l:
        list_l.append({
            'nome_completo': x[0],
            'ano': x[1],
            'materia': x[2],
            'id_turma': x[3],
            'id_bimestre': x[4],
            'total': x[5],
            'id_avaliacao': x[6], 
            'id_atividade': x[7]
        })
    return jsonify(data = list_l)
        
@app.route('/diario/notas/media/', methods = ['GET'])
def get_mean():
    filter_sub = request.args.get('materia')
    filter_cla = request.args.get('turma')
    filter_yea = request.args.get('ano')
    filter_per = request.args.get('bimestre')
    
    #média de todas as turmas de uma determinada matéria
    if filter_sub is not None and filter_cla is not None and filter_per is None and filter_yea is None:  
        query_l = cursor.execute(f"""
                                 SELECT materia, id_turma, AVG(tabela_avaliacao.nota)
                                 FROM tabela_avaliacao INNER JOIN tabela_materias
                                 ON tabela_avaliacao.id_materia = 
                                 tabela_materias.id_materia  INNER JOIN 
                                 tabela_atividade ON tabela_avaliacao.id_atividade = 
                                 tabela_atividade.id_atividade                             
                                 where materia = '{filter_sub}'
                                 GROUP BY materia, id_turma                                
                                 """)        
    query_l = query_l.fetchall()
    print(query_l)
    list_l = []
    for x in query_l:
        list_l.append({
            'materia': x[0],
            'id_turma': x[1],
            'media': x[2],
        })
    return jsonify(message = "dados solicitados", data = list_l) 

#método inserir gustavo
@app.route('/diario/inserir/nota', methods=['POST'])
def insert_nota():
    """Insere uma nova nota"""
    
    act_obj = request.get_json(force=True)
    
    id_aluno = act_obj.get('id_aluno')
    id_materia = act_obj.get('id_materia')
    id_bimestre = act_obj.get('id_bimestre')
    nota = act_obj.get('nota')
    total = act_obj.get('total')
    id_atividade = act_obj.get('id_atividade')
    
    cursor.execute(f"""INSERT INTO tabela_avaliacao (id_materia, 
                   id_bimestre, id_aluno, id_atividade, nota, total)
                   VALUES ({id_materia}, {id_bimestre}, {id_aluno},
                   {id_atividade}, {nota}, {total})""")
    
    cursor.commit()
    
    return jsonify(message=f"Avaliacao inserida com sucesso ", data=act_obj)

@app.route('/diario/notas/inserir/', methods = ['GET', 'POST', 'PUT'])
def post_grades():    
    new_act = request.get_json(force=True)
    if len(new_act) > 1:
        id_atividade = new_act[0].get('id_atividade')
    else:
        id_atividade = new_act.get('id_atividade')
    db_turma = cursor.execute(f"""SELECT id_turma FROM tabela_atividade WHERE 
                              id_atividade = {id_atividade}""")

    if len(new_act) > 1:
        id_turma = db_turma.fetchone()[0]
    else:
        id_turma =db_turma.fetchone()                
    print(f"esse é o id turma {id_turma}")    
    db_ids = cursor.execute(f"""
    SELECT id_aluno from tabela_alunos where id_turma = {id_turma}""")
    list_ids = db_ids.fetchall()
    list_ids = [x for y in list_ids for x in y]
    dic_ids = []
    for x in list_ids:
        dic_ids.append({
            'id_aluno': x
        })
        
    resultado = []    
    for new_act_item in new_act:
        #print(f"esse é um elemento de new_act (item) {new_act_item}")
        for dic_ids_item in dic_ids:
            #print(f"esse é um elemento de dic_ids_item {dic_ids_item}")
            combined_dict = {**new_act_item, **dic_ids_item}
            #print(f"esse é combined dict por linha {combined_dict}")
            if combined_dict not in resultado:  
                resultado.append(combined_dict)
                #print(f"esse é o resultado de agora {resultado}")
    
    for x in resultado:
        cursor.execute(f"""
                       INSERT INTO tabela_avaliacao (id_aluno, id_materia, id_bimestre, nota, 
                       id_atividade) VALUES (
                           {x['id_aluno']}, {x['id_materia']}, {x['id_bimestre']}, {x['nota']}, 
                           {id_atividade}
                           )
                       """)
        cursor.commit()           
   
                
    return jsonify(message = "dados inseridos", data = resultado)
    
@app.route('/diario/notas/atualizar/<int:id_avaliacao>', methods = ['PUT'])
def update_grades(id_avaliacao):
    """Atualiza uma atividade criada. Os campos disponíveis para atualização são:
    id_materia(int)= portugues:	1, ingles:	2, artes:	3, matematica:	4, ciencias: 5
    educacao_fisica: 6, ensino_religioso: 7, historia:	8, geografia:	9  
    id_bimestre(int)= 1, 2, 3, 4 
    nota_5(int) (em breve serão disponibilizadas todas as notas)
    descricao_at(str)   
    
    """
    up_obj = request.get_json(force=True)
    up_per = up_obj['id_bimestre']
    up_gra_5 = up_obj['nota']
    up_sub = up_obj['id_materia']
    
    if up_per is not None and up_des is not None \
        and up_gra_5 is not None and up_sub is not None:
        cursor.execute(f"""UPDATE tabela_avaliacao SET id_materia = {up_sub} , 
                       id_bimestre = {up_per},
                       nota = {up_gra_5} WHERE
                       id_avaliacao = {id_avaliacao}
                   """)        
    cursor.commit()
    up_obj.update({'id_avaliacao': id_avaliacao})
    return jsonify(message="Atividade atualizada", data = up_obj)
    
@app.route('/diario/notas/deletar/<int:id_avaliacao>', methods = ['DELETE'])
def delete_grades(id_avaliacao):
    """Insira o id de alguma atividade e ela será apagada"""
    cursor.execute(f"""DELETE FROM tabela_avaliacao WHERE id_avaliacao = {id_avaliacao}
                   """)
    cursor.commit()
    
    return jsonify(message=f"Atividade {id_avaliacao} apagada!", dado_deletado = id_avaliacao)      
               
               
app.run(debug=True)