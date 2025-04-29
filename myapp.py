import sqlite3
from flask import Flask, render_template, request, session, url_for, redirect
import os
from datetime import datetime

#return render_template('home.html')


def init_db():
    conn = sqlite3.connect('RolsaDatabase')
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    c.execute(""" CREATE TABLE IF NOT EXISTS tblCustomer
        (customerID integer PRIMARY KEY AUTOINCREMENT,
        firstname text,
        surname text,
        email text UNIQUE,
        password text)
        """)

    c.execute(""" CREATE TABLE IF NOT EXISTS tblProduct
        (productID integer PRIMARY KEY AUTOINCREMENT,
        name text,
        description text,
        image text,
        installationPrice text,
        consultationPrice text)
        """)
    

    c.execute('DROP TABLE IF EXISTS tblBooking')

    c.execute("""CREATE TABLE IF NOT EXISTS tblBooking (
        bookingID integer PRIMARY KEY AUTOINCREMENT,
        customerID integer,
        productID integer,
        scheduleDate date,
        installationOrConsultation text,
        FOREIGN KEY(customerID) REFERENCES tblCustomer(customerID),
        FOREIGN KEY(productID) REFERENCES tblProduct(productID)
        )
        """)



    #c.execute(""" CREATE TABLE IF NOT EXISTS tblBillingInfo
     #   (billingID integer PRIMARY KEY AUTOINCREMENT,
    #    firstname text,
     #   surname text,
    #    address text,
    #    country text,
    #    city text,
    #    ZIPCode text,
    #    phoneNum text)
    #    """)


    #ADDS DATA TO THE tblProduct TABLE

    #products = [
    #    ('Home Solar Panels', 
    #    'Home solar panels transform energy within the rays from the sun into electricity, giving you electricity at no price',
    #    'https://www.yorkshireroofing.com/wp-content/uploads/2019/07/solar-example.jpg',
    #    '£3,000',
    #    '£50'),
    #
    #    ('Home Smart Meter',
    #    'Home smart meters allow you to view how much energy you are using(gas and electricity) on a small device in your home.',
    #    'https://images.ctfassets.net/620j9bwnh4b6/2flIOdYhRC9jJbLfIwgdES/ad00e5a89dc8a9fe987556688a93e74b/Eco-MoreWays-Smartt-Image-v1.png?w=1662&h=1168&q=60',
    #    '£50',
    #    '£20'),
    #
    #    ('Home Electric Vehicle Charger',
    #    'Home electric vehicle chargers allow you to charge your electric vehicle at home, negating the worry that your vehicle isnt charged enough',
    #    'https://media.istockphoto.com/vectors/electric-sedan-car-at-the-electro-charger-station-vector-id1412662318?k=20&m=1412662318&s=612x612&w=0&h=3vit_1DTmo2igctHV6IA1FyNlSiraIdJJpLLVju8RJw=',
    #    '£750',
    #    '£50')
    #]

    #c.executemany("""INSERT INTO tblProduct (name, description, image, installationPrice, consultationPrice) VALUES (?,?,?,?,?)""", products)

    #c.execute("""INSERT INTO tblCustomer (firstname, surname, email, password) VALUES (?,?,?,?)""", ("a", "a", "aa@aa.com","admin123"))

    conn.commit()
    conn.close()

init_db()

app = Flask(__name__, static_folder='static', template_folder='templates')


app.secret_key = 'session_managament_key'

@app.context_processor
def inject_logged_in_status():
    return {'logged_in': 'customer_id' in session}


@app.route('/log-in', methods=['POST', 'GET'])
def log_in():

    error = None
    email = None

    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']

        conn = sqlite3.connect('RolsaDatabase')
        c = conn.cursor()

        c.execute("SELECT * FROM tblCustomer WHERE email = ? AND password = ?", (email, password,))
        exsisting_account = c.fetchone()
        conn.close()

        if exsisting_account:
            session['customer_id'] = exsisting_account[0]
            session['firstname'] = exsisting_account[1]
            session['surname'] = exsisting_account[2]
            session['email'] = exsisting_account[3]
            

            return redirect(url_for('account'))
        else:
            #return render_template('/log-in.html', error = "Email or password is incorrect")
            error = "Incorrect email or password"
        
    return render_template('/log-in.html', error=error, email=email)


@app.route('/account')
def account():
    if 'customer_id' not in session:
        return redirect(url_for('log-in'))
    
    conn = sqlite3.connect('RolsaDatabase')
    c = conn.cursor()
    customer = c.execute('SELECT * FROM tblCustomer WHERE customerID = ?', (session['customer_id'],)).fetchone()
    conn.close()

    if customer:
        return render_template('/account.html', customer=customer)



@app.route('/log-out', methods=['POST', 'GET'])
def log_out():
    session.clear()
    return redirect(url_for('log_in'))


@app.route('/')
def send_to_home():
   return render_template('/home.html')

