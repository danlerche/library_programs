An event page app for wagtail with single events, repeating event, event calendar, event categories, and age ranges. Uses JavaScript FullCalendar and bootstrap.

There is an event registration feature currently in the dev branch. For user info it uses the wagtail form builder, rather than wagtail's internal user system.

Installation instructions:

    In your terminal, navigate to your_project_folder/library_programs. Install the dependencies by running pip install -r requirements.txt.
    Edit the settings file (usually found in your_project_folder/your_project_folder/settings/base.py). add "library_programs", the INSTALLED_APPS list
    In your project folder do the usual python manage.py migrate
