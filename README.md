# FastAPI Image Processing System

This project is a FastAPI-based system designed to efficiently process image data from CSV files. It asynchronously processes images, compressing them by 50% of their original quality, and stores the processed images locally. The system also provides APIs to upload CSV files, check processing status, and call a webhook after processing.

## Table of Contents

-   [Installation](#installation)
-   [Running the Project](#running-the-project)
-   [Technical Design Document](#technical-design-document)
    -   [System Diagram](#system-diagram)
    -   [Component Descriptions](#component-descriptions)
        -   [Image Processing Service Interaction](#image-processing-service-interaction)
        -   [Webhook Handling](#webhook-handling)
        -   [Database Interaction](#database-interaction)
-   [Database Schema](#database-schema)
-   [API Documentation](#api-documentation)
-   [API Endpoints](#api-endpoints)
-   [Asynchronous Worker Functions](#asynchronous-worker-functions)
-   [License](#license)

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

    Install Docker and run the following command to start Redis in Docker.

    ```bash
    docker run --name redis -d -p 6379:6379 redis
    ```

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

    Start the Celery worker process:

    ```bash
    celery -A main.celery worker --loglevel=info
    ```

## Technical Design Document

Following is a high-level design of the project:

![high-level-design](https://github.com/pragati08hbtu/fast-api-image-processing/blob/main/high-level-design.png?raw=true)

### Component Descriptions

#### Image Processing API

This service handles the incoming requests for image processing. It validates the CSV content, updates the database with the request details and enqueues the CSV data to Redis message broker and returns the request id to the user. It also contains a status endpoint to return the image processing status from the database.

#### Redis Message Queue

This serves as a message broker to faciliate asynchronous communication between Image Processing API and Celery Worker Service.

#### Celery Worker Service

This service runs continuously in the background and picks up the messages from Redis for image processing. It then fetches images from URLs, compresses them, and stores them in the database. It also updates the database with the status of each image processing request. It additionally calls an optional webhook URL from the request details to notify external clients about completion status.

#### Database Interaction

The application uses SQLite to store the status of processing requests, input image URLs, and output image paths. The database is designed to ensure that each processing request and its associated data are tracked efficiently.

## Database Schema

### **Tables**

1. **`image_processing_requests`**

    | Column        | Type    | Description                                                 |
    | ------------- | ------- | ----------------------------------------------------------- |
    | `id`          | Integer | Primary Key                                                 |
    | `request_id`  | String  | Unique Key                                                  |
    | `status`      | String  | Status of the processing (`Pending`, `Failed`, `Completed`) |
    | `output_csv`  | Text    | Contains the output CSV file as text                        |
    | `webhook_url` | String  | Optional webhook URL to notify on completion                |

## API Documentation

API documentation is available at: http://20.244.98.113/docs.

Postman Collection: [postman-collection](https://github.com/pragati08hbtu/fast-api-image-processing/blob/main/fast_api_image_processing.postman_collection).

## API Endpoints

### **1. Upload CSV**

-   **URL**: `/upload/`
-   **Method**: `POST`
-   **Description**: Accepts a CSV file, validates the formatting, and returns a unique request ID.

### **2. Check Status**

-   **URL**: `/status/{request_id}/`
-   **Method**: `GET`
-   **Description**: Allows users to query the processing status using the request ID.

### **3. Webhook Notification**

-   **Description**: (Optional) After processing all images, a webhook endpoint can be triggered with the results.

## Asynchronous Worker Functions

### **1. Image Processing Task**

The asynchronous worker function for processing images is implemented using Celery. It performs the following tasks:

-   **Fetch Images**: Downloads images from the provided URLs.
-   **Compress Images**: Reduces the image size by 50% of the original quality using the PIL library.
-   **Save Locally**: Stores the processed images locally and updates the output URLs in the database.
-   **Update Status**: Updates the processing status in the database.
-   **Trigger Webhook**: If a webhook URL is provided, the function will send a POST request to the webhook with the processing results.

## License

The project is licensed under MIT license.
