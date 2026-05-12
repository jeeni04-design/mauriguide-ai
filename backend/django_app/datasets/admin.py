import csv
import io
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.utils.html import format_html
from django.contrib import messages
from .models import Beach, FoodOutlet, WaterActivity, LandActivity, SiteToVisit, Hike


# ── Shared CSV export ─────────────────────────────────────────
def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [f.name for f in meta.fields]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, f) for f in field_names])
    return response
export_as_csv.short_description = 'Export selected as CSV'


# ── Shared image preview ──────────────────────────────────────
def image_preview(obj, field='image'):
    img = getattr(obj, field, None)
    if img:
        return format_html(
            '<img src="{}" style="height:60px;width:80px;object-fit:cover;border-radius:6px;border:1px solid #ddd"/>',
            img.url
        )
    return format_html('<span style="color:#999;font-size:12px">No image</span>')
image_preview.short_description = 'Image'


# ── Shared CSV import handler ─────────────────────────────────
def _handle_csv_import(request, Model, required_fields):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'No file uploaded.')
            return _csv_form(Model)
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a .csv file.')
            return _csv_form(Model)
        try:
            decoded = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            created = skipped = 0
            errors = []
            field_names = {f.name for f in Model._meta.fields}
            for i, row in enumerate(reader, start=2):
                try:
                    lat = float(row.get('latitude', '').strip())
                    lng = float(row.get('longitude', '').strip())
                except (ValueError, AttributeError):
                    skipped += 1
                    errors.append(f'Row {i}: invalid coordinates — skipped')
                    continue
                data = {}
                for key, val in row.items():
                    key = key.strip()
                    if key in field_names and key not in ('id', 'created_at', 'image'):
                        data[key] = val.strip() if val else ''
                data['latitude'] = lat
                data['longitude'] = lng
                for f in Model._meta.fields:
                    if f.name in data and f.get_internal_type() == 'IntegerField':
                        try:
                            data[f.name] = int(float(data[f.name]))
                        except (ValueError, TypeError):
                            skipped += 1
                            errors.append(f'Row {i}: invalid int for {f.name}')
                            data = None
                            break
                if data is None:
                    continue
                try:
                    Model.objects.create(**data)
                    created += 1
                except Exception as e:
                    skipped += 1
                    errors.append(f'Row {i}: {e}')
            msg = f'Import complete — {created} created, {skipped} skipped.'
            if errors:
                messages.warning(request, msg + ' Errors: ' + '; '.join(errors[:5]))
            else:
                messages.success(request, msg)
        except Exception as e:
            messages.error(request, f'Failed to process CSV: {e}')
    return _csv_form(Model)


def _csv_form(Model):
    from django.http import HttpResponse
    name = Model._meta.verbose_name_plural.title()
    html = f"""<!DOCTYPE html><html><head><title>Import {name}</title>
    <link rel="stylesheet" href="/static/admin/css/base.css"></head><body>
    <div id="container"><h1>Import {name} CSV</h1>
    <p>latitude and longitude columns are required.</p>
    <form method="post" enctype="multipart/form-data">
    <input type="file" name="csv_file" accept=".csv" required>
    <input type="submit" value="Upload and Import" class="default" style="margin-left:10px">
    </form><p><a href="../">&larr; Back</a></p></div></body></html>"""
    return HttpResponse(html)


# ── Beach ─────────────────────────────────────────────────────
@admin.register(Beach)
class BeachAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'latitude', 'longitude', 'image_thumb', 'created_at')
    search_fields = ('name', 'location', 'description')
    list_filter = ('location',)
    readonly_fields = ('created_at', 'image_thumb')
    ordering = ('name',)
    actions = [export_as_csv]
    fieldsets = (
        ('Basic info', {'fields': ('name', 'location', 'description')}),
        ('Coordinates', {'fields': ('latitude', 'longitude'), 'description': 'Decimal degrees e.g. -20.1234, 57.5678'}),
        ('Image', {'fields': ('image', 'image_thumb')}),
        ('Meta', {'fields': ('created_at',)}),
    )
    def image_thumb(self, obj): return image_preview(obj)
    image_thumb.short_description = 'Preview'
    def get_urls(self):
        return [path('import-csv/', self.admin_site.admin_view(self.import_csv), name='beach-import')] + super().get_urls()
    def import_csv(self, request):
        return _handle_csv_import(request, Beach, ['name', 'location', 'description', 'latitude', 'longitude'])


# ── FoodOutlet ────────────────────────────────────────────────
@admin.register(FoodOutlet)
class FoodOutletAdmin(admin.ModelAdmin):
    list_display = ('name', 'speciality', 'location', 'contact_number', 'latitude', 'longitude', 'image_thumb', 'created_at')
    search_fields = ('name', 'location', 'speciality', 'description')
    list_filter = ('location', 'speciality')
    readonly_fields = ('created_at', 'image_thumb')
    ordering = ('name',)
    actions = [export_as_csv]
    fieldsets = (
        ('Basic info', {'fields': ('name', 'location', 'speciality', 'contact_number', 'description')}),
        ('Coordinates', {'fields': ('latitude', 'longitude')}),
        ('Image', {'fields': ('image', 'image_thumb')}),
        ('Meta', {'fields': ('created_at',)}),
    )
    def image_thumb(self, obj): return image_preview(obj)
    image_thumb.short_description = 'Preview'
    def get_urls(self):
        return [path('import-csv/', self.admin_site.admin_view(self.import_csv), name='food-import')] + super().get_urls()
    def import_csv(self, request):
        return _handle_csv_import(request, FoodOutlet, ['name', 'location', 'contact_number', 'speciality', 'latitude', 'longitude'])


