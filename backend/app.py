from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import random
import smtplib
from email.message import EmailMessage
import os
import json

app = Flask(__name__)
CORS(app)

bcrypt = Bcrypt(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "login.db")

print("DATABASE PATH:", DB_NAME)

# 🔥 CHANGE THIS (KEEP SECRET)
ADMIN_SECRET = "supersecret123"

EMAIL_USER = "avulakarthik189@gmail.com"
EMAIL_PASS = "eiigbdbsyfawqzbr"
# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# CREATE TABLES
# -----------------------------
def create_tables():

    conn = get_db()
    cursor = conn.cursor()

    # SIGNUP TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signup(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE
    )
    """)

    # LOGIN TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    # RESET PASSWORD TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resetpassword(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        otp TEXT,
        new_password TEXT,
        reset_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ✅ ADMIN TABLE (MOVE HERE)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admintable(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
CREATE TABLE IF NOT EXISTS cars(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_email TEXT NOT NULL,

    listing_type TEXT,
    
    company TEXT,
    model TEXT,
    reg_number TEXT,
    year TEXT,
    fuel TEXT,
    transmission TEXT,
    seats TEXT,
    km TEXT,

    driver_name TEXT,
    driver_mobile TEXT,

    location TEXT,
    price_month INTEGER,
    deposit INTEGER,
    notes TEXT,

    images TEXT,

    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
    

    cursor.execute("""
