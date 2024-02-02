import json
from typing import Union
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.utils import timezone
from core.utils import get_post_values, convert_cookies_str_to_dict, handle_uploaded_file
from books.models import Books, Users, BooksBooking, BooksStash, create_unique_url, create_unique_article


def search_article(request: HttpRequest):
    article = request.GET.get("article")
    user_values = convert_cookies_str_to_dict(request.COOKIES.get("user"))
    if article is None or article == "":
        return HttpResponse(render(request, "book.html", context={"book": None}))

    books = Books.get_by_article(article=article)
    book = books[0] if len(books) > 0 else None
    if book is None:
        return HttpResponse(render(request, "book.html", context={"book": None}))

    if user_values is not None:
        bb = BooksBooking.select_booking_by_book(
            book_id=int(book["id"]),
            user_id=int(user_values["id"])
        )
        is_returned = (bb[0])["is_returned"] if len(bb) > 0 else True
    else:
        is_returned = True

    book_stash = list(BooksStash.objects.filter(book_id=int(book["id"])))
    count = 0 if len(book_stash) == 0 else (book_stash[0]).count
    return HttpResponse(render(
        request, "book.html",
        context={"book": book, "count": count, "is_returned": is_returned})
    )


def get_all_books(request: HttpRequest):
    user_values = request.COOKIES.get("user")
    if user_values is None:
        books = Books.get_all()
    else:
        json_object = convert_cookies_str_to_dict(user_values)
        books = BooksBooking.get_books_without_booking(user_id=int(json_object["id"]))
    return render(request, "books.html", context={"books": books})


def create_user_form(request: HttpRequest):
    return render(request=request, template_name="createUser.html")


def create_user(request: HttpRequest):
    items = request.POST.items()
    values = get_post_values(items)
    values["is_author"] = True if values.get("is_author") is not None else False
    u = Users(**values)
    u.save()
    values["id"] = f"{u.id}"
    response = HttpResponseRedirect(redirect_to="/books/readers/")
    response.set_cookie(key="user", value=values, max_age=3600)
    return response


def get_all_users(request: HttpRequest):
    users = Users.objects.all()
    context = {"users": users}
    return render(request=request, template_name="usersList.html", context=context)


def get_user(request: HttpRequest, user_id: Union[int, None] = None):
    try:
        user_values = convert_cookies_str_to_dict(request.COOKIES.get("user"))
        if user_values is None and user_id is None:
            return HttpResponseRedirect(redirect_to="/books/reader-card/form/")

        if user_id is not None:
            user_object = Users.objects.get(pk=user_id)
        else:
            user_object = Users.objects.get(pk=int(user_values["id"]))

        serialized_obj = serializers.serialize('json', {user_object})
        json_obj = json.loads(serialized_obj)
        user = (json_obj[0])["fields"]
        user["id"] = f"{(json_obj[0])['pk']}"
        landing_books = BooksBooking.get_books_with_booking(user_id=int(user["id"]))
        context = {"user": user, "landing_books": landing_books}

        response = HttpResponse(render(request=request, template_name="user.html", context=context))
        response.set_cookie(key="user", value=user, max_age=3600)
        return response

    except Users.DoesNotExist:
        context = {"user": None}
        return render(request=request, template_name="user.html", context=context)

    except Exception as e:
        print(str(e))
        print("Error", "books.views.get_user")
        return HttpResponseRedirect(redirect_to="/books/")


def create_book_form(request: HttpRequest):
    return HttpResponse(render(request=request, template_name="createBook.html"))


def create_book(request: HttpRequest):
    user_values = request.COOKIES.get("user")
    if user_values is None:
        return HttpResponse(render(
            request, "createBook.html",
            context={"message": "You ain't the user"})
        )

    json_object = convert_cookies_str_to_dict(user_values)
    if json_object.get("is_author") is False:
        return HttpResponse(render(
            request, "createBook.html",
            context={"message": "You ain't the author"})
        )
    values = get_post_values(request.POST.items())
    file = request.FILES

    if file.get("cover") is not None:
        image = handle_uploaded_file(image=file["cover"], static_dir="books/static/images")
    else:
        image = ""
    if values.get("pages") is None or values.get("pages") == "":
        values["pages"] = 10

    values["unique_url"], values["article"] = create_unique_url(), create_unique_article()
    values["cover"] = image
    values["user_id"] = int(json_object["id"])
    count = int(values["count"]) if (values.get("count") is not None or values.get("count") != "") else 10
    del values["count"]
    b = Books(**values)
    b.save()
    bs = BooksStash(book_id=b.pk, count=count)
    bs.save()
    return HttpResponseRedirect(redirect_to="/books/")


def add_book_to_lending(request: HttpRequest):
    user_values = request.COOKIES.get("user")
    if user_values is None:
        print("User isn't sign in")
        return HttpResponseRedirect(redirect_to="/books/")

    json_object = convert_cookies_str_to_dict(user_values)
    values = get_post_values(request.POST.items())
    del values["add-lending"]
    values["created_at"] = timezone.datetime.now()
    values["book_id"] = int(values["book_id"])

    try:
        bs = BooksStash.objects.filter(book_id=values["book_id"])
        if bs.count == 0:
            print("Sorry, you cant add this book, wait for when someone return")
            return HttpResponseRedirect(redirect_to="/books/")
    except BooksStash.DoesNotExist:
        print("No book in db with this id")
        return HttpResponseRedirect(redirect_to="/books/")

    values["user_id"] = int(json_object["id"])
    bl = BooksBooking(**values)
    bl.save()
    BooksStash.update_count(book_id=values["book_id"], is_positive=False)
    return HttpResponseRedirect(redirect_to="/books/")


def remove_book_from_lending(request: HttpRequest):
    user_values = request.COOKIES.get("user")
    if user_values is None:
        print("User isn't sign in")
        return HttpResponse()

    json_object = convert_cookies_str_to_dict(user_values)
    values = get_post_values(request.POST.items())
    del values["remove-book"]
    book_id = int(values["book_id"])

    try:
        bs = BooksStash.objects.filter(book_id=book_id)
    except BooksStash.DoesNotExist:
        print("No book in db with this id")
        return HttpResponseRedirect(redirect_to="/books/")

    user_id = int(json_object["id"])
    bb = BooksBooking.remove_book_from_booking(book_id=book_id, user_id=user_id)
    BooksStash.update_count(book_id=book_id, is_positive=True)
    return HttpResponseRedirect(redirect_to=f"/books/reader-card/{user_id}/")
