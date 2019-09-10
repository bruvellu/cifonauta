from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Author name.', unique=True, max_length=200, verbose_name='name')),
                ('slug', models.SlugField(help_text='Author name slug.', max_length=200, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this author.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this author.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'author',
                'verbose_name_plural': 'authors',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='City name.', unique=True, max_length=64, verbose_name='name')),
                ('slug', models.SlugField(help_text='City name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this city.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this city.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Country name.', unique=True, max_length=64, verbose_name='name')),
                ('name_pt', models.CharField(help_text='Country name.', unique=True, max_length=64, verbose_name='name')),
                ('name_en', models.CharField(null=True, max_length=64, blank=True, help_text='Country name.', unique=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='Country name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this country.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this country.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'verbose_name': 'country',
                'verbose_name_plural': 'country',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_filepath', models.CharField(help_text='Local source file.', max_length=200, verbose_name='local source file', blank=True)),
                ('thumb_filepath', models.ImageField(help_text='Folder storing thumbnails.', upload_to='site_media/images/thumbs', verbose_name='web thumbnail')),
                ('old_filepath', models.CharField(help_text='Path to original file.', max_length=200, verbose_name='original source file', blank=True)),
                ('timestamp', models.DateTimeField(help_text='File modification date.', verbose_name='timestamp')),
                ('highlight', models.BooleanField(default=False, help_text='Image that deserves highlight.', verbose_name='highlight')),
                ('cover', models.BooleanField(default=False, help_text='Image aesthetically beautiful to be used on the home page. ', verbose_name='cover image')),
                ('is_public', models.BooleanField(default=False, help_text='Tells if image is visible to anonymous users.', verbose_name='public')),
                ('review', models.BooleanField(default=False, help_text='Tells if image should be revised.', verbose_name='under review')),
                ('notes', models.TextField(help_text='Extra field for annotations about the image.', verbose_name='notes', blank=True)),
                ('notes_pt', models.TextField(help_text='Extra field for annotations about the image.', verbose_name='notes', blank=True)),
                ('notes_en', models.TextField(help_text='Extra field for annotations about the image.', null=True, verbose_name='notes', blank=True)),
                ('pub_date', models.DateTimeField(help_text='Image publication date at Cifonauta.', verbose_name='publication date', auto_now_add=True)),
                ('title', models.CharField(help_text='Image title.', max_length=200, verbose_name='title', blank=True)),
                ('title_pt', models.CharField(help_text='Image title.', max_length=200, verbose_name='title', blank=True)),
                ('title_en', models.CharField(help_text='Image title.', max_length=200, null=True, verbose_name='title', blank=True)),
                ('caption', models.TextField(help_text='Image caption.', verbose_name='caption', blank=True)),
                ('caption_pt', models.TextField(help_text='Image caption.', verbose_name='caption', blank=True)),
                ('caption_en', models.TextField(help_text='Image caption.', null=True, verbose_name='caption', blank=True)),
                ('date', models.DateTimeField(help_text='Image creation date.', verbose_name='date', blank=True)),
                ('geolocation', models.CharField(help_text='Image geolocation in decimal format.', max_length=25, verbose_name='geolocation', blank=True)),
                ('latitude', models.CharField(help_text='Latitude where image was created.', max_length=12, verbose_name='latitude', blank=True)),
                ('longitude', models.CharField(help_text='Longitude where image was created.', max_length=12, verbose_name='longitude', blank=True)),
                ('web_filepath', models.ImageField(help_text='Path to web file.', upload_to='site_media/images/', verbose_name='web file')),
                ('datatype', models.CharField(default='photo', help_text='Media type.', max_length=10, verbose_name='media type')),
                ('city', models.ForeignKey(blank=True, to='meta.City', help_text='City shown in the image (or city where it was collected).', null=True, verbose_name='cidade', on_delete=models.DO_NOTHING)),
                ('country', models.ForeignKey(blank=True, to='meta.Country', help_text='Country shown in the image (or country where it was collected).', null=True, verbose_name='country', on_delete=models.DO_NOTHING)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'photo',
                'verbose_name_plural': 'photos',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Reference identifier (Mendeley ID).', unique=True, max_length=100, verbose_name='name')),
                ('slug', models.SlugField(help_text='Reference identifier slug.', max_length=100, verbose_name='slug', blank=True)),
                ('citation', models.TextField(help_text='Reference formatted reference.', verbose_name='citation', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this reference.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this reference.', verbose_name='number of videos', editable=False)),
                ('images', models.ManyToManyField(help_text='Photos linked to this reference.', to='meta.Image', null=True, verbose_name='photos', blank=True)),
            ],
            options={
                'ordering': ['-citation'],
                'verbose_name': 'reference',
                'verbose_name_plural': 'references',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rights',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Name of the copyrights owner.', unique=True, max_length=64, verbose_name='name')),
                ('slug', models.SlugField(help_text='Copyright owner name slug.', max_length=64, verbose_name='slug', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'copyrights owner',
                'verbose_name_plural': 'copyrights owners',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Size class name.', unique=True, max_length=32, verbose_name='name', choices=[('<0,1 mm', '<0,1 mm'), ('0,1 - 1,0 mm', '0,1 - 1,0 mm'), ('1,0 - 10 mm', '1,0 - 10 mm'), ('10 - 100 mm', '10 - 100 mm'), ('>100 mm', '>100 mm')])),
                ('name_pt', models.CharField(help_text='Size class name.', unique=True, max_length=32, verbose_name='name', choices=[('<0,1 mm', '<0,1 mm'), ('0,1 - 1,0 mm', '0,1 - 1,0 mm'), ('1,0 - 10 mm', '1,0 - 10 mm'), ('10 - 100 mm', '10 - 100 mm'), ('>100 mm', '>100 mm')])),
                ('name_en', models.CharField(null=True, choices=[('<0,1 mm', '<0,1 mm'), ('0,1 - 1,0 mm', '0,1 - 1,0 mm'), ('1,0 - 10 mm', '1,0 - 10 mm'), ('10 - 100 mm', '10 - 100 mm'), ('>100 mm', '>100 mm')], max_length=32, blank=True, help_text='Size class name.', unique=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='Size class name slug.', max_length=32, verbose_name='slug', blank=True)),
                ('description', models.TextField(help_text='Size name description.', verbose_name='description', blank=True)),
                ('description_pt', models.TextField(help_text='Size name description.', verbose_name='description', blank=True)),
                ('description_en', models.TextField(help_text='Size name description.', null=True, verbose_name='description', blank=True)),
                ('position', models.PositiveIntegerField(default=0, help_text='Define size class order in a queryset.', verbose_name='position')),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this size class.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this size class.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'size',
                'verbose_name_plural': 'sizes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Expert name.', unique=True, max_length=200, verbose_name='name')),
                ('slug', models.SlugField(help_text='Expert name slug.', max_length=200, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this expert.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this expert.', verbose_name='number of videos', editable=False)),
                ('images', models.ManyToManyField(help_text='Photos linked to this expert.', to='meta.Image', null=True, verbose_name='photos', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'expert',
                'verbose_name_plural': 'experts',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='State name.', unique=True, max_length=64, verbose_name='name')),
                ('slug', models.SlugField(help_text='State name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this state.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this state.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'state',
                'verbose_name_plural': 'states',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pageviews', models.PositiveIntegerField(default=0, help_text='Number of pageviews of an image.', verbose_name='pageviews', editable=False)),
            ],
            options={
                'verbose_name': 'statistics',
                'verbose_name_plural': 'statistics',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sublocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Place name.', unique=True, max_length=64, verbose_name='name')),
                ('slug', models.SlugField(help_text='Place name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this place.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this place.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'place',
                'verbose_name_plural': 'places',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Tag name.', unique=True, max_length=64, verbose_name='name')),
                ('name_pt', models.CharField(help_text='Tag name.', unique=True, max_length=64, verbose_name='name')),
                ('name_en', models.CharField(null=True, max_length=64, blank=True, help_text='Tag name.', unique=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='Tag name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('description', models.TextField(help_text='Tag description.', verbose_name='description', blank=True)),
                ('description_pt', models.TextField(help_text='Tag description.', verbose_name='description', blank=True)),
                ('description_en', models.TextField(help_text='Tag description.', null=True, verbose_name='description', blank=True)),
                ('position', models.PositiveIntegerField(default=0, help_text='Define tag order in a queryset.', verbose_name='position')),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this tag.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this tag.', verbose_name='number of videos', editable=False)),
                ('images', models.ManyToManyField(help_text='Photos linked to this tag.', to='meta.Image', null=True, verbose_name='photos', blank=True)),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Tag category name.', unique=True, max_length=64, verbose_name='name')),
                ('name_pt', models.CharField(help_text='Tag category name.', unique=True, max_length=64, verbose_name='name')),
                ('name_en', models.CharField(null=True, max_length=64, blank=True, help_text='Tag category name.', unique=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='Tag category name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('description', models.TextField(help_text='Tag category description.', verbose_name='description', blank=True)),
                ('description_pt', models.TextField(help_text='Tag category description.', verbose_name='description', blank=True)),
                ('description_en', models.TextField(help_text='Tag category description.', null=True, verbose_name='description', blank=True)),
                ('position', models.PositiveIntegerField(default=0, help_text='Define category order.', verbose_name='position')),
                ('parent', models.ForeignKey(related_name='tagcat_children', blank=True, to='meta.TagCategory', help_text='Tag category parent.', null=True, verbose_name='father', on_delete=models.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'tag categories',
                'verbose_name_plural': 'tag categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Taxon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Taxon name.', unique=True, max_length=256, verbose_name='name')),
                ('slug', models.SlugField(help_text='Taxon name slug.', max_length=256, verbose_name='slug', blank=True)),
                ('common', models.CharField(help_text='Taxon common name.', max_length=256, verbose_name='common name', blank=True)),
                ('common_pt', models.CharField(help_text='Taxon common name.', max_length=256, verbose_name='common name', blank=True)),
                ('common_en', models.CharField(help_text='Taxon common name.', max_length=256, null=True, verbose_name='common name', blank=True)),
                ('rank', models.CharField(help_text='Taxonomic rank of a taxon.', max_length=256, verbose_name='rank', blank=True)),
                ('rank_pt', models.CharField(help_text='Taxonomic rank of a taxon.', max_length=256, verbose_name='rank', blank=True)),
                ('rank_en', models.CharField(help_text='Taxonomic rank of a taxon.', max_length=256, null=True, verbose_name='rank', blank=True)),
                ('tsn', models.PositiveIntegerField(help_text='TSN, taxon identifier at ITIS.', null=True, blank=True)),
                ('aphia', models.PositiveIntegerField(help_text='APHIA, taxon identifier at WoRMS.', null=True, blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this taxon.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this taxon.', verbose_name='number of videos', editable=False)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('images', models.ManyToManyField(help_text='Photos linked to this taxon.', to='meta.Image', null=True, verbose_name='photos', blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='meta.Taxon', help_text='Taxon parent.', null=True, verbose_name='father', on_delete=models.DO_NOTHING)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'taxon',
                'verbose_name_plural': 'taxa',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Tour name.', unique=True, max_length=100, verbose_name='name')),
                ('name_pt', models.CharField(help_text='Tour name.', unique=True, max_length=100, verbose_name='name')),
                ('name_en', models.CharField(null=True, max_length=100, blank=True, help_text='Tour name.', unique=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='Tour name slug.', max_length=100, verbose_name='slug', blank=True)),
                ('description', models.TextField(help_text='Tour description.', verbose_name='description', blank=True)),
                ('description_pt', models.TextField(help_text='Tour description.', verbose_name='description', blank=True)),
                ('description_en', models.TextField(help_text='Tour description.', null=True, verbose_name='description', blank=True)),
                ('is_public', models.BooleanField(default=False, help_text='Tells if tour is visible to anonymous users.', verbose_name='public')),
                ('pub_date', models.DateTimeField(help_text='Tour publication date at Cifonauta.', verbose_name='publication date', auto_now_add=True)),
                ('timestamp', models.DateTimeField(help_text='Tour modification date.', verbose_name='timestamp', auto_now=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this tour.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this tour.', verbose_name='number of videos', editable=False)),
                ('images', models.ManyToManyField(help_text='Photos linked to this tour.', to='meta.Image', null=True, verbose_name='photos', blank=True)),
                ('references', models.ManyToManyField(help_text='References linked to this tour.', to='meta.Reference', null=True, verbose_name='references', blank=True)),
                ('stats', models.OneToOneField(null=True, editable=False, to='meta.Stats', help_text='Stores tour stats.', verbose_name='statistics', on_delete=models.DO_NOTHING)),
            ],
            options={
                'verbose_name': 'tour',
                'verbose_name_plural': 'tours',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TourPosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.PositiveIntegerField(default=0, help_text='Define image order in a tour.', verbose_name='position')),
                ('photo', models.ForeignKey(to='meta.Image', on_delete=models.DO_NOTHING)),
                ('tour', models.ForeignKey(to='meta.Tour', on_delete=models.DO_NOTHING)),
            ],
            options={
                'ordering': ['position', 'tour__id'],
                'verbose_name': 'position in the tour',
                'verbose_name_plural': 'positions in the tour',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_filepath', models.CharField(help_text='Local source file.', max_length=200, verbose_name='local source file', blank=True)),
                ('thumb_filepath', models.ImageField(help_text='Folder storing thumbnails.', upload_to='site_media/images/thumbs', verbose_name='web thumbnail')),
                ('old_filepath', models.CharField(help_text='Path to original file.', max_length=200, verbose_name='original source file', blank=True)),
                ('timestamp', models.DateTimeField(help_text='File modification date.', verbose_name='timestamp')),
                ('highlight', models.BooleanField(default=False, help_text='Image that deserves highlight.', verbose_name='highlight')),
                ('cover', models.BooleanField(default=False, help_text='Image aesthetically beautiful to be used on the home page. ', verbose_name='cover image')),
                ('is_public', models.BooleanField(default=False, help_text='Tells if image is visible to anonymous users.', verbose_name='public')),
                ('review', models.BooleanField(default=False, help_text='Tells if image should be revised.', verbose_name='under review')),
                ('notes', models.TextField(help_text='Extra field for annotations about the image.', verbose_name='notes', blank=True)),
                ('notes_pt', models.TextField(help_text='Extra field for annotations about the image.', verbose_name='notes', blank=True)),
                ('notes_en', models.TextField(help_text='Extra field for annotations about the image.', null=True, verbose_name='notes', blank=True)),
                ('pub_date', models.DateTimeField(help_text='Image publication date at Cifonauta.', verbose_name='publication date', auto_now_add=True)),
                ('title', models.CharField(help_text='Image title.', max_length=200, verbose_name='title', blank=True)),
                ('title_pt', models.CharField(help_text='Image title.', max_length=200, verbose_name='title', blank=True)),
                ('title_en', models.CharField(help_text='Image title.', max_length=200, null=True, verbose_name='title', blank=True)),
                ('caption', models.TextField(help_text='Image caption.', verbose_name='caption', blank=True)),
                ('caption_pt', models.TextField(help_text='Image caption.', verbose_name='caption', blank=True)),
                ('caption_en', models.TextField(help_text='Image caption.', null=True, verbose_name='caption', blank=True)),
                ('date', models.DateTimeField(help_text='Image creation date.', verbose_name='date', blank=True)),
                ('geolocation', models.CharField(help_text='Image geolocation in decimal format.', max_length=25, verbose_name='geolocation', blank=True)),
                ('latitude', models.CharField(help_text='Latitude where image was created.', max_length=12, verbose_name='latitude', blank=True)),
                ('longitude', models.CharField(help_text='Longitude where image was created.', max_length=12, verbose_name='longitude', blank=True)),
                ('webm_filepath', models.FileField(help_text='Path to .webm file.', upload_to='site_media/videos/', verbose_name='webm file', blank=True)),
                ('ogg_filepath', models.FileField(help_text='Path to .ogg file.', upload_to='site_media/videos/', verbose_name='ogg file', blank=True)),
                ('mp4_filepath', models.FileField(help_text='Path to .mp4 file.', upload_to='site_media/videos/', verbose_name='mp4 file', blank=True)),
                ('datatype', models.CharField(default='video', help_text='Media type.', max_length=10, verbose_name='media type')),
                ('large_thumb', models.ImageField(help_text='Path to large thumbnail of the video.', upload_to='site_media/images/thumbs', verbose_name='large thumbnail')),
                ('duration', models.CharField(default='00:00:00', help_text='Video duration formatted as HH:MM:SS.', max_length=20, verbose_name='duration')),
                ('dimensions', models.CharField(default='0x0', help_text='Video original dimensions.', max_length=20, verbose_name='dimensions')),
                ('codec', models.CharField(default='', help_text='Video original codec.', max_length=20, verbose_name='codec')),
                ('city', models.ForeignKey(blank=True, to='meta.City', help_text='City shown in the image (or city where it was collected).', null=True, verbose_name='cidade', on_delete=models.DO_NOTHING)),
                ('country', models.ForeignKey(blank=True, to='meta.Country', help_text='Country shown in the image (or country where it was collected).', null=True, verbose_name='country', on_delete=models.DO_NOTHING)),
                ('rights', models.ForeignKey(blank=True, to='meta.Rights', help_text='Copyrights owner of the image.', null=True, verbose_name='rights', on_delete=models.DO_NOTHING)),
                ('size', models.ForeignKey(default='', to='meta.Size', blank=True, help_text='Size class of the organism in the image.', null=True, verbose_name='size', on_delete=models.DO_NOTHING)),
                ('state', models.ForeignKey(blank=True, to='meta.State', help_text='State shown in the image (or state where it was collected).', null=True, verbose_name='state', on_delete=models.DO_NOTHING)),
                ('stats', models.OneToOneField(null=True, editable=False, to='meta.Stats', help_text='Store stats about an image.', verbose_name='statistics', on_delete=models.DO_NOTHING)),
                ('sublocation', models.ForeignKey(blank=True, to='meta.Sublocation', help_text='Place shown in the image (or collection site).', null=True, verbose_name='place', on_delete=models.DO_NOTHING)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'video',
                'verbose_name_plural': 'videos',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='tour',
            name='videos',
            field=models.ManyToManyField(help_text='Videos linked to this tour.', to='meta.Video', null=True, verbose_name='videos', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxon',
            name='videos',
            field=models.ManyToManyField(help_text='Videos linked to this taxon.', to='meta.Video', null=True, verbose_name='videos', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='parent',
            field=models.ForeignKey(related_name='tags', blank=True, to='meta.TagCategory', help_text='Category to which this tag belongs.', null=True, verbose_name='father', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='videos',
            field=models.ManyToManyField(help_text='Videos linked to this tag.', to='meta.Video', null=True, verbose_name='videos', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='source',
            name='videos',
            field=models.ManyToManyField(help_text='Videos linked to this expert.', to='meta.Video', null=True, verbose_name='videos', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reference',
            name='videos',
            field=models.ManyToManyField(help_text='Videos linked to this reference.', to='meta.Video', null=True, verbose_name='videos', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='rights',
            field=models.ForeignKey(blank=True, to='meta.Rights', help_text='Copyrights owner of the image.', null=True, verbose_name='rights', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='size',
            field=models.ForeignKey(default='', to='meta.Size', blank=True, help_text='Size class of the organism in the image.', null=True, verbose_name='size', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='state',
            field=models.ForeignKey(blank=True, to='meta.State', help_text='State shown in the image (or state where it was collected).', null=True, verbose_name='state', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='stats',
            field=models.OneToOneField(null=True, editable=False, to='meta.Stats', help_text='Store stats about an image.', verbose_name='statistics', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='sublocation',
            field=models.ForeignKey(blank=True, to='meta.Sublocation', help_text='Place shown in the image (or collection site).', null=True, verbose_name='place', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='author',
            name='images',
            field=models.ManyToManyField(help_text='Photos linked to this author.', to='meta.Image', null=True, verbose_name='photos', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='author',
            name='videos',
            field=models.ManyToManyField(help_text='Videos linked to this author.', to='meta.Video', null=True, verbose_name='videos', blank=True),
            preserve_default=True,
        ),
    ]
