from app.main import main
from flask import render_template, request
from app.api_1_0.errors import forbidden, not_found, unauthorized
from app.api_1_0.errors import internal_server_error


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        return not_found()
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        return internal_server_error() 
    return render_template('500.html'), 500

@main.app_errorhandler(403)
def forbidden_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        return forbidden('forbidden')
    return render_template('403.html'), 403

@main.app_errorhandler(401)
def unauthorized_access(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        return unauthorized('Unauthorized')
    return render_template('401.html'), 401
