# Ultimate Sound
### Video Demo: https://youtu.be/BvPspiwje00
### Description:

#BACKGROUND
--Models.py 
In models.py, the databases are defined. Users contains three columns: id, name, and password_hash;
this table manages the website's users. Transaction contains 5 columns: id, product_id, user_id, price, and date.
Finally, the icing on the cake, Products, contains 6 columns: id, name, price, stock, image_link, and description. 
I believe all columns content are self-explanatory.

--Helpers.py 
It contains helper functions that I placed here to keep everything more organized:
-login_required: facilitates the requirement of a user account.
-admin_required: ensures that only the admin has the possibility to access, adding an extra security step.
-first_letter: used only for a Jinja filter that returns the first letter of a username for a dynamic profile picture.
-addToCart: allows adding products to the cart and, if they already exist, changes the current quantity.
-search: used to make it easier from the HTML, when necessary, to look up information about a given product using only its id, which is almost always present.
-lookup_picture: connects to googleapis to search for an image based on a product name; if there is none or Google returns an error, it creates a placeholder.

--Info 
Ultimate Sound is an e-commerce type website for a fictional online store selling audio and music-related products. It was always thought of as an e-commerce 
site from the very beginning, later taking more shape to become what it is today.

#THE LAYOUT
In layout, we have Bootstrap scripts and links because it was simple enough and served well for these basic parts of the page. It also features a navbar,
which is a Bootstrap component consisting of the "Ultimate Sound" logo and, depending on your device size, two links: one to Home ("/") and another to 
Store ("/store"), plus a dropdown with options to log in /register or, if already registered, your username and the log-out option. It also has the cart, 
which shows all items in session["cart"], allows clearing the cart, and proceeding to checkout. In layout, we have asynchronous functions that allow fetching 
and changing information from the backend, such as show_cart(), which gets the products added to the cart for display, or productQuantity(), which allows 
changing the quantity the user wishes to buy of an item or product directly from the cart. It has a simple footer showing a "company watermark" and direct 
links to Home and Store.

#INDEX
Index contains an image carousel where the first slide is a sort of tribute to CS50 for the very good personal experience I've had, even though I started a bit
late; it contains the CS50 banner and a welcome to the page. The second image is generated dynamically according to the most recently added items or products, 
along with text prompting the user to buy or press the ever-present "Call to action." The third one is generated automatically in the same way but with the 
top-selling products. For the second image, I performed a "SELECT" on the database tables, selecting the products' dates, converting them into a more workable 
date format instead of text, and selecting the most recently added ones according to the current month. For the third one, it was quite challenging: a SELECT 
of the products is performed, followed by a subquery that counts the purchase frequency of distinct products and returns the product IDs, which are then 
selected in the main query. Next, we move to a small introduction section of the page. It is a simple responsive grid that shows a 1fr 2fr layout on devices 
wider than 900px, and on smaller devices, for better comfort on tablets and mobile, it shows only 1fr. It is a text with the essence of the brand and an image 
simulating spatial audio waves to match the text. Afterward, we have a small form for a newsletter subscription (purely decorative for this project. For 
convenience, I did not find it appropriate to create a weekly newsletter that would send AI-generated spam to the staff or anyone testing the page every two or 
three weeks), which features an email input and a simple button to submit the form.

#STORE
Store has the features I had the most fun making. First, a banner that changes using only CSS @keyframes, switching from "Ultimate" to "Store." Then we have 
the products; all of them are contained within a div and are automatically generated with Jinja, which fetches all the information from the Products table in 
the database via app.py. With the addToCart function and the backend API, the system can detect if an inexistent product is maliciously introduced to crash 
the server and prevents it; if the id is valid and the frontend sends it via POST, the product is added to the cart. This function will build the products in 
the cart and is defined in layout.html.

#LOGIN
I used some of the logic behind CS50 Finance. All traces of the session are cleared, then the input validity is verified—whether it is an attack, a typo, or 
invalid, the backend detects and prevents it. Then it performs a "SELECT" of the user and verifies if one exists with that name; if so, it checks if the 
password the user entered matches the hash of that password using werkzeug.security functions. If it doesn't exist or there is an error, it returns error.html; 
otherwise, it starts the session. The frontend is very simple, just a traditional input form and a link to /register. This function also detects if the values 
entered belong to the special "admin" user, redirecting there if so.

REGISTER
This part allows a user to create a new account with their name and password. Just like in login, the backend checks if all input is correct; if so, it 
performs an "INSERT" into the database, adding a new user to Users with this username and a hash of the password, which is hashed in the backend. Usernames 
are unique, so if any field is left blank, is incorrect, or the user already exists, it returns an error. The frontend features a form to enter the name, 
password, and password verification, as well as a link to log in.

#ADMIN
--As requested for the template, the base was generated by AI; I clarify that it did not significantly influence the progress of this section, but most visual 
styles were generated. Admin is the part hidden from the user, accessible only with administrator credentials: username: "Admin" password: "admin12345678". 
The page is designed by panels. The first is the dashboard or general panel, showing business-related data such as lifetime sales, how many users are subscribed, 
and total earnings, as well as a functional graph where the backend from /admin sends a list of 12 spaces (one for each month) and the frontend detects and 
displays the information. The second panel is inventory or stock; this has a table showing all current products in the database and allows adding, editing, and 
deleting products via /admin/manage. The third panel is a list of all transactions made on the site. Elements are generated with data on who made the transaction, 
the value, the ID, and the date. It serves for monitoring data. The last panel is the customers' panel, showing a list generated like the transactions with 
information managed from the backend, consisting of selecting everything from everything—meaning all elements from all tables in the database.

#ADMIN-MANAGE
Admin manage is a sub-link of admin, specialized in managing the input to be sent to the database. It starts with a section to select the action to be performed, 
then redirects to the corresponding form. If adding a product, a form is shown to enter all Product values; these are verified and sent to the DB. The helper 
function lookup_picture() plays an important role here: using a Google Image Search API, providing a functional link for products becomes completely unnecessary. 
lookup_picture goes to googleapis/customsearch/v1 with my credentials (you may use them as you wish, I give my consent as long as it is used by the staff and CS50), 
and it returns a link to the best image it could find for the product. If there is a Google error, it returns a placeholder; due to payment limitations, if the 
daily free requests are exhausted, a placeholder will also be sent. All registered inputs are saved in the DB and ready to use throughout the application for efficiency sake, and 
the links generated by lookup_picture are saved so Google is only queried once. If the action is "remove," for security reasons (if this were a functional site 
with real staff), not everyone should freely delete from the DB directly, so the administrator password is required and a select menu allows for easy selection 
of the product to delete. "Edit" is a mix of both; it has a select menu to choose the product to edit but includes inputs to allow changes. Blank inputs and 
whitespace are ignored by the server and do not edit those parts of the product.

#CHECKOUT
Checkout allows the user to go home happy. If the cart is empty and they attempt to proceed with the purchase, an error is sent. Otherwise, the products in 
the cart are shown with essential information as well as a background photo to give a notion of what is being bought if the user doesn't remember. Below is 
the form to proceed with payment; I only created a verifier, not a real payment process, because, like the newsletter, it is unnecessary and could cause issues 
with applications like PayPal in a development server environment. If everything is correct, the user is redirected to Index.

In templates, all the used templates are located, and in static, some extra styles are found, as most of the time the styling was applied with a framework, either 
Bootstrap or Tailwind or directly with style="" within the HTML for better specificity and to avoid conflicts with the frameworks.