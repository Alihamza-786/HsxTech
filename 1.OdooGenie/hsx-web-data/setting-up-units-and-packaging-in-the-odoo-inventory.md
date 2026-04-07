Source: https://hsxtech.net/setting-up-units-and-packaging-in-the-odoo-inventory/

# How to Set Up Units &amp; Packaging in the Odoo Inventory Module

One of the most important things to do to handle stock in Odoo Inventory Module effectively is to set up Units of Measure (UOM) and Packaging. Both are very important to ensure that your inventory is reported correctly so that there is no operational issue between buying, selling, and transferring stock.

We’re here to assist you through the correct configuration of UOM and Packaging in Odoo Inventory so that you can automate tasks and steer clear of inventory mistakes. You’re just starting to work with Odoo or must get your existing setup easy.

## What are Units of Measure (UOM) in the Odoo Inventory?

### Understanding UOMs in Odoo Inventory
A Unit of Measure (UOM) in Odoo Inventory is an official unit of measurement by which the quantity of a product is measured. It can be anything ranging from pieces, liters, or kilograms to something custom-made as per your business needs.

UOMs are very important while dealing with stocks in the Odoo Inventory. They correctly count your products while receiving, selling, and shipping. For instance:

- When you sell water in packed form, you can use pieces as your UOM, but when buying inventory from a supplier, you can use boxes (inside multiple pieces) as your UOM.
- While selling raw materials such as wood, you can use meters as your UOM for measurement in the inventory.

### Default vs. Custom UOMs in Odoo Inventory
Odoo Inventory does have some standard UOMs (e.g., pieces, kg, liters), but by all means, create custom UOMs if you need something unusual in your business. Custom UOMs enable you to use the system based on how you measure your products on an item-by-item basis.

For instance, if you’re selling by pallet, you can define your own UOM and detail the number of boxes a pallet contains.

A Unit of Measure (UOM) in Odoo Inventory is an official unit of measurement by which the quantity of a product is measured. It can be anything ranging from pieces, liters, or kilograms to something custom-made as per your business needs.

UOMs are very important while dealing with stocks in the Odoo Inventory. They correctly count your products while receiving, selling, and shipping. For instance:

- When you sell water in packed form, you can use pieces as your UOM, but when buying inventory from a supplier, you can use boxes (inside multiple pieces) as your UOM.
- While selling raw materials such as wood, you can use meters as your UOM for measurement in the inventory.

## Configuration of UOM in Odoo Inventory

### Setting Up UOM Categories
Locate UOM Categories as the starting point to organize UOMs in the Odoo Inventory. A UOM Category is a set of measurement categories that have similar ones, i.e., weight, volume, or distance.

To configure UOM Categories in Odoo Inventory:

1. Navigate to Inventory &gt; Configuration &gt; Units of Measure.
2. Create new categories or modify existing categories here. You can create, for instance, a weight category, volume category, or distance category.

### Setting Up New UOM in Odoo Inventory
After you have created UOM categories, you can now proceed and create individual UOMs for your products as follows:

1. Go to Inventory &gt; Configuration &gt; Units of Measure.
2. Click on Create and add a new UOM.
3. Complete the form as below:

- Category: Select a suitable category of UOM (e.g., Weight, Volume).
- UOM Name: Enter UOM name (e.g., Box, Piece).
- Reference Unit of Measure: Select the unit base of your UOM (e.g., Piece).
- Ratio: Enter the conversion factor (e.g., 1 Box = 10 Pieces).

You will then have UOMs most suited for your business operations and inventory.

### Converting Between UOMs in Odoo Inventory
Odoo Inventory enables you to have UOM Conversions installed. This might be useful where you buy in lots but sell in unit quantity. For example, you may buy material in pallets but sell in pieces. Odoo will convert the pallets into pieces for you.

1. Set the Conversion Factor in the UOM form.
2. Thus, when a pallet is received, Odoo is aware that there is a large quantity of pieces that are inside the pallet.

