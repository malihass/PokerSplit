from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pokerSplit import *


# Set up app
app = Flask(__name__)
# Say where the database is (relative path)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# Init database
db = SQLAlchemy(app)

# Create a model
class Players(db.Model):
    # Set up the columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    chips_remaining = db.Column(db.String(200), nullable=False)
    money_invested = db.Column(db.String(200), nullable=False)
    preferred_financial_partner = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        # what to do when we create a new element
        return '<Player %r>' % self.id

# Init the state
def initFromDB(players):
    # Player Names
    nameList = [] 
    for player in players:
        nameList.append(player.name)

    # Make the slate
    initialSlate = {}
    for player in players:
        try:
            initialSlate[player.name] = float(player.chips_remaining)
        except:
            errorSignal = 1
            errorMessage = 'Check chips remaining for ' + player.name
            return (errorSignal, errorMessage)           
        if initialSlate[player.name]<0:
            errorSignal = 1
            errorMessage = 'Chips remaining for ' + player.name + ' should be positive'
            return (errorSignal, errorMessage)           

    if sum([value for _, value in initialSlate.items()])==0:
        errorSignal = 1
        errorMessage = 'Slate probably incomplete'
        return (errorSignal, errorMessage)

    # Money invested
    moneyInvested = {}
    for player in players:
        try:
            moneyInvested[player.name] = float(player.money_invested)
        except:
            errorSignal = 1
            errorMessage = 'Check money invested for ' + player.name
            return (errorSignal, errorMessage)           
        if moneyInvested[player.name]<=0:
            errorSignal = 1
            errorMessage = 'Money invested for ' + player.name + ' should be strictly positive'
            return (errorSignal, errorMessage)           

    # Preferred financial partner
    preferredLinks = {}
    for player in players:
        linkstmp = player.preferred_financial_partner.strip().split(';')
        links = [link.strip() for link in linkstmp]
        for link in links: 
            if not (link in nameList) and (not link==''):
                errorSignal = 1
                errorMessage = 'Check preferred financial partner for ' + player.name
                return (errorSignal, errorMessage)
        
        if links==['']:
            links = []
        preferredLinks[player.name] = links
    
    errorSignal = 0
    return (errorSignal, initialSlate, moneyInvested, preferredLinks)

# Create index route
@app.route('/',methods=['POST','GET'])
def index():
    if request.method=='POST' and request.form['btn_identifier'] == 'playerList':
        player_name = request.form['name']
        player_chips_remaining = request.form['chips']
        player_money_invested = request.form['money']
        player_preferred_financial_partner = request.form['partner']
        # create a new player from the input
        new_player = Players(name=player_name,
                            chips_remaining=player_chips_remaining,
                            money_invested=player_money_invested,
                            preferred_financial_partner=player_preferred_financial_partner)
        try:
            # Try to add player to DB
            db.session.add(new_player)
            db.session.commit()
            return redirect('/')
        except: 
            return 'There was an issue adding player to database'

    elif request.method=='POST' and request.form['btn_identifier'] == 'playerTransactions':
        players = Players.query.order_by(Players.name).all()
        # Make the slate
        init_conditions = initFromDB(players)
        if init_conditions[0] == 1:
            # Failure because of links 
            msg = init_conditions[1]
            return render_template("index.html",players=players,slateOutput=msg)
        elif init_conditions[0] == 0:
            # Success
            # Construct the split
            slate = PlayerSlate(initialSlate=init_conditions[1],
                                moneyInvested=init_conditions[2],
                                preferredLinks=init_conditions[3])
            
            # Equilibriate scores
            slate.equilibrate()
            # Get list of transactions
            Log = slate.getLogTransactions()
            return render_template("index.html",players=players,slateOutput=Log)
    
    elif request.method=='POST' and request.form['btn_identifier'] == 'clearTransactions':
        players = Players.query.order_by(Players.name).all()
        #return render_template("index.html",players=players,slateOutput='')      
        return redirect("/")      

    elif request.method=='POST' and request.form['btn_identifier'] == 'clearPlayerList':
        players = Players.query.order_by(Players.name).all()
        idList = [player.id for player in players]
        for id in idList:
            player_to_delete = Players.query.get_or_404(id)
            db.session.delete(player_to_delete)
        db.session.commit()
        return redirect("/")      
   
    else:
        # Order by date created and return everything
        players = Players.query.order_by(Players.name).all()
        return render_template("index.html",players=players)

@app.route('/delete/<int:id>')
def delete(id):
    player_to_delete = Players.query.get_or_404(id)
    try:
        db.session.delete(player_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "Issue during delete"

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    player_to_update = Players.query.get_or_404(id)
    if request.method=='POST':
        player_to_update.name = request.form['name']
        player_to_update.chips_remaining = request.form['chips']
        player_to_update.money_invested = request.form['money']
        player_to_update.preferred_financial_partner = request.form['partner']
        try:
            db.session.commit()
            return redirect('/') 
        except:
            return "There was an issue for update"
    else:
        return render_template('update.html',player=player_to_update)


if __name__ == "__main__":
     app.run(debug=True)