@app.route('/home', methods=['POST', 'GET'])
def home_page():
    #logged_in= session.get('logged_in', False)
    return render_template('/home.html')

@app.route('/energy-usage', methods=['POST', 'GET'])
def energy_usage():
    return render_template('/energy-usage.html')

@app.route('/carbon-footprint', methods=['POST', 'GET'])
def carbon_footprint():
    return render_template('/carbon-footprint.html')


@app.route('/carbon-footprint-calculator', methods=['POST', 'GET'])
def carbon_footprint_calculator():

    return render_template('/carbon-footprint-calculator.html')


@app.route('/installations-and-consultations', methods=['POST', 'GET'])
def installations_and_consultations():
    return render_template('/installations-and-consultations.html')


@app.route('/green-energy-products', methods=['POST', 'GET'])
def green_energy_products():
    
    if request.method=='GET':
        conn = sqlite3.connect('RolsaDatabase')
        c = conn.cursor()
        
        products = c.execute("SELECT * FROM tblProduct").fetchall()
        conn.close()

        return render_template('/green-energy-products.html', products=products)
    
    return render_template('/green-energy-products.html')


@app.route('/product-info/<int:product_id>', methods=['GET'])
def product_info(product_id):
    conn = sqlite3.connect('RolsaDatabase')
    c = conn.cursor()

    product_id= int(product_id)

    product= c.execute("SELECT * FROM tblProduct WHERE productID = ?", (product_id,)).fetchone()
    conn.close()

    if product:  #if selected product exists
        return render_template('product-info.html', product=product)
    
    else:
        return "product not found"



@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():

    if request.method=='POST':
        firstname=request.form['firstname']
        surname=request.form['surname']
        email=request.form['email']
        password=request.form['password']

        conn = sqlite3.connect('RolsaDatabase')
        c = conn.cursor()

        c.execute("SELECT * FROM tblCustomer WHERE email = ?", (email,))
        existing_email = c.fetchone()

        if existing_email:
            conn.close()
            return render_template('/sign-up.html', error="An account using this email already exists.")
        
        c.execute("INSERT INTO tblCustomer (firstname, surname, email, password) VALUES (?,?,?,?)", (firstname, surname, email, password))
        conn.commit()
        conn.close()

        return render_template('/log-in.html', success="You can now log in!")
        
    return render_template('/sign-up.html')



#MAKE THE "SCHEDULE INSTALLATION/CONSULTATION buttons forms and sumbit the ids as either "installation" or "consultation" on the product-info page

@app.route('/booking/<int:product_id>', methods=['POST', 'GET'])
def booking(product_id):
    conn = sqlite3.connect('RolsaDatabase')
    c = conn.cursor()

    product= int(product_id)

    product= c.execute("SELECT * FROM tblProduct WHERE productID = ?", (product_id,)).fetchone()
    conn.close()

    if request.method=='GET':

        if product:  #if selected product exists
            return render_template('booking.html', product=product)
        
        else:
            return "product not found"
        
    elif request.method=='POST':
        product_id = request.form.get('product_id')  # Hidden field value
        consultation_or_installation = request.form.get('consultation_or_installation')  # Value of the button clicked

        if consultation_or_installation == 'installation':
            consultation_or_installation=consultation_or_installation
            return render_template('booking.html', product=product, consultation_or_installation=consultation_or_installation)
        
        elif consultation_or_installation == 'consultation':
            consultation_or_installation=consultation_or_installation
            return render_template('booking.html', product=product, consultation_or_installation=consultation_or_installation)
        else:
            return "Invalid action"
        


@app.route('/booking-complete', methods=['POST', 'GET'])
def booking_complete():

    product_id= request.form['product_id']
    scheduled_date = request.form['scheduled_date']
    consultation_or_installation = request.form['consultation_or_installation']
    date_formatting = datetime.strptime(scheduled_date, "%Y-%m-%d")

    scheduled_date = date_formatting.strftime("%d/%m/%Y")


    if request.method=='POST':
        conn = sqlite3.connect('RolsaDatabase')
        c = conn.cursor()
        customer = c.execute('SELECT * FROM tblCustomer WHERE customerID = ?', (session['customer_id'],)).fetchone()
        customer_id = customer[0]

        c.execute("INSERT INTO tblBooking (customerID, productID, scheduleDate, installationOrConsultation) VALUES (?,?,?,?)", (customer_id, product_id, scheduled_date, consultation_or_installation))
        conn.commit()
        conn.close()

        return render_template('booking-complete.html', product_id=product_id, scheduled_date=scheduled_date, consultation_or_installation=consultation_or_installation)
            

        

@app.route('/billing-address', methods=['POST', 'GET'])
def billing_address():
     return render_template('billing-address.html')


@app.route('/transaction', methods=['POST', 'GET'])
def transaction():
     return render_template('transaction.html')




@app.route('/forgotten-password-login', methods=['POST', 'GET'])
def forgotten_password():

    return render_template('/forgotten-password-login.html')


if __name__ == '__main__':
    app.run(debug=True)


    