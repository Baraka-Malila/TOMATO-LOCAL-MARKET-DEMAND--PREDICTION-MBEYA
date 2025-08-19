"""
Management command to load sample market data from CSV file.

This command loads data from the combined_file.csv in the data directory
and creates MarketData records for testing.
"""

import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from market_data.models import MarketData


class Command(BaseCommand):
    help = 'Load sample market data from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='../data/combined_file.csv',
            help='Path to CSV file relative to project root'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing market data...')
            MarketData.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))
        
        csv_file = options['file']
        self.stdout.write(f'Loading data from {csv_file}...')
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            created_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Convert boolean fields
                    market_day = str(row['Market_Day']).lower() in ('yes', 'true', '1')
                    school_open = str(row['School_Open']).lower() in ('yes', 'true', '1')
                    
                    # Create or update market data
                    market_data, created = MarketData.objects.get_or_create(
                        week=int(row['Week']),
                        year=int(row['Year']),
                        defaults={
                            'month': str(row['Month']),
                            'rainfall_mm': float(row['Rainfall_mm']),
                            'temperature_c': float(row['Temperature_C']),
                            'market_day': market_day,
                            'school_open': school_open,
                            'disease_alert': str(row['Disease_Alert']),
                            'last_week_demand': str(row['Last_Week_Demand']),
                            'market_demand': str(row['Market_Demand']),
                            'source': 'sample_data_load',
                        }
                    )
                    
                    if created:
                        created_count += 1
                    
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'Error processing row {index + 1}: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully loaded {created_count} records. '
                    f'{error_count} errors encountered.'
                )
            )
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading data: {str(e)}')
            )