## What is Packaging in Odoo Inventory?

### Understanding Packaging in Odoo Inventory
Whereas UOMs enable you to measure your product, Packaging in Odoo Inventory enables you to package the product in order to send or stock it. Packaging enables you to package the stock so that you can easily track and manage it.

For instance, an alternative product (i.e., equipment) but of boxes or crates. Packaging can also be employed to imprint the number of individual pieces included in a box of bulk such that one can deal with the bulk unit in an easily portable form.

### Packaging vs. UOM in Odoo Inventory
There must be a distinction between Packaging and UOMs within the Odoo Inventory:

- UOM is used when calculating and measuring product items (e.g., pieces, liters).
- Packaging is used for shipping and storing packaging (e.g., crate, box).

Packaging can, in most instances, be tied up with your UOM. A unit may be packed singly but handled in lots of 12 units, for instance, packaging may be set up for this.

## Configuration of Packaging in Odoo Inventory

### Setting Up Packaging for Products in the Odoo Inventory

To add Packaging for goods products for products in Odoo, follow the steps below to go to Product settings:

1. Navigate to Inventory &gt; Products &gt; Products.
2. Open the product you wish to configure.
3. In the Packaging tab, add the product packaging (e.g., Box of 12).
4. You can also set a default packaging and thereby automatically use it every time you sell this product.

Packaging makes it easy for you to keep track of and store products in the Odoo Inventory. For instance, if you are selling per unit of the product but in a pack of 12, with this setup your stock levels will always be accurate.

### Managing Multiple Packaging Types in Odoo Inventory

In case you are selling the same product in varying packaging (e.g., Box of 12 and Box of 24), Odoo Inventory provides multiple packaging for one product.

To configure multiple packaging:

1. Go to the Packaging field of the product form.
2. Configure diverse packaging choices (i.e., Box of 12, Box of 24).
3. Odoo will manage the stock by package setup, and easy-to-ship orders irrespective of the package customers prefer.

### Tracking the packaged stock in Odoo Inventory
After installing the packaged, Odoo Inventory will automatically follow packaged stock. In other words, the right amount will be there when shipping orders are due, but it keeps your inventory up-to-date even while working with bulk sizes and packaging.

For example, if you’re tracking a product in both pieces and boxes, Odoo will keep an eye on both quantities and ensure that your inventory reflects both the individual product and the packaged units.

## Integrating UOM and Packaging with Sales and Purchases

### Impact on Sales Orders in Odoo Inventory
When you are performing the sale of products in Odoo Inventory, UOM, and Packaging setup will be used to determine how products are selling. If you are selling a product one product per box then Odoo will automatically calculate how many units are there in a box when you are selling it.

For example, if you are selling 10 pieces of a product, Odoo will calculate how many pieces that would be and then reduce the stock accordingly.

### Impact on Purchase Orders in Odoo Inventory
On the buying side, Odoo Inventory allows you to specify UOM and packaging with your buyers. In the event of buying in bulk units (pallets) but selling in single pieces, the system will automatically set your units of stock to the correct numbers in bulk units (pallets) and single pieces.

### Managing UOM and Packaging with Suppliers and Customers

To have your Packaging and UOM reflected on your buying and selling activities:

- For Suppliers: Refer to where it is being sold (in boxes or pieces).
- For Customers: Refer to the UOM where you are purchasing (pallets).

With both, you have an equilibrium between sales, purchases, and movements in stock.

## Conclusion

Packaging and Units of Measure (UOM) setting of Odoo Inventory is required to manage inventory in an effective and efficient manner. If you set things correctly, then you have control over stock, sales, and purchase orders, so you would never make any mistakes and have inventory properly.

Whether you are handling bulk commodities, the UOM customizations, or which ones are to be set up for a particular product, Odoo Inventory has the feature to set up these settings according to your business requirements.
