# **HobbySub Testing**
 
<details>
<summary>Table of Contents</summary>
[Testing and Validation](#testing-and-validation)
 
 - [Usage Based Functionality Testing](#usage-based-functionality-testing)
 - [Bugs, Issues and challenges](#Bugs-issues-and-challenges) 
 - [Unresolved Bugs](#unresolved-bugs)
 - [HTML Validation](#html-validation)
 - [CSS Validation](#css-validation)
 - [Accessibility](#accessibility)
 - [Performance](#lighthouse-performance-testing)
 - [User Testing](#user-testing)
 -- [Success](#success)
 -- [Partial](#partial)
 -- [Failed](#failed)
 - [User Story Testing](#user-story-testing)
 - [JavaScript Testing](#javascript-testing)
 - [Python Testing](#python-testing)
 - [Device and Browser Testing](#device-and-browser-testing)
 - [Responsiveness](#responsiveness)
 - [Automated testing](#automated-testing)
</details>

# Testing and Validation

## Test Summary

| Test Type                | Status         | Notes                                                  |
|--------------------------|----------------|--------------------------------------------------------|
| Manual Function Testing  | Complete     | All key flows tested manually                          |
| HTML Validation          | Complete     | No critical errors; some cosmetic issues deferred      |
| CSS Validation           | Complete     | Custom CSS valid; 3rd-party minor issues noted         |
| Accessibility (WAVE)     | Partial      | Minor contrast issues remain                          |
| Lighthouse Audits        | Complete     | Logged-in/out tested; scores within acceptable range   |
| JavaScript (JSHint)      | Reviewed     | No blocking issues; optional chaining warning noted    |
| Python (PEP8)            | Reviewed     | Style compliant with minor deferrals noted             |
| Django Automated Tests   | 65 Passed    | All tests passed; 2 warnings (time zone + DB teardown) |
| User Story Validation    | Complete     | All stories reviewed and tested                        |


 
## Usage based functionality testing

Throughout development, I tested features and functions organically to ensure that services and systems were working and rendering correctly. This testing process was continuous and evolved naturally alongside development.
- This hands-on approach revealed a range of issues such as:
  - Stripe not linking orders correctly to users.
  - UI anomalies and display issues.
  - Non-functional buttons during certain flows.
- These issues were identified and addressed in real-time as they surfaced.
Although this method was not fully documented step-by-step, it enabled rapid identification and correction of bugs during the development process.

# Bugs, Issues and challenges 
While I have resolved many of the issues encountered during development, a few outstanding problems remain. These are currently mitigated through logging and defensive programming but are still present. Despite the automated test coverage, these bugs only manifested during hands-on, usage-based testing. making them difficult to trace.

## Unresolved Bugs 
Below are the outstanding issues I am aware of. Some of these may be resolved, but I lack the time to fully test to my satisfaction to be 100% certain. 

### Duplicate Stripe Sub IDs
- Description: 
  - Occasionally, Stripe subscription IDs are duplicated in the database.
- Mitigation:
  - Implemented atomic handling to prevent race conditions.
  - Database is configured to enforce unique constraints.
  - Extensive logging is in place to track occurrences.
- Status: 
  - Mitigated but not resolved. Current measures are seen as temporary workarounds.

### Boxes missing from Orders 
- Description:
-- In rare cases, an order (whether single or subscription) may not have a box assigned.
- Impact:
-- This also affects the shipping date, as it is pulled from the box data.
-- Extremely intermittent, making it hard to trace or replicate during testing.
- Mitigation:
-- Additional logging is present to catch these events.
-- Manual inspection of logs post-order creation is required.
- Status: Unresolved. Root cause still unknown.

### Gifts not always being marked as Gifts. 
- Description: 
  - Subscription gifts are sometimes not flagged as gifts in the front end.
- Likely Cause:
  - Suspected to be a race condition during database writes.
  - May be linked to the issues with subscription ID duplication.
- Mitigation:
  - Adjusted how data is written to the DB for gift orders.
  - Implemented additional checks post-write.
- Status: 
  - Believed to be resolved but marked as outstanding due to lack of final testing.

### Email duplication. 
- Description: Emails occasionally send twice for a single event trigger.
- Likely Cause:
  - Potentially linked to the race conditions affecting subscription ID handling.
- Mitigation:
  - Adjusted event handling logic.
  - Added checks to prevent duplicate sends.
- Status: Believed to be resolved but left marked as outstanding pending further testing.

### Page rendering issues
- Description:
  - On some pages containing <textarea> fields, resizing the browser window can cause the content to visually compress or wrap incorrectly. I have specifically seen this on the Add/Edit Box and Add/Edit Products pages, since they're fundamentally the same underlying form.  
- Likely Cause:
  - Interaction between MaterializeCSS’s layout model and how certain browsers recalculate textarea dimensions during dynamic resizing. May also relate to how unbroken content is handled during flex/grid reflow.
- Mitigation:
  - Isolated the issue to a specific block of HTML.
  - Applied multiple responsive CSS overrides (width, box-sizing, overflow-wrap) — these were later removed as they did not resolve the underlying issue and caused side effects, particularly with the admin dropdown menu.        Removed Materialize’s textareaAutoResize() to avoid conflicting JS behaviour.
- Status:
  - Unresolved. Non-blocking and cosmetic only. A full fix was deprioritised due to time constraints. Reloading the page resolves the issue consistently. No impact on usability or form submission.

### Toasts for updating box contents showing 0
- Description:
  - When assigning orphaned products to a box via the box_products.html page, the form posts successfully, but no checkbox data (product_ids) is received in request.POST.
    - Observed Behavior:
      - The checkboxes render correctly and allow selection.
      - Submitting the form (via the “Assign to Box” button) redirects as expected.
      - However, the server logs consistently show:
        ```
        request.POST.getlist('product_ids') == []
        ```
    - Resulting message:
      - "0 products successfully added to 'BoxName'."
    
- Expected Behavior:
  - Checkboxes for selected orphaned products should be submitted as product_ids in the POST data, and the selected products should be reassigned to the specified box.
    - Confirmed Factors:
      - HTML inputs are correctly named: <input type="checkbox" name="product_ids" value="{{ product.id }}">.
      - CSRF token is present and accepted.
      - No errors or warnings in the browser console.
      - JS disables the submit button on form submission for UX, but this should not block form data unless it fires too early.
- Next Steps / Logging:
  - Issue remains unresolved. No workaround has been applied yet. Will revisit this after higher-priority tasks or consider commenting out the form submit button disable temporarily for confirmation testing.

### Code Formatting Rollback Notice

During final cleanup, HTML and Python files were auto-formatted using Prettier and Flake8 to improve consistency and readability. However, the HTML formatting step introduced layout-breaking issues due to aggressive reflowing of template logic and whitespace-sensitive tags. Due to time constraints and the risk of introducing bugs just before submission, this change was rolled back via Git revert to ensure site stability.

The current templates remain functional and readable, though not fully Prettier-compliant. Formatting improvements will be considered as part of a future release cycle, once automated formatting can be safely aligned with Django template requirements.

## Refactoring and DRY 
Throughout development, I attempted to adhere to DRY (Don't Repeat Yourself) principles wherever possible, aiming to minimise code duplication and improve maintainability. Sadly, in a bit of a rush to clean up the front end towards the end of the project things got a bit out of hand with the CSS file. This is something that I plan to revisit and clean up in the future. 

### Template Reuse
The front-end leverages a modular design, with reusable templates for common elements and page structures.
- Purchase Flows: Both Buy for Myself and Gift Purchase use shared templates, only differing where necessary for specific logic.
- Address Management: Adding, editing, and managing addresses all use the same form template with conditional rendering.
- Modals: Password protection and confirmation modals are standardised across different views, reducing redundancy.
- Various other functions and pages however do have DRY methodology in mind, with a lot of the front end re-using the same templates where possible. 
 
### Backend Structure and Refactoring Needs
During development, I created stripe_handlers.py as a way to break up growing logic blocks into more manageable pieces.
- This file currently handles the bulk of Stripe integration logic, particularly the handle_checkout_session_completed function.
- Known Issue:
  - This function now makes up around two-thirds of the entire file, and is a primary candidate for refactoring.
  - Its complexity grew during the investigation and debugging of issues like race conditions and duplicate IDs.

I acknowledge that further refactoring is required, particularly for:
- Breaking out smaller logic components to streamline handle_checkout_session_completed.
- Improving readability and debugging efficiency by separating concerns into distinct methods.
- Aligning with SRP (Single Responsibility Principle) to make future maintenance easier.

Despite this, many other parts of the application were developed with DRY principles firmly in mind. The structure is designed to be modular and efficient, even if a few key areas still need rework.


## Debounce Implementation for Form Submission
To attempt to address the issue of duplicate Stripe Subscription IDs, I implemented a site-wide debounce mechanism on all forms.

- Purpose of Debounce
  - Prevent Double Submissions: If a button is clicked multiple times in quick succession, debounce logic prevents the form from submitting multiple times.
  - Reduce Duplicate Database Writes: This is particularly important for Stripe subscriptions, where race conditions can lead to multiple subscription IDs being generated.

- Outcome
  - While the debounce did reduce the chances of form duplication, it did not completely resolve the Stripe subscription ID issue.
  - Despite this, I chose to retain the debounce functionality because:
   - It did improve stability across form submissions.
   - It prevented other forms from experiencing double entries, which was a sporadic issue before debounce was applied.

This was part of a wider effort to control input behaviour across the platform, and while not a full solution, it represented a step toward greater stability and control.

## Validation
All validation and accessibility testing was carried out manually using browser-based tools and validator services. Due to the nature of Django-based dynamic rendering and user-specific content behind authentication gates, most testing was done by viewing the rendered page source and manually validating the output.

### Tool Usage Balance:
Lighthouse testing was conducted across a wide range of pages and received the most focus, as it provided actionable feedback on performance, accessibility, and SEO in one go.

WAVE and W3C HTML validation were used more selectively — primarily on form-heavy or complex pages to confirm structure and accessibility. This approach was intentional due to time constraints and the dynamic nature of Django-rendered pages.

The aim was to ensure all core flows were tested with at least one tool, and all major layout or interaction patterns were covered. Not every page was tested with every tool, but representative samples were chosen to surface recurring issues, particularly since there was a lot of re-use of HTML and over multiple pages. 

### HTML Validation
Raw HTML was validated using the [W3C Markup Validation Service](https://validator.w3.org/). As Django renders pages dynamically and includes authenticated content, page source HTML was copied and pasted directly into the tool for validation.
- Critical issues (e.g., malformed elements, missing attributes) were corrected immediately.
- Warning/Minor or cosmetic issues (e.g., redundant attributes or non-breaking semantic tags) were noted but deferred to a future development cycle due to time constraints. Since the HTML included the contents of base.html, some of the warnings appear over all pages, since this is a common page throughout the site. 

The results of this are below. 

<details>
<summary>Index Page</summary>
  <img src="docs/testing/w3schools/index.png">
</details>
<br>

<details>
<summary>Registration Page</summary>
  <img src="docs/testing/w3schools/register.png">
</details>
<br>

<details>
<summary>Login Page</summary>
  <img src="docs/testing/w3schools/login.png">
</details>
<br>


<details>
<summary>Past Boxes Page</summary>
  <img src="docs/testing/w3schools/past-boxes.png">
</details>
<br>


<details>
<summary>Past Box Contents Page</summary>
  <img src="docs/testing/w3schools/past-box-content.png">
</details>
<br>

<details>
<summary>Purchase Selection Page</summary>
  <img src="docs/testing/w3schools/purchase-select.png">
</details>
<br>

<details>
<summary>Address Selection Page</summary>
  <img src="docs/testing/w3schools/order-address-select.png">
</details>
<br>

<details>
<summary>Order Cancel Page</summary>
  <img src="docs/testing/w3schools/order-cancel.png">
</details>
<br>

<details>
<summary>Order Complete Page</summary>
  <img src="docs/testing/w3schools/order-complete.png">
</details>
<br>

<details>
<summary>Gift Message Page</summary>
  <img src="docs/testing/w3schools/gift-message.png">
</details>
<br>

<details>
<summary>My Account Page</summary>
  <img src="docs/testing/w3schools/account-page.png">
</details>
<br>

<details>
<summary>Account Password Change</summary>
  <img src="docs/testing/w3schools/account-password.png">
</details>
<br>

<details>
<summary>Account Edit Page</summary>
  <img src="docs/testing/w3schools/account-edit.png">
</details>
<br>

<details>
<summary>Account Orders Page</summary>
  <img src="docs/testing/w3schools/account-orders.png">
</details>
<br>

<details>
<summary>Box Admin Page</summary>
  <img src="docs/testing/w3schools/box-admin.png">
</details>
<br>

<details>
<summary>Box Admin Editor Page</summary>
  <img src="docs/testing/w3schools/box-edit.png">
</details>
<br>

<details>
<summary>Box Admin Product Page</summary>
  <img src="docs/testing/w3schools/box-products.png">
</details>
<br>

<details>
<summary>Box Admin Product Editor Page</summary>
  <img src="docs/testing/w3schools/box-product-editor.png">
</details>
<br>

<details>
<summary>Box Admin Assign Products Page</summary>
  <img src="docs/testing/w3schools/box-assign-products.png">
</details>
<br>

<details>
<summary>Box Admin Remove Product Page</summary>
  <img src="docs/testing/w3schools/box-remove-product.png">
</details>
<br>

<details>
<summary>User Admin Page</summary>
  <img src="docs/testing/w3schools/user-admin.png">
</details>
<br>

<details>
<summary>User Admin Edit Page</summary>
  <img src="docs/testing/w3schools/user-edit.png">
</details>
<br>

<details>
<summary>User Admin Orders Page</summary>
  <img src="docs/testing/w3schools/user-orders.png">
</details>
<br>

### CSS Validation
The CSS was validated using the [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/). This included checking the main stylesheet and any custom overrides.
- No CSS syntax issues were found with my own CSS. 
- External CSS such as that provided by Materialize did have a few errors. 

<details>
<summary>CSS Results</summary>
  <img src="docs/testing/w3schools/css.png">
</details>
<br>

### Accessibility
Accessibility was assessed using the WAVE Chrome plugin, which checks for WCAG compliance and general usability for assistive technologies.
- Some form labels have contrast ratios below optimal thresholds, which could impact visibility for users with visual impairments. These are noted for revision in a future UI pass. 

<details>
<summary>Index Page</summary>
  <img src="docs/testing/wave/index.png">
</details>
<br>
 
<details>
<summary>Past Boxes Page</summary>
  <img src="docs/testing/wave/pastboxes.png">
</details>
<br>

<details>
<summary>Past Box Items Page</summary>
  <img src="docs/testing/wave/pastboxitems.png">
</details>
<br>

<details>
<summary>Purchase Selection Page</summary>
  <img src="docs/testing/wave/order-choose-box.png">
</details>
<br>

<details>
<summary>Purchase Choose Address Page</summary>
  <img src="docs/testing/wave/order-choose-address.png">
</details>
<br>

<details>
<summary>Purchase Gift Message Page</summary>
  <img src="docs/testing/wave/order-gift-message.png">
</details>
<br>

<details>
<summary>Account Page</summary>
  <img src="docs/testing/wave/account.png">
</details>
<br>

<details>
<summary>Account Edit Page</summary>
  <img src="docs/testing/wave/account-edit.png">
</details>
<br>

<details>
<summary>Account Password Change Page</summary>
  <img src="docs/testing/wave/password-form.png">
</details>
<br>

<details>
<summary>Account Order History Page</summary>
  <img src="docs/testing/wave/account-order-history.png">
</details>
<br>

<details>
<summary>Account Edit Address</summary>
  <img src="docs/testing/wave/edit-address.png">
</details>
<br>

<details>
<summary>Box Admin Page</summary>
  <img src="docs/testing/wave/box-manager.png">
</details>
<br>

<details>
<summary>Box Admin Add Box Page</summary>
  <img src="docs/testing/wave/add-box.png">
</details>
<br>

<details>
<summary>Box Admin Edit Box Page</summary>
  <img src="docs/testing/wave/edit-box.png">
</details>
<br>

<details>
<summary>Box Admin Box Contents Page</summary>
  <img src="docs/testing/wave/box-contents.png">
</details>
<br>

<details>
<summary>Box Admin Edit Product</summary>
  <img src="docs/testing/wave/edit-product.png">
</details>
<br>

<details>
<summary>Box Admin Reassign Products</summary>
  <img src="docs/testing/wave/reassign-products.png">
</details>
<br>

<details>
<summary>Box Admin Remove Product</summary>
  <img src="docs/testing/wave/remove-product.png">
</details>
<br>

<details>
<summary>User Manager</summary>
  <img src="docs/testing/wave/user-manager.png">
</details>
<br>

<details>
<summary>User Order History</summary>
  <img src="docs/testing/wave/user-orders.png">
</details>
<br>

### Lighthouse Performance Testing
Performance and accessibility were further assessed using Lighthouse in Chrome DevTools.
- Each page was tested for performance, accessibility, best practices, and SEO.
- Focus was placed primarily on performance scores, given the heavy use of images and Stripe integrations.
- Results varied slightly by page — this is expected due to dynamic content and external dependencies (e.g., Stripe, Cloudinary).
- SEO scores were significantly lower on pages that require user login or admin access. While this might appear negative at first glance, it's actually a positive outcome; private content should not be indexed by search engines. The low visibility of these pages confirms that access restrictions are working as intended. 
- Similarly, publicly accessible error pages (e.g. 404, 500) also scored low. This is also a desirable result, as such pages should not rank highly or appear in search results.

#### Logged Out

<details> 
<summary>Index Page (Logged Out)</summary> 
    <img src="docs/testing/lighthouse/index-loggedout.png"> 
</details> 
<br> 

<details> 
<summary>About Page (Logged Out)</summary> 
    <img src="docs/testing/lighthouse/about-loggedout.png"> 
</details> 
<br> 

<details> 
<summary>Register Page</summary> 
    <img src="docs/testing/lighthouse/register.png"> 
</details> 
<br> 

<details> 
<summary>Login Page</summary> 
    <img src="docs/testing/lighthouse/login.png"> 
</details> 
<br> 

<details> 
<summary>Past Boxes Page (Logged Out)</summary> 
    <img src="docs/testing/lighthouse/pastboxes-loggedout.png"> 
</details> 
<br> 

<details> 
<summary>Past Box Contents Page (Logged Out)</summary> 
    <img src="docs/testing/lighthouse/pastboxes-content-loggedout.png"> 
</details> 
<br>

#### Logged In

<details> 
<summary>Index Page (Logged In)</summary> 
    <img src="docs/testing/lighthouse/index-loggedin.png"> 
</details> 
<br> 

<details> 
<summary>About Page (Logged In)</summary> 
    <img src="docs/testing/lighthouse/about-loggedin.png"> 
</details> 
<br> 

<details> 
<summary>Past Boxes Page (Logged In)</summary> 
    <img src="docs/testing/lighthouse/pastboxes-loggedin.png"> 
</details> 
<br> 

<details> 
<summary>Past Box Contents Page (Logged In)</summary> 
    <img src="docs/testing/lighthouse/pastboxes-content-loggedin.png"> 
</details> 
<br> 

<details> 
<summary>Self Plan Selection Page</summary> 
    <img src="docs/testing/lighthouse/selfplan-loggedin.png"> 
</details> 
<br> 

<details> 
<summary>Self Plan - Address Selection</summary> 
    <img src="docs/testing/lighthouse/selfplan-address-loggedin.png"> 
</details> 
<br>

<details> 
<summary>Gift Purchase Page</summary> 
    <img src="docs/testing/lighthouse/giftpurchase-loggedin.png"> 
</details> 
<br> 

<details> 
<summary>Gift Purchase - Shipping Page</summary> 
    <img src="docs/testing/lighthouse/giftpurchase-shipping.png"> 
</details> 
<br> 

<details> 
<summary>Gift Message Page</summary> 
    <img src="docs/testing/lighthouse/gift-message.png"> 
</details> 
<br> 

<details> 
<summary>Cancelled Order Page</summary> 
    <img src="docs/testing/lighthouse/cancelledorder.png"> 
</details> 
<br> 

<details> 
<summary>Successful Order Page</summary> 
    <img src="docs/testing/lighthouse/successfulorder.png"> 
</details> 
<br> 

<details> 
<summary>Account Page</summary> 
    <img src="docs/testing/lighthouse/account-loggedin.png"> 
</details> 
<br> 

<details> 
<summary>Order History Page</summary> 
    <img src="docs/testing/lighthouse/account-orderhistory.png"> 
</details> 
<br> 

<details> 
<summary>Address Form Page</summary> 
    <img src="docs/testing/lighthouse/addressform.png"> 
</details> 
<br> 

<details> 
<summary>Edit Account Page</summary> 
    <img src="docs/testing/lighthouse/editaccount.png"> 
</details> 
<br> 

<details> 
<summary>Password Reset - Form Page</summary> 
    <img src="docs/testing/lighthouse/passwordreset-form.png"> 
</details> 
<br> 

<details> 
<summary>Password Reset - Email Sent Page</summary> 
    <img src="docs/testing/lighthouse/passwordresetemail.png"> 
</details> 
<br> 

<details> 
<summary>Password Reset - Confirm Email Page</summary> 
    <img src="docs/testing/lighthouse/passwordresetemailconfirm.png"> 
</details> 
<br>

<details> 
<summary>Password Reset - Complete Page</summary> 
    <img src="docs/testing/lighthouse/passwordresetemailcomplete.png"> 
</details> 
<br> 

<details> 
<summary>Box Admin Add Box Page</summary> 
    <img src="docs/testing/lighthouse/addbox.png"> 
</details> 
<br> 

<details> 
<summary>Box Admin Edit Box Page</summary> 
    <img src="docs/testing/lighthouse/editbox.png"> 
</details> 
<br> 

<details> 
<summary>Box Admin Add Product Page</summary> 
    <img src="docs/testing/lighthouse/addproduct.png"> 
</details>
<br> 

<details> 
<summary>Box Admin Edit Product Page</summary> 
    <img src="docs/testing/lighthouse/editproduct.png"> 
</details> 
<br> 

<details> 
<summary>Box Admin Assign Product to Box Page</summary> 
    <img src="docs/testing/lighthouse/assignproduct.png"> 
</details> 
<br> 

<details> 
<summary>Box Admin Box Contents Page</summary> 
    <img src="docs/testing/lighthouse/boxcontents.png"> 
</details> 
<br> 

<details> 
<summary>Box Admin Page</summary> 
    <img src="docs/testing/lighthouse/boxmanager.png"> 
</details> 
<br> 

<details> 
<summary>User Admin Page</summary> 
    <img src="docs/testing/lighthouse/useradmin.png"> 
</details> 
<br>

<details> 
<summary>Edit User Admin Page</summary> 
    <img src="docs/testing/lighthouse/edituseradmin.png"> 
</details> 
<br> 

<details> 
<summary>User Order Admin Page</summary> 
    <img src="docs/testing/lighthouse/userorderadmin.png"> 
</details> 
<br> 

<details> 
<summary>Error Page</summary> 
    <img src="docs/testing/lighthouse/errorpage.png"> 
</details> 
<br>


### User Testing
 
#### User Story Testing
Each user story was tested and categorised as either:
- Success – Fully meets the criteria
- Partial Success – Some elements met, but not all
- Failed – Does not meet the expected outcome
A full breakdown is provided below.

## Successes 

| **User Story**                                                                                       | **Notes** |
|------------------------------------------------------------------------------------------------------|----------|
| As a user, I want to register and log in securely so I can access my account and manage my subscriptions. | Met – user data is handled by Django's auth system; passwords are hashed; users can register and log in. |
| As a logged-in user, I want to view and update my profile details (like shipping address or email). | Met – there is an account page allowing users to update email, password, and username, as well as add, remove, and edit addresses. |
| As a logged-in user, I want to access only my own data, not see admin pages or other users' info. | Met – all data access is scoped per user; admin pages require staff status to access. |
| As an admin, I want to restrict access to admin features like box creation and order management. | Met – admin-only features are protected by access control and restricted routes. |
| As a user, I want to have options for frequency of payment plans, including its price and shipping schedule. | Met – users can select from multiple subscription durations at different prices, with monthly box shipments. |
| As an admin, I want to create, edit, and remove box offerings to control what's available. | Met – admins can add, edit, and remove boxes, and manage box contents from within the admin dashboard. |
| As a user, I want to subscribe to a box for myself or gift it to someone else. | Met – users can follow either the self-purchase or gift flow using DRY-based functions and shared templates. |
| As a user, I want to see upcoming shipping dates for my subscription boxes. | Met – shipping dates are shown across the site and in the user's order history. |
| As a user, I want to securely check out and save my payment details for recurring billing. | Met – Stripe handles all payment processing; sensitive data is not stored on-site. |
| As a user, I want to see my order history so I can track previous deliveries. | Met – full order history is available per user on their account page. |
| As a user, I want to receive confirmation emails for successful orders and renewals. | Met – emails are sent on order confirmation and subscription renewal events. |
| As an admin, I want to view all orders, linked subscriptions, and user details for support or fulfillment. | Met – admins can view user orders, payment states, shipping addresses, and link directly to related Stripe records. |
| As a user, I want the site to be easy to navigate, even on mobile, so I can find what I need quickly. | Met – the site uses a simple, responsive layout with clearly placed features. |
| As a user, I want clear feedback when I complete actions (e.g., subscribing, pausing, paying). | Met – toast messages provide feedback for user and admin actions. |
| As an admin, I want to manage boxes, subscriptions, and orders via a secure dashboard. | Met – admins have access to a secure custom dashboard for managing users, boxes, products, and orders. |


#### Partial

| **User Story**                                                                                       |  **Notes**  |
| **User Story**                                                                                       | **Notes** |
|------------------------------------------------------------------------------------------------------|----------|
| As a user, I want to pause or cancel my subscription at any time. | Partially met – subscriptions can be cancelled, but the ability to pause a subscription has not been implemented. |
| As a user, I want to choose or update the shipping address for each subscription. | Partially met – users can add, edit, and remove addresses, but cannot change the address on an active subscription once created. |
| As a user, I want to see confirmation of successful or failed payments. | Partially met – payment success/failure is tracked via Stripe and displayed in user/admin views, but this has not been fully tested. |
| As a user, I want to update my payment method if my card changes. | Partially met – this should be possible via Stripe’s customer portal, but has not been fully tested in this project. |
| As a user, I want the site to support screen readers and keyboard navigation for accessibility. | Partially met – Screen reader testing was not completed due to time constraints, but semantic HTML and ARIA labels were used where feasible. |


#### Failed to meet

| **User Story**                                                                                       |  **Notes**  |
| **User Story**                                                                                       | **Notes** |
|------------------------------------------------------------------------------------------------------|----------|
| As a user, I want to browse available subscription boxes so I can choose one that suits me or someone else. | Not met – the site currently offers only a single subscription box option. |
| As a user, I want to view payment details associated with past orders (e.g., card type, last 4 digits). | Not met – this was planned but was not implemented due to time constraints. |


### JavaScript Testing
JavaScript code was tested using [JSHint](https://jshint.com/). No critical issues were identified during testing. Minor warnings were reviewed and addressed where relevant. Full results are included below.

The JSHint report showed one compatibility warning related to optional chaining, which requires ES11 support. Since modern browsers fully support this, no changes were made. Two undefined variables (M and GLOBALS) were also flagged, but these are contextually valid within the local script scope and not runtime errors. Cyclomatic complexity and function size metrics were noted but did not indicate maintainability concerns.

No unit tests were written for JavaScript as all logic was inline and minimal, primarily used for button disabling and UI/UX enhancements.

<details> 
<summary>JSHint Test Results</summary> ß
    <img src="docs/testing/jshint.png"> 
</details> 
<br>

### Python Testing
Python code was validated using the Code Institute-provided [PEP8 Compliance Checker](https://pep8ci.herokuapp.com/). All key files were tested, and any critical style or formatting issues were resolved. Minor whitespace or stylistic warnings were reviewed but de-prioritised due to time constraints.

 ### Device and Browser Testing
The site was tested across multiple platforms and screen sizes:
- Tools used: Chrome DevTools (responsive mode), and physical devices
- Devices tested on:
  - Personal Laptop (Mac OS 15.5)
  - Desktop PC with ultrawide monitor
  - Apple iPhone 15 Pro Max
  - Apple iPad Pro 13
- Browsers tested:
  - Google Chrome (primary)
  - Firefox (brief compatibility check)
  - Edge (brief compatibility check)
  - Safari (brief compatibility check)

No critical compatibility issues were found during testing.

### Responsiveness
Responsiveness was tested both locally and on the deployed Heroku version using Chrome DevTools and real device testing. Most pages adapt fluidly across a wide range of screen sizes, maintaining usability and layout integrity.

The only known exception involves the Box Create/Edit and Box Product Create/Edit pages. On window resize (especially below 992px width), the layout can become compressed or misaligned. However, this resolves on page refresh. This issue is documented in the Known Bugs section and will be addressed in a future development cycle.
 
### Automated testing
Automated testing was implemented to identify and isolate issues as they arose during development. This allowed for more efficient debugging and provided confidence that new features did not introduce regressions.

Full coverage details are available in the interactive HTML report below. This includes per-file breakdowns of which lines were tested, skipped, or missed — and provides a clear overview of test completeness across the project.

[View Coverage Report.](https://monkphin.github.io/HobbySub/htmlcov/)

This report was generated using pytest and the coverage package, and reflects the state of the project as of final testing. It confirms that:
- Core flows and views are covered
- Edge cases and error handling were included where possible
- Further improvements can be made in future iterations to expand logic-level tests and isolate concerns for deeper validation

#### Running the Tests:
To execute the test suite, the following command is used:
  ```
$ pytest --ds=hobbyhub.settings -v --color=yes

  ```
 
  ```
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
  ```

#### Test Coverage
The test suite is divided across different apps and core functionality:
- Boxes:
  - Verifies views, box detail pages, and edge cases for archived boxes.
- Dashboard:
  - Validates form handling, box creation, date updates, user admin interactions, and order status changes.
- HobbyHub:
  - Tests the email notification system, alerting logic, and utility functions for metadata management.
- Home:
  - Confirms registration form validation, password mismatch, and user creation processes.
    Orders:
        Tests Stripe subscription creation, order handling, payment management, and edge cases for race conditions during concurrent submissions.
    Users:
        Validates account views, address management, password resets, and account deletion.

A full HTML breakdown of test coverage is included in the docs/htmlcov folder of this repository and can be viewed directly [here.](https://monkphin.github.io/HobbySub/htmlcov/)

## Warnings and Notes:
The test run completed successfully with 65 tests passing and 2 warnings:
    Django Time Zone Warning:
        USE_TZ will default to True in Django 5.0.
        This is currently set to True and will require adjustment during the upgrade.
    Database Access Warning:
        During teardown, a database concurrency issue was detected:
    ```
    database "test_polar_flock_crook_753623" is being accessed by other users
    ```
    This is most likely due to overlapping sessions during concurrent test execution since I switched to using my PostGreSQL DB later into the dev cycle, since while the site was online, the site was a not a live site and I could be somewhat more destructive with the data and DB changes than I may otherwise be able to be in a true 'live' scenario. 

## Summary:
Automated tests have been vital in catching issues early and preventing regressions. The remaining warnings have been logged for review during the future development cycles.


# Known Limitations
- Only one subscription box is offered; no box selection is currently available.
- Admin features are not protected by a CSRF exemption — admins are trusted users in this version.
- Some accessibility contrast issues and ARIA gaps remain; future iterations will improve semantic clarity.
