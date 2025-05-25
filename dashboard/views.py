from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q, IntegerField, Case, When
from django.db.models.functions import TruncMonth, TruncDate, Extract
from .models import Order
import json
from datetime import datetime
from collections import defaultdict

def dashboard_overview(request):
    """Executive Dashboard View"""
    
    # Get filter parameters - only metric filter
    selected_metric = request.GET.get('metric', 'sales')
    
    # Calculate KPIs
    total_sales = Order.objects.aggregate(total=Sum('item_subtotal'))['total'] or 0
    total_profits = Order.objects.aggregate(total=Sum('profit_per_item'))['total'] or 0
    total_orders = Order.objects.count()
    total_customers = Order.objects.values('customer_id').distinct().count()
    profit_ratio = Order.objects.aggregate(total=Avg('item_profit_ratio'))['total'] or 0
    
    # Monthly data for charts - NO YEAR FILTER
    monthly_sales = list(Order.objects
                        .annotate(month=Extract('order_datetime', 'month'))
                        .values('month')
                        .annotate(total=Sum('item_subtotal'))
                        .order_by('month'))
    
    monthly_profits = list(Order.objects
                          .annotate(month=Extract('order_datetime', 'month'))
                          .values('month')
                          .annotate(total=Sum('profit_per_item'))
                          .order_by('month'))
    
    monthly_orders = list(Order.objects
                         .annotate(month=Extract('order_datetime', 'month'))
                         .values('month')
                         .annotate(total=Count('order_id'))
                         .order_by('month'))
    
    # Segment data - NO YEAR FILTER
    segment_sales = list(Order.objects
                        .values('customer_segment')
                        .annotate(total=Sum('item_subtotal'))
                        .order_by('-total'))
    
    segment_profits = list(Order.objects
                          .values('customer_segment')
                          .annotate(total=Sum('profit_per_item'))
                          .order_by('-total'))
    
    segment_orders = list(Order.objects
                         .values('customer_segment')
                         .annotate(total=Count('order_id'))
                         .order_by('-total'))
    
    # Right side metrics based on selected metric ONLY
    if selected_metric == 'Sales':
        metric_by_country = list(Order.objects
                               .values('order_country')
                               .annotate(total=Sum('item_subtotal'))
                               .order_by('-total')[:5])
        
        metric_by_product = list(Order.objects
                               .values('product_name')
                               .annotate(total=Sum('item_subtotal'))
                               .order_by('-total')[:5])
        
        metric_by_department = list(Order.objects
                                  .values('department_name')
                                  .annotate(total=Sum('item_subtotal'))
                                  .order_by('-total')[:5])
    
    elif selected_metric == 'Profits':
        metric_by_country = list(Order.objects
                               .values('order_country')
                               .annotate(total=Sum('profit_per_item'))
                               .order_by('-total')[:5])
        
        metric_by_product = list(Order.objects
                               .values('product_name')
                               .annotate(total=Sum('profit_per_item'))
                               .order_by('-total')[:5])
        
        metric_by_department = list(Order.objects
                                  .values('department_name')
                                  .annotate(total=Sum('profit_per_item'))
                                  .order_by('-total')[:5])
    
    else:  # orders
        metric_by_country = list(Order.objects
                               .values('order_country')
                               .annotate(total=Count('order_id'))
                               .order_by('-total')[:5])
        
        metric_by_product = list(Order.objects
                               .values('product_name')
                               .annotate(total=Count('order_id'))
                               .order_by('-total')[:5])
        
        metric_by_department = list(Order.objects
                                  .values('department_name')
                                  .annotate(total=Count('order_id'))
                                  .order_by('-total')[:5])
    
    context = {
        'total_sales': total_sales,  # Convert to millions
        'total_profits': total_profits,  # Convert to millions
        'total_orders': total_orders,
        'total_customers': total_customers,
        'profit_ratio': round(profit_ratio, 2),
        'monthly_sales': json.dumps(monthly_sales),
        'monthly_profits': json.dumps(monthly_profits),
        'monthly_orders': json.dumps(monthly_orders),
        'segment_sales': json.dumps(segment_sales),
        'segment_profits': json.dumps(segment_profits),
        'segment_orders': json.dumps(segment_orders),
        'metric_by_country': json.dumps(metric_by_country),
        'metric_by_product': json.dumps(metric_by_product),
        'metric_by_department': json.dumps(metric_by_department),
        'selected_metric': selected_metric,
    }
    
    return render(request, 'dashboard/overview.html', context)