CREATE TABLE IF NOT EXISTS selling(
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    owner_email TEXT NOT NULL,

    company TEXT,
    model TEXT,
    reg_number TEXT UNIQUE,
    year TEXT,
    fuel TEXT,
    transmission TEXT,
    km TEXT,
    owner_type TEXT,

    location TEXT,
    selling_price INTEGER,
    description TEXT,

    images TEXT,

    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    car_id INTEGER,
    car_name TEXT,
    owner_email TEXT,

    customer_email TEXT,
    customer_name TEXT,
    customer_mobile TEXT,
    nominee TEXT,

    rental_type TEXT,

    pickup_location TEXT,
    drop_location TEXT,

    pickup_datetime TEXT,
    drop_datetime TEXT,

    driver_name TEXT,
    driver_mobile TEXT,
    passenger_count INTEGER,

    total_cost INTEGER,

    booking_status TEXT DEFAULT 'Confirmed',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


    conn.commit()
    conn.close()

create_tables()

@app.route("/")
def home():
    return "Backend is running ✅"

# -----------------------------
# EMAIL FUNCTION
# -----------------------------
def send_email(receiver, otp):

    sender_email = "avulakarthik189@gmail.com"
    sender_password = "eiigbdbsyfawqzbr"

    msg = EmailMessage()
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = sender_email
    msg["To"] = receiver

    msg.set_content(f"""
Hello,

Your OTP for password reset is:

{otp}

If you did not request this, ignore this email.
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)


# temporary OTP store
otp_store = {}

def send_booking_email(data):

    receiver = data.get("customer_email")

    # 🔥 SAFETY CHECK (VERY IMPORTANT)
    if not receiver:
        print("No customer email found — skipping email.")
        return

    msg = EmailMessage()
    msg["Subject"] = "🚗 Your Car Booking is Confirmed!"
    msg["From"] = EMAIL_USER
    msg["To"] = receiver

    html = f"""
    <html>
    <body style="font-family:Arial;background:#f2f3f5;padding:20px;">

        <div style="
            max-width:600px;
            background:white;
            padding:30px;
            border-radius:12px;
            box-shadow:0px 3px 10px rgba(0,0,0,0.1);
        ">

            <h2 style="color:#28a745;">✅ Booking Confirmed</h2>

            <p>Hello <b>{data.get("customer_name")}</b>,</p>

            <p>
            Your car booking has been <b>successfully confirmed</b>.  
            Below are your booking details:
            </p>

            <hr>

            <h3 style="color:#333;">🚘 Booking Details</h3>

            <p><b>Car:</b> {data.get("car_name")}</p>
            <p><b>Rental Type:</b> {data.get("rental_type")}</p>
            <p><b>Pickup Location:</b> {data.get("pickup_location")}</p>
            <p><b>Drop Location:</b> {data.get("drop_location")}</p>

            <p><b>Pickup Time:</b> {data.get("pickup_datetime")}</p>
            <p><b>Drop Time:</b> {data.get("drop_datetime")}</p>

            <h2 style="color:#007bff;">
                💰 Total Fare: ₹{data.get("total_cost")}
            </h2>
    """

    # ⭐ ONLY SHOW DRIVER DETAILS IF "WITH DRIVER"
    if data.get("rental_type") == "With Driver":
        html += f"""
            <hr>

            <h3 style="color:#333;">👨‍✈️ Driver Details</h3>

            <p><b>Name:</b> {data.get("driver_name")}</p>
            <p><b>Mobile:</b> {data.get("driver_mobile")}</p>

            <p style="color:#666;font-size:13px;">
            Please contact the driver only for trip coordination.
            </p>
        """

    html += """
            <hr>

            <p style="color:gray;">
            Thank you for choosing our service 🚗  
            Wishing you a safe and comfortable journey!
            </p>

        </div>

    </body>
    </html>
    """

    msg.add_alternative(html, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("✅ Booking email sent successfully!")

    except Exception as e:
        # 🔥 NEVER CRASH BOOKING BECAUSE OF EMAIL
        print("❌ Email failed but booking is saved:", e)


# -----------------------------
# SIGNUP (USER ONLY)
# -----------------------------
@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "message": "Invalid request ❌"}), 400

    first = data.get("first_name")
    last = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not all([first, last, email, password]):
        return jsonify({"success": False, "message": "All fields required ❌"}), 400

    email = email.lower().strip()
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO signup(first_name,last_name,email) VALUES(?,?,?)",
            (first, last, email)
        )

        cursor.execute(
            "INSERT INTO login(email,password) VALUES(?,?)",
            (email, hashed_pw)
        )

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Signup successful ✅ Please login"
        })

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "message": "Email already exists ❌"
        })

    finally:
        conn.close()


# -----------------------------
# 🔥 SINGLE LOGIN (ADMIN + USER)
# -----------------------------
@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "message": "Invalid request ❌"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email & password required ❌"}), 400

    email = email.lower().strip()

    conn = get_db()
    cursor = conn.cursor()

    # ✅ CHECK ADMIN FIRST
    cursor.execute("SELECT * FROM admintable WHERE email=?", (email,))
    admin = cursor.fetchone()

    if admin:

        if not bcrypt.check_password_hash(admin["password"], password):
            conn.close()
            return jsonify({"success": False, "message": "Incorrect password ❌"}), 401

        conn.close()

        return jsonify({
            "success": True,
            "message": "Admin login successful ✅",
            "role": "admin",
            "user": {
                "name": admin["name"],
                "email": admin["email"]
            }
        })

    # ✅ CHECK USER
    cursor.execute("SELECT * FROM login WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"success": False, "message": "User not found ❌"}), 404

    if not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Incorrect password ❌"}), 401

    return jsonify({
    "success": True,
    "message": "Login successful ✅",
    "role": "user",
    "user": {
        "email": email
    }
})


# -----------------------------
# FORGOT PASSWORD
# -----------------------------
@app.route("/forgot-password", methods=["POST"])
def forgot_password():

    data = request.get_json()
    email = data.get("email")

    conn = get_db()
    cursor = conn.cursor()

    # check from signup
    cursor.execute("SELECT * FROM signup WHERE email=?", (email,))
    user = cursor.fetchone()

    if not user:
        return jsonify({
            "success": False,
            "message": "Email not registered ❌"
        })

    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp

    try:
        send_email(email, otp)
    except:
        print("Email failed — printing OTP instead:", otp)

    return jsonify({
        "success": True,
        "message": "OTP sent to email ✅"
    })


# -----------------------------
# RESET PASSWORD
# -----------------------------
@app.route("/reset-password", methods=["POST"])
def reset_password():

    data = request.get_json()

    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")

    if otp_store.get(email) != otp:

        return jsonify({
            "success": False,
            "message": "Invalid OTP ❌"
        })

    hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')

    conn = get_db()
    cursor = conn.cursor()

    # update login table
    cursor.execute("""
    UPDATE login
    SET password=?
    WHERE email=?
    """, (hashed_pw, email))

    # store history
    cursor.execute("""
    INSERT INTO resetpassword(email,otp,new_password)
    VALUES(?,?,?)
    """, (email, otp, hashed_pw))

    conn.commit()
    conn.close()

    otp_store.pop(email, None)

    return jsonify({
        "success": True,
        "message": "Password reset successful ✅ Please login"
    })

# -----------------------------
# 🔥 CREATE ADMIN (SECURED)
# -----------------------------
@app.route("/create-admin", methods=["POST"])
def create_admin():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False}), 400

    if data.get("secret") != ADMIN_SECRET:
        return jsonify({
            "success": False,
            "message": "Unauthorized ❌"
        }), 403

    name = data.get("name")
    email = data.get("email").lower().strip()
    password = data.get("password")

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admintable WHERE email=?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({
            "success": False,
            "message": "Admin already exists ❌"
        })

    cursor.execute(
        "INSERT INTO admintable(name,email,password) VALUES(?,?,?)",
        (name, email, hashed_pw)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Admin created successfully ✅"
    })


@app.route("/add-car", methods=["POST"])
def add_car():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request data ❌"
        }), 400

    print("DATA RECEIVED:", data)

    # ✅ Normalize important fields
    owner_email = data.get("owner_email", "").lower().strip()
    listing_type = data.get("listing_type", "").strip().title()

    company = data.get("company")
    model = data.get("model")
    reg_number = data.get("reg_number", "").upper().strip()

    # 🔥 Validate Required Fields
    if not owner_email or not listing_type or not company or not model or not reg_number:
        return jsonify({
            "success": False,
            "message": "Missing required fields ❌"
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    try:

        # ✅ Prevent duplicate car registration
        cursor.execute(
            "SELECT id FROM cars WHERE reg_number=?",
            (reg_number,)
        )

        if cursor.fetchone():
            return jsonify({
                "success": False,
                "message": "Car already registered ❌"
            }), 400


        cursor.execute("""
        INSERT INTO cars(
            owner_email,
            listing_type,
            company,
            model,
            reg_number,
            year,
            fuel,
            transmission,
            seats,
            km,
            driver_name,
            driver_mobile,
            location,
            price_month,
            deposit,
            notes,
            images
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(
            owner_email,
            listing_type,
            company,
            model,
            reg_number,
            data.get("year"),
            data.get("fuel"),
            data.get("transmission"),
            data.get("seats"),
            data.get("km"),
            data.get("driver_name"),
            data.get("driver_mobile"),
            data.get("location"),
            data.get("price_month") or 0,
            data.get("deposit") or 0,
            data.get("notes"),
            json.dumps(data.get("images", []))
        ))

        conn.commit()

        inserted_id = cursor.lastrowid

        print("INSERT SUCCESS ✅")
        print("Inserted Car ID:", inserted_id)

        cursor.execute("SELECT COUNT(*) FROM cars")
        print("TOTAL CARS:", cursor.fetchone()[0])

        return jsonify({
            "success": True,
            "message": "Car submitted for approval ✅",
            "car_id": inserted_id
        })

    except Exception as e:

        print("🚨 SQLITE ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": "Database error ❌"
        }), 500

    finally:
        conn.close()


@app.route("/approved-cars/<email>/<listing_type>")
def approved_cars(email, listing_type):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM cars
        WHERE status='Approved'
        AND LOWER(owner_email) != LOWER(?)
        AND listing_type=?
    """,(email, listing_type))

    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"success":True,"cars":cars})




@app.route("/admin/pending-cars")
def pending_cars():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars WHERE status='Pending'")
    cars = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({"success":True,"cars":cars})


@app.route("/admin/update-car-status", methods=["POST"])
def update_status():

    data = request.get_json()

    car_id = data.get("car_id")
    status = data.get("status").capitalize()  # Approved / Rejected

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE cars
    SET status=?
    WHERE id=?
    """,(status, car_id))

    conn.commit()
    conn.close()

    return jsonify({"success":True})

