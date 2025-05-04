from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        # Nuke session key if it exists
        request.session.pop('account_verified_email_next', None)

        url = super().get_email_confirmation_url(request, emailconfirmation)

        if '?next=' in url:
            url = url.split('?next=')[0]

        return url
