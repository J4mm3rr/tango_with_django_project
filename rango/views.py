from datetime import datetime
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import Category, Page
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm


def index(request):
        request.session.set_test_cookie()
        category_list = Category.objects.order_by('-likes')[:5]
        page_list = Page.objects.order_by('-views')[:5]
        context_dict = {'categories': category_list,
                        'pages': page_list}

        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']

        response = render(request, 'rango/index.html', context=context_dict)
        return response


def about(request):
        if request.session.test_cookie_worked():
                print("TEST COOKIE WORKED!")
                request.session.delete_test_cookie()

        context_dict = {'boldmessage': "This tutorial has been put together by James"}

        visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']

        return render(request, 'rango/about.html', context=context_dict)


@login_required
def add_page(request, category_name_slug):
        try:
                category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
                category = None

        form = PageForm()

        if request.method == 'POST':
                form = PageForm(request.POST)

                if form.is_valid():
                        if category:
                                page = form.save(commit=False)
                                page.category = category
                                page.views = 0
                                page.save()
                                return show_category(request, category_name_slug)

                else:
                        print(form.errors)

        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context_dict)


@login_required
def add_category(request):
        form = CategoryForm()

        if request.method == 'POST':
                # We only want to process the form if this is a POST request.
                # In other cases, the form is just rendered and returned.
                form = CategoryForm(request.POST)

                if form.is_valid():
                        # Since form is valid, we save the new category to database.
                        # and redirect user to index, where it will appear in list.
                        form.save(commit=True)
                        return index(request)

        else:
                # Errors encountered in form.
                print(form.errors)

        return render(request, 'rango/add_category.html', {'form': form})


def show_category(request, category_name_slug):
        context_dict = {}

        try:
                # Can we find a category slug with the given name?
                category = Category.objects.get(slug=category_name_slug)

                # Retrieve all related pages
                pages = Page.objects.filter(category=category)

                context_dict['pages'] = pages
                context_dict['category'] = category

        except Category.DoesNotExist:
                context_dict['pages'] = None
                context_dict['category'] = None

        return render(request, 'rango/category.html', context_dict)


def register(request):
        # State of this registration
        registered = False

        if request.method == 'POST':
                user_form = UserForm(data=request.POST)
                profile_form = UserProfileForm(data=request.POST)

                if user_form.is_valid() and profile_form.is_valid():
                        user = user_form.save()

                        # Hash password with set_password()
                        user.set_password(user.password)
                        user.save()

                        # Now sort profile, no commit as we must first assign user FK
                        profile = profile_form.save(commit=False)
                        profile.user = user

                        if 'picture' in request.FILES:
                                profile.picture = request.FILES['picture']

                        profile.save()
                        registered = True

                else:
                        # Invalid form(s)
                        print(user_form.errors, profile_form.errors)

        else:
                # Not HTTP POST, render our registration forms
                user_form = UserForm()
                profile_form = UserProfileForm()

        return render(request,
                      'rango/register.html',
                      {'user_form': user_form,
                       'profile_form': profile_form,
                       'registered': registered, })


def user_login(request):
        if request.method == 'POST':
                # If this request is a POST, get the username and password from it.
                username = request.POST.get('username')
                password = request.POST.get('password')

                user = authenticate(username=username, password=password)

                if user:
                        if user.is_active:
                                login(request, user)
                                return HttpResponseRedirect(reverse('index'))
                        else:
                                # this account is inactive
                                return HttpResponse("Your Rango account is disabled.")
                else:
                        # Bad login  details, no login possible
                        print("Invalid login details: {0}, {1}".format(username, password))
                        return HttpResponse("Invalid login details supplied.")

        else:
                # This is not a POST request.
                return render(request, 'rango/login.html')


@login_required
def user_logout(request):
        logout(request)
        return HttpResponseRedirect(reverse(index))


@login_required
def restricted(request):
        return render(request, 'rango/restricted.html')


# HELPER FUNCTIONS
def get_server_side_cookie(request, cookie, default_val=None):
        val = request.session.get(cookie)
        if not val:
                val = default_val
        return val


def visitor_cookie_handler(request):
        visits = int(get_server_side_cookie(request, 'visits', '1'))
        last_visit_cookie = get_server_side_cookie(request, 'last_visit',
                                                   str(datetime.now()))

        last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                            '%Y-%m-%d %H:%M:%S')

        if (datetime.now() - last_visit_time).days > 0:
                visits = visits + 1
                request.session['last_visit'] = str(datetime.now())
        else:
                request.session['last_visit'] = last_visit_cookie

        request.session['visits'] = visits