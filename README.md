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
HobbySub is an online eCommerce site for tabletop wargame and model making hobbyists. It provides a mystery-box subscription service, which ships a new box of hobby supplies every month based on a specific theme. Users can sign up for four subscription options. Month by month, 3 monthly, 6 monthly or yearly. Representing different billing cycles and different price points. With discounts offered for longer subscription terms. Users can also purchase single boxes, if they're not yet ready to subscribe. The site has logic built into it to allow for purchases to be bought as items for the user, or as a gift to someone else, with personalised gift emails sent out when the item is ordered. 

To manage and prioritise tasks, I set up a Kanban board to help track specific parts of the project from inception to completion. I used this in conjunction with a MoSCoW board to help with planning and prioritisation. 

[My MoSCoW board can be found here](https://github.com/users/monkphin/projects/5/views/1)

[My Kanban board can be found here](https://github.com/users/monkphin/projects/6/views/1)

## Site Owner Goals

 - Provide a secure and scalable platform to sell and manage subscription-based box offerings.
 - Allow users to easily subscribe to recurring boxes or gift one-off boxes to others.
 - Enable users to manage their own subscriptions (pause, cancel, change address).
 - Maintain full control over box offerings, shipment schedules, and customer data.
 - Ensure clear separation between admin and regular user functionality for operational security.
 - Offer a professional, responsive, and accessible user interface across all devices.
 - Integrate Stripe or a similar secure payment gateway to handle recurring billing and one-off payments.
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

The initial site design relied heavily on Materialize, so the site does look a little generic. This is quite deliberate. Since I knew the core of the work would be in the backend, getting Django to work how i needed as well as getting it to work with Stripe integrations. Where possible I used DRY approaches, using single HTML templates for similar functions, such as gift or self based purchases etc. 


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
In order to minimise the data I needed to design tables for and to enhance security. I fell back on using DJango's inbuilt users functionality. Additionally for security reasons I have made efforts to not store anything for billing on the site  - this way if the site suffers a breach, while PII (Personally identifiable information) such as home addresses, email addresses, names etc. Will be available. Card details are not at risk. Meaning the impact should be less significant. These are all handled by stripe. 

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
When a user first visits the site, they land on the home page, this should look the same for both logged in and logged out users. Though the menu items and buttons adjust depending on authentication, as well as type of authenticated user. For example the purchase and gift purchase buttons and menu bars have two distinct versions. With the version presented to none registered/signed in users specifically taking them on a registration journey as part of the purchase process, while the versions presented to logged in users does not. This ensure that users are always registered with the site and will have a stripe ID created as part of this process, allowing for robust handling of purchases. Similarly the user is presented with options to login or register when they're logged out. 

Once a user logs in the menu adjusts to show options more fitting for a logged in user. Such as their account page, a log out link and so on. As mentioned previously the purchase buttons also adapt to factor in that the user is logged in. 

The about page gives users a bit of information about the service, outlining who may benefit from this, what the box can include and a call to action at the bottom. 

The buy for myself/give as gift menu items both present similar options to a user. With options for single boxes or the four subs. The page tailors its presentation to suit each possible purchase route available - with messaging reflecting that the purchase is a gift or just a standard purchase. 

The flow for both types of order (gift or personal) is nearly identical so this will apply to both types - within the purchase flow the first screen the user sees is one to choose a plan - be it a single box, or one of the four subscription options. Once selected, they're sent to an address picker where they can choose the shipping address in use for the order. If no address exists one can be added here also. The user is also able to edit or add new addresses at this stage of the flow. Once the address is picked the flows diverge slightly. For orders for the user themselves, they're taken directly to stripe to enter their card data and complete the payment. For gift based purchases the user sees another screen where they can provide their name, the recipients name, the recipients email and a gift message. All of these fields are option and the site will allow for them to not be filled (or even just some of them to be filled and others left blank) this allows for the sender to ship without notifying the recipient - this is intentional, since people may choose to send the boxes as a surprise gift. Finally, once they press the Proceed to checkout button they're taken to stripe to complete the purchase. 

Purchase. The user can cancel the purchase on the stripe screen, if they do so they're taken to a page to allow them to either go home, or to retry, this restarts the purchase flow. If they complete they're taken to another page that lets them go to their account to view their order history or to go home. 

My account grants the user access to their account history and settings. With their user details and order history being quickly accessible in a card at the top of the screen - the order history button opens a new page which lists any historic orders. 
The user also has options to change their password, edit their account or delete their account here. As well as viewing, adding or editing both personal and gift based addresses for purchases. 

Order history this page splits orders by subs or single box purchases in a list of items for each. Each item shows order numbers, the current order state (Pending, processing, shipped or cancelled) the date of the order, if the order was a gift or not, who its shipping to. The estimated shipping date and the renewal date if its a subscription. The user can also using the two buttons see more information - which is mostly just the same data with more detail or can cancel their sub here too - the cancellation button uses a globally located modal that requires their password to cancel the order to provide some defensive programming. 

The change password button takes the user to a new page where they're required to enter their current password and enter a new password twice. Again providing a level of defensive programming. 

Edit account allows for the changing of email, username and the users first and last name. Only the email requires a password to change, which is again offered via a global modal for use on multiple forms like this. 

THe address section shows both personal and gift based addresses if any exist. The use can add either type of address from here, using a DRY form which is displayed when clicking either 'add X address' button. Both types of address also allow for friendly names, such as home, work, etc. THe Personal address field also allows the user to set this as a default address. If the user has no personal address configured, the first they add will become their default shipping address automatically even if this is not checked. Additionally for shipping reasons if the user only has a single personal or gift address they are unable to delete it while any orders are outstanding or subscriptions are ongoing. Since these would be required to allow their goods to be sent to them. 

Finally. if the user is an admin, their is a custom admin menu thats only visible and accessible to admins on the site. This provides a drop down allowing admins to administer boxes or users. 

The box admin section allows admins to add, delete or edit boxes and their contents. They can add individual items here, as well as boxes. They can also see what boxes have been set up and saved as well as their current states - such as shipping dates, if the box is archived due to age and so on. This page also shows a list of 'orphaned products' which represent products that arent assigned to a box. These can be added in bulk using checkbox buttons or one at a time to existing boxes. 

The add new box button allows the admin to create a new box - this requires a name, a description and a date. The image is currently optional - since there may be scenarios where an admin could be bulk adding future boxes before imagary can be found and edited for use. Image uploading uses cloudinary for storage. The admin can also archive a box here. Though this will auto archive if its older than the end of the current month. Once the box is saved they're taken to a page that displays the box and its contents, which for a new box would be empty. Here they can add single products, using the add product button. Or, if their are orphaned products these are visible and addable here too. Any products that are added can be edited, removed (orphaned) or deleted outright, with the delete button requiring a password to prevent accidental deletion. 

The edit button on the box list takes the admin to a section similar to that seen when a new box is created - letting them edit the name, description edit the image or shipping date, as well as change the archived state. Their is also a manage product button here which takes the admin to the same page displayed when clicking the products page on the box manager screen. 

The box products page lists any items in the box, it allows an admin to create a new product to add - this is performed one item at a time. As well as add any orphaned products to the box. Products pictured here can be modified, removed and made orphans or deleted outright. 

The delete box button uses the same global modal to require a password before the box can be delete. 

Finally orphaned products will list any products not assigned to the boxes listed on the box manager page, these can be assigned in bulk to existing boxes. Deleted, or edited from the buttons - with the delete button again using protective modals to prevent accidental removal. 

The user mananger will show all registered users in a list. Giving usernames, emails, if they're admins, if they're active or have deactivated, view their orders, edit the account, sennd a password reset email or deactivate/activate the account (for billing enquieries etc it was decided that prior to deletion users should simply be deactivated. In order to delete a user the admin currently has to use Djangos own backend admin platform.) finally each user has a button to show their accountin stripe to help with billing issues and other queries. 

The orders page allows the admin to see the ID, the date the order was placed, if payment succeeded, change the order states, see if its a gift, cancel a sub and see the name of the due box. 

Editing the user lets the admin change their username, email see when they joined or when they last logged in. As well as sending a password reset email, changing them to be admins or deactivating the account. 

Where users or admins are able to take destructive actions, a modal is fired to request a password to provide some level of defence against accidental deletion or editing. Toasts are used to provide message feedback for activities carried out on the site, such as updating data, etc. A custom error handler exists for error messaging on forms, ensuring the user is kept informed of issues. Email notifications for order state changes and account state changes also exist, though only in plainttext. These elements all exist to create a smooth, user friendly experience with feedback where needed. 


##  [Colour Palette](#colour-palette)
The colour scheme was chosen late in development, to be reasonably easy on the eye using neutral, welcoming colours. Text readability was a factor in this choice also. 
Greens are used through out with varying shades for the nav and top menu and various elements on the site. 
Button colours are aligned with function, greens for positive outcomes reds for places where caution may be needed and blue for neutral actions like edits, updates etc. 

##  [Typography](#typography)
Like the colour palette, fonts were chosen later in development, as the initial focus was on core functionality. Two Google Fonts were selected to provide visual distinction between text, headings, and the nav bar. Each font is clean and sans-serif, ensuring readability across various devices and user types, including those in the neurodiverse community.


##  [Images](#images)
Local images are minimal, with everything hosted by Cloudinary where possible. 


##  [Icons](#icons)
Icons are provided by font awesome and are used for variou features including buttons, bullets etc. 

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

Future features. 
THe site has a lof of scope for future improvements. 

Allowing admins to directly link to customer orders in Stripe would be a nice, quick feature to implement and allow admins to quickly access specific order history in the even of billing disputes and similar. 

Stock handling - while the admin can add items to boxes, this could be extended to allow for stock handling and management - so that admins can know if they're going to need to archive boxes sooner than expected due to lack of availability of items. 

Purchase older boxes. If stock was able to be tracked, this would allow less popular boxes to be sold as single items in addition to the currently shipping box - this would allow for admins to shift inventory which may not be moving quickly. It would also help gauge what may or may not be popular in terms of specific contents. 

Address lookup - one feature that would be highly advantageous is tying into a global address lookup system, which would facilitate users quickly adding details, rather than having to type everything out by hand. This would also help ensure accuracy for admins. 

Showing address data to admins on orders - this should have been in the initial release - its only since I've started to get to the end of the project that I realised this feature may be useful to allow admins to see where they're shipping boxes to. 

Racapchta on sign up forms. As it stands, automated bot based sign up is possible. Sadly I lacked time to implement Captcha functionality to prevent this. 

Similarly to the above a contact form while not required would be useful - but having has issues with this the last time I implemented it on a website for this course, where I couldn't get Captcha working properly in the the time I had for the project. I opted to not implement this at this time, since previously the last project became something of an issue for spam mails being sent using the form. 


Security defenceive programming abd best practiceis. 

Password security - this is all handled by Django - my user accounts are saved and stored using its built in features, so password hashing is handled directly by Django itself, so should follow best practices here. 

Account change notifications - the users will get emails when their account is updated, allowing them to be aware of any changes they may not have made. 

Modal based deletion protection. All destructive or dangerouse changes, such as email changes etc are protected by a modal that requires password based authentication. This includes admin actions as well as user actions and creates a secure two stage process - where the user gets a warning and that warning requires a password to action, ensuring that only the user should be able to take the action. 

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