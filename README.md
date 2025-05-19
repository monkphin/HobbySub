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

# Technology
## Frameworks and Programs
 ### Languages
 - [HTML](https://www.w3schools.com/html/) - used to create the front end of the website.
 - [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) - Used to style the website. 
 - [Javascript](https://developer.mozilla.org/en-US/docs/Web/javascript) - Used for front-end interactions and adjustments. 
 - [Python](https://www.python.org/) - The backend programming language. 

 ### Version Control and Deploying. 
 - [Github](https://github.com/) - Used to store the website's codebase in a repo. 
 - [Git](https://git-scm.com/) - A CLI based tool used for version control and uploading to Github. 
 - [Heroku](https://www.heroku.com/) - Hosting the final deployed version of the website. 
 - [GitHub Projects](https://github.com/) - used to help plan and manage my project. 

 ### Frameworks 
 - [Materialise](https://materializecss.com/) - a Front end library used to provide some templating and layout, as well as some Javascript-powered features such as modals, carousels and so on. 
 - [Django](https://www.djangoproject.com/) - The Python framework that powers the site. 
 - [Awesomeplete](https://projects.verou.me/awesomplete/) - Used to provide auto-complete functions for Tags

 ### Database
 - [PostGreSQL](https://www.postgresql.org/) - A relational database used to store the data for the site. 

 ### Coding Environment 
 - [VSCode](https://code.visualstudio.com/) - My IDE of choice. 

 ### Other Tools and Utilities
 - [ERD DB Designer](https://erd.dbdesigner.net/) - Used to help with ERD diagrams and understanding the DB relationships
 - [Balsamiq](https://balsamiq.com/) - Wire-framing program.
 - [Djecrety](https://djecrety.ir/) - Used to generate secret keys.
 - [Cloudinary](https://cloudinary.com/users/login) - Used to host image files
 - [Stripe](https://stripe.com/) - The payment platform used to handle payments and subscription automation. 
 - [Google](https://google.com) - Used to provide Mail services. 
 - [Chrome Dev Tools]() - Used to help analyse performance, responsiveness and tweak CSS in a live situation to ensure accurate adjustments. 
 - [WAVE](https://wave.webaim.org/) - Used for accessibility testing
 - [Google Fonts](https://fonts.google.com/) - Used to import fonts to the style sheet. 
 - [Techsini](https://techsini.com/) - Mockup generator
 - [Favicon.io](https://favicon.io/favicon-converter/) - Used to generate Favicons. 

# Testing and Validation

Testing is covered in the following document: [Testing And Validation](TESTING.md)

# Version control and Deployment

The live site is deployed on Heroku, configured to automatically update from GitHub with every commit. It currently utilises a PostgreSQL relational database provided by Code Institute. Upon project completion and marking, I plan to migrate the database to a Heroku-hosted PostgreSQL instance to allow me to continue developing and running the site as an ongoing project.

## Repo Creation

A new repo was generated using the Code Institute's ci-full-template with the following steps:

1. Navigate to https://github.com/Code-Institute-Org/ci-full-template
2. Click the green 'Use this template' button and select 'Create a new repository'
3. On the newly loaded page, in the text field enter a name for the repo, in this case, Colour Forge was entered.
4. An optional description can be added in the text box below this. In this instance, this was left blank.
5. Select the visibility as either public or private. Since this needs to be visible for assessment and marking, the default 'Public' option was left checked.
6. Click the Create repository button and wait for a few moments, once this has been cloned into your account the page will reload and you'll be presented with the code space for the repo.

## Cloning Locally

I work with VSCode, so use the built-in CLI to run the commands needed to clone the repo to my local machine for editing. 

1. In VSCode, I opened the Terminal window, by visiting the 'Terminal' menu in VSCode and selecting 'New Terminal'
2. Within this terminal window, I made sure I was in the correct folder for where I wanted to store my work, if this was not correct I would have used the bash command cd to navigate to the correct folder. In this case, ~/Code, which is a folder called 'Code' in my logged-in user Home Folder.
3. In a web browser, I navigated to the GitHub repository for the project and clicked on the green '<> Code' button, this presented me with several options for cloning. I selected the 'HTTPS' option and copied the URL in the text field.
4. In Visual Studio Code’s terminal, I typed git clone https://github.com/monkphin/HobbySub.git and pressed enter, which cloned the repo to my local machine as shown by the below output.
   ```
    Code here
   ```


5. Once this had finished cloning I used cd to navigate into the relevant folder - in this case, cd HobbySub
   
  ```
  darren@localhost MINGW64 ~/Code (main)
  $ cd HobbySub/
  darren@localhost MINGW64 ~/Code/HobbySub (main)
  ```
6. I am now able to work on the project on my local machine.

I used the ability to clone locally to allow me to work on several devices throughout the creation of the app and its readme file. It's worth noting that at several points I was working on the project on a computer provided by my employer as part of our allocated "10% Time" where we're allowed to focus on studying and personal development. Any commits made from this device will show my work GitHub profile (Movonkphin) as being responsible for them.

## Adding and Updating Files on the Repo. 

Much like all previous instructions this will be carried out via CLI. 

1. Once you are ready to upload a new or a changed file, within the terminal type: 

  ``` 
  git add -A
  ```
to add multiple files or

  ```
  git add filename.extension
  ```
to add a single file. 
This adds the file to the current staging area. 

eg: 

  ```
  darre@Anton MINGW64 ~/Code/HobbySub (main)
  $ git add -A 
  ```
It's worth being aware that using git add -a will update all files, so to avoid sending private or secret data you may need to create a .gitignore file, which will contain a list of files that you want git to not upload to GitHub when using git add commands. 

eg 

  ```
  core.Microsoft*
  core.mongo*
  core.python*
  env.py
  __pycache__/
  *.py[cod]
  node_modules/
  .github/
  cloudinary_python.txtsendgrid.env
  sendgrid.env
  testmail.py
  reset_db.py
  ```

2. Once you are ready to commit the change from staging use the following command 

  ```
  git commit -m 'description of the changes made' 
  ```

This creates the commit, ready to be pushed to Github and will show some output in terms of what the commit message is and what files have been changed and how. 

eg: 
  ```
  Code here
  ```

3. Finally, to push the changes to git type 
  ```
  git push
  ```
This should generate some output to confirm the actions being taken to transfer the files to GitHub. 
eg: 
  ```
  Code here
  ```


### Working on Multiple Devices
Assuming you have already cloned the repo to any other computers you may want to work on the code on, you need to ensure that you have the latest version of the code. Luckily this is relatively simple, using a single command.

  ```
  git pull
  ```
This will show some output to show what files its downloading from github as well as any changes or adjustments made to files that are stored locally and need to be updated
eg
  ```
  Code here
  ```
 
## Branching and Merging

During development, I used a Git branching strategy to keep main features and experimental code isolated from the main branch.

### Creating a Branch
To create a new branch for a feature or bug fix:
  ```
  git checkout -b feature/branch-name
  ```

### Switching Branches
To switch back to the main branch:
  ```
  git checkout main
  ```

### Merging Changes
When the feature is complete and tested, switch to the main branch and merge:
  ```
  git checkout main
  git merge feature/branch-name
  ```

### Conflict Resolution
If conflicts arise, Git will prompt you to resolve them before completing the merge.

### Deleting the Branch
Once merged, you can safely delete the feature branch:
  ```
  git branch -d feature/branch-name
  ```

## Local Deployment
For testing reasons it is beneficial to have the site be able to run locally. As mentioned, you can clone the repo to a machine you are working on, allowing you to access the codebase that exists on GitHub. 
Local deployment allows for the testing of modified files before uploading them to GitHub, to ensure the code does what you expect it to, helping minimise the number of commits needed and ensure fewer errors are committed. 

 - We've already covered cloning a repo above. However, you may also need to pull any modules you're using. This can be done with the below command. 
  ```
  pip install requirements -r requirements.txt
  ```
 
Once the required modules are imported, you will also need to ensure you have a local env.py file, since this should never be uploaded to GitHub and can be set to be ignored using the .gitignore file as previously mentioned.
This file needs to be at the root level of your project and should include the environment variables needed to ensure the application can run. 

  ```
  import os

  os.environ.setdefault("IP", "0.0.0.0")
  os.environ.setdefault("PORT", "5000")
  os.environ.setdefault("SECRET_KEY", "insert secret key")
  os.environ.setdefault("DEBUG", "True")
  os.environ.setdefault("DEVELOPMENT", "True")
  os.environ.setdefault("DB_URL", "insert DB URL")
  ```

In the above file we're using a development and debug-enabled environment, this can be useful to allow for debug messages to be pushed to the console. But should never be used in a live production environment since it can create a security risk. 

As you can see from the below, I have configured Heroku to not be in debug or development mode. 

<img src="docs/deployment/debug-config.png">

## PostGres DB Creation

To create the Postgres DB, I used the Code Institute provided Database hosting service, located here: https://dbs.ci-dbs.net/

It provides a guided setup process, which is outlined below. 

 - 1 enter your email address in the field provided
 - 2 Wait for the tool to create the DB
 - 3 Wait for the email to be sent. 

<br>
<details>
<summary>The three DB Creation stage</summary>
<img src="docs/deployment/db-creation.png">
<img src="docs/deployment/db-construction.png">
<img src="docs/deployment/db-deployment.png">
</details>
<br>

Once the email has been received this will confirm the details of your new database. 

<img src="docs/deployment/db-details.png">

## Heroku Set up and Configuration. 
As mentioned this project is hosted on Heroku, a service that allows developers to host applications and websites using tools such as containerisation to create lightweight, isolated servers on the internet, which Heroku refers to as 'Dynos'. 

The below steps outline how to create a Heroku Dyno, once you have an account with them. 

 - Click on 'New' in the drop-down in the top-right of the Heroku Dashboard and select 'create new app' from the menu that appears. 

<img src="docs/deployment/heroku-dyno-deployment.png">

 - Choose a unique app name and choose a region that fits your requirements, typically the one that's geographically closest to you, then click on the 'Create App' button. 

<img src="docs/deployment/heroku-app-name.png">

- Once the next page loads, your dyno is created. However, there are further steps that may be needed to get the app to work. 
- As part of the development process of the app, you will have likely created an env.py file, which stores various pieces of data needed to run the application, such as database URLs, usernames, keys and so on. This information will need to be configured in Heroku. 
- In the tabbed page that will appear after the Dyno has been created, click the 'settings' tab. 

<img src="docs/deployment/heroku-settings.png">

Within the settings screen, scroll down until you see the 'reveal config vars' button, click this to show a form that allows you to enter any variables you may have. 

<img src="docs/deployment/config-vars.png">

Examples of these include:

| key          |   value         |
| ------------ | --------------- |
| IP           |  0.0.0.0        |  
| PORT         |    5000         |
| DB_URL       | url of DB       |
| SECRET_KEY   | users key       |
| OTHER VALUES | set as required |

 - Once this has been saved, you need to create two additional files in your IDE. 
    - requirements.txt
    - profile

The requirements file is used to ensure any imported modules that may be used by your app are included whenever the Dyno is deployed, including things like 'Math', 'Cloudinary', 'Flask' and so on. 
The Procfile is used to tell the Dyno how to start your python application, in this case using the command 'web: python run.py'

 - To generate the requirements file, simply issue the following command:
  ```
  pip freeze -- local > requirements.txt
  ```
The requirements file will need to be updated any time new modules and imports are added to your codebase to ensure it can run the required external functions you may be calling on. 

 - Creating the Procfile can be done either manually, by creating the Procfile itself and then editing its contents in a text editor or IDE or via CLI. 
 - To create via CLI simply issue the below command, assuming your flask app is launched from run.py, otherwise, this will need to be changed to whatever this file is called, e.g. app.py. 
  ''' 
  echo web: python app.py > Procfile
  '''

 - To deploy your code on Heroku, you can either use the Heroku terminal, or alternatively configure the app on Heroku to auto deploy whenever you push a commit to github. 
 - For automatic deployments, within Herokus website, click on the Deployment tab, click 'Connect to Github, choose your account in the dropdown if it's not already there and fill in the name of the repo you wish to deploy from. 

<img src="docs/deployment/deploy-menu.png">
<img src="docs/deployment/deployment-git.png">

 - Once you have selected the appropriate repo, Heroku will spend a few moments connecting to it and if it is successful display the following:

<img src="docs/deployment/connected-git.png">

- This will now allow you to set up auto deploys if you should so choose to, which will allow Heroku to automatically update on changes to the GitHub repo to do this, simply click the 'Enable Automatic Deploys' button.  

<img src="docs/deployment/auto-deploys.png">

 - Alternatively below this is a manual deployment option, which requires you to click the 'Deploy Branch' button each time you're ready to deploy.

<img src="docs/deployment/manual-deploy.png">

Finally, you can, as mentioned, use the Heroku CLI. Where previously you would need to select the GitHub option on the Deploy page, you can simply leave this set to 'Heroku Git' since this is the default setting. 

 - To use the Heroku terminal, you need to login to it using the following command: 
  ```
  $ heroku login
  ```
 - You will then need to set the remote for Heroku. 
  ```
  $ heroku git:remote -a insert-your-app-name
  ```
 - Once done, after using the typical Git-based add, commit and push commands you can deploy to Heroku directly using the following: 
  ```
  $ git push heroku main
  ```

# Credits


# Acknowledgements
 - [Iuliia Konovalova](https://github.com/IuliiaKonovalova), my Code Institute Mentor for your help, insight and advice throughout this project. 
 - The fine community built around [The Fluffenhammer](https://www.thefluffenhammer.com/) for tolerating me going on about this so much in discord and constantly asking if they could test functionality - some of the issues found would still be there if not for you gents. 
 - My incredibly patient wife for putting up with me vanishing for hours at a time while I worked on this over the last couple of months
 - My workmates for putting up with me heavily leaning on my 10% time at work between internal project work to get a bit more time to focus on this. 
