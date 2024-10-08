import customtkinter
import tkinter as tk
from tkinter import messagebox
import json
import os
from tkinter import filedialog, messagebox
from recipe import recipe_search
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import datetime
import sqlite3

customtkinter.set_appearance_mode("dark")#light
customtkinter.set_default_color_theme("dark-blue") #green


#connecting to db
conn = sqlite3.connect('recipe_generator.db')
# Create a cursor object
cursor = conn.cursor()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Recipe Generator")
        self.current_username = None  # Store the logged-in username
        # Create a login page
        self.create_login_page()  
        # Create a user table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        #create a reviews table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            date DATE NOT NULL,
            username TEXT NOT NULL,
            recipe TEXT NOT NULL,
            rating INT NOT NULL,
            comment TEXT NOT NULL
        )
        ''')
  
    #initilaizing a dict to save all the recipes
    rec_frames = {}
    
    def insert_user_to_db(self,name, password):
        #function to insert new users to the db
        cursor.execute('''
        INSERT INTO users (name, password) VALUES (?, ?)
        ''', (name, password))
        conn.commit()
   
    def insert_review_to_db(self,date,username,recipe,rating,comment):
        #function to insert new reviews to the db
        cursor.execute('''
        INSERT INTO reviews (date,username,recipe,rating,comment) VALUES (?, ?,?,?,?)
        ''', (date,username,recipe,rating,comment))
        conn.commit()

    def create_login_page(self):
        """Create the login page."""
        self.clear_window()

        self.username_label = customtkinter.CTkLabel(self, text="Username:")
        self.username_label.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.username_entry = customtkinter.CTkEntry(self)
        self.username_entry.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.password_label = customtkinter.CTkLabel(self, text="Password:")
        self.password_label.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.password_entry = customtkinter.CTkEntry(self, show="*")
        self.password_entry.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.login_button = customtkinter.CTkButton(self, text="Login", command=self.login)
        self.login_button.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.register_button = customtkinter.CTkButton(self, text="Register", command=self.register)
        self.register_button.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

    def clear_window(self):
        """Clear all widgets from the main window."""
        for widget in self.winfo_children():
            widget.destroy()

    def login(self):
        """Validate user credentials."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        users_db = self.fetch_users_db()
        num_users=len(users_db)
        i=0
        for user in users_db:
            if username==user[1] and user[2]==password:
                self.current_username = username
                self.open_app_window()
            else:
                i+=1
        #counting to ensure we went over all users
        if i==num_users:
            messagebox.showwarning("Login Error", "Invalid username or password.")

    def set_widgets(self):
        #ceating all the widgests on the main window

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Let's find you\n the perfect recipe!", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="\nWelcome to our Recipe genrator!\n\n Here you can free search for recipes.\n Base your search on dietary\n prefrences or a specific ingrideint.\n\n Give it a try!\n\n", anchor="w")
        self.scaling_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
       # create main entry and button
        self.search_frame = customtkinter.CTkFrame(self)
        self.search_frame.grid(row=0,column=1,columnspan=3,padx=20, pady=20, sticky="nsew")
        # Configure the grid to have two columns
        self.search_frame.grid_columnconfigure(0, weight=2)  # 2 parts
        self.search_frame.grid_columnconfigure(1, weight=1)  # 1 part
        self.entry = customtkinter.CTkEntry(self.search_frame, placeholder_text="What recipes are you looking for? Try: meat, chicken,non-dairy,nut-free...")
        self.entry.grid(row=0, column=0,padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.search_button_1 = customtkinter.CTkButton(self.search_frame, fg_color="transparent", border_width=2,text="Search" ,text_color=("gray10", "#DCE4EE"),command=self.search)
        self.search_button_1.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        #set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
    
    def open_app_window(self):
        #configuring the main window
        self.clear_window()
        self.geometry(f"{1400}x{650}")
        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure((2, 3), weight=2)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure((1, 2), weight=1)
        self.set_widgets()       
    
    def search(self):
        search_string=self.entry.get()
        recipes=recipe_search(search_string)
        #in case API is maxed out you can use the saved chicken recipes to work the app
        '''with open('recipedata.json', 'r') as file:
             recipes = json.load(file)'''
        #frame to hold both recipes and recipe buttons
        self.mainframe= customtkinter.CTkFrame(self)
        self.mainframe.grid(row=1, column=1,columnspan=3, padx=20, pady=20, sticky="nsew")
        self.mainframe.grid_columnconfigure(0, weight=1)
        self.mainframe.grid_columnconfigure(1, weight=1)
         # Create a frame to hold the recipe list (left side)
        recipe_list_frame = customtkinter.CTkFrame(self.mainframe)
        recipe_list_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        #canvas to show recipes
        self.canvas = customtkinter.CTkCanvas(self.mainframe,bg="#404040")
        self.canvas.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
         # Create a scrollbar
        scrollbar = customtkinter.CTkScrollbar(self.mainframe, orientation='vertical', command=self.canvas.yview)
        scrollbar.grid(row=0, column=2, sticky='nsew')#'ns')
        # Configure the canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        # Create a frame inside the canvas
        scrollable_frame = customtkinter.CTkFrame(self.canvas)
        # Create a window in the canvas to hold the scrollable frame
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        # Update scroll region
        def update_scroll_region(event):
             self.canvas.configure(scrollregion=self.canvas.bbox('all'))

        scrollable_frame.bind('<Configure>', update_scroll_region)
        # Create a frame to hold the buttons
        self.buttons_frame = customtkinter.CTkFrame(self)
        self.buttons_frame.grid(row=2, column=1,columnspan=3, padx=20, pady=20, sticky="nsew")
        # Configure columns to have equal weight
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        self.buttons_frame.grid_columnconfigure(2, weight=1)    
        for i in range(len(recipes)):
            self.rec_name=recipes[i][0]
            button_rec_name=recipes[i][0]
            recipe='\n'.join(map(str, self.split_by_spaces(recipes[i], 65)))
            cleaned_recipe = re.sub(r"<.*?>", "", recipe)
            self.rec_frames[self.rec_name] = cleaned_recipe
            recipe_button = customtkinter.CTkButton(recipe_list_frame, text=button_rec_name, command = lambda name=button_rec_name: self.button_click(scrollable_frame, name))
            recipe_button.grid(padx=10, pady=5,sticky="nsew")
        #creating the buttons
        self.save_button = customtkinter.CTkButton(self.buttons_frame, text="Save Content", command = self.on_save_button_click)
        self.save_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.open_email_window_button = customtkinter.CTkButton(self.buttons_frame, text="Email Recipe", command = self.open_email_window)
        self.open_email_window_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.reviews_rating_button = customtkinter.CTkButton(self.buttons_frame, text="Ratings and Reviews",command = self.open_review_window)
        self.reviews_rating_button.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        #getting the first recipe to display
        self.update_content(scrollable_frame,self.rec_frames.get(recipes[0][0]))
        self.rec_name=recipes[0][0]

    def update_content(self,scrollable_frame, content):
        # Clear existing content
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        label = customtkinter.CTkLabel(scrollable_frame, text=content)
        label.grid(row=1, column=0,sticky='w', padx=10, pady=20)
    
    def button_click(self,scrollable_frame, recipe_name):
        #updating to the current recipe on display
        self.rec_name=recipe_name
        self.update_content(scrollable_frame, self.rec_frames.get(recipe_name))
    
    def save_file_with_header(self,content, filename):
        #saving recipe localy to your PC
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                                            initialfile=filename)
        if file_path:
            with open(file_path, 'w') as file:
                # Write the filename as the first line followed by the content
                file.write(filename + "\n\n" + content)

    def on_save_button_click(self):
            # Extract text from the selected frame
            content = self.rec_frames[self.rec_name]
            # Use the recipe name as the filename for demonstration
            filename = self.rec_name +".txt"
            # Save the content with the filename as the header
            self.save_file_with_header(content, filename)
  
    def split_by_spaces(self,input_list, max_length=50):
        #splitting parts of the recipe that are too long to show on the scrolling frame
        result = []
        for item in input_list:
            if len(item) > max_length:
                # Split the item into words
                words = item.split()
                current_chunk = ""
                
                for word in words:
                    # Check if adding the next word exceeds the max_length
                    if len(current_chunk) + len(word) + 1 > max_length:
                        # Append the current chunk to the result
                        result.append(current_chunk.strip())
                        # Start a new chunk with the current word
                        current_chunk = word
                    else:
                        # Add the word to the current chunk
                        if current_chunk:
                            current_chunk += " "
                        current_chunk += word

                # Add the last chunk
                if current_chunk:
                    result.append(current_chunk.strip())
            else:
                # No need to split, add the item as is
                result.append(item)
        return result

    def open_email_window(self):
        self.email_window = customtkinter.CTkToplevel(self)
        self.email_window.title("Email Sender")
        self.email_window.attributes("-topmost", True)

        # Email input fields in the new window
        to_entry = customtkinter.CTkEntry(self.email_window, placeholder_text="Recipient Email")
        to_entry.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Send button
        send_button = customtkinter.CTkButton(self.email_window, text="Send Email", command=lambda: self.send_email(to_entry.get()))
        send_button.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

    def send_email(self,to_email):
        #frame = recipe_frames[recipe_name]
        body = self.rec_frames[self.rec_name]
        subject = self.rec_name
        # Set up the email parameters
        msg = MIMEMultipart()
        msg['From'] = "recipegenerator2024@gmail.com"  # Replace with your email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            # Send the email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Use your mail server
                server.starttls()
                server.login("recipegenerator2024@gmail.com", "fdxs tgut xexe cibo")  # Replace with your credentials
                server.send_message(msg)

            messagebox.showinfo("Success", "Email sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")
        self.email_window.destroy()
    
    def fetch_users_db(self):
        cursor.execute('SELECT * FROM users')
        return cursor.fetchall()  # Fetch all rows
    
    def fetch_reviews_db(self):
        cursor.execute('SELECT * FROM reviews')
        return cursor.fetchall()  # Fetch all rows

    def register(self):
        """Register a new user."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter a username and password.")
            return

        users_db = self.fetch_users_db()
        num_users=len(users_db)
        i=0
        for user in users_db:
            if username==user[1]:
                messagebox.showwarning("Registration Error", "Username already exists.")
            else:
                i+=1
        #counting to ensure we went over all users
        if i==num_users:
            self.insert_user_to_db(username,password)
            messagebox.showinfo("Success", "Account created successfully! You can now log in.")

    def open_review_window(self):
        """Open the review input window."""
        self.reviews_ratings_window = customtkinter.CTkToplevel(self)
        self.reviews_ratings_window.title("Ratings and Reviews")
        self.reviews_ratings_window.attributes("-topmost", True)

        
        self.reviews= self.fetch_reviews_db() # Load existing reviews
        self.selected_rating = 0  # Track the selected rating

        # Create star buttons
        self.star_frame = customtkinter.CTkFrame(self.reviews_ratings_window)
        self.star_frame.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.stars = []
        for i in range(1, 6):
            star_button = customtkinter.CTkButton(self.star_frame, text='⭐', command=lambda i=i: self.select_rating(i), width=40)
            star_button.grid(row=0, column=i-1)
            self.stars.append(star_button)

        self.comment_label = customtkinter.CTkLabel(self.reviews_ratings_window, text="Comment:")
        self.comment_label.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.comment_entry = customtkinter.CTkEntry(self.reviews_ratings_window)
        self.comment_entry.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.submit_button = customtkinter.CTkButton(self.reviews_ratings_window, text="Submit Review", command = self.submit_review)
        self.submit_button.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.view_reviews_button = customtkinter.CTkButton(self.reviews_ratings_window, text="View Past Reviews", command = self.view_reviews)
        self.view_reviews_button.grid(padx=(20, 20), pady=(20, 20), sticky="nsew")

    def select_rating(self, rating):
        """Select a rating and visually update the star buttons."""
        self.selected_rating = rating
        for i, star in enumerate(self.stars):
            star.configure(fg_color="yellow" if i < rating else "gray")

    def submit_review(self):
        """Submit a new review."""
        comment = self.comment_entry.get()

        if self.selected_rating > 0 and comment:
            self.insert_review_to_db(datetime.date.today().strftime("%Y-%m-%d"),self.current_username,self.rec_name,self.selected_rating,comment)
            self.selected_rating = 0  # Reset selected rating
            self.comment_entry.delete(0, customtkinter.END)
            self.reset_stars()
            messagebox.showinfo("Success", "Review submitted successfully!")
        else:
            messagebox.showwarning("Input Error", "Please select a rating and enter a comment.")
        
        self.reviews_ratings_window.destroy()
   
    def reset_stars(self):
        """Reset the visual representation of stars."""
        for star in self.stars:
            star.configure(fg_color="gray")

    def view_reviews(self):
        """Open a new window to display past reviews."""
        reviews_window = customtkinter.CTkToplevel(self.master)
        reviews_window.title("All Reviews")
        reviews_window.attributes("-topmost", True)

        # Create a frame for the table
        table_frame = customtkinter.CTkFrame(reviews_window)
        table_frame.grid(pady=10)

        # Create table headers
        customtkinter.CTkLabel(table_frame, text="Date", width=10).grid(row=0, column=0, padx=5, pady=5)
        customtkinter.CTkLabel(table_frame, text="Username", width=10).grid(row=0, column=1, padx=5, pady=5)
        customtkinter.CTkLabel(table_frame, text="Rating", width=10).grid(row=0, column=2, padx=5, pady=5)
        customtkinter.CTkLabel(table_frame, text="Comment", width=50).grid(row=0, column=3, padx=5, pady=5)

        # Add past reviews to the table
        cursor.execute('SELECT * FROM reviews')
        reviews = cursor.fetchall()
        for idx,review in enumerate(reviews):
            if review[2]==self.rec_name:
                customtkinter.CTkLabel(table_frame, text=review[0]).grid(row=idx + 1, column=0, padx=5, pady=5)
                customtkinter.CTkLabel(table_frame, text=review[1]).grid(row=idx + 1, column=1, padx=5, pady=5)
                customtkinter.CTkLabel(table_frame, text=str(review[3])).grid(row=idx + 1, column=2, padx=5, pady=5)
                customtkinter.CTkLabel(table_frame, text=review[4]).grid(row=idx + 1, column=3, padx=5, pady=5)

        self.reviews_ratings_window.destroy()
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

if __name__ == "__main__":
    app = App()
    app.mainloop()
    cursor.close()
    conn.close()
    
