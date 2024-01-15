from .database import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    date_of_creating_account = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

class Genre(db.Model):
    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    thumbnail_url = db.Column(db.String(255))  # Add this line to include the genre thumbnail URL

class Album(db.Model):
    album_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_name = db.Column(db.String(255), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.genre_id'), nullable=False)
    creater_user_id = db.Column(db.Integer, db.ForeignKey('creater_user.creater_user_id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    thumbnail_url = db.Column(db.String(255))  # Add this line to include the album cover image URL

    genre = db.relationship('Genre', backref='albums')
    creater_user = db.relationship('CreaterUser', backref='albums')

class Song(db.Model):
    song_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    singer_name = db.Column(db.String(255), nullable=False)
    release_date = db.Column(db.Date)
    lyrics = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.album_id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.genre_id'))
    ratings = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Time)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    thumbnail_url = db.Column(db.String(10000))  # Add this line to include the thumbnail URL

    album = db.relationship('Album', backref='songs')
    genre = db.relationship('Genre', backref='songs')
    
    creater_id = db.Column(db.Integer, db.ForeignKey('creater_user.creater_user_id'))
    creater_user = db.relationship('CreaterUser', backref='songs')  # Adjust backref as needed

class CreaterUser(db.Model):
    creater_user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)

    user = db.relationship('User', backref='creater_user')  # Adjust backref as needed


    # song = db.relationship('Song', backref='songs')

class NormalUser(db.Model):
    normal_user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)


class AdminUser(db.Model):
    admin_user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)


class Playlist(db.Model):
    playlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playlist_name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    thumbnail_url = db.Column(db.String(1000))  # Add this line to include the playlist thumbnail URL

    user = db.relationship('User', backref='playlists')


class PlaylistSong(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.playlist_id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.song_id'), primary_key=True)

    playlist = db.relationship('Playlist', backref='playlist_songs')
    song = db.relationship('Song', backref='playlist_songs')


class Rating(db.Model):
    __tablename__ = 'ratings'

    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.song_id'), primary_key=True)
    rating_value = db.Column(db.Integer, nullable=False)

    # Remove the backref argument
    user = db.relationship('User')
    song = db.relationship('Song')


class BlacklistedUser(db.Model):
    blacklisted_user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creater_user_id = db.Column(db.Integer, db.ForeignKey('creater_user.creater_user_id'), nullable=False)

    # Define the relationship to the CreaterUser table
    creater_user = db.relationship('CreaterUser', backref='blacklisted_users')