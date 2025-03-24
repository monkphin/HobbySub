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

- Provide a secure and scalable e-commerce platform to sell products or services.
- Allow users to easily browse, purchase, and manage orders with minimal friction.
- Offer subscription or one-off purchasing options (depending on the product model).
- Maintain full control over product listings, order fulfillment, and customer data.
- Ensure a professional, responsive, and accessible user interface across all devices.
- Integrate a secure payment system (e.g. Stripe) that complies with best practices.
- Maintain separation between regular users and admin-level features for security.
- Provide clear documentation and error handling to reduce customer support needs.
- Deploy and maintain the site using cloud-based infrastructure for high availability.

## Visitor Goals

- Easily browse the product or service catalog by category, search, or filters.
- View detailed product or service information before making a purchase.
- Create an account to track orders, save preferences, and manage personal info.
- Add items to a cart or subscription and complete secure checkout quickly.
- Receive confirmation and updates on order/payment status via email.
- View order history and track current orders from their account dashboard.
- Interact with an reactive, mobile-friendly design that’s easy to navigate.
- Trust that their data is secure, and payments are processed safely.
- Receive support or help if issues arise with orders or payments.
- Use accessibility features such as keyboard navigation and screen reader compatibility.


[My MoSCoW board can be found here](https://github.com/users/monkphin/projects/3/views/1)

[My Kanban board can be found here](https://github.com/users/monkphin/projects/1)

# User Stories
| **Category**                | **User Story**                                                                                      |
|----------------------------|------------------------------------------------------------------------------------------------------|
| Authentication & Permissions | As a user, I want to register and log in securely so I can access my account and manage my purchases. |
|                            | As a logged-in user, I want to access my profile and order history, but not see admin pages or other users' data. |
|                            | As a logged-in user, I want to update my account information (e.g., address, email) so that I can ensure receipts and shipments are sent to me. |
|                            | As an admin, I want to restrict critical actions (like product creation or order editing) to admin users only. |
| Products and Browsing      | As a user, I want to browse all available products or services so that I can choose one that fits my needs. |
|                            | As a user, I want to view details about a product or service (e.g., description, price, availability) so I can make informed decisions. |
|                            | As an admin, I want to create, edit, and delete products/services in the catalog so I can manage the offering. |
| Cart & Checkout            | As a user, I want to add one or more products to my cart so that I can review them before checkout. |
|                            | As a user, I want to edit the quantity or remove items from my cart so that I can adjust my order before paying. |
|                            | As a user, I want to securely check out and pay using an online payment system (e.g. Stripe) so that I can complete my purchase. |
|                            | As a user, I want to see a clear message confirming whether my payment was successful or not. |
| Orders & Post-Purchase Flow | As a user, I want to see my order history in my account so that I can track what I’ve bought or subscribed to. |
|                            | As an admin, I want to see and manage all customer orders so I can fulfill them or troubleshoot issues. |
|                            | As a user, I want to receive an email confirmation with my order summary so that I know it was processed. |
| Testing and Reliability    | As a developer, I want to write tests for forms, models, and views so that I can confirm the application works correctly at all times. |
|                            | As a developer, I want to follow a TDD approach so I can build out functionality reliably and document my process through git commits. |
|                            | As a tester, I want to simulate common failure cases (e.g. payment failure, missing input) so I can confirm the app handles errors gracefully. |
| UX and Accessibility       | As a user, I want to easily navigate the site using a clear, accessible layout so that I can find what I need without confusion. |
|                            | As a user, I want the site to provide clear feedback after every interaction (e.g., forms, purchases) so that I know what happened. |
|                            | As a user, I want all interactive elements to be accessible via keyboard and screen readers so that I can use the site regardless of ability. |
| Admin & Configuration      | As an admin, I want to manage product data and orders via a dashboard so that I can keep the store up to date. |
|                            | As a developer, I want to keep all configuration in environment variables so that I can deploy securely and easily switch between environments. |
|                            | As a developer, I want to ensure no secret data is ever committed to Git so that the app stays secure. |
| Documentation & Deployment | As a developer, I want to document all stages of the project in a well-structured README so that the development process is clear. |
|                            | As a reviewer, I want to see a data schema and system architecture diagram so that I can understand the app’s structure quickly. |
|                            | As a tester, I want to follow a documented deployment and testing process so that I can verify everything works as expected. |

# Design Choices

## [Wireframes](#wireframes)
##  [Schema](#schema)
##  [UX](#ux)
##  [Colour Palette](#colour-palette)
##  [Typography](#typography)
##  [Images](#images)
##  [Icons](#icons)
##  [Features](#features)
