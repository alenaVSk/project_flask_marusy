from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin, getUserByEmail, addUser
import connect_db as con_db


def get_post(post_id):   # вызов поста по ID
    conn = con_db.get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
app.config['SECRET_KEY'] = 'lUhj7dHS4ldiEYkkKHgs8lAse'
app.config['MAX_CONTENT_LENGTH'] = 4 * 512 * 512


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"


@login_manager.user_loader  # передача в сессию информации о зарегистрированном пользователе
def load_user(user_id):
    return UserLogin().fromDB(user_id)


def choose_key_user():
    if current_user.is_authenticated:
        key_user = "Профиль"
    else:
        key_user = "Авторизация"

    return key_user


@app.route('/')  # просмотр домашней страницы (все посты)
def index():
    conn = con_db.get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()

    key_user = choose_key_user()

    return render_template('index.html', posts=posts, key_user=key_user)


@app.route('/about')  # страница о сайте
def about():
    key_user = choose_key_user()

    return render_template('about.html', key_user=key_user)


@app.route('/<int:post_id>')  # просмотр поста по ID
def post(post_id):
    key_user = choose_key_user()
    post_t = get_post(post_id)

    return render_template('post.html', post=post_t, key_user=key_user)


@app.route('/create', methods=('GET', 'POST'))  # создание нового поста(показывает форму для заполнения)
@login_required    # страница доступна только авторизованным пользователям
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Название обязательно!')
        else:
            conn = con_db.get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    key_user = choose_key_user()

    return render_template('create.html', key_user=key_user)


@app.route('/<int:id>/edit', methods=('GET', 'POST'))  # редактирование поста
@login_required    # страница доступна только авторизованным пользователям
def edit(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Название обязательно!')
        else:
            conn = con_db.get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    key_user = choose_key_user()

    return render_template('edit.html', post=post, key_user=key_user)


@app.route('/<int:id>/delete', methods=('POST',))  # удаление поста
@login_required   # страница доступна только авторизованным пользователям
def delete(id):
    post = get_post(id)
    conn = con_db.get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" был успешно удалён!'.format(post['title']))
    return redirect(url_for('index'))


@app.route("/login", methods=["POST", "GET"])  # обработчик для авторизации пользователя
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    key_user = choose_key_user()

    return render_template("login.html", key_user=key_user)


@app.route("/register", methods=["POST", "GET"])  # обработчик для регистрации пользователя
def register():
    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = addUser(request.form['name'], request.form['email'], hash)

            user = getUserByEmail(request.form['email'])
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)

            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('index'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")

    key_user = choose_key_user()

    return render_template("register.html", key_user=key_user)


@app.route('/logout')   # выход из профиля
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route('/profile')   # страница профиля
@login_required   # страница доступна только авторизованным пользователям
def profile():
    info = {
        'name_id': current_user.name_id(),
        'email_id': current_user.email_id(),
        'key_user': choose_key_user(),
    }

    return render_template('profile.html', info=info)


if __name__ == "__main__":
    app.run(debug=False)

