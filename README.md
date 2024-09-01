# FastAPI Image Processing System

This project is a FastAPI-based system designed to efficiently process image data from CSV files. It asynchronously processes images, compressing them by 50% of their original quality, and stores the processed images locally. The system also provides APIs to upload CSV files, check processing status, and call a webhook after processing.

## Table of Contents

- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Asynchronous Worker Functions](#asynchronous-worker-functions)
- [License](#license)

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/pragati08hbtu/fastapi-image-processing.git
    cd fastapi-image-processing
    ```

2. **Set up a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up Redis:**

    Install Redis for your system and start the Redis server.

5. **Configure environment variables:**

    Create a `.env` file and add your Redis credentials and the database URL.

    ```plaintext
    REDIS_URL=redis://localhost:6379/0
    DATABASE_URL=sqlite:///./requests.db
    ```

## Running the Project

1. **Start the FastAPI server:**

    ```bash
    uvicorn main:app --reload
    ```

    The server will be running at `http://127.0.0.1:8000` and Swagger doc is accessible at `http://127.0.0.1:8000/docs`.

2. **Run asynchronous workers:**

    Start the celery worker process:

    ```bash
    celery -A main.celery worker --loglevel=info
    ```

## Database Schema

### **Tables**

1. **`image_processing_requests`**

    | Column          | Type    | Description                                  |
    |-----------------|---------|----------------------------------------------|
    | `id`            | Integer | Primary Key                                  |
    | `request_id`    | String  | Unique Key                                   |
    | `status`        | String  | Status of the processing (`Pending`, `Failed`, `Completed`) |
    | `output_csv`    | Text    | Contains the output CSV file as text         |
    | `webhook_url`   | String  | Optional webhook URL to notify on completion |

## API Endpoints

### **1. Upload CSV**

- **URL**: `/upload/`
- **Method**: `POST`
- **Description**: Accepts a CSV file, validates the formatting, and returns a unique request ID.

### **2. Check Status**

- **URL**: `/status/{request_id}/`
- **Method**: `GET`
- **Description**: Allows users to query the processing status using the request ID.

### **3. Webhook Notification**

- **Description**: (Optional) After processing all images, a webhook endpoint can be triggered with the results.

## Asynchronous Worker Functions

### **1. Image Processing Task**

The asynchronous worker function for processing images is implemented using Celery. It performs the following tasks:

- **Fetch Images**: Downloads images from the provided URLs.
- **Compress Images**: Reduces the image size by 50% of the original quality using the PIL library.
- **Save Locally**: Stores the processed images locally and updates the output URLs in the database.
- **Update Status**: Updates the processing status in the database.
- **Trigger Webhook**: If a webhook URL is provided, the function will send a POST request to the webhook with the processing results.

## License

The project is licensed under MIT license.