from flask import Flask, request, redirect, url_for, flash
from flask import render_template,session
from flask import current_app as app
from application.models import *
from datetime import datetime
from werkzeug.security import check_password_hash
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy import desc



from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'mp3', 'wav'}  # Define the allowed file extensions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET","POST"])
def home():
    return render_template("index.html")


@app.route('/login/user', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            # if check_password_hash(user.password, password):
            normal_user = NormalUser.query.filter_by(user_id=user.userid).first()
            admin_user = AdminUser.query.filter_by(user_id=user.userid).first()

            if admin_user:
                flash('User not found in Normal user', 'error')
                return redirect(url_for('login_user'))
            elif normal_user:
                flash('Logged in as Normal User!', 'success')
                return redirect(url_for('normal_user_dashboard', username=username))
            else:
                flash('User not found in Normal or Admin User table', 'error')
                return redirect(url_for('login_user'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login_user'))

    return render_template('login.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            # if check_password_hash(user.password, password):
            normal_user = NormalUser.query.filter_by(user_id=user.userid).first()
            admin_user = AdminUser.query.filter_by(user_id=user.userid).first()

            if admin_user:
                flash('Logged in as Admin!', 'success')
                return redirect(url_for('admin_dashboard',username=username))
            elif normal_user:
                flash('Logged in as Normal User!', 'success')
                return redirect(url_for('normal_user_dashboard', username=username))
            else:
                flash('User not found in Normal or Admin User table', 'error')
                return redirect(url_for('login_admin'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login_admin'))

    return render_template('login_admin.html')

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()

    # Redirect the user to the login page
    return redirect(url_for('login_user'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        user_type = request.form['user-type']

        # Add user to the User table
        new_user = User(username=username, password=password, name=name, dob=dob)
        db.session.add(new_user)
        db.session.commit()

        # Add user to the appropriate user type table
        if user_type == 'normal':
            normal_user = NormalUser(user_id=new_user.userid)
            db.session.add(normal_user)
        elif user_type == 'admin':
            admin_user = AdminUser(user_id=new_user.userid)
            db.session.add(admin_user)

        db.session.commit()
        
        return redirect(url_for('login_user'))  # Change to the appropriate route

    return render_template('register.html')  # Update with your actual template file


@app.route('/<username>/dashboard')
def normal_user_dashboard(username):
    # Get user information
    user = User.query.filter_by(username=username).first()

    is_creater = CreaterUser.query.filter_by(user_id = user.userid).first()
    
    if is_creater:
        isCreater= True
    else:
        isCreater=False

    is_Admin = AdminUser.query.filter_by(user_id = user.userid).first()

    if is_Admin:
        isAdmin = True
    else:
        isAdmin = False

    # Section 2: Recommended Tracks
    recommended_tracks = Song.query.order_by(Song.ratings.desc()).limit(5).all()

    # Section 3: Playlists Created by the User
    user_playlists = Playlist.query.filter_by(user_id=user.userid).all()

    # Section 4: Display 3-4 songs genre-wise
    genres = Genre.query.all()
    genre_wise_songs = {}

    for genre in genres:
        genre_songs = Song.query.filter_by(genre_id=genre.genre_id).limit(4).all()
        genre_wise_songs[genre] = genre_songs

    return render_template('user_dashboard.html', user=user, recommended_tracks=recommended_tracks,
                           user_playlists=user_playlists, genre_wise_songs=genre_wise_songs, username=user.username, isCreater=isCreater,isAdmin=isAdmin)




@app.route('/<username>/register_as_creator', methods=['GET', 'POST'])
def register_as_creator(username):
    # Get user information

    if request.method == 'POST':
        user = User.query.filter_by(username=username).first()
        if user:
            new_creator = CreaterUser(user_id = user.userid)
            db.session.add(new_creator)
            db.session.commit()

            return redirect(url_for('creator_dashboard',username=username))
        
    else:
        return render_template('register_creator.html', username=username)



@app.route('/<username>/creator_dashboard', methods=['GET', 'POST'])
def creator_dashboard(username):
    # Get user information
    user = User.query.filter_by(username=username).first()
    # print(user)
    # Get the creator_user_id
    creator_user = CreaterUser.query.filter_by(user_id=user.userid).first()

    if creator_user:
        creator_user_id = CreaterUser.query.filter_by(user_id=user.userid).first().creater_user_id
    else:
        return render_template("register_creator.html", username=username)
    
    creator_user_id = creator_user.creater_user_id

    # Check if the creator_user_id is blacklisted
    if BlacklistedUser.query.filter_by(creater_user_id=creator_user_id).first():
        return render_template("blocked_creater.html", username=username)

    # Get the number of songs created by this creator
    song_count = Song.query.filter_by(creater_id=creator_user_id).count()

    # Get the average rating of all songs created by this creator
    avg_rating = db.session.query(func.avg(Song.ratings).label('average')).filter_by(creater_id=creator_user_id).scalar()

    # Get the number of albums created by this creator
    album_count = Album.query.filter_by(creater_user_id=creator_user_id).count()

    # Get the list of songs with this creator as the creater
    song_list = Song.query.filter_by(creater_id=creator_user_id).all()

    genres = Genre.query.all()

    # print(genres)
    if request.method == 'POST':
            if 'song_id' and 'edit-title' in request.form:
                print("HEYY")
                # It's an update
                song_id = request.form['song_id']
                song = Song.query.get(song_id)

                if song:
                    # Update song details
                    song.title = request.form['edit-title']
                    song.singer_name = request.form['edit-singer_name']
                    song.release_date = datetime.strptime(request.form['edit-release_date'], '%Y-%m-%d').date()
                    song.lyrics = request.form['edit-lyrics']
                    song.thumbnail_url = request.form['edit-thumbnail_url']

                    

                    # Update genre and album
                    song.genre_id = request.form['genre_id']
                    song.album.album_name = request.form['edit-album_name']

                    db.session.commit()

                    flash('Song updated successfully!')
                else:
                    flash('Song not found!')
            
            elif 'song_id' in request.form and request.form['song_id']:
                # It's a delete operation
                print("EHYY")
                song_id = request.form['song_id']
                song = Song.query.get(song_id)

                if song:
                    # Delete associated ratings
                    Rating.query.filter_by(song_id=song_id).delete()

                    # Delete associated playlist songs
                    PlaylistSong.query.filter_by(song_id=song_id).delete()
                    # Delete the song
                    db.session.delete(song)
                    db.session.commit()
                    song_list = Song.query.filter_by(creater_id=creator_user_id).all()

                    flash('Song deleted successfully!')
                else:
                    flash('Song not found!')


            else:
                # Retrieve form data
                title = request.form['title']
                singer_name = request.form['singer_name']
                release_date_str = request.form['release_date']
                lyrics = request.form['lyrics']
                thumbnail_url = request.form['thumbnail_url']

                release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()  # Convert the string to a date object

                duration_str = '00:05:00'
                duration = datetime.strptime(duration_str, '%H:%M:%S').time()  # Convert the string to a time object

                # Check if the file part is present in the request
                # if 'file' not in request.files:
                #     flash('No file part')
                #     print("NOT REQ")
                #     return redirect(request.url)

                file = request.files['file']

                # Check if the file is allowed
                if file and allowed_file(file.filename):
                    # Securely save the file to the upload folder
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)

                    # Assuming you have a logged-in creater_user
                    # creater_user_id = 1  # Replace with the actual creater_user_id

                    genre_id = request.form['genre_id']

                    # Get or create the album based on the provided album name
                    album_name = request.form['album_name']
                    album = Album.query.filter_by(album_name=album_name, creater_user_id=creator_user_id).first()

                    if not album:
                        # Album doesn't exist, create a new one
                        album = Album(
                            album_name=album_name,
                            genre_id=genre_id,  # Use the appropriate genre_id
                            creater_user_id=creator_user_id,
                            thumbnail_url=thumbnail_url
                        )
                        db.session.add(album)
                        db.session.commit()

                    # Insert into Song table
                    song = Song(
                        title=title,
                        singer_name=singer_name,
                        release_date=release_date,
                        lyrics=lyrics,
                        file_path=file_path,  # Save the file path in the database
                        album_id=album.album_id,
                        genre_id=genre_id,
                        ratings=1,  # You need to define ratings before using it
                        duration=duration,  # You need to define duration before using it
                        creater_id=creator_user_id,
                        thumbnail_url=thumbnail_url
                    )

                    db.session.add(song)
                    db.session.commit()

                return render_template('creator_dashboard.html', user=user, username=user.username, song_count=song_count, avg_rating=avg_rating, album_count=album_count, song_list=song_list, genres=genres)


    return render_template('creator_dashboard.html', user=user, username=user.username, song_count=song_count, avg_rating=avg_rating, album_count=album_count, song_list=song_list, genres=genres)



# from flask import jsonify

@app.route('/<username>/<int:song_id>', methods=['GET', 'POST'])
def song_page(username, song_id):
    # Get user information
    user = User.query.filter_by(username=username).first()

    # Get song information
    song = Song.query.get(song_id)

    is_creater = CreaterUser.query.filter_by(user_id = user.userid).first()

    if is_creater:
        isCreater= True
    else:
        isCreater = False

    is_Admin = AdminUser.query.filter_by(user_id = user.userid).first()

    if is_Admin:
        isAdmin = True
    else:
        isAdmin = False

    if user is None or song is None:
        # Handle the case where the user or song is not found
        flash('User or song not found', 'error')
        return redirect(url_for('normal_user_dashboard', username=username))

    if request.method == 'POST':
        # Get the rating value from the form

        # Check if the form was submitted for adding to the playlist
        if 'playlistOption' in request.form:
            playlist_option = request.form['playlistOption']

            if playlist_option == 'existing':
                # Adding to an existing playlist
                existing_playlist_id = request.form['existingPlaylist']

                # Check if the song is already in the playlist
                existing_entry = PlaylistSong.query.filter_by(playlist_id=existing_playlist_id, song_id=song.song_id).first()

                if not existing_entry:
                    # Add the song to the existing playlist
                    playlist_song = PlaylistSong(playlist_id=existing_playlist_id, song_id=song.song_id)
                    db.session.add(playlist_song)
                    db.session.commit()
                    flash('Song added to the existing playlist successfully!', 'success')
                else:
                    flash('Song is already in the playlist!', 'info')

            elif playlist_option == 'new':
                # Creating a new playlist
                new_playlist_name = request.form['newPlaylistName']
                new_playlist_thumbnail = request.form['newPlaylistThumbnail']

                # Create a new playlist
                new_playlist = Playlist(playlist_name=new_playlist_name, user_id=user.userid, thumbnail_url=new_playlist_thumbnail)
                db.session.add(new_playlist)
                db.session.commit()

                # Add the song to the new playlist
                playlist_song = PlaylistSong(playlist_id=new_playlist.playlist_id, song_id=song.song_id)
                db.session.add(playlist_song)
                db.session.commit()

                flash('Song added to the new playlist successfully!', 'success')
        else:

            rating_value = int(request.form['rating'])

            # Check if the user has already rated the song
            existing_rating = Rating.query.filter_by(user_id=user.userid, song_id=song.song_id).first()

            if existing_rating:
                # Update the existing rating
                existing_rating.rating_value = rating_value
            else:
                # Add a new rating entry
                new_rating = Rating(user_id=user.userid, song_id=song.song_id, rating_value=rating_value)
                print(rating_value)
                db.session.add(new_rating)

            # Commit changes to the database
            db.session.commit()

            # Calculate and update the average rating for the song
            update_average_rating(song.song_id)

    # Query the current user's rating for the song
    user_rating = Rating.query.filter_by(user_id=user.userid, song_id=song.song_id).first()

    # Get all ratings for the song
    all_ratings = Rating.query.filter_by(song_id=song.song_id).all()

    user_playlists = Playlist.query.filter_by(user_id=user.userid).all()

    # You can pass additional data to the template if needed
    return render_template(
            'song_page.html',
            username=username,
            track=song,
            user_rating=user_rating,
            all_ratings=all_ratings,
            isCreater=isCreater,
            user_playlists=user_playlists , isAdmin=isAdmin )
def update_average_rating(song_id):
    # Calculate the average rating for the given song
    average_rating = db.session.query(func.avg(Rating.rating_value)).filter_by(song_id=song_id).scalar()

    # Update the song's average rating in the database
    song = Song.query.get(song_id)
    song.ratings = round(average_rating, 2) if average_rating else None
    db.session.commit()



# from sqlalchemy import or_, and_

@app.route('/<username>/search', methods=['GET'])
def search(username):
    # Retrieve the search queries from the query parameters
    user = User.query.filter_by(username=username).first()

    is_creater = CreaterUser.query.filter_by(user_id = user.userid).first()

    if is_creater:
        isCreater= True
    else:
        isCreater = False

    is_Admin = AdminUser.query.filter_by(user_id = user.userid).first()

    if is_Admin:
        isAdmin = True
    else:
        isAdmin = False

    search_query = request.args.get('search_query', '')
    creater_name_query = request.args.get('creater_name', '')
    genre_query = request.args.get('genre_id', '')
    ratings_query = request.args.get('ratings', '')



    # Initialize an empty list to store the results
    matching_songs = []

    genre = Genre.query.all()

    # Perform searches for songs based on individual queries
    if search_query:
        song_list = Song.query.filter(Song.title.ilike(f'%{search_query}%')).all()
        matching_songs.extend(song_list)

    if creater_name_query:
        creater_user = (
            CreaterUser.query
            .join(User, CreaterUser.user_id == User.userid)  # Explicit join condition
            .filter(User.name.ilike(f'%{creater_name_query}%'))
            .first()
        )
        if creater_user:
            song_list = Song.query.filter(Song.creater_id == creater_user.creater_user_id).all()
            matching_songs.extend(song_list)


    if genre_query:
        song_list = Song.query.filter(Song.genre_id == genre_query).all()
        matching_songs.extend(song_list)

    if ratings_query:
        song_list = Song.query.filter(Song.ratings >= ratings_query).all()
        matching_songs.extend(song_list)

    # Pass the matching songs to the template
    return render_template('song_search.html', matching_songs=matching_songs,
                           search_query=search_query, creater_name_query=creater_name_query,
                           genre_query=genre_query, ratings_query=ratings_query, username=username, all_genres = genre, isCreater=isCreater, isAdmin=isAdmin)





# ADMIN DASHBOARD -----------------------------------------------------



@app.route("/<username>/admin_dashboard", methods=['GET', 'POST'])
def admin_dashboard(username):
    # Count of Normal users
    user = User.query.filter_by(username=username).first()

    is_creater = CreaterUser.query.filter_by(user_id = user.userid).first()

    if is_creater:
        isCreater= True
    else:
        isCreater = False

    is_Admin = AdminUser.query.filter_by(user_id = user.userid).first()

    if is_Admin:
        isAdmin = True
    else:
        isAdmin = False

    # Count of Creater users
    creater_users_count = CreaterUser.query.count()

    # Count of Admin users
    admins_count = AdminUser.query.count()

    # Number of tracks
    number_of_tracks = Song.query.count()

    # Number of albums
    number_albums = Album.query.count()

    normal_users_count = User.query.count() - admins_count - creater_users_count

    # Number of genres
    genre_count = Genre.query.count()

    # Top 5 songs with highest average ratings
    top_songs = Song.query.order_by(desc(Song.ratings)).limit(5).all()

    # Genres with the most songs
    popular_genres = Genre.query.join(Song).group_by(Genre.genre_id).order_by(desc(db.func.count(Song.song_id))).limit(5).all()
    popular_genres_data = [{'genre_name': genre.genre_name, 'song_count': len(genre.songs)} for genre in popular_genres]

    # Creators with most uploads (Top 5)
    # Creators with most uploads (Top 5)
    top_creators = CreaterUser.query.join(Song).group_by(CreaterUser.creater_user_id).order_by(desc(db.func.count(Song.song_id))).limit(5).all()

    # Convert CreaterUser objects to dictionaries
    top_creators_data = [{'username': User.query.get(creator.user_id).username, 'upload_count': len(creator.songs)} for creator in top_creators]

    recommended_tracks = Song.query.order_by(Song.ratings.desc()).limit(5).all()

    if(request.method == 'POST'):
        if 'song_id' in request.form and request.form['song_id']:
                    # It's a delete operation
                    print("EHYY")
                    song_id = request.form['song_id']
                    song = Song.query.get(song_id)

                    if song:
                        # Delete associated ratings
                        Rating.query.filter_by(song_id=song_id).delete()

                        # Delete associated playlist songs
                        PlaylistSong.query.filter_by(song_id=song_id).delete()

                        # Delete the song
                        db.session.delete(song)
                        db.session.commit()
                        recommended_tracks = Song.query.order_by(Song.ratings.desc()).limit(5).all()

                        flash('Song deleted successfully!')
                    else:
                        flash('Song not found!')
        
        if 'blacklist_song_id' in request.form and request.form['blacklist_song_id']:
            blacklist_song_id = request.form['blacklist_song_id']
            
            # Get the creator_user_id based on the provided song_id
            song = Song.query.get(blacklist_song_id)
            if song:
                creator_user_id = song.creater_user.creater_user_id
                
                # Check if the creator_user_id is not already blacklisted
                if not BlacklistedUser.query.filter_by(creater_user_id=creator_user_id).first():
                    # Add the creator_user_id to the blacklisted_users table
                    blacklisted_user = BlacklistedUser(creater_user_id=creator_user_id)

                    # user = User.query.filter_by()e

                    db.session.add(blacklisted_user)
                    db.session.commit()
                    flash(f'Creator {song.creater_user.user.username} blacklisted successfully!')
                else:
                    flash(f'Creator {song.creater_user.user.username} is already blacklisted.')
            else:
                flash('Invalid song ID for blacklisting.')

            return redirect(url_for('admin_dashboard', username=username))
        
        elif 'whitelist_song_id' in request.form and request.form['whitelist_song_id']:
            whitelist_song_id = request.form['whitelist_song_id']

            # Get the creator_user_id based on the provided song_id
            song = Song.query.get(whitelist_song_id)
            if song:
                creator_user_id = song.creater_user.creater_user_id

                # Check if the creator_user_id is blacklisted
                blacklisted_user = BlacklistedUser.query.filter_by(creater_user_id=creator_user_id).first()

                if blacklisted_user:
                    # Remove the creator_user_id from the blacklisted_users table
                    db.session.delete(blacklisted_user)
                    db.session.commit()
                    flash(f'Creator {song.creater_user.user.username} whitelisted successfully!')
                else:
                    flash(f'Creator {song.creater_user.user.username} is not blacklisted.')
            else:
                flash('Invalid song ID for whitelisting.')

            return redirect(url_for('admin_dashboard', username=username))


    # Convert Song objects to dictionaries
    top_songs_data = [{'title': song.title, 'ratings': song.ratings} for song in top_songs]

    print(top_songs_data, "\n", top_creators_data,"\n", popular_genres_data)
    return render_template("admin_dashboard.html", username=username,
                           normal_users_count=normal_users_count,
                           creater_users_count=creater_users_count,
                           admins_count=admins_count,
                           number_of_tracks=number_of_tracks,
                           number_albums=number_albums,
                           genre_count=genre_count,
                           top_songs=top_songs_data,
                           popular_genres=popular_genres_data,
                           top_creators=top_creators_data, songs=recommended_tracks, isCreater=isCreater, isAdmin=isAdmin)



@app.route('/<username>/<playlist_name>/<int:playlist_id>', methods=['GET','POST'])
def playlist_page(username, playlist_name,playlist_id):
    user = User.query.filter_by(username=username).first()

    is_creater = CreaterUser.query.filter_by(user_id = user.userid).first()
    
    if is_creater:
        isCreater= True
    else:
        isCreater=False
    is_Admin = AdminUser.query.filter_by(user_id = user.userid).first()

    if is_Admin:
        isAdmin = True
    else:
        isAdmin = False
    # Get user information
    user = User.query.filter_by(username=username).first()

    # Get playlist information
    playlist = Playlist.query.get(playlist_id)

    if user is None or playlist is None:
        # Handle the case where the user or playlist is not found
        flash('User or playlist not found', 'error')
        return redirect(url_for('normal_user_dashboard', username=username))

    # Get songs in the playlist
    playlist_songs = db.session.query(Song).join(PlaylistSong).filter(PlaylistSong.playlist_id == playlist_id).all()

    return render_template('playlist_page.html', user=user, playlist=playlist, playlist_songs=playlist_songs, isCreater=isCreater, isAdmin=isAdmin)

