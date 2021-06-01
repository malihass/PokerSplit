from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    prefered_financial_partner = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        # what to do when we create a new element
        return '<Player %r>' % self.id


# Create index route
@app.route('/',methods=['POST','GET'])
def index():
    if request.method=='POST':
        player_name = request.form['name']
        player_chips_remaining = request.form['chips']
        player_money_invested = request.form['money']
        player_prefered_financial_partner = request.form['partner']
        # create a new player from the input
        new_player = Players(name=player_name,
                            chips_remaining=player_chips_remaining,
                            money_invested=player_money_invested,
                            prefered_financial_partner=player_prefered_financial_partner)
        try:
            # Try to add player to DB
            db.session.add(new_player)
            db.session.commit()
            return redirect('/')
        except: 
            return 'There was an issue'
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
        player_to_update.prefered_financial_partner = request.form['partner']
        try:
            db.session.commit()
            return redirect('/') 
        except:
            return "There was an issue for update"
    else:
        return render_template('update.html',player=player_to_update)


if __name__ == "__main__":
     app.run(debug=True)
