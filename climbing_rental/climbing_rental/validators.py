import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SimplePasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 6:
            raise ValidationError(_('Hasło musi mieć co najmniej 6 znaków.'), code='password_too_short')
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_('Hasło musi zawierać co najmniej 1 wielką literę.'), code='no_upper')
        if not re.search(r'\d', password):
            raise ValidationError(_('Hasło musi zawierać co najmniej 1 cyfrę.'), code='no_digit')

    def get_help_text(self):
        return _('Hasło musi mieć min. 6 znaków, 1 wielką literę i 1 cyfrę.')