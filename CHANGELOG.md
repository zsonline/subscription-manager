# Changelog

## Version 1.0

### New

- User accounts can be created.
- Users can authenticate themselves through tokens, which are sent via email.
- Subscriptions can be created.
- Subscription addresses can be updated.
- Subscriptions can be canceled.
- The payment status and information with regard to a subscription is shown.
- Django's admin application is used for maintenance. Payments can be manually confirmed, which activates a subscription. Active subscriptions can be exported as a .csv file. 


## Version 1.1

### New

- Emails are sent asynchronously with celery and redis.

### Changed

- Scss files are now compiled with django-compressor instead of gulp. Hence, Node.js and all node modules have been removed as dependencies.


## Version 2.0

This release is not backwards compatible. It does not include the necessary database migrations.

### New

- The user interface has been overhauled with focus on simplicity and code clarity.
- Users can add multiple email adresses, which can be verified independently. A primary email address is used for user authentication and email correspondence. Email addresses are stored in a separate database table.
- Subscription plans support new options such as: `is_purchasable`, `is_renewable`, `eligible_active_subscriptions_per_user`, and `eligible_email_domains`.
- A dedicated management page simplifies common management tasks: Payments can be easier confirmed and active subscriptions can be exported with just one click.

### Changed

- The database has been remodeled in order to support subscription renewals. Subscription periods are now stored in their own database table.
- Tokens can now be used for multiple purposes such as user login and email verification.
- The admin interface has been improved such that the data can be easier modified and exported.

## Version 2.1

### New

- A statistics overview has been added to the management pages. The charts depict the amount of active subscriptions, the changes in subscription numbers, and the number of renewed subscriptions over time.