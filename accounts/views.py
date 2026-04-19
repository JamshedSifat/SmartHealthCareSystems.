from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import redirect, render

from .forms import UserForm, UserProfileForm
from .models import UserProfile

# Optional: only if these apps exist in your project
try:
    from appointments.models import Appointment
except Exception:
    Appointment = None


def login(request):
    if request.method == "POST":
        username = request.POST.get("u_name")
        password = request.POST.get("u_password")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect("accounts:login")

        authenticated_user = authenticate(request, username=username, password=password)

        if authenticated_user is not None:
            auth_login(request, authenticated_user)
            messages.success(request, f"Welcome, {username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


def register(request):
    if request.method == "POST":
        u_name = request.POST.get("u_name", "").strip()
        u_fname = request.POST.get("u_fname", "").strip()
        u_lname = request.POST.get("u_lname", "").strip()
        u_email = request.POST.get("u_email", "").strip()
        u_password = request.POST.get("u_password", "")
        u_age = request.POST.get("u_age", "")
        u_address = request.POST.get("u_address", "").strip()
        u_mobile = request.POST.get("u_mobile", "").strip()
        u_gender = request.POST.get("u_gender", "")

        # Only username, email, and password are required
        if not u_name or not u_email or not u_password:
            messages.error(request, "Username, email, and password are required.")
            return redirect('accounts:register')

        if User.objects.filter(username=u_name).exists():
            messages.error(request, "Username already in use. Please choose another.")
            return redirect('accounts:register')

        if User.objects.filter(email=u_email).exists():
            messages.error(request, "Email already in use. Please try another one.")
            return redirect('accounts:register')

        # Age is optional; default to 0 if empty or invalid
        try:
            age_int = int(u_age) if u_age else 0
        except ValueError:
            age_int = 0

        try:
            user = User.objects.create_user(
                username=u_name,
                first_name=u_fname,
                last_name=u_lname,
                email=u_email,
                password=u_password
            )
        except IntegrityError:
            messages.error(request, "There was an issue creating your account. Please try again.")
            return redirect('accounts:register')

        UserProfile.objects.create(
            user=user,
            age=age_int,
            address=u_address,
            mobile=u_mobile,
            gender=u_gender if u_gender in dict(UserProfile.GENDER) else "Male"
        )

        authenticated_user = authenticate(request, username=u_name, password=u_password)
        if authenticated_user:
            auth_login(request, authenticated_user)
            messages.success(request, "Your account has been successfully created.")
            return redirect("home")

        messages.success(request, "Account created. Please log in.")
        return redirect('accounts:login')

    return render(request, "accounts/register.html")


@login_required
def user_profile(request):
    # Ensure a profile exists
    user_profile, _created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'age': 0, 'address': '', 'mobile': '', 'gender': 'Male'}
    )
    profile_form = UserProfileForm(instance=user_profile)
    user_form = UserForm(instance=request.user)

    appointments = Appointment.objects.filter(user=request.user) if Appointment else []

    if request.method == "POST":
        if "delete_account" in request.POST:
            request.user.delete()
            auth_logout(request)
            messages.success(request, "Your account has been deleted.")
            return redirect('accounts:login')

        profile_form = UserProfileForm(request.POST, instance=user_profile)
        user_form = UserForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:user_profile')
        else:
            messages.error(request, "Error updating profile. Please check the form.")

    context = {
        'user_profile': user_profile,
        'profile_form': profile_form,
        'user_form': user_form,
        'appointments': appointments,
    }
    return render(request, 'accounts/user_profile.html', context)


@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "Logged out Successfully!")
    return redirect('home')
