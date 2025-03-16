from flask import Flask, render_template, request, flash, redirect, url_for
import jwt
import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MongoDB Configuration
MONGO_URI = "mongodb+srv://cluster0.mcjuw.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCertificateKeyFile=r"templates/X509-cert-7398551624606348947.pem"
)
db = client["UserDB"]
users_collection = db["users"]

# JWT Secret Key
JWT_SECRET = "S!mpleJWTS3cretK3y!2025@Secure"


@app.route("/")
def index():
    """Home route to prevent URL errors."""
    return "Welcome to the Homepage!"


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Handle password reset using the token sent via email."""
    token = request.args.get("token")

    if not token:
        flash("Invalid or expired reset link!", "danger")
        return redirect(url_for("index"))

    try:
        print("Received token:", token)  # Debugging line
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        email = data["email"]
        print("Decoded email:", email)  # Debugging line
    except jwt.ExpiredSignatureError:
        print("Error: Token expired!")  # Debugging line
        flash("Reset link expired!", "danger")
        return redirect(url_for("index"))
    except jwt.InvalidTokenError:
        print("Error: Invalid token!")  # Debugging line
        flash("Invalid reset token!", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        new_password = request.form.get("password")

        if len(new_password) < 6:
            flash("Password must be at least 6 characters long!", "danger")
            return redirect(url_for("reset_password", token=token))

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Update password in the database
        users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
        
        flash("Password updated successfully!", "success")
        return redirect(url_for("index"))

    return render_template("reset_password.html", token=token)


if __name__ == "__main__":
    app.run(debug=True)
