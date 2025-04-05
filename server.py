from utils import (
    load_clubs,
    load_competitions,
    is_competition_in_past,
    retrieve_data,
    book_places,
)
from flask import Flask, render_template, request, redirect, flash, url_for


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()

MAXIMUM_PLACES_AUTHORIZED = 12
CACHED_QUERY = {}


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

        club = retrieve_data(email, clubs, CACHED_QUERY, lookup_key='email')

        if not club:
            flash(f"No club in database with the e-mail : {email}")
            return redirect(url_for('index'))

    else:
        club_name = request.args.get('club', None)
        club = retrieve_data(club_name, clubs, CACHED_QUERY)
        if not club:
            return redirect(url_for('index'))

    return render_template('welcome.html',
                           club=club,
                           competitions=competitions,
                           clubs=clubs)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = retrieve_data(club, clubs, CACHED_QUERY)
    found_competition = retrieve_data(competition, competitions, CACHED_QUERY)

    if (found_competition and
            is_competition_in_past(found_competition)):
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
                               competitions=competitions,
                               clubs=clubs)


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    form_competition = request.form.get('competition', None)
    competition = retrieve_data(form_competition, competitions, CACHED_QUERY)

    form_club = request.form.get('club', None)
    club = retrieve_data(form_club, clubs, CACHED_QUERY)

    if competition and is_competition_in_past(competition):
        flash("You can't book places for past competitions")
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions)

    places_request = request.form.get('places', 0)
    club['points'], competition['numberOfPlaces'] = book_places(
        places_request, club, competition, MAXIMUM_PLACES_AUTHORIZED)
    flash('Great-booking complete!')
    return render_template('welcome.html',
                           club=club,
                           competitions=competitions,
                           clubs=clubs)


@app.route('/board/<club>', methods=['GET'])
def board(club):
    club_found = retrieve_data(club, clubs, CACHED_QUERY)
    if club_found:
        return render_template('board.html',
                               club=club_found,
                               competitions=competitions,
                               clubs=clubs)
    else:
        return redirect(url_for('show_summary', club=club_found))


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
