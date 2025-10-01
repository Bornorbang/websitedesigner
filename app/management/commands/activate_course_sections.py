from django.core.management.base import BaseCommand
from app.models import CourseSection


class Command(BaseCommand):
    help = 'Ensure all course sections are active by default for enrolled students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find all inactive sections
        inactive_sections = CourseSection.objects.filter(is_active=False)
        
        if not inactive_sections.exists():
            self.stdout.write(
                self.style.SUCCESS('All course sections are already active!')
            )
            return
        
        section_count = inactive_sections.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would activate {section_count} course sections:')
            )
            for section in inactive_sections:
                self.stdout.write(f'  - {section.course.title}: {section.title}')
        else:
            # Update all inactive sections to be active
            updated = inactive_sections.update(is_active=True)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully activated {updated} course sections!')
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    'All enrolled students now have access to these sections unless '
                    'admin manually deactivates them.'
                )
            )