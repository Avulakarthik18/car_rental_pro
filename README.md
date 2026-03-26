# CarRentalPro | Premium Mobility & Logistics Platform

![CarRentalPro Banner](https://img.shields.io/badge/Status-Development-orange?style=for-the-badge)
![Tech](https://img.shields.io/badge/Tech-Flask%20%7C%20Supabase%20%7C%20Glassmorphism-blue?style=for-the-badge)

CarRentalPro is a high-end web application that seamlessly integrates **Car Rentals**, **Auto Marketplace (Buy/Sell)**, and **Parcel Logistics** into a single, premium user experience. Built with a modern aesthetic featuring Glassmorphism, it provides a sophisticated interface for users, drivers, and administrators.

---

## 🌟 Key Features

### 🚗 Car Rental Services
- **Self-Drive & With Driver**: Choose between personal freedom or professional chauffeur service.
- **Luxury Fleet**: Curated selection of premium sedans and SUVs.
- **Dynamic Booking**: Real-time availability and transparent pricing.
- **Location-Based Search**: Find vehicles near your pickup point.

### 📦 Smart Parcel Logistics
- **Route Matching**: Parcels are delivered by drivers already traveling on matching routes, maximizing efficiency.
- **Secure Verification**: QR-code based pickup and OTP-based delivery verification.
- **Live Tracking**: Real-time status updates for both senders and receivers.
- **Email Notifications**: Instant confirmation and status alerts.

### 💰 Marketplace (Buy & Sell)
- **Direct Listings**: Users can list their cars for sale with detailed specifications.
- **Marketplace Browsing**: Premium buyer experience with high-quality visuals.
- **Bidding System**: Integrated bidding for seamless price negotiation.

### 🛡️ Core Infrastructure
- **Secure Authentication**: Encrypted passwords and role-based access control (User/Admin/Driver).
- **Payment Gateway**: Integrated **Razorpay** for secure transactions.
- **Real-Time Tracking**: Live GPS tracking for active bookings.
- **Admin Dashboard**: Centralized management for car approvals, bookings, and user support.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Vanilla), Glassmorphism UI, Font Awesome |
| **Backend** | Python, Flask, SQLAlchemy |
| **Database** | Supabase (PostgreSQL) |
| **Payments** | Razorpay Integration |
| **Communication** | SMTP (Email Notifications), Simulated SMS |

---

## 📂 Project Structure

```bash
project/
├── backend/          # Flask API, Database models, and scripts
├── parcel/           # Frontend pages for parcel services
├── driver/           # Driver-specific portals and tracking
├── customer/         # Customer dashboard and live tracking
├── book_car/         # Car rental booking flow
├── sell_buy/         # Marketplace frontend
├── admin/            # Administrative management tools
├── service/          # Support and informational pages
└── design_system.css # Centralized premium styling
```

---

## 🚀 Getting Started

### 1. Backend Setup
1. Navigate to the `backend` folder.
2. Install dependencies:
   ```bash
   pip install flask flask-cors flask-bcrypt sqlalchemy psycopg2 razorpay
   ```
3. Update `DATABASE_URL` in `app.py` with your Supabase credentials.
4. Run the server:
   ```bash
   python app.py
   ```

### 2. Frontend Setup
1. Simply open `index.html` in any modern web browser.
2. Ensure the backend is running to enable interactive features.

---

## 🎨 Design Philosophy
The project employs a **Premium Glassmorphism** design language. High transparency, subtle blurs, and vibrant gradients create a "depth" that makes the application feel modern and professional.

---

*Developed with ❤️ for the future of urban mobility.*