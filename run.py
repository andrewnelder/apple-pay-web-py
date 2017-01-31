import os
import stripe
import pprint
from flask import Flask, render_template, jsonify, request, Response

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
VERIFIED = False

app = Flask(__name__)
stripe.api_key = STRIPE_SECRET_KEY


class LoggingMiddleware(object):
    def __init__(self, app):
        self._app = app

    def __call__(self, environ, resp):
        errorlog = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(('RESPONSE', status, headers), stream=errorlog)
            return resp(status, headers, *args)

        return self._app(environ, log_response)


@app.route("/")
def index():
    # register_domain(request.host.split(':')[0])
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


# DOMAIN REGISTRATION #

# def register_domain(domain):
#     global VERIFIED
#     if not VERIFIED:
#         print "Attempting to register <{}>...".format(domain)
#         try:
#             stripe.ApplePayDomain.create(domain_name=domain)
#             print "Successful registration!"
#         except Exception as e:
#             pass
#     VERIFIED = True

# END DOMAIN REGISTRATION #


if __name__ == "__main__":

    if not STRIPE_SECRET_KEY:
        raise ValueError("Please pass the `STRIPE_SECRET_KEY` envionment variable.")

    if not STRIPE_PUBLISHABLE_KEY:
        raise ValueError("Please pass the `STRIPE_PUBLISHABLE_KEY` envionment variable.")

    app.wsgi_app = LoggingMiddleware(app.wsgi_app)
    app.run(host='0.0.0.0', port=5000, debug=True)
