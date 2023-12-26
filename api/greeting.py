from flask import Blueprint, request

user = Blueprint('user', __name__)
@user.route('/greeting')
def greeting():
    return 'Hello, lowly normal user!'