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


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

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
    return render_template('welcome.html',club=club,competitions=competitions)


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
        return render_template('welcome.html', club=foundClub, competitions=competitions), 404
    else:
        flash("Lost connection, please login")
        return redirect(url_for('index'))


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)
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

        purchase_power = int(club.get('points', 0))
        if purchase_power < placesRequired:
            flash(f"You don't have enough points to proceed with your request. Requested : {placesRequired}, still allowed : {purchase_power}")
            return render_template('booking.html', club=club, competition=competition), 403

        competition_available = int(competition.get('numberOfPlaces', 0))
        if competition_available < placesRequired:
            flash(f"Not enough available places for this competition. Requested : {placesRequired}, still available : {competition_available}")
            return render_template('booking.html', club=club, competition=competition), 403

        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired

        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)
    elif club:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions), 404
    else:
        flash("Lost connection, please login")
        return redirect(url_for('index'))


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
