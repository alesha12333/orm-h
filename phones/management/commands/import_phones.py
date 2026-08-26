import csv
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from phones.models import Phone


class Command(BaseCommand):
    help = 'Import phones from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to CSV file',
            default='phones.csv'
        )

    def handle(self, *args, **options):
        file_path = options['file']

        # Если путь не абсолютный, ищем в корне проекта
        if not os.path.isabs(file_path):
            base_dir = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__))
                    )
                )
            )
            file_path = os.path.join(base_dir, file_path)

        # Проверяем существование файла
        if not os.path.exists(file_path):
            self.stderr.write(
                self.style.ERROR(f'❌ File not found: {file_path}')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'📁 Importing phones from: {file_path}')
        )

        imported_count = 0
        error_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Определяем разделитель (; или ,)
                sample = file.readline()
                file.seek(0)
                delimiter = ';' if ';' in sample else ','

                reader = csv.DictReader(file, delimiter=delimiter)

                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Очищаем данные
                        name = row['name'].strip()
                        price_str = row['price'].strip().replace(',', '.')

                        # Создаем или обновляем запись
                        phone, created = Phone.objects.update_or_create(
                            id=int(row['id']),
                            defaults={
                                'name': name,
                                'price': float(price_str),
                                'image': row['image'].strip(),
                                'release_date': row['release_date'].strip(),
                                'lte_exists': row['lte_exists'].strip().lower() in ['true', '1', 'yes'],
                                'slug': slugify(name)
                            }
                        )

                        if created:
                            imported_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'✅ Created: {phone.name}')
                            )
                        else:
                            imported_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'🔄 Updated: {phone.name}')
                            )

                    except Exception as e:
                        error_count += 1
                        self.stderr.write(
                            self.style.ERROR(f'❌ Error in row {row_num}: {e}')
                        )
                        self.stderr.write(f'   Data: {row}')

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'❌ Unexpected error: {e}')
            )
            return

        # Выводим итоговую статистику
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 Successfully processed {imported_count} phones')
        )
        if error_count > 0:
            self.stderr.write(
                self.style.WARNING(f'⚠️  {error_count} errors occurred')
            )