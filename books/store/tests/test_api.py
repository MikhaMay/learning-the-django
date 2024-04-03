import json
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from django.contrib.auth.models import User

from store.serializers import BooksSerializer
from store.models import Book


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=55, author_name='Author5')
        self.book_3 = Book.objects.create(name='Test book Author 1', price=55, author_name='Author2')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)

        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})

        serializer_data = BooksSerializer([self.book_1, self.book_3], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter_price(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 55})

        serializer_data = BooksSerializer([self.book_2, self.book_3], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
    
    def test_get_order(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-price'})

        serializer_data = BooksSerializer([self.book_2, self.book_3, self.book_1], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Programming in Python 3",
            "price": 150,
            "author_name": "Mark Summerfield" 
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual("Programming in Python 3", Book.objects.all()[3].name)
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name 
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)
    
    def test_delete(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        count1 = Book.objects.all().count()
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        count2 = Book.objects.all().count()
        self.assertEqual(1, count1-count2)

    def test_get_one(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        
        response = self.client.get(url)
        serializer_data = BooksSerializer(self.book_1, many=False).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_update_not_owner(self):
        url = reverse('book-detail', args=(self.book_2.id,))
        data = {
            "name": self.book_2.name,
            "price": 575,
            "author_name": self.book_2.author_name 
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')}, response.data)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_2.refresh_from_db()
        self.assertEqual(55, self.book_2.price)

    def test_delete_not_user(self):
        self.user2 = User.objects.create(username='other_user')
        url = reverse('book-detail', args=(self.book_1.id,))
        self.client.force_login(self.user2)
        count1 = Book.objects.all().count()
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        count2 = Book.objects.all().count()
        self.assertEqual(0, count1-count2)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)

        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            "name": self.book_1.name,
            "price": 575,
            "author_name": self.book_1.author_name 
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)