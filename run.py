import os
import stripe
from flask import Flask, render_template, jsonify, request, Response, g

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
URL = os.environ.get("URL", None)

app = Flask(__name__)
stripe.api_key = STRIPE_SECRET_KEY


@app.route("/")
def index():
    register_heroku_domain()
    return render_template("index.html", **{
        "STRIPE_PUBLISHABLE_KEY": STRIPE_PUBLISHABLE_KEY
    })

@app.route("/.well-known/apple-developer-merchantid-domain-association")
def verify():
    with open('static/apple-developer-merchantid-domain-association') as fo:
        return Response(fo.read(), mimetype="text/plain")
    return ""

@app.route("/charge", methods=["POST"])
def charge():
    token = request.form.get("token")
    amount = int(float(request.form.get("amount")) * 100)  # convert to int for Stripe
    if not token or not amount:
        return "ERROR", 400

    # Create Customer
    cus = stripe.Customer.create(
        description="Apple Pay for the Web Test",
        source=token,
        email="test@test.test",
        metadata={
            "token": token,
        }
    )

    # Create Charge
    ch = stripe.Charge.create(
        amount=amount,
        customer=cus.id,
        currency="usd"
    )
    return jsonify({'charge': ch, 'customer': cus})


# HEROKU DOMAIN REGISTRATION #

g.apftw_verified = False if URL else True
def register_heroku_domain():
    if not g.apftw_verified:
        try:
            stripe.ApplePayDomain.create(domain_name=URL)
            g.apftw_verified = True
        except Exception as e:
            pass

# END HEROKU DOMAIN REGISTRATION #


if __name__ == "__main__":

    if not STRIPE_SECRET_KEY:
        raise ValueError("Please pass the `STRIPE_SECRET_KEY` envionment variable.")

    if not STRIPE_PUBLISHABLE_KEY:
        raise ValueError("Please pass the `STRIPE_PUBLISHABLE_KEY` envionment variable.")

    app.run(debug=True)
