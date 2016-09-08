import os
import stripe
from flask import Flask, render_template, jsonify, request

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")

app = Flask(__name__)
stripe.api_key = STRIPE_SECRET_KEY


@app.route("/")
def index():
    return render_template("index.html", **{
        "STRIPE_PUBLISHABLE_KEY": STRIPE_PUBLISHABLE_KEY
    })


@app.route("/charge", methods=["POST"])
def charge():
    token = request.form.get("token")
    amount = int(request.form.get("amount") * 100)  # convert to int for Stripe
    if not token or not amount:
        return "ERROR", 400
    ch = stripe.Charge.create(amount=amount, source=token, currency="usd")
    return jsonify(ch)

if __name__ == "__main__":

    if not STRIPE_SECRET_KEY:
        raise ValueError("Please pass the `STRIPE_SECRET_KEY` envionment variable.")

    if not STRIPE_PUBLISHABLE_KEY:
        raise ValueError("Please pass the `STRIPE_PUBLISHABLE_KEY` envionment variable.")

    app.run(debug=True)
