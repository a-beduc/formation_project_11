from datetime import datetime
import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        for club in listOfClubs:
            club['points'] = int(club['points'])
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        for comp in listOfCompetitions:
            comp['numberOfPlaces'] = int(comp['numberOfPlaces'])
        return listOfCompetitions


def is_competition_in_past(competition, date=None):
    time_directive = '%Y-%m-%d %H:%M:%S'
    time_competition = competition.get('date', None)
    date = date or datetime.today()
    return date > datetime.strptime(time_competition, time_directive)


def split_competitions_per_dates(competitions_list):
    past_comps_ids, future_comps_ids = [], []
    date = datetime.today()
    for c_id, comp in enumerate(competitions_list):
        if is_competition_in_past(comp, date=date):
            past_comps_ids.append(c_id)
        else:
            future_comps_ids.append(c_id)
    return past_comps_ids, future_comps_ids


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

MAXIMUM_PLACES_AUTHORIZED = 12
PAST_TRANSACTION = {}

past_competitions_ids, future_competitions_ids = (
    split_competitions_per_dates(competitions))


def get_split_competitions():
    past_comps = [competitions[c_id] for c_id in past_competitions_ids]
    future_comps = [competitions[c_id] for c_id in future_competitions_ids]
    return past_comps, future_comps


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary',methods=['POST'])
def showSummary():
    try:
        club = [club for club in clubs if club['email'] == request.form.get('email')][0]
    except IndexError:
        flash('The provided email is not valid.')
        return render_template('index.html'), 401
    past_competitions, future_competitions = get_split_competitions()
    return render_template('welcome.html',club=club,past_competitions=past_competitions,future_competitions=future_competitions)


@app.route('/book', defaults={'competition': '', 'club': ''}, strict_slashes=False)
@app.route('/book/<competition>', defaults={'club': ''}, strict_slashes=False)
@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    elif foundClub:
        flash("Something went wrong-please try again")
        past_competitions, future_competitions = get_split_competitions()
        return render_template('welcome.html', club=foundClub, past_competitions=past_competitions,future_competitions=future_competitions), 404
    else:
        flash("Lost connection, please login")
        return redirect(url_for('index'))


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form.get('competition', None)), None)
    club = next((c for c in clubs if c['name'] == request.form.get('club', None)), None)

    if club and competition:
        try:
            placesRequired = int(request.form.get('places', 0))
        except ValueError:
            placesRequired = 0
        if placesRequired <= 0:
            flash('You must enter a valid number of places')
            return render_template('booking.html', club=club, competition=competition), 403

        quota_left = MAXIMUM_PLACES_AUTHORIZED - PAST_TRANSACTION.get((competition['name'], club['name']), 0)
        if quota_left <= 0:
            flash(f"Your club has already bought {MAXIMUM_PLACES_AUTHORIZED} places for this competition. No more purchases allowed")
            past_competitions, future_competitions = get_split_competitions()
            return render_template('welcome.html', club=club,past_competitions=past_competitions,future_competitions=future_competitions), 302
        if placesRequired > quota_left:
            flash(f"Your request exceed the maximum allowed. Requested : {placesRequired}, still allowed {quota_left}")
            return render_template('booking.html', club=club, competition=competition), 403

        purchase_power = int(club.get('points', 0))
        if purchase_power < placesRequired:
            flash(f"You don't have enough points to proceed with your request. Requested : {placesRequired}, still allowed : {purchase_power}")
            return render_template('booking.html', club=club, competition=competition), 403

        competition_available = int(competition.get('numberOfPlaces', 0))
        if competition_available < placesRequired:
            flash(f"Not enough available places for this competition. Requested : {placesRequired}, still available : {competition_available}")
            return render_template('booking.html', club=club, competition=competition), 403

        if is_competition_in_past(competition):
            flash("This competition is already over.")
            past_competitions, future_competitions = get_split_competitions()
            return render_template('welcome.html', club=club,past_competitions=past_competitions,future_competitions=future_competitions), 302

        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        club['points'] = int(club['points']) - placesRequired

        PAST_TRANSACTION.setdefault((competition['name'], club['name']), 0)
        PAST_TRANSACTION[(competition['name'], club['name'])] += placesRequired

        flash('Great-booking complete!')
        past_competitions, future_competitions = get_split_competitions()
        return render_template('welcome.html', club=club, past_competitions=past_competitions,future_competitions=future_competitions)
    elif club:
        flash("Something went wrong-please try again")
        past_competitions, future_competitions = get_split_competitions()
        return render_template('welcome.html', club=club, past_competitions=past_competitions,future_competitions=future_competitions), 404
    else:
        flash("Lost connection, please login")
        return redirect(url_for('index'))


@app.route('/board')
def board():
    return render_template('board.html', clubs=clubs)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))

#
# if __name__ == '__main__':
#     app.run(debug=True)
