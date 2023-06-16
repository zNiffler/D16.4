from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group


class CommonSignupForm(SignupForm):

    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        Group.objects.get(name='common').user_set.add(user)
        return user
