import random
import string
from flask import Blueprint, request, render_template, redirect, url_for, flash,session
from flask_login import login_user, logout_user, login_required,current_user
from .models import db, User
from werkzeug.security import generate_password_hash ,check_password_hash
from .utils import nocache

auth_bp = Blueprint('auth', __name__)

# 회원가입
@nocache
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 1) 폼 값
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        confirm  = request.form.get('confirm_password') or ''
        email    = (request.form.get('email') or '').strip()
        agree    = request.form.get('agree_terms')  # 체크시 "on", 미체크시 None

        # 2) 기본 검증
        if not username or not password or not email:
            flash("아이디, 비밀번호, 이메일을 모두 입력하세요.")
            return redirect(url_for('auth.register'))

        if password != confirm:
            flash("비밀번호가 서로 일치하지 않습니다.")
            return redirect(url_for('auth.register'))

        if agree is None:
            flash("약관에 동의해 주세요.")
            return redirect(url_for('auth.register'))

        # 3) 중복 확인
        if User.query.filter_by(username=username).first():
            flash("이미 존재하는 아이디입니다.")
            return redirect(url_for('auth.register'))

        # (선택) 이메일이 unique인 경우 중복 체크
        if hasattr(User, 'email') and User.query.filter_by(email=email).first():
            flash("이미 사용 중인 이메일입니다.")
            return redirect(url_for('auth.register'))

        # 4) 생성 & 커밋
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password, email=email)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("회원가입 처리 중 오류가 발생했습니다. 다시 시도해 주세요.")
            return redirect(url_for('auth.register'))

        flash("회원가입 완료! 로그인 해주세요.")
        return redirect(url_for('auth.login'))

    # GET
    return render_template('register.html')


# 비밀번호 초기화
@nocache
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash("아이디를 입력하세요.")
            return render_template('forgot_password.html')

        user = User.query.filter_by(username=username).first()
        if user:
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.password = generate_password_hash(temp_password)
            db.session.commit()

            flash(f"임시 비밀번호는 {temp_password} 입니다. 로그인 후 반드시 비밀번호를 변경하세요.")
        else:
            flash("존재하지 않는 아이디입니다.")

    return render_template('forgot_password.html')

# 로그인
@nocache
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("아이디와 비밀번호를 모두 입력하세요.")
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)  # flask_login 로그인 처리
            flash(f"{user.username}님 로그인 되었습니다.")
            return redirect(url_for('web.index'))
        else:
            flash("아이디 또는 비밀번호가 올바르지 않습니다.")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

# 로그아웃
@nocache
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("로그아웃 되었습니다.","logout")
    return redirect(url_for('web.index'))


#비밀번호 변경
@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form['current_password']
        new_pw = request.form['new_password']
        confirm_pw = request.form['confirm_password']

        user = current_user

        if not check_password_hash(user.password, current_pw):
            flash('현재 비밀번호가 올바르지 않습니다.', 'error')
            return redirect(url_for('auth.change_password'))

        if new_pw != confirm_pw:
            flash('새 비밀번호가 일치하지 않습니다.', 'error')
            return redirect(url_for('auth.change_password'))

        user.password = generate_password_hash(new_pw)
        db.session.commit()
        flash('비밀번호가 성공적으로 변경되었습니다.', 'success')
        return redirect(url_for('auth.login'))  # 원하는 페이지로 이동

    return render_template('change_password.html')