@app.route("/my-car-status/<email>")
def my_car_status(email):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM cars
    WHERE owner_email=?
    ORDER BY created_at DESC
    """,(email,))

    cars = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        "success":True,
        "cars":cars
    })


@app.route("/book-car", methods=["POST"])
def book_car():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid request ❌"
        }),400

    conn = get_db()
    cursor = conn.cursor()

    try:

        customer_email = data.get("customer_email")
        if not customer_email:

            return jsonify({
                "success": False,
                "message": "Customer email missing ❌"
    }),400
        customer_email = customer_email.lower().strip()
        car_id = data.get("car_id")
        rental_type = data.get("rental_type")

        # ✅ Validate required fields
        if not car_id or not customer_email:
            return jsonify({
                "success": False,
                "message": "Missing required fields ❌"
            }),400


        # ✅ Validate rental type
        if rental_type not in ["Rental Only", "With Driver"]:
            return jsonify({
                "success":False,
                "message":"Invalid rental type ❌"
            }),400


        # 🔥 Check car exists AND is approved
        cursor.execute("""
            SELECT owner_email, status
            FROM cars
            WHERE id=?
        """,(car_id,))

        car = cursor.fetchone()

        if not car:
            return jsonify({
                "success":False,
                "message":"Car not found ❌"
            }),404

        if car["status"] != "Approved":
            return jsonify({
                "success":False,
                "message":"Car is not available for booking ❌"
            }),400


        # 🔥 Prevent owner booking own car
        if car["owner_email"] and car["owner_email"].lower() == customer_email:
            return jsonify({
                "success": False,
                "message": "You cannot book your own car ❌"
            }),400


        # 🔥 PREVENT TOO MANY ACTIVE BOOKINGS (SMART PROTECTION)
        cursor.execute("""
        SELECT COUNT(*) as total
        FROM bookings
        WHERE customer_email=?
        AND booking_status='Confirmed'
        """,(customer_email,))

        result = cursor.fetchone()
        active = result["total"] if result else 0   

        if active >= 2:
            return jsonify({
                "success":False,
                "message":"Booking limit reached (Max 2 active) ❌"
            }),400


        # 🔥 DATE CONFLICT CHECK (PRO LEVEL)
        pickup = data.get("pickup_datetime")
        drop = data.get("drop_datetime")

        if not pickup or not drop:
            return jsonify({
                "success":False,
                "message":"Pickup & Drop required ❌"
            }),400


        cursor.execute("""
        SELECT * FROM bookings
        WHERE car_id=?
        AND booking_status='Confirmed'
        AND (
            pickup_datetime <= ?
            AND drop_datetime >= ?
        )
        """,(car_id, drop, pickup))

        conflict = cursor.fetchone()

        if conflict:
            return jsonify({
                "success":False,
                "message":"Car already booked for selected dates ❌"
            }),400
        
        # SAFE TYPE CONVERSION
        try:
            passenger_count = int(data.get("passenger_count")) if data.get("passenger_count") else None
        except:
            passenger_count = None

        try:
            total_cost = int(data.get("total_cost")) if data.get("total_cost") else 0
        except:
            total_cost = 0

        # ✅ INSERT BOOKING (UPGRADED)
        cursor.execute("""
        INSERT INTO bookings(
            car_id,
            car_name,
            owner_email,

            customer_name,
            customer_email,
            customer_mobile,
            nominee,

            rental_type,

            pickup_location,
            drop_location,

            pickup_datetime,
            drop_datetime,

            driver_name,
            driver_mobile,
            passenger_count,

            total_cost,
            booking_status
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(

            car_id,
            data.get("car_name"),
            car["owner_email"],

            data.get("customer_name"),
            customer_email,
            data.get("customer_mobile"),
            data.get("nominee"),

            rental_type,

            data.get("pickup_location"),
            data.get("drop_location"),

            pickup,
            drop,

            data.get("driver_name"),
            data.get("driver_mobile"),
            passenger_count,
            total_cost, 
            "Confirmed"
        ))

        conn.commit()

        try:
            send_booking_email(data)
        except Exception as mail_error:
            print("Email failed but booking saved:", mail_error)

        booking_id = cursor.lastrowid

        print("BOOKING SUCCESS ✅ ID:", booking_id)

        

        return jsonify({
            "success": True,
            "message": "Booking confirmed ✅",
            "booking_id": booking_id
        })

        import traceback
    except Exception as e:
        print("\n🔥🔥🔥 REAL BACKEND ERROR 🔥🔥🔥")
        traceback.print_exc()
        print("🔥🔥🔥 END ERROR 🔥🔥🔥\n")

        return jsonify({
        "success": False,
        "message": "Booking failed ❌"
    }),500


    finally:
        conn.close()



