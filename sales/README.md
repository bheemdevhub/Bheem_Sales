# Sales Management Module

## Overview
The Sales Management Module is a comprehensive revenue generation system that handles the complete sales process from quotes to payments. It integrates seamlessly with CRM, Inventory, and Accounting modules to provide end-to-end sales management.

## Features

### 🎯 **Core Sales Features**
- **Quote Management** - Create, send, and track sales quotes
- **Order Processing** - Convert quotes to orders and manage fulfillment  
- **Invoice Generation** - Automated invoicing with customizable templates
- **Payment Processing** - Multi-method payment tracking and reconciliation
- **Customer Management** - Comprehensive customer database with credit management

### 💼 **Advanced Features**
- **Product Bundles** - Create and sell product/service bundles
- **Commission Tracking** - Automated sales commission calculations
- **Price Lists** - Multiple pricing tiers and customer-specific pricing
- **Multi-Currency Support** - Handle international sales transactions
- **Tax Management** - Automated tax calculations and compliance

### 📊 **Analytics & Reporting**
- **Sales Analytics** - Real-time sales performance metrics
- **Revenue Reporting** - Comprehensive revenue analysis
- **Commission Reports** - Sales team performance tracking
- **Customer Analytics** - Customer behavior and profitability analysis

## Module Structure

```
app/modules/sales/
├── core/
│   ├── models/          # Database models
│   │   └── sales_models.py
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── repositories/    # Data access layer
├── api/
│   └── v1/
│       └── routes/      # API endpoints
│           ├── quotes.py
│           ├── orders.py
│           ├── invoices.py
│           ├── customers.py
│           ├── payments.py
│           └── analytics.py
├── events/              # Event handlers
├── integrations/        # External integrations
├── migrations/          # Database migrations
├── tests/              # Unit and integration tests
├── workers/            # Background tasks
├── config.py           # Module configuration
└── module.py           # Module class
```

## Database Models

### Core Entities
- **Customer** - Customer information and billing details
- **Quote** - Sales quotes with line items
- **SalesOrder** - Confirmed orders with fulfillment tracking
- **SalesInvoice** - Invoices with payment tracking
- **CustomerPayment** - Payment records and reconciliation

### Supporting Entities
- **ProductBundle** - Bundled products/services
- **SalesCommission** - Commission calculations
- **PriceList** - Pricing management

## API Endpoints

### Quotes
- `POST /quotes` - Create new quote
- `GET /quotes` - List quotes with filtering
- `GET /quotes/{id}` - Get quote details
- `PUT /quotes/{id}` - Update quote
- `POST /quotes/{id}/send` - Send quote to customer
- `POST /quotes/{id}/convert` - Convert quote to order

### Orders
- `POST /orders` - Create new order
- `GET /orders` - List orders with filtering
- `GET /orders/{id}` - Get order details
- `PUT /orders/{id}` - Update order
- `POST /orders/{id}/ship` - Mark order as shipped
- `POST /orders/{id}/cancel` - Cancel order

### Invoices
- `POST /invoices` - Create new invoice
- `GET /invoices` - List invoices with filtering
- `GET /invoices/{id}` - Get invoice details
- `POST /invoices/{id}/send` - Send invoice to customer
- `POST /invoices/{id}/void` - Void invoice

### Customers
- `POST /customers` - Create new customer
- `GET /customers` - List customers
- `GET /customers/{id}` - Get customer details
- `PUT /customers/{id}` - Update customer
- `GET /customers/{id}/orders` - Get customer orders
- `GET /customers/{id}/invoices` - Get customer invoices

### Payments
- `POST /payments` - Record new payment
- `GET /payments` - List payments
- `GET /payments/{id}` - Get payment details
- `POST /payments/{id}/refund` - Process refund

### Analytics
- `GET /analytics/revenue` - Revenue analytics
- `GET /analytics/sales-performance` - Sales team performance
- `GET /analytics/customer-analysis` - Customer analytics
- `GET /analytics/commission-summary` - Commission reports

## Integration Points

### CRM Module
- **Opportunity Conversion** - Convert won opportunities to quotes/orders
- **Customer Sync** - Synchronize customer data
- **Activity Tracking** - Log sales activities in CRM

### Inventory Module
- **Stock Checking** - Verify product availability
- **Reservation** - Reserve inventory for orders
- **Allocation** - Allocate products for shipping

### Accounting Module
- **Journal Entries** - Automatic accounting entries
- **Revenue Recognition** - Post revenue to appropriate accounts
- **Accounts Receivable** - Manage customer balances

### HR Module
- **Sales Team** - Link sales reps to transactions
- **Commission Calculation** - Calculate and track commissions

## Event System

### Published Events
- `sales.quote.created` - New quote created
- `sales.order.created` - New order created
- `sales.invoice.created` - New invoice created
- `sales.payment.received` - Payment received
- `sales.commission.calculated` - Commission calculated

### Subscribed Events
- `crm.opportunity.won` - Create order from won opportunity
- `inventory.stock.low` - Alert sales team of low stock
- `accounting.invoice.overdue` - Handle overdue invoices

## Configuration

### Sales Settings
```python
QUOTE_VALIDITY_DAYS = 30
ORDER_NUMBER_PREFIX = "SO"
INVOICE_NUMBER_PREFIX = "INV"
DEFAULT_PAYMENT_TERMS = 30
DEFAULT_COMMISSION_RATE = 5.0
```

### Integration Settings
```python
SYNC_WITH_CRM = True
SYNC_WITH_ACCOUNTING = True
SYNC_WITH_INVENTORY = True
AUTO_SEND_INVOICES = True
```

## Permissions

The module implements granular permissions for:
- Quote management
- Order processing
- Invoice handling
- Customer management
- Payment processing
- Analytics viewing
- Commission management
- Administrative functions

## Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

3. **Configure Settings**
   Update `config.py` with your business requirements

4. **Start Using**
   The module will be automatically loaded by the ERP system

## Development

### Adding New Features
1. Create/update models in `core/models/`
2. Add business logic in `core/services/`
3. Create API endpoints in `api/v1/routes/`
4. Add tests in `tests/`
5. Update documentation

### Testing
```bash
pytest app/modules/sales/tests/
```

## Future Enhancements

- **Subscription Management** - Recurring billing for services
- **Advanced Pricing Rules** - Volume discounts, time-based pricing
- **Integration with Payment Gateways** - Stripe, PayPal, etc.
- **Mobile App Support** - Sales team mobile application
- **AI-Powered Insights** - Predictive sales analytics
- **E-commerce Integration** - Online store connectivity

## Support

For questions and support, please refer to the main ERP system documentation or contact the development team.
