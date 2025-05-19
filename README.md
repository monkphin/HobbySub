# Contents

[Site Concept](#site-concept)

  - [Site Owner Goals](#site-owner-goals)
  - [A Visitors Goals](#visitor-goals)

[User Stories](#user-stories)

  - [Account Registration and Authentication](#account-registration-and-authentication)
  - [Paint Collection Management](#paint-collection-management)
  - [Recipe Creation and Management](#recipe-creation-and-management)
  - [Viewing and Searching](#viewing-and-searching)    
  - [User Experience and Visuals](#user-experience-and-visuals)    
  - [Security and Error Handling](#security-and-error-handling)    
  - [Data Management](#data-management)    
  - [Administration](#administration)    
  - [Social Features](#social-features)   

[Scope](#scope) 

[Design](#design)

  - [Wireframes](#wireframes)
  - [Schema](#schema)
  - [UX](#ux)
  - [Colour Palette](#colour-palette)
  - [Typography](#typography)
  - [Images](#images)
  - [Icons](#icons)
  - [Features](#features)

[Code Design](#code-design)

[Future Features](#future-features)

[Security, Defensive Programming and best Practices](#security-defensive-programming-and-best-practices)  

[Technology](#technology)
  - [Frameworks and Programs](#frameworks-and-programs)

[Testing](#testing-and-validation)

 [Version Control and Deployment](#version-control-and-deployment)

  - [Repository Creation](#repo-creation)
  - [Cloning Locally](#cloning-locally)
  - [Adding and Updating Files on the Repo](#adding-and-updating-files-on-the-repo) 
  - [Working on Multiple Devices](#working-on-multiple-devices)
  - [Local Deployment](#local-deployment)
  - [PostGres DB Creation](#postgres-db-creation)
  - [Heroku Setup and Configuration](#heroku-set-up-and-configuration)
  - [DNS Configuration](#dns-configuration)

[Credits](#credits)

[Acknowledgements](#acknowledgements)


# Site Concept
HobbySub is an online eCommerce site for tabletop wargame and model making hobbyists. It provides a mystery-box subscription service, which ships a new box of hobby supplies every month based on a specific theme. Subscriptions are available on a monthly, quarterly (3-month), biannual (6-month), or annual basis, with discounted pricing for longer commitments. Users can also purchase single boxes, if they're not yet ready to subscribe. The site has logic built into it to allow for purchases to be bought as items for the user, or as a gift to someone else, with personalised gift emails sent out when the item is ordered. 

To manage and prioritise tasks, I used a Kanban board to track project progress from inception to completion, alongside a MoSCoW board for structured planning and prioritisation. 

[My MoSCoW board can be found here](https://github.com/users/monkphin/projects/5/views/1)

[My Kanban board can be found here](https://github.com/users/monkphin/projects/6/views/1)

## Site Owner Goals

 - Provide a secure and scalable platform to sell and manage subscription-based box offerings.
 - Allow users to easily subscribe to recurring boxes or gift one-off boxes to others.
 - Enable users to manage their own subscriptions (pause, cancel, change address).
 - Maintain full control over box offerings, shipment schedules, and customer data.
 - Ensure clear separation between admin and regular user functionality for operational security.
 - Offer a professional, responsive, and accessible user interface across all devices.
 - Integrate Stripe to handle recurring billing and one-off payments.
 - Track and manage recurring orders and payments tied to active subscriptions.
 - Provide a reliable mechanism for scheduling box shipments based on renewal dates.
 - Deploy the platform on scalable, cloud-based infrastructure with minimal downtime.
 - Reduce support load through clear UI, meaningful feedback, and user-accessible history.

## Visitor Goals

 - Browse available subscription box options and view what types of products they typically include.
 - View detailed info about each months box: theme, contents summary, and shipping frequency options.
 - Easily subscribe to a box for themselves or send it as a gift to another address.
 - Register and log in to manage subscriptions, update shipping details, and view upcoming shipments.
 - Pause or cancel their subscription without needing to contact support.
 - View order history, upcoming delivery dates, and previous payments in one place.
 - Check payment method details and update card info securely if needed.
 - Receive confirmation emails for each successful order and payment.
 - Use a mobile-friendly, accessible site with support for keyboard navigation and screen readers.
 - Feel confident that their personal and payment information is handled securely.
 - Get help or support quickly if they run into issues with orders, addresses, or billing.


# User Stories

| **Category**                | **User Story**                                                                                      |
|----------------------------|------------------------------------------------------------------------------------------------------|
| Authentication & Permissions | As a user, I want to register and log in securely so I can access my account and manage my subscriptions. |
|                            | As a logged-in user, I want to view and update my profile details (like shipping address or email). |
|                            | As a logged-in user, I want to access only my own data, not see admin pages or other users' info. |
|                            | As an admin, I want to restrict access to admin features like box creation and order management. |
|----------------------------|------------------------------------------------------------------------------------------------------|
| Boxes & Subscription Browsing | As a user, I want to browse available subscription boxes so I can choose one that suits me or someone else. |
|                            | As a user, I want to have options for frequency of payment plans, including its price and shipping schedule. |
|                            | As an admin, I want to create, edit, and remove box offerings to control what's available. |
|----------------------------|------------------------------------------------------------------------------------------------------|
| Subscription Management    | As a user, I want to subscribe to a box for myself or gift it to someone else. |
|                            | As a user, I want to pause or cancel my subscription at any time. |
|                            | As a user, I want to choose or update the shipping address for each subscription. |
|                            | As a user, I want to see upcoming shipping dates for my subscription boxes. |
|----------------------------|------------------------------------------------------------------------------------------------------|
| Checkout & Payment         | As a user, I want to securely check out and save my payment details for recurring billing. |
|                            | As a user, I want to see confirmation of successful or failed payments. |
|                            | As a user, I want to update my payment method if my card changes. |
|----------------------------|------------------------------------------------------------------------------------------------------|
| Orders & Post-Purchase Flow | As a user, I want to see my order history so I can track previous deliveries. |
|                            | As a user, I want to view payment details associated with past orders (e.g., card type, last 4 digits). |
|                            | As a user, I want to receive confirmation emails for successful orders and renewals. |
|                            | As an admin, I want to view all orders, linked subscriptions, and user details for support or fulfillment. |
|----------------------------|------------------------------------------------------------------------------------------------------|
| UX and Accessibility       | As a user, I want the site to be easy to navigate, even on mobile, so I can find what I need quickly. |
|                            | As a user, I want clear feedback when I complete actions (e.g., subscribing, pausing, paying). |
|                            | As a user, I want the site to support screen readers and keyboard navigation for accessibility. |
|----------------------------|------------------------------------------------------------------------------------------------------|
| Admin & Configuration      | As an admin, I want to manage boxes, subscriptions, and orders via a secure dashboard. |



# Design Choices

The initial site design is intentionally minimal, leveraging Materialize for a clean, responsive layout. This choice was made to prioritise backend functionality and Stripe integration over heavy front-end customisation. By using Materialize's grid and component system, development time was optimised, allowing more focus on core application logic and data flow.

The backend implementation was designed with DRY (Don't Repeat Yourself) principles in mind. For example, single HTML templates are used for similar user flows, such as self-purchases and gift purchases, reducing redundancy and simplifying maintenance. This approach also extends to subscription management, order handling, and admin views, ensuring consistency across the site.

## [Wireframes](#wireframes)
Wireframes were created with Balsamiq and provided rough initial mockups for how the site should look. Some variation from these occurred as the project developed. 

Homepage
  <img src="docs/wireframes/homepage.png">
Subscription Page
  <img src="docs/wireframes/subs_page.png">
Basket
  <img src="docs/wireframes/basket.png">
Checkout
  <img src="docs/wireframes/checkout.png">
Past Boxes
  <img src="docs/wireframes/past_boxes.png">
Account Page
  <img src="docs/wireframes/accounts.png">


    <img src="docs/wireframes/homepage.png">
##  [Schema](#schema)
To enhance security and streamline data management, I opted to leverage Django's built-in User model for authentication and user management. This decision minimised the need for custom table designs while taking advantage of Django's proven security mechanisms, such as password hashing and session management.

For payment processing, all sensitive billing information is exclusively handled by Stripe. This means that no credit card details are stored on the site itself, significantly reducing risk in the event of a data breach. While PII (Personally Identifiable Information) like home addresses, email addresses, and names are stored for order fulfillment, payment data remains isolated and protected by Stripe's secure environment. This separation ensures that the financial impact of any potential breach is minimised.

  <img src="docs/erd.png">
| Model                  | Purpose                                                                                                                                                                             | Key Fields                                                                                                                                                                                                                                       | Relationships                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| User                   | Stores all user accounts, including regular users and admin accounts.                                                                                                               | [`user_id` (PK), `username`, `email`, `password`, `is_admin` (boolean), `date_joined`]                                                                                                                   | One-to-many with ShippingAddress, StripeSubscriptionMeta, Order, Payment                         |
| ShippingAddress        | Stores one or more delivery addresses per user. Used for personal or gifted boxes.                                                                                                  | [`shipping_id` (PK), `user_id` (FK) → User, `recipient_name` and full address fields, `is_default` (boolean)]                                                                                            | Many-to-one with User; One-to-many with Order and StripeSubscriptionMeta                         |
| StripeSubscriptionMeta | Links a Stripe-managed subscription to internal data. Captures shipping address and gift status.                                                                                    | [`id` (PK), `user_id` (FK) → User, `stripe_subscription_id`, `stripe_price_id`, `shipping_address_id` (FK), `is_gift` (boolean), `created_at`, `cancelled_at`]                                           | Many-to-one with User and ShippingAddress; One-to-many with Order                                |
| Box                    | Admin-created box offerings. Archived boxes stay viewable in history.                                                                                                               | [`box_id` (PK), `name`, `slug`, `description`, `image_url`, `shipping_date` (nullable), `is_active`, `is_archived`, `created_at`]                                                                       | One-to-many with Order and BoxProduct                                                            |
| Order                  | Represents a single box shipment. Created via Stripe webhook after successful charge.                                                                                               | [`order_id` (PK), `user_id` (FK) → User, `shipping_address_id` (FK) → ShippingAddress, `box_id` (FK) → Box, `stripe_subscription_id` (from Stripe), `order_date`, `scheduled_shipping_date`, `status`]   | Many-to-one with User, ShippingAddress, Box; One-to-one with BoxHistory; One-to-many with Payment |
| BoxHistory             | Snapshot of the box at time of shipment. Used for historical accuracy.                                                                                                              | [`history_id` (PK), `order_id` (FK) → Order, `box_name`, `slug`, `image_url`, `description`, `created_at`]                                                                                               | One-to-one with Order                                                                            |
| Payment                | Logs each payment attempt/success. Created by webhook when Stripe charge occurs. Card info is fetched live from Stripe or hydrated at webhook time (e.g. 'Visa •••• 4242').        | [`payment_id` (PK), `user_id` (FK) → User, `order_id` (FK) → Order, `payment_date`, `amount`, `status`, `payment_method`]                                                                                | Many-to-one with User and Order                                                                  |
| BoxProduct             | Represents each item in a box. Used to display box contents in carousels or lists.                                                                                                  | [`content_id` (PK), `box_id` (FK) → Box, `name`, `image_url`, `description`, `quantity`]                                                                                                                          | Many-to-one with Box                                                                             |

When reading up on Django models, I encountered this, which seemed helpful since I had a few issues with getting tooltips to play nice on my last project. So this seems like it may help with this. https://docs.djangoproject.com/en/3.2/ref/models/fields/#help-text

##  [UX](#ux)
UX Design and User Flow

When a user first visits the site, they land on the Home Page, which looks the same for both logged-in and logged-out users. However, navigation menus and buttons dynamically adjust based on the user's authentication status and role. For example, purchase and gift purchase buttons have two distinct versions:

Logged-out Users: These buttons guide users through a registration journey as part of the purchase flow, ensuring every buyer is registered and linked with a Stripe ID.

Logged-in Users: The flow skips registration and goes directly to the purchase stage, streamlining the checkout process.

This logic guarantees that all users are fully registered before making a purchase, enhancing order tracking and payment processing.

Navigation and Menu Logic

Once logged in, users are presented with a tailored menu:

Account Page Access — View and manage orders, addresses, and subscription details.

Logout Button — A simple and accessible way to end the session.

Dynamic Purchase Buttons — Adjust to reflect that the user is authenticated.

Page Overviews:

About Page

The About page provides users with information about the service, including who might benefit from it, typical box contents, and a call to action for subscriptions or single-box purchases.

Buy for Myself / Give as a Gift

Both menu items present similar options:

Users can select from single boxes or four subscription tiers (monthly, quarterly, biannual, annual).

Messaging and layout dynamically adjust to reflect whether the purchase is a gift or for personal use.

Purchase Flow

The purchase flow is nearly identical for both personal and gift orders:

Plan Selection: Users choose between a single box or one of four subscription plans.

Address Picker: The user selects a shipping address. If none exist, they can add one at this stage, as well as edit or add new addresses.

Gift Divergence:

For personal orders, users proceed directly to Stripe for payment.

For gift orders, the user is prompted to enter optional fields: sender's name, recipient's name, recipient's email, and a personalised message. All fields are optional, allowing for anonymous or surprise gifting if desired.

Stripe Checkout: Users complete their purchase securely via Stripe. If they cancel, they are redirected to a page offering options to retry or return home. Successful purchases take users to a confirmation page with links to account details and order history.

My Account Page

The My Account page grants users access to:

User Details and Order History — Quick access to past orders and account information.

Change Password — Requires the current password for validation.

Edit Account Information — Update email, username, and names.

Address Management — Add, edit, or remove personal and gift addresses.

If only one personal address exists, it cannot be deleted while active orders or subscriptions are ongoing to prevent delivery issues.

Friendly names (e.g., Home, Work) can be assigned for clarity.

Order History Page

Orders are split into two categories: Subscriptions and Single Boxes.

Each item displays order number, status (Pending, Processing, Shipped, Cancelled), order date, recipient info (if a gift), estimated shipping date, and renewal date for subscriptions.

Users can view more detailed information or cancel subscriptions directly from this page.

A globally-located password-protected modal is used for destructive actions like cancellation to prevent accidental misuse.

Admin Dashboard

If the user is an admin, an additional Admin Menu becomes available, offering access to:

Box Management — Add, edit, delete, or archive boxes.

Archived automatically if past the current month.

Cloudinary is used for image uploads, with images optional for early box creation.

Orphaned products (those not assigned to a box) are listed and can be bulk-added to boxes.

Product Management — Add, remove, or orphan products within a box.

Products can be edited or deleted, with password-protected modals to prevent accidental removal.

User Management — View all registered users, their details, and subscription statuses.

Admins can activate, deactivate, or reset passwords for users, as well as view their account in Stripe for billing support.

Order Management — Monitor order IDs, payment status, order state, and manage subscription cancellations.

Security Features

Where destructive or sensitive actions occur (e.g., cancelling subscriptions, deleting products, changing sensitive user data), password-protected modals are used for defensive programming. Toast notifications are displayed for actions like updates or changes, providing clear feedback to the user.

Additionally, email notifications are triggered for key events:

Order Confirmation

Subscription Renewals

Account State Changes

Emails are currently plaintext, but provide necessary feedback for user assurance.


##  [Colour Palette](#colour-palette)
The color scheme was chosen late in development to create a welcoming and easy-on-the-eye experience. The primary colors are neutral and calming, with a focus on readability and accessibility.

Primary Color: Various shades of green are used throughout the site, particularly for navigation menus and headers, creating a consistent visual identity.

Button Colors:

Green: Positive actions (e.g., submit, confirm)

Red: Caution or destructive actions (e.g., delete, cancel)

Blue: Neutral actions (e.g., edits, updates)

This color-coding ensures that users can quickly understand the purpose of each button, enhancing usability and reducing the chance of errors.

By keeping the color scheme simple and purposeful, the site remains both functional and aesthetically pleasing.

##  [Typography](#typography)
Similar to the color palette, font choices were made later in development, with initial focus placed on core functionality. Two Google Fonts were selected to provide clear visual distinction between headings, body text, and navigation elements.

Both fonts are clean, sans-serif, and optimised for readability across devices.

They were also chosen with accessibility in mind, ensuring clarity for all users, including those in the neurodiverse community.

This careful selection supports readability and user comfort throughout the site experience.


##  [Images](#images)
Local images are kept to a minimum, with all primary visual assets hosted on Cloudinary. This approach reduces server load, improves site performance, and simplifies image management.

Cloudinary handles image storage, optimisation, and delivery, ensuring fast load times.

This also enables easy updates and versioning without the need for redeployment.

Image URLs are securely referenced, reducing exposure to direct access vulnerabilities.

By leveraging Cloudinary, the site remains lightweight and efficient, even as image content scales.

##  [Icons](#icons)
Icons throughout the site are provided by Font Awesome, enhancing navigation and user interactions with clean, universally recognisable symbols.

Icons are used for key features such as:

Buttons (e.g., edit, delete, submit)

Bullet Points for lists

Navigation Links

Font Awesome ensures consistency and scalability across all devices, maintaining a professional look while simplifying UI elements.

This choice keeps the interface intuitive and visually consistent, improving the user experience.

##  [Features](#features)



testing 

$ pytest --ds=hobbyhub.settings -v --color=yes
==================================================== test session starts =====================================================
platform win32 -- Python 3.12.3, pytest-8.3.5, pluggy-1.6.0 -- C:\Users\darre\Code\HobbySub\venv\Scripts\python.exe
cachedir: .pytest_cache
django: version: 4.2.20, settings: hobbyhub.settings (from option)
rootdir: C:\Users\darre\Code\HobbySub
plugins: django-4.11.1
collected 65 items                                                                                                            

boxes/tests/test_boxes.py::TestPastBoxesView::test_past_boxes_view_success PASSED                                        [  1%]
boxes/tests/test_boxes.py::TestPastBoxesView::test_past_boxes_view_no_archived_boxes PASSED                              [  3%]
boxes/tests/test_boxes.py::TestBoxDetailView::test_box_detail_view_success PASSED                                        [  4%]
boxes/tests/test_boxes.py::TestBoxDetailView::test_box_detail_view_not_found PASSED                                      [  6%]
dashboard/tests/test_dashboard.py::test_box_form_missing_fields PASSED                                                   [  7%]
dashboard/tests/test_dashboard.py::test_box_form_invalid_date PASSED                                                     [  9%]
dashboard/tests/test_dashboard.py::test_box_form_valid_creation PASSED                                                   [ 10%]
dashboard/tests/test_dashboard.py::test_box_form_auto_archive PASSED                                                     [ 12%]
dashboard/tests/test_dashboard.py::test_box_form_editing PASSED                                                          [ 13%]
dashboard/tests/test_dashboard.py::test_box_form_invalid_file PASSED                                                     [ 15%]
dashboard/tests/test_dashboard.py::test_create_box PASSED                                                                [ 16%]
dashboard/tests/test_dashboard.py::test_edit_box_image_update PASSED                                                     [ 18%]
dashboard/tests/test_dashboard.py::test_edit_box_date_forward PASSED                                                     [ 20%]
dashboard/tests/test_dashboard.py::test_user_admin_overview PASSED                                                       [ 21%]
dashboard/tests/test_dashboard.py::test_toggle_user_state PASSED                                                         [ 23%]
dashboard/tests/test_dashboard.py::test_admin_password_reset PASSED                                                      [ 24%]
dashboard/tests/test_dashboard.py::test_order_status_update PASSED                                                       [ 26%]
dashboard/tests/test_dashboard.py::test_admin_cancel_subscription PASSED                                                 [ 27%]
hobbyhub/tests/test_hobbyhub.py::TestMailFunctions::test_send_gift_confirmation_to_sender PASSED                         [ 29%]
hobbyhub/tests/test_hobbyhub.py::TestMailFunctions::test_send_gift_notification_to_recipient PASSED                      [ 30%]
hobbyhub/tests/test_hobbyhub.py::TestMailFunctions::test_send_order_confirmation_email PASSED                            [ 32%]
hobbyhub/tests/test_hobbyhub.py::TestMailFunctions::test_send_payment_failed_email PASSED                                [ 33%]
hobbyhub/tests/test_hobbyhub.py::TestMailFunctions::test_send_subscription_confirmation_email PASSED                     [ 35%]
hobbyhub/tests/test_hobbyhub.py::TestMailFunctions::test_send_upcoming_renewal_email PASSED                              [ 36%]
hobbyhub/tests/test_hobbyhub.py::TestUtilsFunctions::test_alert PASSED                                                   [ 38%]
hobbyhub/tests/test_hobbyhub.py::TestUtilsFunctions::test_build_shipping_details PASSED                                  [ 40%]
hobbyhub/tests/test_hobbyhub.py::TestUtilsFunctions::test_get_gift_metadata PASSED                                       [ 41%]
hobbyhub/tests/test_hobbyhub.py::TestUtilsFunctions::test_get_subscription_duration_display PASSED                       [ 43%]
hobbyhub/tests/test_hobbyhub.py::TestUtilsFunctions::test_get_subscription_status PASSED                                 [ 44%]
hobbyhub/tests/test_hobbyhub.py::TestUtilsFunctions::test_get_user_default_shipping_address PASSED                       [ 46%]
home/tests/test_home.py::test_register_form_required_fields PASSED                                                       [ 47%]
home/tests/test_home.py::test_register_form_max_length PASSED                                                            [ 49%]
home/tests/test_home.py::test_register_form_invalid_email PASSED                                                         [ 50%]
home/tests/test_home.py::test_register_form_password_mismatch PASSED                                                     [ 52%]
home/tests/test_home.py::test_register_form_success PASSED                                                               [ 53%]
orders/test/test_orders.py::TestStripeSubscriptionMeta::test_subscription_creation PASSED                                [ 55%]
orders/test/test_orders.py::TestStripeSubscriptionMeta::test_subscription_string_representation PASSED                   [ 56%]
orders/test/test_orders.py::TestOrder::test_order_creation PASSED                                                        [ 58%]
orders/test/test_orders.py::TestPayment::test_payment_creation PASSED                                                    [ 60%]
orders/test/test_orders.py::test_select_purchase_type_view PASSED                                                        [ 61%]
orders/test/test_orders.py::test_order_success_view PASSED                                                               [ 63%]
orders/test/test_orders.py::test_order_cancel_view PASSED                                                                [ 64%]
orders/test/test_orders.py::test_order_history_view PASSED                                                               [ 66%]
orders/test/test_orders.py::test_choose_shipping_address_view PASSED                                                     [ 67%]
orders/test/test_orders.py::test_handle_purchase_type_view PASSED                                                        [ 69%]
orders/test/test_orders.py::test_gift_message_view PASSED                                                                [ 70%]
orders/test/test_orders.py::test_secure_cancel_subscription PASSED                                                       [ 72%]
orders/test/test_orders.py::test_handle_purchase_type_no_shipping_id PASSED                                              [ 73%]
orders/test/test_orders.py::test_choose_shipping_address_no_addresses PASSED                                             [ 75%]
orders/test/test_orders.py::test_choose_shipping_address_valid_and_invalid_ids PASSED                                    [ 76%]
orders/test/test_orders.py::test_create_subscription_checkout_missing_shipping_id PASSED                                 [ 78%]
orders/test/test_orders.py::test_concurrent_order_creation PASSED                                                        [ 80%]
orders/test/test_orders.py::test_secure_cancel_subscription_wrong_password PASSED                                        [ 81%]
orders/test/test_orders.py::test_gift_order_creation PASSED                                                              [ 83%]
users/tests/test_users.py::TestUsersViews::test_account_view PASSED                                                      [ 84%]
users/tests/test_users.py::TestUsersViews::test_add_address PASSED                                                       [ 86%]
users/tests/test_users.py::TestUsersViews::test_edit_account PASSED                                                      [ 87%]
users/tests/test_users.py::TestUsersViews::test_edit_address PASSED                                                      [ 89%]
users/tests/test_users.py::TestUsersViews::test_password_reset_confirm PASSED                                            [ 90%]
users/tests/test_users.py::TestUsersViews::test_password_reset_request PASSED                                            [ 92%]
users/tests/test_users.py::TestUsersViews::test_secure_delete_account PASSED                                             [ 93%]
users/tests/test_users.py::TestUsersViews::test_secure_delete_address PASSED                                             [ 95%]
users/tests/test_users.py::TestUsersViews::test_set_default_address PASSED                                               [ 96%]
users/tests/test_users.py::ShippingAddressTest::test_address_cannot_be_deleted_if_linked_to_order_or_subscription PASSED [ 98%]
orders/test/test_orders.py::test_concurrent_subscription_creation PASSED                                                 [100%]

====================================================== warnings summary ====================================================== 
venv\Lib\site-packages\django\conf\__init__.py:241
  C:\Users\darre\Code\HobbySub\venv\Lib\site-packages\django\conf\__init__.py:241: RemovedInDjango50Warning: The default value of USE_TZ will change from False to True in Django 5.0. Set USE_TZ to False in your project settings if you want to keep the current default behavior.
    warnings.warn(

orders/test/test_orders.py::test_concurrent_subscription_creation
  C:\Users\darre\Code\HobbySub:0: PytestWarning: Error when trying to teardown test databases: OperationalError('database "test_polar_flock_crook_753623" is being accessed by other users\nDETAIL:  There are 2 other sessions using the database.\n')       

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
========================================= 65 passed, 2 warnings in 131.76s (0:02:11) ========================================= 
Admin Enhancements
Direct Stripe Links:
Allowing admins to directly link to customer orders in Stripe would streamline the resolution of billing disputes and provide quick access to payment histories.

Stock Handling and Management:
Extending the current admin functionality to include stock management would enable real-time inventory tracking. This would allow admins to predict when a box may need to be archived due to low stock levels and help with future planning.

Customer Experience Improvements
Purchase Older Boxes:
If stock management is implemented, it would allow the sale of older, less popular boxes as single items. This would enable admins to clear out slower-moving inventory while providing more choice to customers. It would also provide valuable insights into which items are in higher demand.

Address Lookup Integration:
Adding a global address lookup service would speed up the checkout process for users and ensure accuracy. This would minimise address-related errors and reduce admin overhead for manual corrections.

Security and Validation
reCAPTCHA on Signup Forms:
Currently, bot-based signups are possible as reCAPTCHA was not implemented due to time constraints. Adding this would enhance security and prevent automated signups.

Communication and Support
Contact Form:
A contact form would improve user support options. However, it was not implemented due to previous issues with spam and difficulties integrating Captcha in earlier projects. Future versions will aim to address this with proper spam protection.

Admin Address Visibility:
As it stands, admins cannot directly view address information linked to orders. This feature would streamline shipping processes and improve overall management.

These planned improvements are designed to build on the solid foundation of the existing platform, enhancing both usability and backend efficiency in future iterations.


Security defenceive programming abd best practiceis. 
Security is a core aspect of the platform, with several layers of protection implemented to safeguard user data and prevent unauthorised changes.

Password Security
User account passwords are handled entirely by Django's built-in authentication system, which includes:

Password Hashing: All passwords are hashed using industry-standard algorithms, ensuring that raw password data is never stored in the database.

Django Best Practices: By leveraging Django's robust security features, the platform benefits from regular security updates and best practices without custom implementation.

Account Change Notifications
To maintain transparency and security, users receive email notifications whenever their account information is updated. This allows users to be immediately aware of any changes, preventing unauthorised alterations from going unnoticed.

Modal-Based Deletion Protection
All potentially destructive or sensitive actions are protected by a password-protected modal.

This includes:

Email Changes

Account Deletions

Admin Actions on User Accounts

The modal prompts for the user's password before finalising the action, adding a secure second layer of verification.

This two-stage process ensures that only authenticated users can complete these operations, significantly reducing the risk of accidental or malicious changes.

This multi-layered approach to security is designed to protect user data, prevent unauthorised access, and maintain the integrity of sensitive account information.

Technology 
Frameworks and programs. 
Languages
HTMLCSS
JAvascript
Python

version control and deplyoments. 
Github
GitherokuGithub projects. 

Frameworks
Django
Materialize

Database
PostGreSQL

Coding Environment. 
VSCode. 

Othertools and utilities
ERD DB DEisgner
Balsamiq
DJecrety
Cloudinary
Google
Chrome Dev Tools
WAVE
Google Fonts
Techsini
Favicon.io

Testing and validation 

Version control and Deployment
repo Creation
Cloning Locally
Adding and Updating Files on the Repo.
Forking and Merging
Local Deployment
PostGres DB Creation
Heroku Set up and Configuration.
Credits
Acknowledgements