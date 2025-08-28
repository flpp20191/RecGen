# RecGen
A brief description of what this Django project is about and its main features.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Clone the Repository](#step-1-clone-the-repository)
- [Step 2: Create a Virtual Environment](#step-2-create-a-virtual-environment)
- [Step 3: Install Dependencies](#step-3-install-dependencies)
- [Step 4: Configure the Database and Environment Variables](#step-4-configure-the-database-and-environment-variables)
- [Step 5: Run the Setup Command](#step-5-run-the-setup-command)
- [Step 6: Run the Development Server](#step-6-run-the-development-server)
- [Step 7: Upload Data Using Excel Files](#step-7-upload-data-using-excel-files)
- [Step 8: Set Up Google SMTP Server](#step-8-set-up-google-smtp-server)
- [Additional Commands](#additional-commands)
- [Deactivating the Virtual Environment](#deactivating-the-virtual-environment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before you begin, make sure you have the following installed on your system:

- **Python 3.x**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python's package installer (included with Python 3.x)
- (optional) **MySQL** : Ensure that MySQL is installed and running on your machine if you choose to use them.

## Step 1: Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/flpp20191/RecGen.git
cd RecGen
```

## Step 2: Create a Virtual Environment

It’s recommended to use a virtual environment to manage project dependencies. Follow the instructions below based on your operating system.

### On macOS and Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

After activating the virtual environment, you should see `(venv)` at the beginning of your command line prompt.

## Step 3: Install Dependencies

With the virtual environment activated, install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This command will install all necessary packages for the Django project.

## Step 4: Configure the Database and Environment Variables

The project can be configured to use SQLite or MySQL. By default, Django is configured to use SQLite, but you can switch to another database if needed.

### 1. **Copy `.env.example` to `.env`**:

In the root of your project directory, copy the `.env.example` file to create a new `.env` file:

#### On macOS/Linux:

```bash
cp .env.example .env
```

#### On Windows:

```bash
copy .env.example .env
```

### 2. **Generate a Secure `SECRET_KEY`**:

To ensure the `SECRET_KEY` is secure, generate a random key by running the following command:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

This will output a secure key that you should copy and paste into your `.env` file under the `SECRET_KEY` variable:

```bash
SECRET_KEY=placeholder_generated_secret_key
```

### 3. **Configure the Database**:

In your `.env` file, set the `DB_ENGINE` to select which database backend you want to use. The available options are `sqlite3`, `mysql`.

#### **Default SQLite Setup**

If you want to use SQLite (default setup), set the following in your `.env` file:

```bash
DB_ENGINE=sqlite3
```

The default SQLite configuration requires no additional setup. It will create a `db.sqlite3` file in the project directory.

#### **Optional MySQL Setup**

To use MySQL, set the following in your `.env` file:

```bash
DB_ENGINE=mysql
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=3306
```

Ensure that your MySQL server is up and running before proceeding.


## Step 5: Run the Setup Command

After configuring the environment variables, run the setup command to create the database, apply migrations, and populate initial data:

```bash
python manage.py setup
```

This command will:

- Connect to the database using the credentials from the `.env` file.
- Create the database (if it doesn't already exist).
- Run all Django migrations to set up the database schema.
- Populate initial data, such as entries in the `Question_type` table.

## Step 6: Run the Development Server

Once the setup is complete, start the Django development server:

```bash
python manage.py runserver
``` 

Visit `http://127.0.0.1:8000/` in your web browser to see the project in action.

## Step 7: Upload Data Using Excel Files

To upload data to the system, use the provided Excel files. You can download the template Excel file, fill it out, and upload it via the interface.

1. **Download the Excel Template**:
   Navigate to `Analytics` > `Data Upload` in the application to download the Excel template file.

2. **Fill Out the Excel File**:
   - The Excel file contains multiple sheets including `Category`, `Recommendation`, `Question`, and `RecommendationQuestion`.
   - Fill in the appropriate data for each sheet as per the headers provided.
   - Ensure that the data in the sheets is consistent to avoid validation errors during the upload.

3. **Upload the Filled Excel File**:
   - Once you have filled out the Excel file, go to `Analytics` > `Data Upload` and use the upload form to upload the completed file.
   - The system will validate the data, and if successful, insert it into the database.
   - Any errors found during the validation process will be displayed for correction.

## Step 8: Set Up Google SMTP Server

To enable email functionality in your Django application using Google's SMTP server, follow these steps:

1. **Enable Less Secure Apps**:
   - Go to your Google Account settings and enable access for less secure apps: [Less Secure Apps](https://myaccount.google.com/lesssecureapps).
   - Note: This option may not be available if you have 2-Step Verification enabled. You may need to set up an App Password instead.

2. **Set Up App Password (Optional)**:
   - If you have 2-Step Verification enabled, you need to create an App Password.
   - Go to your Google Account's Security settings and create an App Password: [App Passwords](https://myaccount.google.com/apppasswords).
   - Use this App Password instead of your regular Google account password.

3. **Configure SMTP Settings in `.env`**:
   Add the following SMTP settings to your `.env` file:

   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_email_password_or_app_password
   DEFAULT_FROM_EMAIL=your_email@gmail.com
   ```

   Replace `your_email@gmail.com` with your Gmail address and `your_email_password_or_app_password` with either your Google account password or the App Password you generated.

4. **Test the Email Setup**:
   - You can test if the email setup is working correctly by running the Django shell:

   ```bash
   python manage.py shell
   ```

   Then run the following commands in the shell:

   ```python
   from django.core.mail import send_mail
   send_mail(
       'Test Email',
       'This is a test email from Django.',
       'your_email@gmail.com',
       ['recipient@example.com'],
       fail_silently=False,
   )
   ```

   If the email is sent successfully, your SMTP setup is working.

## Additional Commands

### Creating a Superuser

To create a superuser account for accessing the Django admin interface, run:

```bash
python manage.py createsuperuser
```

Follow the on-screen prompts to set up the username, email, and password.

### Running Tests

If the project includes tests, you can run them with:

```bash
python manage.py test
```

## Deactivating the Virtual Environment

When you are done working on the project, deactivate the virtual environment by running:

```bash
deactivate
```

## Troubleshooting

- **Database Connection Issues**: Ensure that your database server is running and that the credentials in the `.env` file are correct.
- **Missing Packages**: If you encounter missing package errors, verify that your virtual environment is activated before running any commands.
- **Excel File Upload Errors**: Ensure that the data in the Excel file is consistent, all required fields are filled, and all sheet names match the expected format (`Category`, `Recommendation`, `Question`, `RecommendationQuestion`).
- **Email Sending Issues**: Verify your SMTP settings in the `.env` file and ensure that you have enabled access for less secure apps or set up an App Password if using Google SMTP.

## Contributing

If you'd like to contribute to this project, you can fork the repository and submit a pull request with your changes.

Copyright 2025 RecGenProject

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0


Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
