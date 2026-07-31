from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from .models import Category, Product, Order, OrderItem
from .cart import Cart


class MockRequest:
    def __init__(self, session):
        self.session = session


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics', slug='electronics', description='Gadgets'
        )

    def test_str(self):
        self.assertEqual(str(self.category), 'Electronics')

    def test_get_absolute_url(self):
        url = self.category.get_absolute_url()
        self.assertEqual(url, reverse('store:product_list_by_category', args=['electronics']))


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Books', slug='books')
        self.product = Product.objects.create(
            category=self.category, name='Django Book', slug='django-book',
            price=Decimal('29.99'), stock=10, available=True
        )

    def test_str(self):
        self.assertEqual(str(self.product), 'Django Book')

    def test_get_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertEqual(url, reverse('store:product_detail', args=[self.product.id, 'django-book']))


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Shoes', slug='shoes')
        self.product = Product.objects.create(
            category=self.category, name='Sneakers', slug='sneakers',
            price=Decimal('50.00'), stock=5
        )
        self.order = Order.objects.create(
            user=self.user, address='123 Main St', city='Lahore',
            postal_code='54000', phone='03001234567', payment_method='card', paid=True
        )
        OrderItem.objects.create(order=self.order, product=self.product, price=Decimal('50.00'), quantity=2)

    def test_str(self):
        self.assertEqual(str(self.order), f'Order {self.order.id}')

    def test_get_total_cost(self):
        self.assertEqual(self.order.get_total_cost(), Decimal('100.00'))

    def test_order_item_get_cost(self):
        item = self.order.items.first()
        self.assertEqual(item.get_cost(), Decimal('100.00'))


class ProductListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Gadgets', slug='gadgets')
        self.product = Product.objects.create(
            category=self.category, name='Widget', slug='widget',
            price=Decimal('9.99'), stock=5, available=True
        )
        self.unavailable = Product.objects.create(
            category=self.category, name='Hidden', slug='hidden',
            price=Decimal('5.00'), stock=1, available=False
        )

    def test_product_list_status(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_shows_available(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertContains(response, 'Widget')
        self.assertNotContains(response, 'Hidden')

    def test_category_filter(self):
        response = self.client.get(reverse('store:product_list_by_category', args=['gadgets']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Widget')


class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Tools', slug='tools')
        self.product = Product.objects.create(
            category=self.category, name='Hammer', slug='hammer',
            price=Decimal('15.00'), stock=3, available=True
        )

    def test_product_detail_status(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product.id, 'hammer']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hammer')

    def test_product_detail_404(self):
        response = self.client.get(reverse('store:product_detail', args=[999, 'nonexistent']))
        self.assertEqual(response.status_code, 404)


class CartTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.category, name='Item', slug='item',
            price=Decimal('10.00'), stock=5
        )

    def test_add_to_cart(self):
        response = self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 2})
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 2)

    def test_add_exceeds_stock(self):
        response = self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 10})
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertNotIn(str(self.product.id), session.get('cart', {}))

    def test_remove_from_cart(self):
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 1})
        response = self.client.post(reverse('store:cart_remove', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(session.get('cart', {}), {})

    def test_cart_detail(self):
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 1})
        response = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Item')

    def test_cart_length(self):
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 3})
        request = MockRequest(self.client.session)
        cart = Cart(request)
        self.assertEqual(len(cart), 3)

    def test_cart_total(self):
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 2})
        request = MockRequest(self.client.session)
        cart = Cart(request)
        self.assertEqual(cart.get_total_price(), Decimal('20.00'))

    def test_cart_clear(self):
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 1})
        request = MockRequest(self.client.session)
        cart = Cart(request)
        cart.clear()
        self.assertEqual(len(cart), 0)


class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@test.com')

    def test_register_page(self):
        response = self.client.get(reverse('store:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        response = self.client.post(reverse('store:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_page(self):
        response = self.client.get(reverse('store:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('store:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('store:logout'))
        self.assertEqual(response.status_code, 302)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('store:profile'))
        self.assertEqual(response.status_code, 302)

    def test_profile_page(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('store:profile'))
        self.assertEqual(response.status_code, 200)


class CheckoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='buyer', password='buyer123', email='buyer@test.com')
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            category=self.category, name='Widget', slug='widget',
            price=Decimal('25.00'), stock=10, available=True
        )

    def test_checkout_requires_login(self):
        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_empty_cart(self):
        self.client.login(username='buyer', password='buyer123')
        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_page(self):
        self.client.login(username='buyer', password='buyer123')
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 2})
        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_card_payment(self):
        self.client.login(username='buyer', password='buyer123')
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 2})
        response = self.client.post(reverse('store:checkout'), {
            'address': '123 Street',
            'city': 'Lahore',
            'postal_code': '54000',
            'phone': '03001234567',
            'payment_method': 'card',
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.latest('id')
        self.assertTrue(order.paid)
        self.assertEqual(order.items.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

    def test_checkout_cod_payment(self):
        self.client.login(username='buyer', password='buyer123')
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 1})
        response = self.client.post(reverse('store:checkout'), {
            'address': '456 Ave',
            'city': 'Karachi',
            'postal_code': '74000',
            'phone': '03211234567',
            'payment_method': 'cod',
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.latest('id')
        self.assertFalse(order.paid)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)

    def test_order_confirmation(self):
        self.client.login(username='buyer', password='buyer123')
        self.client.post(reverse('store:cart_add', args=[self.product.id]), {'quantity': 1})
        self.client.post(reverse('store:checkout'), {
            'address': '789 Blvd',
            'city': 'Islamabad',
            'postal_code': '44000',
            'phone': '03331234567',
            'payment_method': 'card',
        })
        order = Order.objects.latest('id')
        response = self.client.get(reverse('store:order_confirmation', args=[order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Widget')


class SignalTest(TestCase):
    def test_order_email_sent_on_creation(self):
        user = User.objects.create_user(
            username='emailuser', password='pass1234', email='test@example.com'
        )
        cat = Category.objects.create(name='Books', slug='books')
        product = Product.objects.create(
            category=cat, name='Django Book', slug='django-book',
            price=Decimal('25.00'), stock=10,
            description='A book about Django'
        )
        order = Order.objects.create(
            user=user, address='123 Main St', city='Lahore',
            postal_code='54000', phone='03001234567',
            payment_method='card', paid=True
        )
        OrderItem.objects.create(
            order=order, product=product, price=product.price, quantity=2
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Order #', mail.outbox[0].subject)
        self.assertIn('test@example.com', mail.outbox[0].to)
