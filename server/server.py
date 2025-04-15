#!/usr/bin/python3

import pyotp
import qrcode
import os
import keyring

from flask import Flask, jsonify, request, redirect, Response

app = Flask(__name__, static_url_path='/static')

def retrieveCredentials() -> str:
    """
    Retrieve OTP token from system wallet. If none could be found, generate a new one and store it.
    """
    token = keyring.get_password("system", "signalHandler_token")

    if token is None:
        print("Token could not be retrieved.")
        try:
            token = keyring.set_password("system", "signalHandler_token", pyotp.random_base32())
            print("Generated token.")
        except:
            print("Token generation failed. Aborting...")
            print("Ensure you have dbus-python installed on your system")
            exit()
    return token

secret = retrieveCredentials()


@app.route("/qr", methods=['GET'])
def generateChallenge():
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name='signalHandler', issuer_name='panderu')
    img = qrcode.make(uri)
    img_path = 'static/qrcode.png'
    img.save(img_path)

    return redirect(f"/{img_path}")

@app.route("/fetchContent", methods=['POST'])
def fetchContent():
    token = request.json.get('token')
    totp = pyotp.TOTP(secret)

    if(totp.verify(token)):
        print("yay")
        return "yay"
    else:
        return "", 401


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

