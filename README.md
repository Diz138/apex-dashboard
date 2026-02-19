# Apex Legends Dashboard

A dashboard for visualizing Apex Legends statistics, built with Astro and Python. This project consists of two main components:

- **Frontend Dashboard**: An Astro-based web interface for displaying player statistics
- **Python Retriever**: A Python script that fetches and stores Apex Legends stats data from Apex Legends Staus api

## Setup

### Frontend (Astro Dashboard)

1. Install Node.js dependencies:
   ```sh
   npm install
   ```

### Python Retriever

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already:
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Install Python dependencies (uv will automatically create and manage the virtual environment):
   ```sh
   uv sync
   ```

3. Configure environment variables:
   - Create a `.env` file in the project root
   - Add the following variables:
     ```env
     APEX_API_KEY=your_api_key_here
     APEX_UIDS=123456789,987654321,555555555
     ```
   - `APEX_API_KEY`: Your API key from [Apex Legends Status API](https://apexlegendsapi.com/)
   - `APEX_UIDS`: Comma-separated list of player UIDs to track

4. Run the stats retriever
   -  ```sh
      uv run retriever/retrieve_stats.py
      ```

### Start the Astro Dashboard

```sh
npm run dev
```

The dashboard will be available at `http://localhost:4321`

