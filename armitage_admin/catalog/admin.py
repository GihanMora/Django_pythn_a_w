import random
from io import StringIO, BytesIO

import pymongo
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
# Register your models here.

from .models import Author, Genre, Book, BookInstance, Language, Project
from .add_projects.add_new_projects import create_and_queue_project, get_project_state, get_completion_state
from .dump_projects.dump_results_of_a_project import project_simplified_dump, \
    project_simplified_dump_with_sources_and_confidence
from .send_mails.send_emails import send_notifications

from django.http import HttpResponse
import os, tempfile, zipfile
from wsgiref.util import FileWrapper
from django.conf import settings
import mimetypes

"""Minimal registration of Models.
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language)
"""

# admin.site.register(Genre)
# admin.site.register(Language)


class BooksInline(admin.TabularInline):
    """Defines format of inline book insertion (used in AuthorAdmin)"""
    model = Book


# @admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administration object for Author models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields),
       grouping the date fields horizontally
     - adds inline addition of books in author view (inlines)
    """
    list_display = ('last_name',
                    'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]


class BooksInstanceInline(admin.TabularInline):
    """Defines format of inline book instance insertion (used in BookAdmin)"""
    model = BookInstance


class BookAdmin(admin.ModelAdmin):
    """Administration object for Book models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of book instances in book view (inlines)
    """
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


class ProjectAdmin(admin.ModelAdmin):
    actions = ["export_as_csv"]


# admin.site.register(Book, BookAdmin)


# @admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    """Administration object for BookInstance models.
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )



class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        try:
            if(len(queryset)==1):
                for each_project in queryset:
                    project_id = each_project.project_id
                    # proj_state = get_project_state(project_id)
                    # print('state',proj_state)
                    filename = project_simplified_dump_with_sources_and_confidence(project_id)
                    print('here',filename)
                    download_name = each_project.project_name+'_'+str(project_id)+'.csv'
                    wrapper = FileWrapper(open(filename,errors='ignore'))
                    # content_type = mimetypes.guess_type(filename)[0]

                    response = HttpResponse(wrapper)
                    response['Content-Length'] = os.path.getsize(filename)
                    response['Content-Disposition'] = "attachment; filename=%s" % download_name
                    self.message_user(request, ngettext(
                        'The %s was successfully Exported.',
                        'The %s was successfully Exported.',
                        1,
                    ) % 'project', messages.SUCCESS)
                    return response
            elif(len(queryset)>1):
                filenames = []
                for each_project in queryset:
                    project_id = each_project.project_id
                    filename = project_simplified_dump_with_sources_and_confidence(project_id)
                    filenames.append(filename)

                zip_subdir = "project_group_dump"
                zip_filename = "%s.zip" % zip_subdir
                s = BytesIO()
                zf = zipfile.ZipFile(s, "w")

                for fpath in filenames:
                    # Calculate path for file in zip
                    fdir, fname = os.path.split(fpath)
                    zip_path = os.path.join(zip_subdir, fname)
                    zf.write(fpath, zip_path)
                zf.close()
                resp = HttpResponse(s.getvalue(), content_type='application/octet-stream')
                resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
                self.message_user(request, ngettext(
                    'The %s was successfully Exported.',
                    'The %s was successfully Exported.',
                    1,
                ) % 'project', messages.SUCCESS)
                return resp


        except pymongo.errors.ServerSelectionTimeoutError:

            self.message_user(request, ngettext(
                'Mongo server is offline',
                'Mongo server is offline',
                1,
            ), messages.ERROR)
        except Exception:

            self.message_user(request, ngettext(
                'Exception Occured, inform the developer',
                'Exception Occured, inform the developer',
                1,
            ), messages.ERROR)



    export_as_csv.short_description = "Export Selected Projects"


class QueueProjectAtWorkerMixin:
    def queue_project(self, request, queryset):
        try:
            for each_project in queryset:
                project_name = each_project.project_name

                key_phrases = [k.strip() for k in each_project.key_phrases.split(',')]
                project_id = each_project.project_id
                if(each_project.project_status=='Created'):
                    send_notifications(each_project.project_id,each_project.project_name)
                    create_and_queue_project(project_name,key_phrases,project_id)
                    print("project is added to the queue",project_name)
                    print("id",each_project.project_id)
                    each_project.project_status = "Queued"
                    each_project.save()

                self.message_user(request, ngettext(
                    'The project %s was successfully queued.',
                    'The project %s was successfully queued.',
                    1,
                ) % project_name, messages.SUCCESS)
        except pymongo.errors.ServerSelectionTimeoutError:

            self.message_user(request, ngettext(
                'Mongo server is offline, automatically informed to the developer.',
                'Mongo server is offline, automatically informed to the developer.',
                1,
            ), messages.ERROR)
        except Exception:

            self.message_user(request, ngettext(
                'Exception Occured, inform the developer',
                'Exception Occured, inform the developer',
                1,
            ), messages.ERROR)

    queue_project.short_description = "Queue Selected Projects"

class UpdateProjectAtWorkerMixin:
    def update_project_status(self, request, queryset):
        try:
            for each_project in queryset:
                project_name = each_project.project_name
                key_phrases = [k.strip() for k in each_project.key_phrases.split(',')]
                project_id = each_project.project_id
                proj_state = get_project_state(project_id)
                print('state', proj_state)
                each_project.project_status = proj_state
                each_project.save()
                print(project_name,"updating")
                completion_data = get_completion_state(project_id)
                completion_state,completion_count = completion_data[0],completion_data[1]
                each_project.project_completion = completion_state
                each_project.completion_counts = completion_count
                each_project.save()
                # create_and_queue_project(project_name,key_phrases,project_id)
                # print("project is added to the queue",project_name)
                # print("id",each_project.project_id)
                # each_project.project_status = "Queued"
                # each_project.save()
                self.message_user(request, ngettext(
                    'The state of the project %s was successfully updated.',
                    'The state of the project %s was successfully updated.',
                    1,
                ) % project_name, messages.SUCCESS)


        except pymongo.errors.ServerSelectionTimeoutError:

            self.message_user(request, ngettext(
                'Mongo server is offline',
                'Mongo server is offline',
                1,
            ), messages.ERROR)
        except Exception:

            self.message_user(request, ngettext(
                'Exception Occured, inform the developer',
                'Exception Occured, inform the developer',
                1,
            ), messages.ERROR)



    update_project_status.short_description = "Update Status of Selected Projects"

@admin.register(Project)
class HeroAdmin(admin.ModelAdmin, ExportCsvMixin, QueueProjectAtWorkerMixin, UpdateProjectAtWorkerMixin):
    # list_display = ("project_name", "key_phrases", "project_id", "created_date")
    list_display = ("project_name", "key_phrases", "project_id", "project_status", "created_date","project_completion","completion_counts")
    list_filter = ("project_name", "key_phrases", "created_date","project_completion","completion_counts")
    actions = ["export_as_csv", "queue_project","update_project_status"]