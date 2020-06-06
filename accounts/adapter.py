from allauth.account.adapter import DefaultAccountAdapter
from .tasks import send_async_mail

class AccountAdapter(DefaultAccountAdapter):
    
    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        send_async_mail(msg)