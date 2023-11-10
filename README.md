# library_programs
An event page app for wagtail with single events, repeating event, event calendar, event categories, and age ranges. Uses JavaScript FullCalendar and bootstrap. There is an event registration feature currently in development. It uses the wagtail form builder, rather than wagtail's internal user system.

It's called library programs as it was design to support a public library's public programs, but could be used for a variety of use cases. 

Installation instructions: 
1) In your terminal, navigate to your_project_folder/library_programs. Install the dependencies by running pip install -r requirements.txt. 
2) Edit the settings file (usually found in your_project_folder/your_project_folder/settings/base.py). add "library_programs", the INSTALLED_APPS list
