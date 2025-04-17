from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    """
    Extract data from a json file and return it as a list.
    :return: a list of dictionaries containing club information
    :rtype: List[Dict]
    """
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
        for club in list_of_clubs:
            club['points'] = int(club['points'])
        return list_of_clubs


def loadCompetitions():
    """
    Extract data from a json file and return it as a list.
    :return: a list of dictionaries containing competition information
    :rtype: List[Dict]
    """
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        for comp in list_of_competitions:
            comp['numberOfPlaces'] = int(comp['numberOfPlaces'])
        return list_of_competitions


def is_competition_in_past(competition, date=None):
    """
    Check if competition is in the past and return a bool.
    :param Dict competition: competition dictionary
    :param datetime date: Optional date in case of a test using a fixed date
    :return: A boolean indicating if competition is in the past
    :rtype: bool
    """
    time_directive = '%Y-%m-%d %H:%M:%S'
    time_competition = competition.get('date', None)
    date = date or datetime.today()
    return date > datetime.strptime(time_competition, time_directive)


def split_competitions_per_dates(competitions_list):
    """
    Extract the id of competition from a list and separate them in two
    list based on the competition date.
    :param List competitions_list:
    :return: two lists containing int representing the index of
             dictionaries found in the competitions list
    :rtype: Tuple[List[int], List[int]]
    """
    past_comps_ids, future_comps_ids = [], []
    date = datetime.today()
    for c_id, comp in enumerate(competitions_list):
        if is_competition_in_past(comp, date=date):
            past_comps_ids.append(c_id)
        else:
            future_comps_ids.append(c_id)
    return past_comps_ids, future_comps_ids


# Initialize the Flask app.
app = Flask(__name__)
app.secret_key = 'something_special'

# Initialize the application data.
competitions = loadCompetitions()
clubs = loadClubs()

# Misc globals
MAXIMUM_PLACES_AUTHORIZED = 12
PAST_TRANSACTION = {}
past_competitions_ids, future_competitions_ids = (
    split_competitions_per_dates(competitions))


def get_split_competitions():
    """
    Use two comprehension list to get the competitions list for past
    dates and future dates.
    :return: two list of dictionaries containing competition information
    :rtype: Tuple[List[Dict], List[Dict]]
    """
    past_comps = [competitions[c_id] for c_id in past_competitions_ids]
    future_comps = [competitions[c_id] for c_id in future_competitions_ids]
    return past_comps, future_comps


@app.route('/')
def index():
    """
    Render the login page where users can enter their email to log in.
    :return: Rendered HTML of the index page.
    :rtype: str
    """
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    """
    Display the welcome template after the user login.
    :return: Rendered HTML of the summary page or the index page with a
             401 status if login fails.
    :rtype: str | Tuple[str, int]
    """
    try:
        club = [club for club in clubs if club['email'] == request.form.get(
            'email')][0]
    except IndexError:
        flash('The provided email is not valid.')
        return render_template('index.html'), 401
    past_competitions, future_competitions = get_split_competitions()
    return render_template('welcome.html',
                           club=club,
                           past_competitions=past_competitions,
                           future_competitions=future_competitions)


@app.route('/book', defaults={'competition': '', 'club': ''},
           strict_slashes=False)
@app.route('/book/<competition>', defaults={'club': ''},
           strict_slashes=False)
