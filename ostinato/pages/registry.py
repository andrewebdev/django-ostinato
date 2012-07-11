from django.utils.datastructures import SortedDict
from appregister import SortedRegistry


class ContentRegister(SortedRegistry):
    base = 'ostinato.pages.models.PageContent'
    discovermodule = 'models'

    def get_template_choices(self):
        template_choices = (('', '--------'),)

        for v in self.all():
            content_type = '%s.%s' % (v._meta.app_label, v.__name__)
            verbose_name = '%s | %s' % (v._meta.app_label, v._meta.verbose_name)
            template_choices += ((content_type.lower(), verbose_name.title()), )

        return template_choices

    def get_template_name(self, template_id):
        choices = self.get_template_choices()
        
        for c in choices:
            if c[0] == template_id:
                return c[1]

        return template_id


page_content = ContentRegister()

