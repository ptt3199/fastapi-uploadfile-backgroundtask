# File Upload Background Tasks API

This API provides endpoints for uploading files with speed control, pausing, resuming, and canceling uploads using FastAPI UploadFile and BackgroundTasks.

## Table of Contents

1. [Installation](#installation)
2. [Dependencies](#dependencies)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [API Endpoints](#api-endpoints)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)
9. [License](#license)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/ptt3199/fastapi-uploadfile-backgroundtask.git
   cd fastapi-uploadfile-backgroundtask
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```
   fastapi dev app/main.py
   ```
   For production, use `fastapi run app/main.py`

The API will be available at `http://localhost:8000`.

## Dependencies

- Python 3.9+
- FastAPI
- python-multipart
- aiofiles

See `requirements.txt` for the full list of dependencies and their versions.

## Configuration

The following environment variables can be set to configure the API:

- `UPLOAD_DIR`: Directory where uploaded files are stored (default: "uploads")
- `DEFAULT_UPLOAD_SPEED`: Default upload speed in bytes per second (default: 1048576)

You can set these in a `.env` file in the project root or export them in your shell.

## Usage

After starting the server, you can interact with the API using HTTP requests. The API supports file uploads with speed control, as well as pausing, resuming, and canceling uploads.

Here I use a json file to store the upload status, and the file content is stored in the `uploads` directory for simplicity.

## API Endpoints

### 1. Start Upload

- **URL:** `/api/upload`
- **Method:** `POST`
- **Query Parameters:**
  - `speed`: Upload speed in bytes per second (default: 1048576 B/s or 1 MB/s)
- **Body:** Form-data with file
- **Response:**
  ```json
  {
    "upload_id": "string",
    "status": "started",
    "total_size": integer,
    "speed": integer
  }
  ```

### 2. Pause Upload

- **URL:** `/api/upload/{upload_id}/pause`
- **Method:** `POST`
- **Response:**
  ```json
  {
    "status": "paused"
  }
  ```

### 3. Resume Upload

- **URL:** `/api/upload/{upload_id}/resume`
- **Method:** `POST`
- **Query Parameters:**
  - `speed`: New upload speed in bytes per second (optional)
- **Response:**
  ```json
  {
    "status": "resumed",
    "speed": integer
  }
  ```

### 4. Cancel Upload

- **URL:** `/api/upload/{upload_id}/cancel`
- **Method:** `POST`
- **Response:**
  ```json
  {
    "status": "canceled"
  }
  ```

### 5. Get Upload Status

- **URL:** `/api/upload/{upload_id}/status`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "status": "string",
    "filename": "string",
    "uploaded_size": integer,
    "total_size": integer,
    "current_speed": float,
    "target_speed": integer
  }
  ```

### 6. List All Uploads

- **URL:** `/api/uploads`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "uploads": [
      {
        "upload_id": "string",
        "filename": "string",
        "status": "string",
        "uploaded_size": integer,
        "total_size": integer,
        "current_speed": float,
        "target_speed": integer
      }
    ]
  }
  ```

### 7. List All Files

- **URL:** `/api/files`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "files": [
      {
        "upload_id": "string",
        "filename": "string",
        "status": "string"
      }
    ]
  }
  ```

### 8. Delete a File

- **URL:** `/api/files/{upload_id}`
- **Method:** `DELETE`
- **Response:**
  ```json
  {
    "status": "deleted",
    "upload_id": "string",
    "filename": "string"
  }
  ```

## Examples

### Starting an Upload
```bash
curl -X POST "http://localhost:8000/api/upload?speed=1048576" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@/path/to/your/file.zip"
```

### Pausing an Upload
```bash
curl -X POST "http://localhost:8000/api/upload/{upload_id}/pause" -H "accept: application/json"
```
### Resuming an Upload
```bash
curl -X POST "http://localhost:8000/api/upload/{upload_id}/resume?speed=2097152" -H "accept: application/json"
```

### Canceling an Upload

```bash
curl -X POST "http://localhost:8000/api/upload/{upload_id}/cancel" -H "accept: application/json"
```
### Getting Upload Status
```bash
curl "http://localhost:8000/api/upload/{upload_id}/status" -H "accept: application/json"
```

### Listing All Uploads

```bash
curl -X GET "http://localhost:8000/api/uploads" -H "accept: application/json"
```
Replace `{upload_id}` with the actual upload ID returned when starting the upload.

### Listing All Files

```bash
curl -X GET "http://localhost:8000/api/files" -H "accept: application/json"
```

### Deleting a File

```bash
curl -X DELETE "http://localhost:8000/api/files/{upload_id}" -H "accept: application/json"
```
Replace `{upload_id}` with the actual upload ID.

## Troubleshooting

- If you encounter "Address already in use" errors, make sure no other service is running on port 8000, or specify a different port using `fastapi run dev --port 8080`.
- If uploads are failing, check the server logs for detailed error messages.
- Ensure that the `UPLOAD_DIR` is writable by the user running the FastAPI server.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.