@app.route("/admin/block-car", methods=["POST"])
def block_car():

    data = request.get_json()
    car_id = data.get("car_id")

    conn = get_db()
    cursor = conn.cursor()

    # 🚨 Check active booking
    cursor.execute("""
        SELECT * FROM bookings
        WHERE car_id=?
        AND booking_status='Confirmed'
    """,(car_id,))

    if cursor.fetchone():
        return jsonify({
            "success":False,
            "message":"Car has active booking ❌ Cannot block"
        }),400


    cursor.execute("""
        UPDATE cars
        SET status='Blocked'
        WHERE id=?
    """,(car_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "success":True,
        "message":"Car blocked successfully 🚫"
    })

@app.route("/sell-car", methods=["POST"])
def sell_car():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success":False}),400

    owner_email = data.get("owner_email").lower().strip()
    reg_number = data.get("reg_number").upper().strip()

    conn = get_db()
    cursor = conn.cursor()

    # 🔥 prevent duplicate registration
    cursor.execute("""
        SELECT id FROM selling
        WHERE reg_number=?
    """,(reg_number,))

    if cursor.fetchone():
        return jsonify({
            "success":False,
            "message":"Car already listed for sale ❌"
        }),400


    cursor.execute("""
    INSERT INTO selling(
        owner_email,
        company,
        model,
        reg_number,
        year,
        fuel,
        transmission,
        km,
        owner_type,
        location,
        selling_price,
        description,
        images
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,(
        owner_email,
        data.get("company"),
        data.get("model"),
        reg_number,
        data.get("year"),
        data.get("fuel"),
        data.get("transmission"),
        data.get("km"),
        data.get("owner_type"),
        data.get("location"),
        data.get("selling_price"),
        data.get("description"),
        json.dumps(data.get("images",[]))
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success":True,
        "message":"Car submitted for approval ✅"
    })


@app.route("/admin/pending-selling")
def pending_selling():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM selling
        WHERE status='Pending'
    """)

    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"success":True,"cars":cars})

