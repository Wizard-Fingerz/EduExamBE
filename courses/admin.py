from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Course, Module, Lesson

class CourseResource(resources.ModelResource):
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'instructor', 'thumbnail', 'price',
                 'is_published', 'created_at', 'updated_at')
        export_order = fields

class ModuleResource(resources.ModelResource):
    class Meta:
        model = Module
        fields = ('id', 'course', 'title', 'description', 'order', 'created_at', 'updated_at')
        export_order = fields

class LessonResource(resources.ModelResource):
    class Meta:
        model = Lesson
        fields = ('id', 'module', 'title', 'content', 'video_url', 'duration',
                 'order', 'created_at', 'updated_at')
        export_order = fields

@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    resource_class = CourseResource
    list_display = ('title', 'instructor', 'price', 'is_published', 'created_at')
    list_filter = ('is_published', 'instructor')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    raw_id_fields = ('instructor', 'students')

@admin.register(Module)
class ModuleAdmin(ImportExportModelAdmin):
    resource_class = ModuleResource
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    ordering = ('course', 'order')
    raw_id_fields = ('course',)

@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):
    resource_class = LessonResource
    list_display = ('title', 'module', 'order', 'duration', 'created_at')
    list_filter = ('module__course', 'module')
    search_fields = ('title', 'content')
    ordering = ('module', 'order')
    raw_id_fields = ('module',)
