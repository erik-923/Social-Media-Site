from django import forms
from .models import Chat, Message
from django.contrib.auth import get_user_model
from django.utils.html import format_html


User = get_user_model()

class ChatForm(forms.Form):
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['recipients'] = forms.ModelMultipleChoiceField(
            queryset=request.user.profile.friends.all(),
            widget=forms.CheckboxSelectMultiple(),
            label = ''
        )

        self.fields['recipients'].label_from_instance = self.label_from_user_instance

    def label_from_user_instance(self, user):
        # Customize the label for each user instance with an image
        image_html = format_html('<img src="{}" alt="{}" class="rounded-circle img-fluid" height="50" width="50">', user.profile_pic.url, user.user.username)
        return format_html('<div class="p-2 my-1">{} {} {}</div>', image_html, user.user.first_name, user.user.last_name)

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('message', )