@app.route("/admin/update-selling-status", methods=["POST"])
def update_selling_status():

    data = request.get_json()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE selling
        SET status=?
        WHERE id=?
    """,(data.get("status"), data.get("car_id")))

    conn.commit()
    conn.close()

    return jsonify({"success":True})

@app.route("/admin/approve-sell/<int:car_id>", methods=["POST"])
def approve_sell(car_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE selling
        SET status='Approved'
        WHERE id=?
    """,(car_id,))

    conn.commit()
    conn.close()

    print("SELLING CAR APPROVED:", car_id)

    return jsonify({
        "success":True,
        "message":"Car Approved ✅"
    })

@app.route("/admin/reject-sell/<int:car_id>", methods=["POST"])
def reject_sell(car_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE selling
        SET status='Rejected'
        WHERE id=?
    """,(car_id,))

    conn.commit()
    conn.close()

    print("SELLING CAR REJECTED:", car_id)

    return jsonify({
        "success":True,
        "message":"Car Rejected ❌"
    })


@app.route("/approved-selling/<email>")
def approved_selling(email):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM selling
        WHERE status='Approved'
        AND LOWER(owner_email) != LOWER(?)
    """,(email,))

    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({"success":True,"cars":cars})

@app.route("/my-selling-status/<email>")
def my_selling_status(email):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM selling
        WHERE LOWER(owner_email)=LOWER(?)
        ORDER BY created_at DESC
    """,(email,))

    cars = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify({
        "success":True,
        "cars":cars
    })





# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=True)
