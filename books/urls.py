from django.urls import path
from books.views import (
    get_all_books, create_user, create_user_form, create_book_form, get_all_users,
    create_book, get_user, remove_book_from_lending, add_book_to_lending, search_article
)

urlpatterns = [
    path("", get_all_books, name="all books"),
    path("create/form/", create_book_form, name="create book form"),
    path("create/", create_book, name="create book"),
    path("add-book/", add_book_to_lending, name="add book"),
    path("remove-book/", remove_book_from_lending, name="remove book"),
    path("search/", search_article, name="search book article"),
    path("readers/", get_all_users, name="all users"),
    path("reader-card/", get_user, name="preload get user"),
    path("reader-card/form/", create_user_form, name="create user form"),
    path("reader-card/create/", create_user, name="create user"),
    path("reader-card/<int:user_id>/", get_user, name="get user"),

]
