import base64  
import requests  
import json  
import tkinter as tk  
from tkinter import ttk, simpledialog, messagebox  
import csv  
  
class ForioDataDownloader:  
   def __init__(self, root):  
      self.root = root  
      self.root.title("Forio Data Downloader")  
  
      # Create a frame for the API key and secret  
      api_frame = ttk.Labelframe(self.root, text="API Credentials")  
      api_frame.grid(row=0, column=0, padx=10, pady=10, sticky="W")  
  
      # Create entry fields for API key and secret  
      self.api_key_label = ttk.Label(api_frame, text="API Key:")  
      self.api_key_label.grid(row=0, column=0, padx=10, pady=10)  
      self.api_key_entry = ttk.Entry(api_frame, width=50)  
      self.api_key_entry.grid(row=0, column=1, padx=10, pady=10)  
  
      self.api_secret_label = ttk.Label(api_frame, text="API Secret:")  
      self.api_secret_label.grid(row=1, column=0, padx=10, pady=10)  
      self.api_secret_entry = ttk.Entry(api_frame, width=50, show="*")  
      self.api_secret_entry.grid(row=1, column=1, padx=10, pady=10)  
  
      # Create a frame for the Forio credentials  
      forio_frame = ttk.Labelframe(self.root, text="Forio Credentials")  
      forio_frame.grid(row=1, column=0, padx=10, pady=10, sticky="W")  
  
      # Create entry fields for Forio username, project name, and model name  
      self.username_label = ttk.Label(forio_frame, text="Username:")  
      self.username_label.grid(row=0, column=0, padx=10, pady=10)  
      self.username_entry = ttk.Entry(forio_frame, width=50)  
      self.username_entry.grid(row=0, column=1, padx=10, pady=10)  
  
      self.project_name_label = ttk.Label(forio_frame, text="Project Name:")  
      self.project_name_label.grid(row=1, column=0, padx=10, pady=10)  
      self.project_name_entry = ttk.Entry(forio_frame, width=50)  
      self.project_name_entry.grid(row=1, column=1, padx=10, pady=10)  
  
      self.model_name_label = ttk.Label(forio_frame, text="Model Name:")  
      self.model_name_label.grid(row=2, column=0, padx=10, pady=10)  
      self.model_name_entry = ttk.Entry(forio_frame, width=50)  
      self.model_name_entry.grid(row=2, column=1, padx=10, pady=10)  
  
      # Create a frame for the variables  
      variables_frame = ttk.Labelframe(self.root, text="Variables")  
      variables_frame.grid(row=2, column=0, padx=10, pady=10, sticky="W")  
  
      # Create a text field for variables  
      self.variables_label = ttk.Label(variables_frame, text="Variables (comma-separated):")  
      self.variables_label.grid(row=0, column=0, padx=10, pady=10)  
      self.variables_entry = tk.Text(variables_frame, width=50, height=5)  
      self.variables_entry.grid(row=1, column=0, padx=10, pady=10)  
  
      # Create a frame for the group selection  
      group_frame = ttk.Labelframe(self.root, text="Select Groups")  
      group_frame.grid(row=3, column=0, padx=10, pady=10, sticky="W")  
  
      # Create a listbox for groups  
      self.group_listbox = tk.Listbox(group_frame, selectmode=tk.MULTIPLE)  
      self.group_listbox.grid(row=0, column=0, padx=10, pady=10)  
  
      # Create a button to add a new group  
      add_group_button = ttk.Button(group_frame, text="Add Group", command=self.add_group)  
      add_group_button.grid(row=1, column=0, padx=10, pady=10)  
  
      # Create a button to remove selected groups  
      remove_group_button = ttk.Button(group_frame, text="Remove Group(s)", command=self.remove_selected_groups)  
      remove_group_button.grid(row=2, column=0, padx=10, pady=10)  
  
      # Create a button to download data  
      download_button = ttk.Button(self.root, text="Download Data", command=self.download_data)  
      download_button.grid(row=4, column=0, padx=10, pady=10)  
  
   def add_group(self):  
      """  
      Adds a new group to the listbox  
      """  
      new_group = simpledialog.askstring("Add Group", "Enter group name:")  
      if new_group:  
        self.group_listbox.insert(tk.END, new_group)  
  
   def remove_selected_groups(self):  
      """  
      Removes selected groups from the listbox  
      """  
      selected_indices = self.group_listbox.curselection()  
      for index in reversed(selected_indices):  
        self.group_listbox.delete(index)  
  
   def url_encode(self, s):  
      """  
      Simple URL encoding without using urllib  
      Replaces commas with %2C for API compatibility  
      """  
      return s.replace(',', '%2C')  
  
   def get_access_token(self):  
      """  
      Retrieve access token using client credentials  
      """  
      # Encode username:secret to Base64  
      credentials = base64.b64encode(f"{self.api_key_entry.get()}:{self.api_secret_entry.get()}".encode('utf-8')).decode('utf-8')  
  
      # Token request headers and payload  
      headers = {  
        'Content-Type': 'application/x-www-form-urlencoded',  
        'Authorization': f'Basic {credentials}'  
      }  
      payload = {'grant_type': 'client_credentials'}  
  
      try:  
        # Make token request  
        response = requests.post(  
           'https://api.forio.com/v2/oauth/token',  
           headers=headers,  
           data=payload  
        )  
        response.raise_for_status()  # Raise an exception for bad responses  
  
        # Extract access token  
        return response.json()['access_token']  
      except requests.RequestException as e:  
        print(f"Error retrieving access token: {e}")  
        return None  
  
   def fetch_forio_data(self, access_token, selected_groups):  
      """  
      Fetch data from Forio API using access token and specified variables  
      """  
      # URL encode the variables  
      encoded_variables = self.url_encode(self.variables_entry.get("1.0", tk.END).strip())  
  
      all_data = []  
      for group in selected_groups:  
        # Build group selection string  
        group_string = f'scope.group={group}'  
  
        # API call headers  
        headers = {  
           'Authorization': f'Bearer {access_token}'  
        }  
  
        try:  
           # Make API request  
           response = requests.get(  
              f'https://forio.com/v2/run/{self.username_entry.get()}/{self.project_name_entry.get()}/;saved=true;trashed=false;model={self.model_name_entry.get()};{group_string}'  
              f'?sort=created&direction=desc&include={encoded_variables}&startRecord=0&endRecord=100',  
              headers=headers  
           )  
           response.raise_for_status()  
           all_data.extend(response.json())  
        except requests.RequestException as e:  
           print(f"Error retrieving data: {e}")  
           return None  
  
      return all_data  
  
   def save_to_csv(self, data, filename):  
      """  
      Save data to a CSV file  
      """  
      with open(filename, 'w', newline='') as csvfile:  
        fieldnames = data[0].keys()  
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  
        writer.writeheader()  
        for row in data:  
           writer.writerow(row)  
  
   def download_data(self):  
      """  
      Downloads data from Forio API and saves it to a CSV file  
      """  
      selected_groups = [self.group_listbox.get(i) for i in self.group_listbox.curselection()]  
      if not selected_groups:  
        messagebox.showerror("Error", "Please select at least one group.")  
        return  
  
      access_token = self.get_access_token()  
      if not access_token:  
        messagebox.showerror("Error", "Failed to retrieve access token.")  
        return  
  
      data = self.fetch_forio_data(access_token, selected_groups)  
      if not data:  
        messagebox.showerror("Error", "Failed to fetch data from Forio.")  
        return  
  
      self.save_to_csv(data, "forio_data.csv")  
      messagebox.showinfo("Success", "Data saved to forio_data.csv")  
  
if __name__ == '__main__':  
   root = tk.Tk()  
   app = ForioDataDownloader(root)  
   root.mainloop()
