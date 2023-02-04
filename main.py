from flask import Flask, send_from_directory, render_template, request, session, redirect
import os
from datetime import datetime


app = Flask(__name__)
app.secret_key = os.environ['secret']


@app.route('/')
def home():
  width = 1000
  for device in ('Android', 'iPhone'):
    if device in request.headers['User-Agent']:
      width = 350
  
  return render_template('index.html', width=width, notify=session.pop('notify', False), failed=session.pop('failed', False),
check_in_after=session.pop('check_in_after', False), past=session.pop('past', False),
                        just_checked_out=session.pop('just_checked_out', False))

@app.post('/cart')
def cart():
  if 'cart' not in session:
      session['cart'] = []
  if not all(request.form.get(key) for key in ('Select a room', 'check_in', 'check_out')):
    session['failed'] = True
  else:


    form = dict(request.form)
    if form['Select a room'] == 'cozy':
      form['price'] = 299
    elif form['Select a room'] == 'suite':
      form['price'] = 549
    else:
      form['price'] = 849

    # check if the checkin is after the checkout
    t1, t2 = datetime.strptime(form['check_in'], '%Y-%m-%d'), datetime.strptime(form['check_out'], '%Y-%m-%d')
    if t1 > t2:
      session['check_in_after'] = True
    elif t1 < datetime.now():
      session['past'] = True
    else:      
      form['price'] *= (t2 - t1).days
      session['cart'].append(form)
      session['notify'] = True

  return redirect('/')
      

@app.get('/cart')
def show_cart():
  if 'cart' not in session:
      session['cart'] = []
  return render_template('cart.html', cart=session['cart'], price=sum(f['price'] for f in session['cart']))


@app.post('/checkout')
def check_out():
  # reset the cart
  session['cart'] = []
  session['just_checked_out'] = True
  
  return redirect('/')


@app.get('/final')
def final():
  return render_template('final.html', price=sum(f['price'] for f in session['cart']))  
  

app.run(host='0.0.0.0')
