from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Task, User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func

app = Flask(__name__)

# Настройка подключения к SQLite
# Путь к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
# Отключаем отслеживание изменений
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'
db.init_app(app)

jwt = JWTManager(app)


@app.before_request
def create_tables():
    db.create_all()  # Создаем таблицы при первом запросе

# Маршруты для работы с задачами

# Вход пользователя


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({"message": "Неверное имя пользователя или пароль."}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


@app.route('/api/validate-token', methods=['POST'])
@jwt_required()
def validate_token():
    # Получаем информацию о пользователе из токена
    current_user = get_jwt_identity()
    # Возвращаем успешный ответ с информацией о пользователе
    return jsonify({"message": "Токен действителен.", "user": current_user}), 200


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sortBy', 'default')  # Получаем параметр сортировки

    query = Task.query
        # Применяем сортировку в зависимости от параметра
    if sort_by == 'username asc':
        query = query.order_by(func.lower(Task.username).asc())
    elif sort_by == 'username desc':
        query = query.order_by(func.lower(Task.username).desc())
    elif sort_by == 'email asc':
        query = query.order_by(func.lower(Task.email).asc())
    elif sort_by == 'email desc':
        query = query.order_by(func.lower(Task.email).desc())
    elif sort_by == 'text asc':
        query = query.order_by(func.lower(Task.text).asc())
    elif sort_by == 'text desc':
        query = query.order_by(func.lower(Task.text).desc())
    # Пагинация по 3 задачи на страницу
    tasks = query.paginate(page=page, per_page=3)
    return jsonify({
        'tasks': [task.to_dict() for task in tasks.items],
        'pages': tasks.pages,
        'current_page': tasks.page,
        'total': tasks.total
    })

# Добавление новой задачи


@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    new_task = Task(username=data['username'],
                    email=data['email'], text=data['text'])
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

# Редактирование задачи

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    data = request.get_json()
    
    # Получаем новые значения из запроса
    new_text = data.get('text')
    new_completed_status = data.get('completed')  # Получаем новый статус завершенности

    # Находим задачу по ID
    task = Task.query.get(task_id)
    
    if task:
        # Обновляем текст задачи, если он был передан
        if new_text is not None:  # Проверяем, что новое значение текста не None
            task.text = new_text
        
        # Обновляем статус завершенности задачи, если он был передан
        if new_completed_status is not None:  # Проверяем, что новое значение статуса не None
            task.completed = new_completed_status

        db.session.commit()  # Сохраняем изменения в базе данных
        return jsonify({"message": "Задача обновлена.", "task": task.to_dict()}), 200
    
    return jsonify({"message": "Задача не найдена."}), 404
# Удаление задачи


@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return '', 204

