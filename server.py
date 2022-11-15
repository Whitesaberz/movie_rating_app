"""Server for movie ratings app."""

from flask import Flask, render_template, request, flash, session, redirect
from model import connect_to_db, db
import crud
from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = "moviebuff"
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def homepage():
    return render_template("homepage.html")

@app.route('/movies')
def all_movies():
    movies = crud.get_all_movies()
    return render_template("all_movies.html", movies = movies)

@app.route('/movies/<movie_id>')
def movie_info(movie_id):
    movie = crud.get_movie_by_id(movie_id)
    return render_template("movie_details.html", movie=movie)

@app.route('/users')
def all_users():
    # email = session.get("user_email")
    # user = crud.get_user_by_email(email)
    # if session[user] == None:
    #     flash("Please sign in.")
    #     return redirect('/')
    # else:
        users = crud.get_all_users()
        return render_template("all_users.html", users = users)
    
@app.route('/users/<user_id>')
def user_info(user_id):
    user = crud.get_user_by_id(user_id)
    return render_template("user_details.html", user = user)

@app.route('/users', methods=['POST'])
def register_user():
    email = request.form.get("email")
    password = request.form.get("password")

    user = crud.get_user_by_email(email)
    if user:
        flash("User email already in use.")
    else:
        user = crud.create_user(email, password)
        db.session.add(user)
        db.session.commit()
        flash("User account created, please log in.")
        
        return redirect('/')
    
@app.route('/login', methods=['POST'])
def retrieve_login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = crud.get_user_by_email(email)
    if not user or user.password != password:
        flash("The email or password you entered was incorrect.")
    else:
        session["user_email"] = user.email
        flash(f"Signed in successfully, {user.email}!")

    return redirect("/")

@app.route('/movies/<movie_id>/ratings', methods=['POST'])
def add_new_rating(movie_id):
    user_session = session.get("user_email")
    rating_score = request.form.get("rating")
    
    if user_session is None:
        flash("Please log in to use this function.")
    elif not rating_score:
        flash("Please enter a rating score.")
    else:
        user = crud.get_user_by_email(user_session)
        movie = crud.get_movie_by_id(movie_id)
        rating = crud.create_rating(user, movie, int(rating_score))
        db.session.add(rating)
        db.session.commit()
        flash(f"You gave {movie.title} a {rating_score}")
    return redirect(f'/movies/{movie_id}')


if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)