# ── WaterActivity ─────────────────────────────────────────────
@admin.register(WaterActivity)
class WaterActivityAdmin(admin.ModelAdmin):
    list_display = ('activity', 'category', 'segment', 'location', 'latitude', 'longitude', 'image_thumb', 'created_at')
    search_fields = ('activity', 'location', 'description')
    list_filter = ('category', 'segment')
    readonly_fields = ('created_at', 'image_thumb')
    ordering = ('activity',)
    actions = [export_as_csv]
    fieldsets = (
        ('Basic info', {'fields': ('activity', 'category', 'segment', 'location', 'description')}),
        ('Coordinates', {'fields': ('latitude', 'longitude')}),
        ('Image', {'fields': ('image', 'image_thumb')}),
        ('Meta', {'fields': ('created_at',)}),
    )
    def image_thumb(self, obj): return image_preview(obj)
    image_thumb.short_description = 'Preview'
    def get_urls(self):
        return [path('import-csv/', self.admin_site.admin_view(self.import_csv), name='water-import')] + super().get_urls()
    def import_csv(self, request):
        return _handle_csv_import(request, WaterActivity, ['activity', 'category', 'segment', 'location', 'latitude', 'longitude'])


# ── LandActivity ──────────────────────────────────────────────
@admin.register(LandActivity)
class LandActivityAdmin(admin.ModelAdmin):
    list_display = ('activity', 'category', 'place', 'latitude', 'longitude', 'image_thumb', 'created_at')
    search_fields = ('activity', 'place', 'description')
    list_filter = ('category',)
    readonly_fields = ('created_at', 'image_thumb')
    ordering = ('activity',)
    actions = [export_as_csv]
    fieldsets = (
        ('Basic info', {'fields': ('activity', 'category', 'place', 'description')}),
        ('Coordinates', {'fields': ('latitude', 'longitude')}),
        ('Image', {'fields': ('image', 'image_thumb')}),
        ('Meta', {'fields': ('created_at',)}),
    )
    def image_thumb(self, obj): return image_preview(obj)
    image_thumb.short_description = 'Preview'
    def get_urls(self):
        return [path('import-csv/', self.admin_site.admin_view(self.import_csv), name='land-import')] + super().get_urls()
    def import_csv(self, request):
        return _handle_csv_import(request, LandActivity, ['activity', 'place', 'latitude', 'longitude', 'category'])


# ── Hike ──────────────────────────────────────────────────────
@admin.register(Hike)
class HikeAdmin(admin.ModelAdmin):
    list_display = ('trail_name', 'difficulty', 'latitude', 'longitude', 'image_thumb', 'created_at')
    search_fields = ('trail_name', 'details')
    list_filter = ('difficulty',)
    readonly_fields = ('created_at', 'image_thumb')
    ordering = ('difficulty', 'trail_name')
    actions = [export_as_csv]
    fieldsets = (
        ('Basic info', {'fields': ('trail_name', 'difficulty', 'details')}),
        ('Coordinates', {'fields': ('latitude', 'longitude')}),
        ('Image', {'fields': ('image', 'image_thumb')}),
        ('Meta', {'fields': ('created_at',)}),
    )
    def image_thumb(self, obj): return image_preview(obj)
    image_thumb.short_description = 'Preview'
    def get_urls(self):
        return [path('import-csv/', self.admin_site.admin_view(self.import_csv), name='hike-import')] + super().get_urls()
    def import_csv(self, request):
        return _handle_csv_import(request, Hike, ['trail_name', 'difficulty', 'latitude', 'longitude', 'details'])


# ── SiteToVisit ───────────────────────────────────────────────
@admin.register(SiteToVisit)
class SiteToVisitAdmin(admin.ModelAdmin):
    list_display = ('place', 'location', 'best_time', 'latitude', 'longitude', 'image_thumb', 'created_at')
    search_fields = ('place', 'location', 'address', 'why_visit')
    list_filter = ('location',)
    readonly_fields = ('created_at', 'image_thumb')
    ordering = ('place',)
    actions = [export_as_csv]
    fieldsets = (
        ('Basic info', {'fields': ('place', 'location', 'address')}),
        ('Details', {'fields': ('why_visit', 'visitor_info', 'best_time', 'tips')}),
        ('Coordinates', {'fields': ('latitude', 'longitude')}),
        ('Image', {'fields': ('image', 'image_thumb')}),
        ('Meta', {'fields': ('created_at',)}),
    )
    def image_thumb(self, obj): return image_preview(obj)
    image_thumb.short_description = 'Preview'
    def get_urls(self):
        return [path('import-csv/', self.admin_site.admin_view(self.import_csv), name='site-import')] + super().get_urls()
    def import_csv(self, request):
        return _handle_csv_import(request, SiteToVisit, ['place', 'address', 'location', 'latitude', 'longitude', 'why_visit'])