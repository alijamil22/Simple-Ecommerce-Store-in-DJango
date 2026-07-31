# Simple E-Commerce Store

A fully functional e-commerce web application built with Django 6.0.7. Single-app architecture with session-based cart, user accounts, checkout, and order confirmation emails.

## Features

- **Product Catalog** — Browse products by category with pagination and product detail pages
- **Shopping Cart** — Session-based cart with add/remove, quantity updates, and stock validation
- **User Authentication** — Register, login, logout, and password reset via Gmail SMTP
- **Checkout** — Address form with Cash on Delivery and Pay Now (card stub) payment options
- **Order Management** — Order history, confirmation page, and email notifications via Django signals
- **Admin Panel** — Django admin with inline order items for managing products, categories, and orders
- **Responsive UI** — Bootstrap 5 with clean, minimal styling

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 6.0.7, Python 3.14 |
| Database | SQLite3 |
| Frontend | Bootstrap 5, HTML, CSS |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| Email | Gmail SMTP (via python-dotenv for credentials) |
| Packages | django-debug-toolbar, django-extensions, Pillow |

## Project Structure

```
Simple-Ecommerce-Store/
├── django_ecommerce_store/        # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                         # Main app
│   ├── models.py                  # Category, Product, Order, OrderItem
│   ├── views.py                   # All views
│   ├── urls.py                    # App URLs (namespaced: store:)
│   ├── forms.py                   # RegistrationForm, CheckoutForm
│   ├── cart.py                    # Session-based Cart class
│   ├── signals.py                 # Order confirmation email signal
│   ├── apps.py                    # StoreConfig with ready()
│   ├── admin.py                   # Admin configuration
│   ├── context_processors.py      # Categories context processor
│   ├── tests.py                   # 33 tests
│   ├── templatetags/cart_tags.py  # cart_count filter
│   ├── templates/store/           # All templates
│   └── static/store/css/base.css  # Styling
├── media/                         # Uploaded files
├── db.sqlite3
├── .env
├── requirements.txt
├── manage.py
└── AGENTS.md
```

## Setup

### 1. Clone and activate virtual environment

```bash
git clone <repo-url>
cd Simple-Ecommerce-Store
python -m venv venv
venv\Scripts\activate              # Windows
# source venv/bin/activate         # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` file

```env
SECRET_KEY=your-django-secret-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

> For Gmail, generate an [App Password](https://myaccount.google.com/apppasswords) (requires 2FA).

### 4. Run and start

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## URL Routes

| URL | Name | Description |
|-----|------|-------------|
| `/` | `product_list` | Product listing |
| `/category/<slug>/` | `product_list_by_category` | Products by category |
| `/product/<id>/<slug>/` | `product_detail` | Product detail page |
| `/cart/` | `cart_detail` | Shopping cart |
| `/cart/add/<id>/` | `cart_add` | Add to cart (POST) |
| `/cart/remove/<id>/` | `cart_remove` | Remove from cart (POST) |
| `/register/` | `register` | User registration |
| `/login/` | `login` | Login |
| `/logout/` | `logout` | Logout |
| `/profile/` | `profile` | Profile and order history |
| `/checkout/` | `checkout` | Checkout form |
| `/order/<id>/` | `order_confirmation` | Order confirmation |
| `/password_reset/` | `password_reset` | Password reset |
| `/admin/` | — | Django admin |

## Running Tests

```bash
python manage.py test store
```

All 33 tests covering models, views, cart, auth, checkout, and email signals.

## Development Notes

- Cart is session-based — stored in `request.session['cart']`
- Order confirmation email sent via Django `post_save` signal on Order
- Product images fallback to `store/static/store/images/no-image.svg` when none uploaded (tracked in git)
- Debug toolbar only active when `DEBUG=True`
- Categories in navbar via context processor — no need to pass manually in views