@app.route('/book/<competition>/<club>')
def book(competition, club):
    """
    Display the booking page for a given competition and club.
    :param str competition: Name of the competition
    :param str club: Name of the club
    :return: Booking page id both parameters are valid,
             otherwise the welcome or the index page with appropriate
             error/status.
    :rtype: str | Tuple[str, int] | BaseResponse
    """
    found_club = next((c for c in clubs if c['name'] == club), None)
    found_competition = next(
        (c for c in competitions if c['name'] == competition), None)
    if found_club and found_competition:
        return render_template('booking.html',
                               club=found_club,
                               competition=found_competition)
    elif found_club:
        flash("Something went wrong-please try again")
        past_competitions, future_competitions = get_split_competitions()
        return render_template('welcome.html',
                               club=found_club,
                               past_competitions=past_competitions,
                               future_competitions=future_competitions), 404
    else:
        flash("Lost connection, please login")
        return redirect(url_for('index'))


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    """
    Verify the request and process the booking of places for a club if
    conditions are met.
    It can :
        - Process request (process)
        - Block request and render welcome.html (block)
        - Block request and render booking.html (try again)
        - Error (logout)

    Validates constraints :
        - Number of places requested
          (Int between 0 and 12)
        - Club's available points
        - Remaining competition places
        - Maximum quota of places per club per competition
          (Verify past transactions)
        - Competition date validity

    :return: Rendered page with updated points, a status and a message.
    :rtype: Tuple[str, int] | str | BaseResponse
    """
    competition = next((c for c in competitions if c['name'] ==
                        request.form.get('competition', None)),
                       None)
    club = next((c for c in clubs if c['name'] ==
                 request.form.get('club', None)),
                None)

    if club and competition:
        try:
            places_required = int(request.form.get('places', 0))
        except ValueError:
            places_required = -1

        # Zero place requested (process)
        if places_required == 0:
            past_competitions, future_competitions = get_split_competitions()
            flash("You didn't buy any places")
            return render_template(
                'welcome.html',
                club=club,
                past_competitions=past_competitions,
                future_competitions=future_competitions), 200

        # Negative or wrong type of places requested (try again)
        if places_required < 0:
            flash('You must enter a valid number of places')
            return render_template(
                'booking.html',
                club=club,
                competition=competition), 400

        # Verify past transaction to update maximum authorized
        quota_left = MAXIMUM_PLACES_AUTHORIZED - PAST_TRANSACTION.get(
            (competition['name'], club['name']), 0)

        # Club already bought the maximum places authorized (block)
        if quota_left <= 0:
            flash(f"Your club has already bought {MAXIMUM_PLACES_AUTHORIZED} "
                  f"places for this competition. No more purchases allowed")
            past_competitions, future_competitions = get_split_competitions()
            return render_template(
                'welcome.html',
                club=club,
                past_competitions=past_competitions,
                future_competitions=future_competitions), 302

        # Request would exceed maximum authorized (try again)
        if places_required > quota_left:
            flash(f"Your request exceed the maximum allowed. Requested : "
                  f"{places_required}, still allowed {quota_left}")
            return render_template(
                'booking.html',
                club=club,
                competition=competition), 400

        purchase_power = int(club.get('points', 0))

        # Not enough club points (try again)
        if purchase_power < places_required:
            flash(f"You don't have enough points to proceed with your "
                  f"request. Requested : {places_required}, still allowed : "
                  f"{purchase_power}")
            return render_template(
                'booking.html',
                club=club,
                competition=competition), 400

        competition_available = int(competition.get('numberOfPlaces', 0))

        # Not enough competition places (try again)
        if competition_available < places_required:
            flash(f"Not enough available places for this competition. "
                  f"Requested : {places_required}, still available : "
                  f"{competition_available}")
            return render_template(
                'booking.html',
                club=club,
                competition=competition), 400

        # Is competition in the past (block)
        if is_competition_in_past(competition):
            flash("This competition is already over.")
            past_competitions, future_competitions = get_split_competitions()
            return render_template(
                'welcome.html',
                club=club,
                past_competitions=past_competitions,
                future_competitions=future_competitions), 302

        # Process request (process)
        competition['numberOfPlaces'] = (
                int(competition['numberOfPlaces']) - places_required)
        club['points'] = int(club['points']) - places_required

        PAST_TRANSACTION.setdefault((competition['name'], club['name']), 0)
        PAST_TRANSACTION[(competition['name'], club['name'])] += (
            places_required)

        flash('Great-booking complete!')
        past_competitions, future_competitions = get_split_competitions()
        return render_template(
            'welcome.html',
            club=club,
            past_competitions=past_competitions,
            future_competitions=future_competitions)

    # competition not found (block)
    elif club:
        flash("Something went wrong-please try again")
        past_competitions, future_competitions = get_split_competitions()
        return render_template(
            'welcome.html',
            club=club,
            past_competitions=past_competitions,
            future_competitions=future_competitions), 404

    # club not found (logout)
    else:
        flash("Lost connection, please login")
        return redirect(url_for('index'))


@app.route('/board')
def board():
    """
    Render the board page where non-logged users can see clubs points.
    :return: Rendered HTML of the board page.
    :rtype: str
    """
    return render_template('board.html', clubs=clubs)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    """
    Redirect the user to the login page.
    :return: Redirect toward index.html
    :rtype: BaseResponse
    """
    return redirect(url_for('index'))


# # Uncomment these lines if you want to launch the application.
#
# if __name__ == '__main__':
#     app.run(debug=True)
