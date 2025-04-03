from utils import load_clubs, load_competitions
from flask import Flask, render_template, request, redirect, flash, url_for


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['GET', 'POST'])
def show_summary():
    if request.method == 'GET':
        return redirect(url_for('index'))

    email = request.form.get('email', None)
    if not email:
        flash(f"You need to enter an e-mail address.")
        return redirect(url_for('index'))

    club = next((club for club in clubs if club['email'] == email), None)

    if not club:
        flash(f"No club in database with the e-mail : {email}")
        return redirect(url_for('index'))

    return render_template('welcome.html',
                           club=club,
                           competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = [c for c in clubs if c['name'] == club][0]
    found_competition = [c for c in competitions
                         if c['name'] == competition][0]
    if found_club and found_competition:
        return render_template('booking.html',
                               club=found_club,
                               competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = \
        [c for c in competitions if c['name'] == request.form['competition']][
            0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    places_required = int(request.form['places'])
    competition['numberOfPlaces'] = int(
        competition['numberOfPlaces']) - places_required
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club,
                           competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
