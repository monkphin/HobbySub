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

[My MoSCoW board can be found here](https://github.com/users/monkphin/projects/5/views/1)

[My Kanban board can be found here](https://github.com/users/monkphin/projects/6/views/1)

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

## [Wireframes](#wireframes)
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
  <img src="docs/erd.png">
### User
**Purpose:**  
Stores user authentication and identity information.  
Each user can have one or more subscriptions, shipping addresses, orders, payments, and a linked payment profile.

**Key Fields:**  
- `username`, `email`, `password`  
- `date_joined`

---

### ShippingAddress
**Purpose:**  
Stores one or more delivery addresses per user.  
Used for both personal subscriptions and gifting. Linked to subscriptions and orders so you know where each box is shipped.

**Key Fields:**  
- `recipient_name`, `address_line_1`, `postcode`, `country`, etc.  
- `is_default` flag for preferred address

---

### SubscriptionPlan
**Purpose:**  
Defines the available subscription options.  
Each plan specifies a duration (e.g. 1, 3, or 6 months) and a price.

**Key Fields:**  
- `name` (e.g., "Monthly", "3 Months")  
- `duration_in_months`  
- `price`  
- `is_active` (used to hide deprecated plans)

---

### Subscription
**Purpose:**  
Represents a user’s active or historical subscription to the service.  
Tracks their selected plan, status (e.g. active, paused), start and renewal dates, and delivery address.

**Key Fields:**  
- Foreign keys to `User`, `SubscriptionPlan`, and `ShippingAddress`  
- `status` (active, paused, cancelled)  
- `start_date`, `renewal_date`  
- Optional `cancelled_at` and `paused_at` timestamps

---

### Order
**Purpose:**  
Represents a single scheduled or completed box delivery.  
Generated from an active subscription based on the renewal date.

**Key Fields:**  
- Foreign keys to `Subscription`, `User`, and `ShippingAddress`  
- `order_date` (when it was created)  
- `scheduled_shipping_date`  
- `status` (pending, shipped, cancelled)

---

### Payment
**Purpose:**  
Stores payment records for each order.  
Tracks the charge status, amount, and payment method used.

**Key Fields:**  
- Foreign keys to `User` and `Order`  
- `payment_date`, `amount`  
- `status` (paid, failed)  
- `payment_method` (e.g. Stripe)

---

### PaymentProfile
**Purpose:**  
Stores safe, reusable Stripe metadata for a user’s saved payment method.  
Used to power recurring billing and display masked card info.

**Key Fields:**  
- Stripe IDs for customer and payment method  
- `last4`, `brand`, `exp_month`, `exp_year`

---



##  [UX](#ux)
##  [Colour Palette](#colour-palette)
##  [Typography](#typography)
##  [Images](#images)
##  [Icons](#icons)
##  [Features](#features)
