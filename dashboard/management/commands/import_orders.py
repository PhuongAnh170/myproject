import pandas as pd
from django.core.management.base import BaseCommand
from dashboard.models import Order
from django.utils import timezone
from datetime import datetime

class Command(BaseCommand):
    help = 'Imports order data from a CSV file into the Order model'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)

            # Iterate over the rows and create Order instances
            for index, row in df.iterrows():
                Order.objects.update_or_create(
                    order_id=row['Order Id'],
                    defaults={
                        'payment_type': row['Type'],
                        'days_for_shipping_real': row['Days for shipping (real)'],
                        'days_for_shipment_scheduled': row['Days for shipment (scheduled)'],
                        'delivery_status': row['Delivery Status'],
                        'late_delivery': row['Late Delivery'],
                        'category_name': row['Category Name'],
                        'store_city': row['Store City'],
                        'store_country': row['Store Country'],
                        'category_id': row['Category Id'],
                        'customer_id': row['Customer Id'],
                        'customer_name': row['Customer Name'],
                        'customer_segment': row['Customer Segment'],
                        'customer_zipcode': row['Customer Zipcode'],
                        'store_state': row['Store State'],
                        'store_street': row['Store Street'],
                        'department_id': row['Department Id'],
                        'department_name': row['Department Name'],
                        'latitude': row['Latitude'],
                        'longitude': row['Longitude'],
                        'market': row['Market'],
                        'order_city': row['Order City'],
                        'order_country': row['Order Country'],
                        'order_customer_id': row['Order Customer Id'],
                        'order_datetime': row['Order Datetime'],
                        'order_item_cardprod_id': row['Order Item Cardprod Id'],
                        'order_item_discount': row['Order Item Discount'],
                        'item_discount_rate': row['Item Discount Rate'],
                        'order_item_id': row['Order Item Id'],
                        'item_product_price': row['Item Product Price'],
                        'item_profit_ratio': row['Item Profit Ratio'],
                        'item_quantity': row['Item Quantity'],
                        'item_subtotal': row['Item Subtotal'],
                        'item_total': row['Item Total'],
                        'profit_per_item': row['Profit per Item'],
                        'order_region': row['Order Region'],
                        'order_state': row['Order State'],
                        'order_status': row['Order Status'],
                        'product_id': row['Product Id'],
                        'product_category_id': row['Product Category Id'],
                        'product_name': row['Product Name'],
                        'product_price': row['Product Price'],
                        'shipping_datetime': row['Shipping Datetime'],
                        'shipping_mode': row['Shipping Mode'],
                    }
                )
            self.stdout.write(self.style.SUCCESS(f'Successfully imported data from {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))