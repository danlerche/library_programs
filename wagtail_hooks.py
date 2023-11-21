from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from wagtail.admin.panels import FieldPanel, TabbedInterface, ObjectList
from wagtail.admin.ui.tables import UpdatedAtColumn
from .models import (EventCategory, Event, EventAudience, EventAge, EventAge, FullCalendarLink, RegistrationUserFormBuilder, Registration, RegistrationFormPage)
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail.admin.filters import WagtailFilterSet
import json, csv
from django.http import HttpResponse
from wagtail import hooks
from wagtail.snippets.bulk_actions.snippet_bulk_action import SnippetBulkAction
from wagtail.admin.views.bulk_action import BulkAction
from .views import events_with_registration
from django.urls import path, reverse
from wagtail.admin.menu import MenuItem

@hooks.register('register_admin_urls')
def event_with_reg_url():
    return [
        path('events_with_registration/', events_with_registration, name='event_regisitration'),
    ]

@hooks.register('register_admin_menu_item')
def register_event_reg_menu_item():
    return MenuItem('Event Registrations', reverse('event_regisitration'), icon_name="date")

class EventCategoryAdmin(SnippetViewSet):
    model = EventCategory
    menu_label = 'Event Category'
    icon = 'list-ul'
    base_url_path = "category"

class EventAudienceAdmin(SnippetViewSet):
    model = EventAudience
    menu_label = 'Audience'
    icon = 'list-ul'
    list_display = ('audience_name',)
    base_url_path = "audience"

class EventAgeAdmin(SnippetViewSet):
    model = EventAge
    menu_label = 'Age Range'
    icon = 'list-ul'
    base_url_path = "age"

class EventFilterSet(WagtailFilterSet):
    class Meta:
        model = Event
        fields = ['enable_registration', 'event_category_id', 'age_range', 'event_date']

class EventAdmin(SnippetViewSet):
    model = Event
    menu_label = 'Event'
    icon = 'date'
    list_display = ('title', 'event_date', 'time_from', 'time_to', 'repeats', 'until', 'featured_on_home_page', UpdatedAtColumn())
    #list_filter = {'event_category_id', 'age_range'}
    index_template_name = 'library_programs/registration/admin_snippet/event_admin_index.html'
    filterset_class = EventFilterSet
    base_url_path = "event"

class LinkToCalendarAdmin(SnippetViewSet):
    model = FullCalendarLink
    menu_label = 'Link to the full calendar page'
    icon = 'link'
    base_url_path = "calendar_link"

class FilterByEvent(WagtailFilterSet):
    class Meta:
        model = Registration
        fields = ['event_name']

class RegistrationAdmin(SnippetViewSet):
    model = Registration
    menu_label = 'Registrations' 
    icon = 'doc-full'
    base_url_path = 'registration'
    list_display = ('name','email', 'event_name', 'registration_date' ,'wait_listed')
    index_template_name = 'library_programs/registration/index.html'
    filterset_class = FilterByEvent
    edit_template_name = 'library_programs/registration/admin_snippet/edit.html'

    edit_handler = TabbedInterface([
        ObjectList([FieldPanel("registration_date", read_only=True), FieldPanel("user_info", read_only=True), FieldPanel("wait_list")], 
            heading="Registrant"),
    ])

#deletes the registration form entry when the registration is deleted
    @hooks.register('after_delete_snippet')
    def after_snippet_delete(request, objects):
        for obj in objects: 
            user_id = obj.user_info.id
            user_info = RegistrationUserFormBuilder.objects.get(id=user_id)
            user_info.delete()
        #return HttpResponse(f"{user_info} has been deleted", content_type="text/plain")
        return request

@hooks.register('register_bulk_action')
class ExportCSV(BulkAction):
    display_name = "Export CSV"
    aria_label = "Export CSV"
    action_type = "export_csv"
    template_name = "library_programs/registration/admin_snippet/export_csv.html"
    models = [Registration]
    
    @hooks.register("before_bulk_action")
    def hook_function(request, action_type, objects, action_class_instance, **kwargs):
        if action_type == 'export_csv':
            fields = []
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="export_registration_info.csv"'
            writer = csv.writer(response)

            for obj in objects:
                #the user_info labels are extracted from json in a single field
                user_fields = list(obj.user_info.form_data.keys())
                #convert the obj class to dictionary and extract the keys
                obj_dic_keys = vars(obj).keys()
                #convert to a list
                obj_keys_list = list(obj_dic_keys)
            #remove uneeded labels
            obj_keys_list.remove('user_info_id')
            obj_keys_list.remove('_state')

            #clean up names
            static_fields = []
            for okl in obj_keys_list:
                okl_replace = okl.replace("event_name_id", "event_name")
                static_fields.append(okl_replace)

            fields = static_fields + user_fields

            field_labels = []
            for flds in fields:
                field_labels.append(flds.replace("_", " ").title())
            writer.writerow(field_labels)

            user_info_values = []
            static_values = []
            for obj in objects:
                user_info_values.append(obj.user_info.form_data.values())
                if obj.wait_list == True:
                    wait_list = 'Yes'
                elif obj.wait_list == False:
                    wait_list = 'No'
                static_values.append(list((obj.id, str(obj.event_name), obj.registration_date.strftime("%Y-%m-%d %H:%M"), wait_list)))

            user_values = [list(val) for val in user_info_values]

            #clean up boolean field output
            for user_info in user_values:
                if ['No'] in user_info:
                    user_info[user_info.index(['No'])] = 'No'
                if ['Yes'] in user_info:
                    user_info[user_info.index(['Yes'])] = 'Yes'

            registration_values = []

            for static, user in zip(static_values, user_values):
                registration_values.append(static + user)

            for rv in registration_values:
                writer.writerow(rv)
            #uncomment to test output without exporting a CSV
            #return HttpResponse(f"{registration_values}", content_type="text/plain")
            return response

class RegistrationFormAdmin(SnippetViewSet):
    model = RegistrationFormPage
    menu_label = 'Registration Form'
    icon = 'form'
    base_url_path = "registration-form"

class EventAdminGroup(SnippetViewSetGroup):
    menu_label = 'Programs & Events'
    menu_icon = 'date'
    menu_order = 200
    items = (EventAdmin, EventCategoryAdmin, EventAudienceAdmin, EventAgeAdmin, LinkToCalendarAdmin, 
        RegistrationFormAdmin, RegistrationAdmin)

register_snippet(EventAdminGroup)