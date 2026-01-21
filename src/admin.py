import os
from flask_admin import Admin
from models import db, User, People, Planets, UserPeopleFavorite, UserPlanetFavorite
from flask_admin.contrib.sqla import ModelView


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')


# class VideojuegoAdmin(ModelView):
# column_list = ('id', 'nombre', 'year', 'empresa')
# form_columns = ('nombre', 'year', 'empresa')

    class UserPeopleFavoriteAdmin(ModelView):
        form_columns = ("user_id", "people_id")
        column_list = ("user_id", "people_id")

    class UserPlanetFavoriteAdmin(ModelView):
        column_list = ("user_id", "planet_id")
        form_columns = ("user_id", "planet_id")

    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(ModelView(Planets, db.session))

    admin.add_view(UserPeopleFavoriteAdmin(UserPeopleFavorite, db.session))
    admin.add_view(UserPlanetFavoriteAdmin(UserPlanetFavorite, db.session))

    # admin.add_view(VideojuegoAdmin(Videojuego, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))
