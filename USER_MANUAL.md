# DAW-Sheet User Manual

## Introduction

Welcome to DAW-Sheet! This application helps you manage your songs, including lyrics and chords. It consists of a web frontend, a backend API, and a database.

## Getting Started

### Prerequisites

- Docker and Docker Compose must be installed on your system.

### Launching the Application

To start the application, simply run the `start-app.bat` script. This will start all the necessary services in the background.

```bash
.\start-app.bat
```

After a few moments, the application will be accessible at the following URLs:

- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000](http://localhost:8000)

### Stopping the Application

To stop the application, run the following command in your terminal:

```bash
docker-compose down
```

## Using the Application

When you first launch the application, you will notice that the song list is empty. This is normal. The application starts with a fresh, empty database. You need to add songs to see them in the list.

### Adding a Song

1.  Navigate to the **Songs** page (usually the main page).
2.  You will see a form with fields for **Title**, **Artist**, and **Content**.
3.  Fill in the details for your song.
4.  Click the **Create** button.

Your new song will appear in the song list.

### Viewing and Editing a Song

- To **view** the details of a song, click on its title in the song list or click the "View" button.
- To **edit** a song, click the **Edit** button next to the song in the list. This will open an editor where you can change the song's details.
- To **delete** a song, click the **Delete** button.

## Troubleshooting

### The song list is empty

As mentioned above, this is expected on the first run or if you haven't added any songs yet. Follow the instructions in the "Adding a Song" section to populate your song list.

### I'm seeing errors

If you encounter errors, you can check the logs of the services using the following command:

```bash
docker-compose logs -f
```

This will show you the logs for the frontend and backend, which can help in diagnosing the problem.