def dashboard_delivery(request):
    """Delivery Performance Dashboard View - Simplified"""
    
    # Calculate delivery KPIs
    total_orders = Order.objects.count()
    
    # Handle different late_delivery values
    try:
        on_time_orders = Order.objects.filter(late_delivery='No late').count()
        late_orders = Order.objects.filter(late_delivery='Late').count()
    except:
        try:
            on_time_orders = Order.objects.filter(late_delivery__icontains='No').count()
            late_orders = Order.objects.filter(late_delivery__icontains='Yes').count()
        except:
            on_time_orders = 0
            late_orders = 0
    
    on_time_rate = (on_time_orders / total_orders * 100) if total_orders > 0 else 0
    late_rate = (late_orders / total_orders * 100) if total_orders > 0 else 0
    
    avg_shipping_days = Order.objects.aggregate(avg=Avg('days_for_shipping_real'))['avg'] or 0
    avg_scheduled_days = Order.objects.aggregate(avg=Avg('days_for_shipment_scheduled'))['avg'] or 0
    
    # Monthly delivery performance
    monthly_delivery = list(Order.objects
                          .annotate(month=Extract('order_datetime', 'month'))
                          .values('month')
                          .annotate(
                              total_orders=Count('order_id'),
                              avg_days=Avg('days_for_shipping_real')
                          )
                          .order_by('month'))
    
    # Shipping mode performance
    shipping_mode_performance = list(Order.objects
                                   .values('shipping_mode')
                                   .annotate(
                                       total=Count('order_id'),
                                       avg_days=Avg('days_for_shipping_real')
                                   )
                                   .order_by('-total')[:5])
    
    # Delivery status distribution
    delivery_status_dist = list(Order.objects
                              .values('delivery_status')
                              .annotate(total=Count('order_id'))
                              .order_by('-total'))
    
    # Top countries by order volume
    country_performance = list(Order.objects
                             .values('order_country')
                             .annotate(total=Count('order_id'))
                             .order_by('-total')[:10])
    
    context = {
        'total_orders': total_orders,
        'on_time_rate': round(on_time_rate, 1),
        'late_rate': round(late_rate, 1),
        'on_time_orders': on_time_orders,
        'late_orders': late_orders,
        'avg_shipping_days': round(avg_shipping_days, 1),
        'avg_scheduled_days': round(avg_scheduled_days, 1),
        'monthly_delivery': json.dumps(monthly_delivery),
        'shipping_mode_performance': json.dumps(shipping_mode_performance),
        'delivery_status_dist': json.dumps(delivery_status_dist),
        'country_performance': json.dumps(country_performance),
    }
    
    return render(request, 'dashboard/delivery.html', context)

def api_metric_data(request):
    """API endpoint for metric filtering"""
    metric = request.GET.get('metric', 'sales')
    
    if metric == 'Sales':
        by_country = list(Order.objects
                         .values('order_country')
                         .annotate(total=Sum('item_subtotal'))
                         .order_by('-total')[:5])
        
        by_product = list(Order.objects
                         .values('product_name')
                         .annotate(total=Sum('item_subtotal'))
                         .order_by('-total')[:5])
        
        by_department = list(Order.objects
                           .values('department_name')
                           .annotate(total=Sum('item_subtotal'))
                           .order_by('-total')[:5])
    
    elif metric == 'Profits':
        by_country = list(Order.objects
                         .values('order_country')
                         .annotate(total=Sum('profit_per_item'))
                         .order_by('-total')[:5])
        
        by_product = list(Order.objects
                         .values('product_name')
                         .annotate(total=Sum('profit_per_item'))
                         .order_by('-total')[:5])
        
        by_department = list(Order.objects
                           .values('department_name')
                           .annotate(total=Sum('profit_per_item'))
                           .order_by('-total')[:5])
    
    else:  # orders
        by_country = list(Order.objects
                         .values('order_country')
                         .annotate(total=Count('order_id'))
                         .order_by('-total')[:5])
        
        by_product = list(Order.objects
                         .values('product_name')
                         .annotate(total=Count('order_id'))
                         .order_by('-total')[:5])
        
        by_department = list(Order.objects
                           .values('department_name')
                           .annotate(total=Count('order_id'))
                           .order_by('-total')[:5])
    
    return JsonResponse({
        'by_country': by_country,
        'by_product': by_product,
        'by_department': by_department
    })

def api_delivery_data(request):
    """API endpoint for delivery dashboard filtering"""
    market = request.GET.get('market', 'all')
    shipping_mode = request.GET.get('shipping_mode', 'all')
    
    # Apply filters
    queryset = Order.objects.all()
    
    if market != 'all':
        if market == 'us':
            queryset = queryset.filter(order_country='United States')
        elif market == 'eu':
            queryset = queryset.filter(order_country__in=['France', 'Germany', 'United Kingdom'])
        elif market == 'asia':
            queryset = queryset.filter(order_country__in=['Australia', 'Japan', 'Singapore'])
    
    if shipping_mode != 'all':
        queryset = queryset.filter(shipping_mode__icontains=shipping_mode.replace('-', ' '))
    
    # Recalculate metrics
    total_orders = queryset.count()
    
    try:
        on_time_orders = queryset.filter(late_delivery='0').count()
        late_orders = queryset.filter(late_delivery='1').count()
    except:
        on_time_orders = queryset.filter(late_delivery__icontains='No').count()
        late_orders = queryset.filter(late_delivery__icontains='Yes').count()
    
    on_time_rate = (on_time_orders / total_orders * 100) if total_orders > 0 else 0
    avg_shipping_days = queryset.aggregate(avg=Avg('days_for_shipping_real'))['avg'] or 0
    avg_scheduled_days = queryset.aggregate(avg=Avg('days_for_shipment_scheduled'))['avg'] or 0
    
    return JsonResponse({
        'total_orders': total_orders,
        'on_time_rate': round(on_time_rate, 1),
        'late_orders': late_orders,
        'avg_shipping_days': round(avg_shipping_days, 1),
        'avg_scheduled_days': round(avg_scheduled_days, 1)
    })