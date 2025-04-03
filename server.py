from datetime import datetime

from utils import load_clubs, load_competitions
from flask import Flask, render_template, request, redirect, flash, url_for


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()

MAXIMUM_PLACES_AUTHORIZED = 12


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['GET', 'POST'])
def show_summary():
    if request.method == 'POST':
        email = request.form.get('email', None)
        if not email:
            flash(f"You need to enter an e-mail address.")
            return redirect(url_for('index'))

        club = next((club for club in clubs if club['email'] == email), None)

        if not club:
            flash(f"No club in database with the e-mail : {email}")
            return redirect(url_for('index'))

    else:
        club_name = request.args.get('club', None)
        club = next((c for c in clubs if c['name'] == club_name), None)
        if not club:
            return redirect(url_for('index'))

    return render_template('welcome.html',
                           club=club,
                           competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = next((c for c in clubs if c['name'] == club), None)
    found_competition = next((c for c in competitions
                              if c['name'] == competition), None)

    time_directive = '%Y-%m-%d %H:%M:%S'
    time_competition = found_competition.get('date', None)
    is_date_over = (datetime.today() >
                    datetime.strptime(time_competition, time_directive))

    if is_date_over:
        flash("You can't book places for past competitions")
        return redirect(url_for('show_summary', club=club))

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
    form_competition = request.form.get('competition', None)
    competition = next(
        (c for c in competitions if c['name'] == form_competition),
        None)
    form_club = request.form.get('club', None)
    club = next((c for c in clubs if c['name'] == form_club), None)

    time_directive = '%Y-%m-%d %H:%M:%S'
    time_competition = competition.get('date', None)
    is_date_over = (datetime.today() >
                    datetime.strptime(time_competition, time_directive))

    if is_date_over:
        flash("You can't book places for past competitions")
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions)

    places_required = min(MAXIMUM_PLACES_AUTHORIZED,
                          int(request.form['places']),
                          int(club['points']))
    competition['numberOfPlaces'] = int(
        competition['numberOfPlaces']) - places_required
    flash('Great-booking complete!')
    return render_template('welcome.html',
                           club=club,
                           competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
