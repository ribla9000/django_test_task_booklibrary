from django.db import models, connection
from django.utils import timezone
from core.utils import get_table_values
import datetime
import random
import uuid


def create_unique_url():
    return uuid.uuid4()


def create_unique_article():
    return str(random.randint(10**5, 10**8))


def get_gener():
    _GENRES_ = {
        "FAN": "fantastic",
        "MEL": "melodrama",
        "MUS": "musical",
        "DET": "detective",
        "COM": "comedy",
        "STU": "standup",
        "LER": "learning",
        "HOR": "horror"
    }
    return {gener: gener for gener in _GENRES_}


class Users(models.Model):
    name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    father_name = models.CharField(max_length=32, null=True)
    is_author = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now(), null=False)


class Books(models.Model):
    #add to_field
    user_id = models.IntegerField()
    title = models.CharField(max_length=40, null=False)
    description = models.CharField(max_length=512, null=True)
    cover = models.TextField(null=True)
    pages = models.IntegerField()
    unique_url = models.CharField(max_length=32, null=False)
    article = models.CharField(max_length=32, null=False)
    created_at = models.DateTimeField(default=timezone.now(), null=False)

    @staticmethod
    def get_all():
        query = """
            SELECT * FROM books_books
            JOIN (SELECT id as userId, name, last_name, father_name  FROM books_users) AS books_users   
            ON books_books.user_id = books_users.userId
        """
        cursor = connection.cursor()
        cursor.execute(query)
        desc = cursor.description
        data = cursor.fetchall()
        cursor.close()
        return get_table_values(description=desc, data=data)

    @staticmethod
    def get_by_article(article: str):
        cursor = connection.cursor()
        query = f"""
            SELECT * FROM books_books
            WHERE article = {article}
        """
        cursor.execute(query)
        desc = cursor.description
        data = cursor.fetchall()
        cursor.close()
        return get_table_values(description=desc, data=data)


class Genres(models.Model):
    name = models.CharField(max_length=3, choices=get_gener())


class BooksGenres(models.Model):
    book_id = models.IntegerField()
    gener_id = models.IntegerField()


class BooksPages(models.Model):
    book_id = models.IntegerField(null=False)
    page = models.IntegerField(null=False)
    page_text = models.TextField(null=False)


class BooksStash(models.Model):
    book_id = models.IntegerField()
    count = models.IntegerField()

    @staticmethod
    def update_count(book_id: int, is_positive: bool):
        cursor = connection.cursor()
        sign = "-" if not is_positive else "+"
        query = f"""
        UPDATE books_booksstash
        SET count = count {sign} 1
        WHERE book_id = {book_id}
        """
        cursor.execute(query)
        cursor.close()
        return None


class BooksBooking(models.Model):
    user_id = models.IntegerField()
    book_id = models.IntegerField()
    created_at = models.DateTimeField(null=False)
    is_returned = models.BooleanField(default=False)
    returned_at = models.DateTimeField(null=True)

    @staticmethod
    def get_books_without_booking(user_id: int):
        cursor = connection.cursor()
        query = f"""
            SELECT b.id, b.title, b.description, b.user_id, b.pages, b.article, b.cover, u.name, u.last_name, u.father_name
            FROM books_books AS b
            JOIN books_users AS u ON b.user_id = u.id
            LEFT JOIN (
                SELECT book_id, is_returned, user_id as uui, MAX(created_at) as max_created_at
                FROM books_booksbooking
                WHERE uui = {user_id}
                GROUP BY book_id
            ) AS ub ON b.id = ub.book_id
            WHERE ub.book_id IS NULL OR (ub.is_returned IS TRUE)
            GROUP BY b.id
        """
        cursor.execute(query)
        desc = cursor.description
        data = cursor.fetchall()
        cursor.close()
        return get_table_values(description=desc, data=data)

    @staticmethod
    def get_books_with_booking(user_id: int) -> Books:
        cursor = connection.cursor()
        query = f"""
            SELECT b.id, b.title, b.description, b.user_id, b.pages, b.article, b.cover, u.name, u.last_name, u.father_name
            FROM books_books AS b
            JOIN books_users AS u ON b.user_id = u.id
            LEFT JOIN (
                SELECT book_id, is_returned, user_id as uui, MAX(created_at) as max_created_at
                FROM books_booksbooking
                WHERE uui = {user_id}
                GROUP BY book_id
            ) AS ub ON b.id = ub.book_id
            WHERE ub.book_id IS NOT NULL AND ub.is_returned IS FALSE
            GROUP BY b.id
        """
        cursor.execute(query)
        desc = cursor.description
        data = cursor.fetchall()
        cursor.close()
        return get_table_values(description=desc, data=data)

    @staticmethod
    def remove_book_from_booking(book_id: int, user_id: int):
        cursor = connection.cursor()
        now = timezone.now()
        query = f"""
            UPDATE books_booksbooking 
            SET is_returned = True, returned_at = '{now}'
            WHERE id IN (
                SELECT id
                FROM books_booksbooking
                WHERE book_id = {book_id} AND user_id = {user_id}
                GROUP BY book_id
                HAVING MAX(created_at)
            )
        """
        cursor.execute(query)
        cursor.close()
        return None

    @staticmethod
    def select_booking_by_book(book_id: int, user_id: int):
        query = f"""
            SELECT is_returned FROM books_booksbooking
            WHERE user_id = {user_id} AND book_id = {book_id}
        """
        cursor = connection.cursor()
        cursor.execute(query)
        desc = cursor.description
        data = cursor.fetchall()
        cursor.close()
        return get_table_values(description=desc, data=data)

