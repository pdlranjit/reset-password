from django.shortcuts import render,redirect
from.models import StudentUser,PasswordReset
from.forms import RegisterForm,Loginform,ForgotPassword,ResetPasswordForm
from django.contrib.auth import logout,login
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse


# Create your views here.
def RegisterView(request):
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
            
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request,'login_api/register.html',{'form':form})

            
        
    else:
            form=RegisterForm()
            return render(request,'login_api/register.html',{'form':form})
    
        
def LoginView(request):
    if request.method=='POST':
        form=Loginform(request.POST)
        if form.is_valid():
           user = form.get_user()  # Get the authenticated user
           login(request, user)

           messages.success(request, "Successfully logged in!")
           return redirect('logout')
        else:
             form=Loginform()
             return render(request,'login_api/logout.html',{'form':form})
       
             

    else:
        form=Loginform()
        return render(request,'login_api/login.html',{'form':form})
    
def LogoutView(request):
    logout(request)
    return render(request, 'login_api/login.html')
     

    
def forgot_password(request):
    if request.method=='POST':
        email=request.POST.get('email')
        print(email)
        try:
            user=StudentUser.objects.get(email=email)
            
            new_password_reset=PasswordReset(user=user)
            new_password_reset.save()

            #create password url
            password_reset_url=reverse('reset-password',kwargs={'reset_id':new_password_reset.reset_id})

            full_password_reset_url=f'{request.scheme}://{request.get_host()}{password_reset_url}'

            #email_content
            email_body=f'Reset your password using the link below:\n\n\n{full_password_reset_url}'

            email_message=EmailMessage(
                'Reset your Password',#email subject
                email_body,
                settings.EMAIL_HOST_USER,#email sender
                [email] 
                )#email receiver

            email_message.fail_silently=True
            email_message.send()

            return redirect('password-reset-sent',reset_id=new_password_reset.reset_id)
            

            
           
            
        except StudentUser.DoesNotExist:
            messages.error(request,f'No user with this {email} found')
            return redirect('forgot-password')

    form= ForgotPassword()
    return render(request,'login_api/forgot_password.html',{'form':form})
def PasswordResetSent(request, reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
       return render(request, 'login_api/password_reset_sent.html')
    else:
        #redirect to forgot password page if code does not exist
        return redirect('forgot-password')

def ResetPassword(request, reset_id):
    # Try to fetch the reset object
    try:
        password_reset = PasswordReset.objects.get(reset_id=reset_id)
    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid reset link')
        return redirect('forgot-password')

    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            passwords_have_error = False

            # Check if passwords match
            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')

            # Check password length
            if len(password) < 5:
                passwords_have_error = True
                messages.error(request, 'Password must be at least 5 characters long')

            # Check if reset link expired
            expiration_time = password_reset.created_at + timezone.timedelta(minutes=10)
            if timezone.now() > expiration_time:
                password_reset.delete()
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

            if not passwords_have_error:
                # Reset password
                user = password_reset.user
                user.set_password(password)
                user.save()

                # Delete reset record
                password_reset.delete()

                messages.success(request, 'Password reset successful. Proceed to login')
                return redirect('login')

    return render(request, 'login_api/reset_password.html', {'form': form})

